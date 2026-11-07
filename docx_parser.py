from __future__ import annotations

import hashlib
import io
import zipfile
from xml.etree import ElementTree as ET

from models import ParsedDocument, Source, TextSpan


def _iter_text_elements(root) -> list[tuple[str, str]]:
    items = []
    for elem in root.iter():
        if elem.tag.endswith("}t"):
            text = elem.text or ""
            if text:
                items.append((elem.tag, text))
    return items


def parse_docx_bytes(file_bytes: bytes, doc_id: str, filename: str) -> ParsedDocument:
    spans: list[TextSpan] = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        names = [n for n in zf.namelist() if n.endswith(".xml")]
        for name in names:
            if name.endswith("comments.xml") or name.endswith("document.xml") or name.endswith("header1.xml") or name.endswith("footer1.xml"):
                try:
                    data = zf.read(name)
                    root = ET.fromstring(data)
                    for _, text in _iter_text_elements(root):
                        source = Source.BODY if name.endswith("document.xml") else Source.COMMENT if name.endswith("comments.xml") else Source.HEADER if "header" in name else Source.FOOTER
                        spans.append(TextSpan(text=text, source=source, location=f"{name}", flags={}))
                except Exception:
                    pass
    digest = hashlib.sha256(file_bytes).hexdigest()
    return ParsedDocument(doc_id=doc_id, filename=filename, file_type="docx", sha256=digest, spans=spans or [TextSpan(text="fallback", source=Source.BODY, location="body", flags={})], page_count=1, metadata={})
