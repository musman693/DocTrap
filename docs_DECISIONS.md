# Design decisions

- The project uses a simplified but runnable implementation focused on the non-optional requirements in the master prompt.
- PDF/DOCX extraction is intentionally lightweight and library-aware; if PyMuPDF or python-docx are unavailable the code degrades to safe baseline extraction instead of crashing.
- Hidden prompt detection prioritizes explainability and fail-closed behavior over exhaustive coverage.
