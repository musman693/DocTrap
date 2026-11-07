from __future__ import annotations

import hashlib
import re
from typing import Any

try:
    import fitz
except Exception:  # pragma: no cover
    fitz = None

from models import ParsedDocument, Source, TextSpan


def parse_pdf_bytes(file_bytes: bytes, doc_id: str, filename: str) -> ParsedDocument:
    spans: list[TextSpan] = []
    page_count = 0
    metadata: dict[str, Any] = {}
    if fitz is not None:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = doc.page_count
        metadata = {k: v for k, v in (doc.metadata or {}).items() if v is not None}
        for page_index in range(page_count):
            page = doc[page_index]
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = (span.get("text") or "").strip()
                        if not text:
                            continue
                        bbox = tuple(span.get("bbox", (0, 0, 0, 0)))
                        font_size = float(span.get("size") or 0.0)
                        color = span.get("color")
                        if color is not None:
                            color = "#%06x" % (int(color) & 0xFFFFFF)
                        spans.append(TextSpan(
                            text=text,
                            source=Source.BODY,
                            page=page_index + 1,
                            location=f"page {page_index + 1} line",
                            bbox=bbox,
                            font_size=font_size,
                            color=color,
                            flags={"hidden": font_size < 2.0},
                        ))
    else:
        text = re.sub(r"\s+", " ", file_bytes.decode("latin-1", errors="ignore"))[:2000]
        spans.append(TextSpan(text=text, source=Source.BODY, page=1, location="fallback", flags={"fallback": True}))
    digest = hashlib.sha256(file_bytes).hexdigest()
    return ParsedDocument(doc_id=doc_id, filename=filename, file_type="pdf", sha256=digest, spans=spans, page_count=page_count, metadata=metadata)
