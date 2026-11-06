# Technical Assignment – Round 2 | FastAPI Edition

Prepared by: Jeya Mathesh G  
Target environment: Windows 10/11, localhost  
Copyright: © 2026 Jeya Mathesh G. All rights reserved.

Two independent local Retrieval-Augmented Generation (RAG) applications. Both use FastAPI, a browser-based HTML/CSS/JavaScript interface, and Ollama for local AI inference.

| Project | Directory | Local URL | Main technologies |
|---|---|---|---|
| Task 1 — Leadership Knowledge Base Hub | `task1_knowledge_hub/` | http://127.0.0.1:8000 | FastAPI, SQLite, FAISS, Ollama |
| Task 2 — Local Document RAG Chatbot | `task2_local_rag/` | http://127.0.0.1:8001 | FastAPI, ChromaDB, Ollama |

## 1. Prerequisites

- Windows 10/11 and Python 3.11 (64-bit) recommended.
- Ollama installed and running: https://ollama.com/download/windows
- Internet for initial dependency/model downloads and Task 1 external website retrieval.
- Optional: Docker Desktop for Task 1 container execution.

In PowerShell or Command Prompt:

```powershell
py -3.11 --version
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama list
```

Ollama models are downloaded separately; model weights are not included in the project ZIP. If the Ollama server is not already running, start it with `ollama serve` in a separate terminal. Do not start a second server if Ollama is already active.

## 2. Running Task 1 — Leadership Knowledge Base Hub

From the extracted project root, run:

```powershell
.\run_task1_windows.bat
```

Alternatively, from the root:

```powershell
cd task1_knowledge_hub
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000; Swagger docs: http://127.0.0.1:8000/docs.

Upload a CSV or XLSX file of leadership website URLs, wait for harvesting and indexing, and then ask questions about indexed leadership content. The supplied spreadsheet was previously tested with five URLs; in one local run three URLs were processed successfully, while two returned HTTP 403/404. Site responses can change.

Task 1 API routes (as documented in the project specification):

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/upload` | Upload CSV/XLSX URL list |
| GET | `/api/urls/` | Inspect stored URL records and processing outcomes, including raw HTML where present |
| POST | `/api/search` | Search indexed website content and generate a grounded answer |
| GET | `/api/health` | Health endpoint |

Example search JSON:

```json
{"question":"Summarize the leadership information in the indexed sources.","top_k":5}
```

Architecture: CSV/XLSX → URL validation → requests/BeautifulSoup → SQLite raw HTML/metadata → text chunks (500 characters, 100 overlap) → Ollama `nomic-embed-text` → persistent FAISS index → retrieval → Ollama `llama3.2:3b` → answer with source references.

Task 1 includes an index rebuild command, run from `task1_knowledge_hub`:

```powershell
python -m scripts.rebuild_index
```

Documented generated files include `data/harvest.sqlite3` and `data/vectors.faiss`; confirm actual file paths in the running installation.

## 3. Running Task 2 — Local Document RAG Chatbot

From the project root:

```powershell
.\run_task2_windows.bat
```

Or manually:

```powershell
cd task2_local_rag
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001; Swagger docs: http://127.0.0.1:8001/docs.

Upload a PDF, DOCX, TXT, or Markdown file. After ingestion, ask a question about the uploaded content and inspect the cited source excerpts. Scanned PDFs without selectable text are not supported without OCR.

Task 2 API routes (as documented in the project specification):

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/documents/upload` | Upload a document |
| POST | `/api/chat` | Ask a question using indexed documents |
| GET | `/api/documents` | List document records |
| GET | `/api/health` | Health endpoint |

Example chat JSON:

```json
{"question":"What does the document say about RAG?","top_k":5}
```

Architecture: document upload → file parser → overlapping chunks with source references → Ollama embeddings → persistent ChromaDB → semantic retrieval → Ollama `llama3.2:latest` → answer with document citations.

Optional command-line ingestion, from `task2_local_rag`:

```powershell
python -m scripts.ingest samples/overview.txt
```

The exact example file must exist for this command to succeed.

## 4. Automated testing

Run tests independently from each project directory:

```powershell
cd task1_knowledge_hub
.\.venv\Scripts\python.exe -m pytest -q
cd ..\task2_local_rag
.\.venv\Scripts\python.exe -m pytest -q
```

Previously observed Windows local results: Task 1: 5 passed; Task 2: 9 passed (14 total). These results were reported earlier in the development process. Rerun and capture current terminal output after the latest logging changes. Unit/API tests that mock AI calls are not substitutes for a real Ollama/browser end-to-end demonstration.

See `docs/TEST_REPORT.md` for the distinction between the initial Linux static checks and subsequent Windows local verification.

## 5. Logging (implemented in both projects)

Both applications were updated with a `setup_logging()` configuration and logging statements for application startup and relevant ingestion/chat operations. Logging was reported completed during local development. Each project uses its own log file:

- `task1_knowledge_hub/logs/application.log`
- `task2_local_rag/logs/application.log`

From the relevant task folder:

```powershell
Get-Content .\logs\application.log -Tail 20
```

A Task 2 startup log was directly observed in the terminal on 2026-11-06. The logger may also print to the console. Avoid logging passwords, confidential document contents, or complete prompts. Verify event-specific log entries after performing each operation.

## 6. Docker (optional bonus)

Task 1's Docker image was built and its container started successfully in local testing. From the project root, after building the image and with the required Ollama connectivity configured:

```powershell
docker compose up -d --no-deps --no-build knowledge-hub
docker compose ps
docker compose logs knowledge-hub
```

The first command starts an existing image; it does not build one. Task 2 Docker build was not completed on the development machine due to memory limitations. Do not describe Task 2 container execution as verified. Cloud deployment and Jenkins CI/CD were paused/not completed.

## 7. Troubleshooting

| Symptom | Resolution |
|---|---|
| `py -3.11` not found | Install Python 3.11 and restart terminal |
| Ollama unavailable / model not found | Check `ollama list` and that the Ollama server is running |
| `ModuleNotFoundError` | Activate the correct task's virtual environment and install its requirements |
| `[Errno 10048]` on port 8000/8001 | Another process already uses that port; check the existing application before restarting |
| Website 403/404 or JavaScript-only content | Respect website restrictions; the application should report the failure |
| No answer / poor retrieval | Check ingested text, embeddings, vector index, and returned chunks |
| Scanned PDF returns no text | OCR is not included by default |
| No log file | Confirm `app/core/logging_config.py` exists and that `setup_logging()` is imported/executed |

To inspect the process listening on port 8001:

```powershell
Get-NetTCPConnection -LocalPort 8001 -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```

Only stop a process after confirming it belongs to an old application server.

## 8. Submission and evidence

Suggested submission structure:

```text
AI_Round2_Reference_Style/
├── task1_knowledge_hub/
├── task2_local_rag/
├── run_task1_windows.bat
├── run_task2_windows.bat
├── docker-compose.yml
├── README.md
├── docs/
│   ├── IMPLEMENTATION.md
│   └── TEST_REPORT.md
└── evidence/
    ├── screenshots/
    └── videos/
```

Capture genuine screenshots of each frontend, upload result, grounded answer, test output, and log file. Record demos if requested. Do not include fabricated results. Exclude `.venv`, `__pycache__`, and unnecessary local secrets or large temporary files. Ensure the final ZIP retains all source code, dependency files, and required run scripts.

## 9. Scope and limitations

These are local assignment prototypes, not publicly deployed multi-user services. Task 1 requires external network access to scrape websites; Task 2 can work without cloud AI services after dependencies and Ollama models are installed. Retrieval and generated answers can be imperfect. Public hosting would require authentication, rate limiting, monitoring, stronger upload validation, and network controls.

Author: Jeya Mathesh G  
Copyright: © 2026 Jeya Mathesh G. All rights reserved.