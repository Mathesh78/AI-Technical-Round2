from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)


def test_home():
    assert client.get("/").status_code == 200


def test_health():
    assert client.get("/api/health").json()["service"] == "local-rag"


def test_reject_extension():
    response = client.post("/api/documents/upload", files={"file": ("x.exe", b"abc")})
    assert response.status_code == 400


def test_chat_returns_sources(monkeypatch):
    monkeypatch.setattr(main, "retrieve", lambda question, top_k: [{"citation": "[1]", "filename": "demo.txt", "page": 1, "chunk": 0, "text": "Maya is CEO"}])
    monkeypatch.setattr(main, "answer", lambda prompt: "Maya is CEO [1].")
    data = client.post("/api/chat", json={"question": "Who is CEO?"}).json()
    assert "[1]" in data["answer"]
    assert data["sources"][0]["filename"] == "demo.txt"
