"""Bulk ingest local documents: python scripts/ingest.py samples/overview.txt"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.store import ingest  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Ingest files into the local Chroma vector database")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.files:
        try:
            print(ingest(path.name, path.read_bytes()))
        except (ValueError, OSError, RuntimeError) as exc:
            print(f"ERROR {path}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
