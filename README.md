# DocTrap

DocTrap is a compact document security gateway. It inspects uploaded PDF and DOCX files for hidden text, invisible Unicode, metadata prompts, and suspicious instructions. It produces an explainable risk score and can quarantine or sanitize risky documents before they reach a downstream RAG system.

## Quick start

1. Install the backend dependencies:
   `python -m pip install -e .`
2. Build the React frontend:
   `cd frontend`
   `npm install`
   `npm run build`
3. Start the API from the project root:
   `python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000`
4. Open `http://localhost:8000`

For frontend development with hot reload, run `npm run dev` in `frontend` and start the backend in a second terminal. The Vite development server proxies API requests to `http://localhost:8000`.
Open `http://127.0.0.1:5173` while using the development server.

Upload a PDF or DOCX file to see its risk score, scan decision, and detected findings. The upload limit is 20 MB.

## Features

- PDF/DOCX ingestion and validation
- Hidden-content detection and Unicode analysis
- Rules engine + lightweight ML scoring
- Risk reporting with evidence
- Quarantine and sanitize workflow
- RAG demo and evaluation scripts

## Notes

This is a practical implementation based on the project specification in `DocTrap_Copilot_Prompt.md`.
