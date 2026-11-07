from __future__ import annotations

import argparse
from pathlib import Path

from pipeline import scan_document
from sanitizer import sanitize_docx_bytes, sanitize_pdf_bytes


def main() -> None:
    parser = argparse.ArgumentParser(description="DocTrap CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="scan a document")
    scan.add_argument("file")
    sanitize = sub.add_parser("sanitize", help="sanitize a document")
    sanitize.add_argument("file")
    args = parser.parse_args()
    if args.command == "scan":
        report = scan_document(args.file)
        print(f"risk={report.risk_score} level={report.risk_level} decision={report.decision}")
    elif args.command == "sanitize":
        path = Path(args.file)
        if path.suffix.lower() == ".pdf":
            out = sanitize_pdf_bytes(path.read_bytes())
        else:
            out = sanitize_docx_bytes(path.read_bytes())
        target = path.with_name(path.stem + "_sanitized" + path.suffix)
        target.write_bytes(out)
        print(f"sanitized copy written to {target}")


if __name__ == "__main__":
    main()
