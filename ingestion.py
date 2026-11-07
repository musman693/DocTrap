from __future__ import annotations

import hashlib
import os
import re
import zipfile
from pathlib import Path
from uuid import uuid4

from config import get_config, get_data_root
from db import log_audit, save_document_record
from models import DocumentRecord


def sanitize_filename(name: str, max_len: int = 120) -> str:
    clean = re.sub(r"[\\/\r\n]+", "_", name or "upload")
    clean = clean.strip(". ")[:max_len]
    return clean or "upload"


def validate_file(file_bytes: bytes, filename: str) -> tuple[str, str]:
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in {"pdf", "docx"}:
        raise ValueError("Only .pdf and .docx files are allowed.")
    if ext == "pdf" and not file_bytes.startswith(b"%PDF-"):
        raise ValueError("File does not look like a valid PDF.")
    if ext == "docx":
        if not file_bytes.startswith(b"PK\x03\x04"):
            raise ValueError("File does not look like a valid DOCX.")
        with zipfile.ZipFile(__import__('io').BytesIO(file_bytes)) as zf:
            names = zf.namelist()
            if "word/document.xml" not in names:
                raise ValueError("DOCX archive missing word/document.xml.")
            conf = get_config()
            total_uncompressed = sum(info.file_size for info in zf.infolist())
            max_bytes = conf.get("max_docx_uncompressed_mb", 100) * 1024 * 1024
            if total_uncompressed > max_bytes:
                raise ValueError("DOCX archive exceeds uncompressed size limit.")
            if len(names) > conf.get("max_docx_entries", 2000):
                raise ValueError("DOCX archive exceeds entry count limit.")
    return ext, "ok"


def ingest(file_bytes: bytes, filename: str) -> DocumentRecord:
    """Validate, hash, store, and persist a document upload."""
    validate_file(file_bytes, filename)
    dig = hashlib.sha256(file_bytes).hexdigest()
    conf = get_config()
    max_size = int(conf.get("max_upload_mb", 20)) * 1024 * 1024
    if len(file_bytes) > max_size:
        raise ValueError(f"Uploaded file exceeds {conf.get('max_upload_mb', 20)} MB limit.")
    ext = Path(filename).suffix.lower().lstrip(".")
    data_root = get_data_root()
    uploads_dir = data_root / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{dig}.{ext}"
    destination = uploads_dir / stored_name
    if not destination.exists():
        with destination.open("wb") as fh:
            fh.write(file_bytes)
        os.chmod(destination, 0o444)
    doc_id = str(uuid4())
    rec = DocumentRecord(
        id=doc_id,
        filename=sanitize_filename(filename),
        sha256=dig,
        file_type=ext,
        size=len(file_bytes),
        status="uploaded",
        original_path=str(destination),
        sanitized_path="",
    )
    save_document_record(rec)
    log_audit(doc_id, "upload", detail=f"stored as {stored_name}")
    return rec
