from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from models import DocumentRecord

DB_PATH = Path(__file__).resolve().parent / "data" / "doctrap.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class Base(DeclarativeBase):
    pass


class DocumentORM(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="uploaded")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String, default="low")
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    original_path: Mapped[str | None] = mapped_column(String, nullable=True)
    sanitized_path: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class FindingORM(Base):
    __tablename__ = "findings"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    doc_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id"), nullable=False)
    detector: Mapped[str] = mapped_column(String)
    entry_type: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str] = mapped_column(String)
    exact_text: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    details: Mapped[str] = mapped_column(Text, default="{}")


class AuditLogORM(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id"), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    actor: Mapped[str] = mapped_column(String, default="system")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    detail: Mapped[str | None] = mapped_column(Text)


class RAGIndexEntryORM(Base):
    __tablename__ = "rag_index_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id"), nullable=False)
    chunk_id: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="approved")


engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)


def save_document_record(doc: DocumentRecord) -> None:
    with get_session() as session:
        record = DocumentORM(
            id=doc.id,
            filename=doc.filename,
            sha256=doc.sha256,
            file_type=doc.file_type,
            size=doc.size,
            status=doc.status,
            risk_score=doc.risk_score,
            risk_level=doc.risk_level,
            original_path=doc.original_path,
            sanitized_path=doc.sanitized_path,
            reviewer_note=doc.reviewer_note,
            reviewed_at=doc.reviewed_at,
        )
        session.merge(record)
        session.commit()


def get_document_record(doc_id: str) -> DocumentRecord | None:
    with get_session() as session:
        row = session.get(DocumentORM, doc_id)
        if not row:
            return None
        return DocumentRecord(
            id=row.id,
            filename=row.filename,
            sha256=row.sha256,
            file_type=row.file_type,
            size=row.size,
            status=row.status,
            risk_score=row.risk_score,
            risk_level=row.risk_level,
            original_path=row.original_path or "",
            sanitized_path=row.sanitized_path or "",
            reviewer_note=row.reviewer_note or "",
            reviewed_at=row.reviewed_at.isoformat() if row.reviewed_at else None,
        )


def log_audit(doc_id: str, action: str, detail: str = "", actor: str = "system") -> None:
    with get_session() as session:
        session.add(AuditLogORM(doc_id=doc_id, action=action, detail=detail, actor=actor))
        session.commit()
