import pytest
from app.services.chunking import chunk_text
from app.services.documents import extract_pages


def test_chunks_for_short_text():
    assert chunk_text("hello  world") == ["hello world"]


def test_long_text_splits():
    parts = chunk_text("alpha beta " * 300, size=120, overlap=20)
    assert len(parts) > 10
    assert all(len(part) <= 120 for part in parts)


def test_invalid_settings():
    with pytest.raises(ValueError):
        chunk_text("hello", size=100, overlap=100)


def test_text_loader():
    assert extract_pages("notes.txt", b"Hi world") == [(1, "Hi world")]


def test_reject_binary_format():
    with pytest.raises(ValueError):
        extract_pages("image.png", b"abc")
