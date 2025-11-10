#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

from src.doc_analizer.crew import DocAnalizer


def validate_document(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Document not found: {path_str}")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Path is not a file: {path_str}")
    return str(path.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Document Analyzer Agent.")
    parser.add_argument(
        "--doc",
        "--document",
        dest="documents",
        action="append",
        required=True,
        type=validate_document,
        help="Path to document(s) to analyze.",
    )
    parser.add_argument(
        "--analysis",
        dest="analysis_type",
        default="financial report",
        help="Type of analysis to perform.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="output",
        help="Directory to store generated reports.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show stack traces on failure.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    inputs = {
        "file_paths": args.documents,
        "analysis_type": args.analysis_type,
    }

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    try:
        DocAnalizer().crew().kickoff(inputs=inputs)
        print(f"Reports stored in '{args.output_dir}'")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
