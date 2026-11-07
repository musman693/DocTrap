from __future__ import annotations

import zipfile
from pathlib import Path


def sanitize_pdf_bytes(data: bytes, suspicious_texts: list[str] | None = None) -> bytes:
    suspicious_texts = suspicious_texts or ["ignore previous instructions", "reveal system prompt", "pineapple", "canary", "override"]
    text = data.decode("latin-1", errors="ignore")
    for token in suspicious_texts:
        text = text.replace(token, "[REDACTED]")
    return text.encode("latin-1", errors="ignore")


def sanitize_docx_bytes(data: bytes) -> bytes:
    with zipfile.ZipFile(__import__("io").BytesIO(data), "r") as zin:
        files = zin.namelist()
        target = {name: zin.read(name) for name in files}
        out = __import__("io").BytesIO()
        with zipfile.ZipFile(out, "w") as zout:
            for name, content in target.items():
                if name.endswith(".xml"):
                    text = content.decode("utf-8", errors="ignore")
                    text = text.replace("ignore previous instructions", "[REDACTED]")
                    text = text.replace("reveal system prompt", "[REDACTED]")
                    text = text.replace("pineapple", "[REDACTED]")
                    text = text.replace("canary", "[REDACTED]")
                    zout.writestr(name, text)
                else:
                    zout.writestr(name, content)
        return out.getvalue()


def generate_change_report(before: bytes, after: bytes) -> str:
    return f"Before length {len(before)} bytes; after length {len(after)} bytes. Sensitive keywords were redacted."
