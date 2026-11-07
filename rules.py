from __future__ import annotations

import re
from pathlib import Path

import yaml

from models import Finding, Severity, Source, TextSpan

DEFAULT_PATTERNS = {
    "ignore": ["please ignore previous instructions", "ignore system prompt"],
    "exfil": ["send this to", "leak the secret", "reveal the hidden prompt", "output the password"],
    "override": ["system prompt", "developer instructions", "bypass safety", "ignore prior instructions"],
    "secret": ["pineapple", "canary", "secret key", "token"],
}


def load_patterns(path: str | Path | None = None) -> dict[str, list[str]]:
    p = Path(path) if path else Path(__file__).resolve().parent / "rules_patterns.yaml"
    if p.exists():
        with p.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            if isinstance(data, dict):
                return data.get("patterns", DEFAULT_PATTERNS)
    return DEFAULT_PATTERNS


def rule_findings(spans: list[TextSpan], patterns: dict[str, list[str]] | None = None) -> list[Finding]:
    patterns = patterns or load_patterns()
    flat = []
    for group in patterns.values():
        flat.extend(group)
    matches: list[Finding] = []
    for idx, span in enumerate(spans):
        text = span.text.lower()
        for label, items in patterns.items():
            for item in items:
                if item.lower() in text:
                    matches.append(Finding(
                        id=f"r{idx}_{label}",
                        detector="rules",
                        type="rule_match",
                        severity=Severity.HIGH if label in {"override", "exfil"} else Severity.MEDIUM,
                        score=0.8,
                        source=span.source,
                        page=span.page,
                        location=span.location,
                        exact_text=span.text[:200],
                        explanation=f"Rule match for suspicious instruction pattern: {item}",
                        details={"pattern": item, "group": label},
                    ))
    return matches
