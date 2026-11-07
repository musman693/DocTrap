from __future__ import annotations

from models import Finding, Severity, TextSpan


def pdf_forensics(spans: list[TextSpan]) -> list[Finding]:
    findings: list[Finding] = []
    for idx, span in enumerate(spans):
        text = span.text.strip()
        if not text:
            continue
        keywords = ["ignore previous instructions", "reveal system prompt", "override", "canary", "pineapple"]
        if any(k in text.lower() for k in keywords):
            findings.append(Finding(
                id=f"pdf{idx}",
                detector="pdf_forensics",
                type="hidden_instruction",
                severity=Severity.HIGH,
                score=0.9,
                source=span.source,
                page=span.page,
                location=span.location,
                exact_text=text[:200],
                explanation="The document contains instruction-like content that is hidden or suspicious in the extracted text stream.",
                details={"font_size": span.font_size, "bbox": span.bbox},
            ))
    return findings
