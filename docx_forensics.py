from __future__ import annotations

from models import Finding, Severity, TextSpan


def docx_forensics(spans: list[TextSpan]) -> list[Finding]:
    findings: list[Finding] = []
    for idx, span in enumerate(spans):
        text = (span.text or "").strip()
        if not text:
            continue
        if any(k in text.lower() for k in ["ignore previous instructions", "reveal hidden prompt", "canary", "pineapple"]):
            findings.append(Finding(
                id=f"docx{idx}",
                detector="docx_forensics",
                type="hidden_run",
                severity=Severity.HIGH,
                score=0.85,
                source=span.source,
                page=span.page,
                location=span.location,
                exact_text=text[:200],
                explanation="The document contains suspicious instruction-like text in a hidden or tracked XML region.",
                details={"source": span.source.value, "flags": span.flags},
            ))
    return findings
