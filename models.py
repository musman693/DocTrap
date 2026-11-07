from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class Source(str, Enum):
    BODY = "body"
    COMMENT = "comment"
    METADATA = "metadata"
    HYPERLINK = "hyperlink"
    HEADER = "header"
    FOOTER = "footer"
    TRACKED_INSERT = "tracked_insert"
    TRACKED_DELETE = "tracked_delete"
    OCR = "ocr"
    ALT_TEXT = "alt_text"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TextSpan:
    text: str
    source: Source
    page: int | None = None
    location: str = ""
    bbox: tuple[float, float, float, float] | None = None
    font_size: float | None = None
    color: str | None = None
    flags: dict = field(default_factory=dict)


@dataclass
class Finding:
    id: str
    detector: str
    type: str
    severity: Severity
    score: float
    source: Source
    page: int | None
    location: str
    exact_text: str
    explanation: str
    details: dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    doc_id: str
    filename: str
    file_type: Literal["pdf", "docx"]
    sha256: str
    spans: list[TextSpan]
    page_count: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RiskReport:
    doc_id: str
    filename: str
    sha256: str
    file_type: str
    risk_score: int
    risk_level: str
    sub_scores: dict[str, float]
    findings: list[Finding]
    decision: str
    scan_time_ms: float
    created_at: datetime
    notes: list[str]


@dataclass
class DocumentRecord:
    id: str
    filename: str
    sha256: str
    file_type: str
    size: int
    status: str
    risk_score: int = 0
    risk_level: str = "low"
    original_path: str = ""
    sanitized_path: str = ""
    reviewer_note: str = ""
    reviewed_at: str | None = None
