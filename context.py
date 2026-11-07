from __future__ import annotations

from models import Finding, Severity


def context_adjust(findings: list[Finding]) -> list[Finding]:
    adjusted: list[Finding] = []
    for finding in findings:
        score = float(finding.score)
        if "instruction" in finding.type.lower() or "override" in finding.type.lower():
            score = min(1.0, score + 0.15)
        if finding.severity in {Severity.HIGH, Severity.CRITICAL}:
            score = min(1.0, score + 0.1)
        finding.score = score
        adjusted.append(finding)
    return adjusted
