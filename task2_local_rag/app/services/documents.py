"""Load text from PDF, DOCX, Markdown and TXT files, preserving pages."""
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def extract_pages(filename: str, data: bytes) -> list[tuple[int, str]]:
    extension = Path(filename).suffix.lower()
    if extension not in EXTENSIONS:
        raise ValueError("Supported formats: PDF, DOCX, TXT, MD")
    if extension == ".pdf":
        try:
            reader = PdfReader(BytesIO(data))
            return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
        except Exception as exc:
            raise ValueError(f"Unable to parse PDF: {exc}") from exc
    if extension == ".docx":
        try:
            doc = Document(BytesIO(data))
            return [(1, "\n".join(par.text for par in doc.paragraphs))]
        except Exception as exc:
            raise ValueError(f"Unable to parse DOCX: {exc}") from exc
    try:
        return [(1, data.decode("utf-8-sig"))]
    except UnicodeError as exc:
        raise ValueError("Text files must use UTF-8") from exc
