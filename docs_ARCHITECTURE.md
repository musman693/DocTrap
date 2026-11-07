# DocTrap architecture

```mermaid
flowchart LR
A[Upload PDF/DOCX] --> B[Ingestion]
B --> C[PDF/DOCX Extraction]
C --> D[Forensics + Unicode]
D --> E[Rules + ML]
E --> F[Context + Scoring]
F --> G[Workflow: approve/quarantine/sanitize]
G --> H[RAG + Dashboard + Evaluation]
```

This project implements the core pipeline in a compact, explainable manner: ingestion validates files, parsing extracts text, forensics detects hidden or disguised instructions, then scoring decides whether to approve or quarantine the document.
