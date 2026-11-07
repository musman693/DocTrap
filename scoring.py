from __future__ import annotations

from datetime import datetime

from models import Finding, RiskReport


def score_report(findings: list[Finding], doc_id: str, filename: str, sha256: str, file_type: str) -> RiskReport:
    hidden = sum(1 for f in findings if "hidden" in f.type.lower() or f.detector in {"pdf_forensics", "docx_forensics"})
    unicode_count = sum(1 for f in findings if f.detector == "unicode")
    rules_count = sum(1 for f in findings if f.detector == "rules")
    ml_count = sum(1 for f in findings if f.detector == "ml")
    weighted = 0.30 * min(1.0, hidden / 3) + 0.15 * min(1.0, unicode_count / 3) + 0.25 * min(1.0, rules_count / 3) + 0.20 * min(1.0, ml_count / 3) + 0.10 * 0.5
    risk_score = int(round(weighted * 100))
    if risk_score < 0:
        risk_score = 0
    if risk_score > 100:
        risk_score = 100
    level = "low"
    if risk_score >= 75:
        level = "critical"
    elif risk_score >= 50:
        level = "high"
    elif risk_score >= 25:
        level = "medium"
    decision = "approved"
    if risk_score >= 25:
        decision = "quarantined"
    return RiskReport(
        doc_id=doc_id,
        filename=filename,
        sha256=sha256,
        file_type=file_type,
        risk_score=risk_score,
        risk_level=level,
        sub_scores={"hidden_content": round(min(1.0, hidden / 3), 3), "unicode": round(min(1.0, unicode_count / 3), 3), "rules": round(min(1.0, rules_count / 3), 3), "ml": round(min(1.0, ml_count / 3), 3), "location": 0.5},
        findings=findings,
        decision=decision,
        scan_time_ms=0.0,
        created_at=datetime.utcnow(),
        notes=[]
    )
