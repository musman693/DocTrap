from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ingestion import ingest
from pipeline import scan_document

app = FastAPI(title="DocTrap")
UI_DIST = Path(__file__).parent / "doctrap_ui" / "dist"


@app.get("/", response_class=HTMLResponse)
def root():
    index = UI_DIST / "index.html"
    if not index.is_file():
        raise HTTPException(
            status_code=503,
            detail="The frontend has not been built. Run `npm install` and `npm run build` in the frontend directory.",
        )
    return index.read_text(encoding="utf-8")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    try:
        record = ingest(data, file.filename or "upload.bin")
        report = scan_document(data, filename=record.filename)
        return {
            "status": "ok",
            "document_id": record.id,
            "filename": report.filename,
            "file_type": report.file_type,
            "sha256": report.sha256,
            "risk_score": report.risk_score,
            "risk_level": report.risk_level,
            "decision": report.decision,
            "scan_time_ms": round(report.scan_time_ms, 1),
            "findings": [
                {
                    "id": finding.id,
                    "type": finding.type,
                    "severity": finding.severity.value,
                    "source": finding.source.value,
                    "page": finding.page,
                    "location": finding.location,
                    "exact_text": finding.exact_text,
                    "explanation": finding.explanation,
                }
                for finding in report.findings
            ],
        }
    except ValueError as exc:
        raise HTTPException(status_code=415 if "Only .pdf" in str(exc) or "DOCX" in str(exc) else 413, detail=str(exc)) from exc


@app.get("/documents")
def documents():
    return {"documents": []}


if (UI_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=UI_DIST / "assets"), name="frontend-assets")
