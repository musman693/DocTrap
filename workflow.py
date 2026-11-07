from __future__ import annotations

from pathlib import Path

from models import RiskReport


def apply_workflow(report: RiskReport) -> RiskReport:
    if report.risk_score >= 25:
        report.decision = "quarantined"
    else:
        report.decision = "approved"
    return report


def sanitize_write(source: str, dest: str) -> str:
    src = Path(source)
    dst = Path(dest)
    dst.write_bytes(src.read_bytes())
    return str(dst)
