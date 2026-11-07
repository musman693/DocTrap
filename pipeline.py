from __future__ import annotations

import hashlib
import time
from datetime import datetime
from pathlib import Path

from context import context_adjust
from db import log_audit
from ingestion import ingest
from ml_classifier import InjectionClassifier, ml_findings
from models import Finding, ParsedDocument, RiskReport, TextSpan
from pdf_parser import parse_pdf_bytes
from docx_parser import parse_docx_bytes
from rules import rule_findings
from scoring import score_report
from unicode_inspect import unicode_findings


def scan_document(path: str | Path | bytes, filename: str | None = None) -> RiskReport:
    """Scan a document and return a risk report."""
    start = time.time()
    if isinstance(path, (bytes, bytearray)):
        file_bytes = bytes(path)
        if filename is None:
            filename = "upload.bin"
    else:
        p = Path(path)
        file_bytes = p.read_bytes()
        filename = filename or p.name
    doc = ingest(file_bytes, filename)
    parsed: ParsedDocument
    if filename.lower().endswith(".pdf"):
        parsed = parse_pdf_bytes(file_bytes, doc_id=doc.sha256, filename=filename)
    elif filename.lower().endswith(".docx"):
        parsed = parse_docx_bytes(file_bytes, doc_id=doc.sha256, filename=filename)
    else:
        raise ValueError("Unsupported file type")

    findings: list[Finding] = []
    findings.extend(unicode_findings(parsed.spans))
    findings.extend(rule_findings(parsed.spans))
    classifier = InjectionClassifier(['ignore previous instructions', 'this is normal text'], [1, 0])
    findings.extend(ml_findings(parsed.spans, classifier, threshold=0.5))
    findings = context_adjust(findings)
    report = score_report(findings, doc.id, doc.filename, doc.sha256, doc.file_type)
    report.scan_time_ms = (time.time() - start) * 1000
    report.created_at = datetime.utcnow()
    log_audit(doc.id, "scan", detail=f"risk={report.risk_score}")
    return report
