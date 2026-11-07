from __future__ import annotations

import re
import unicodedata

from models import Finding, Severity, Source, TextSpan

ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\ufeff"}
BIDI = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e"}


def detect_zero_width(value: str) -> int:
    return sum(1 for ch in value if ch in ZERO_WIDTH)


def detect_bidi(value: str) -> bool:
    return any(ch in BIDI for ch in value)


def mixed_script_score(value: str) -> float:
    letters = [ch for ch in value if ch.isalpha()]
    if not letters:
        return 0.0
    latin = sum(1 for ch in letters if unicodedata.name(ch, "").startswith("LATIN"))
    non_latin = sum(1 for ch in letters if not unicodedata.name(ch, "").startswith("LATIN"))
    return (non_latin / len(letters)) * 0.5 + (latin / len(letters)) * 0.5 if latin else 0.0


def unicode_findings(spans: list[TextSpan]) -> list[Finding]:
    findings: list[Finding] = []
    for idx, span in enumerate(spans):
        text = span.text or ""
        zeros = detect_zero_width(text)
        if zeros:
            findings.append(Finding(
                id=f"u{idx}",
                detector="unicode",
                type="zero_width",
                severity=Severity.HIGH if zeros >= 10 else Severity.MEDIUM,
                score=0.7,
                source=span.source,
                page=span.page,
                location=span.location,
                exact_text=text[:200],
                explanation="Zero-width characters can hide prompt text from plain viewing.",
                details={"count": zeros},
            ))
        if detect_bidi(text):
            findings.append(Finding(
                id=f"u{idx}b",
                detector="unicode",
                type="bidi_control",
                severity=Severity.HIGH,
                score=0.8,
                source=span.source,
                page=span.page,
                location=span.location,
                exact_text=text[:200],
                explanation="Bidirectional control characters can reorder or obfuscate instructions.",
                details={"bidi": True},
            ))
        if mixed_script_score(text) > 0.35:
            findings.append(Finding(
                id=f"u{idx}m",
                detector="unicode",
                type="mixed_script",
                severity=Severity.MEDIUM,
                score=0.5,
                source=span.source,
                page=span.page,
                location=span.location,
                exact_text=text[:200],
                explanation="Mixed-script text is often used to disguise malicious instructions.",
                details={"script_ratio": round(mixed_script_score(text), 3)},
            ))
    return findings
