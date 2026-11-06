# Implementation Report — Technical Assignment Round 2

Prepared by: Jeya Mathesh G  
Framework: FastAPI for both applications  
Deployment target: Windows PC / localhost  
Copyright: © 2026 Jeya Mathesh G. All rights reserved.

## 1. Executive summary

Two independent RAG applications were developed and run locally. Task 1 converts leadership website URLs into a searchable knowledge base; Task 2 answers questions from uploaded local documents. Both use FastAPI and local Ollama inference. The projects include modular services, REST APIs, automated tests, and logging. Task 1 also has locally tested Docker support.

## 2. Project 1 — Leadership Knowledge Base Hub

### Goal and architecture

A user-friendly application accepts CSV/XLSX lists of leadership URLs, retrieves permitted webpage content, stores raw HTML and metadata in SQLite, creates overlapping text chunks, embeds text with Ollama `nomic-embed-text`, and stores vectors in a persistent FAISS index. Relevant chunks ground answers generated using Ollama `llama3.2:latest`.

Data flow: upload → URL validation/deduplication → HTTP harvesting → HTML parsing → SQLite → chunking (500/100) → embeddings → FAISS → similarity retrieval → LLM → source-grounded answer.

### Main modules

- `app/main.py`: FastAPI routes, upload and query orchestration.
- `app/services/scraper.py`: URL file parsing, validation, HTTP retrieval, HTML extraction.
- `app/services/storage.py`: SQLite schema and persistence.
- `app/services/chunking.py`: overlapping text splitting.
- `app/services/vector.py`: embeddings and persistent FAISS indexing.
- `app/services/llm.py`: context-grounded answer generation.
- `scripts/rebuild_index.py`: rebuilding vectors from stored content.
- `app/static/`: browser interface.
- `app/core/logging_config.py`: logging configuration added during subsequent development.

### REST API

`POST /api/upload`, `GET /api/urls/`, `POST /api/search`, `GET /api/health`.

The documented `GET /api/urls/` output includes URL, HTTP status, raw HTML, title, description, extracted text, errors, and timestamps where available.

### Features and observed behavior

- CSV and XLSX input; deduplicated URLs and upsert-style storage as documented.
- Source excerpts, URLs, and retrieval scores for review.
- Transparent HTTP errors rather than fabricated website content.
- Local SQLite and FAISS persistence.
- Automated tests and local Docker image/container verification.
- Logging added for application and processing events.

A previous local ingestion of five URLs resulted in three successful retrievals and two failures (HTTP 403/404), with 13 indexed chunks. These outcomes are sample-run results, not guarantees for future requests.

## 3. Project 2 — Local Document RAG Chatbot

### Goal and architecture

The application ingests PDF, DOCX, TXT, and Markdown files, extracts text, creates overlapping chunks with document references, generates local Ollama embeddings, and persists them in ChromaDB. At query time it retrieves relevant chunks and uses Ollama `llama3.2:3b` to answer with source citations and excerpts.

Data flow: document upload → validation/extraction → text chunks → embeddings → ChromaDB → query embedding → nearest-neighbor retrieval → LLM → cited answer.

### Main modules

- `app/main.py`: FastAPI routes and chat pipeline.
- `app/services/documents.py`: file readers and page extraction.
- `app/services/chunking.py`: deterministic text splitting.
- `app/services/store.py`: ChromaDB indexing and retrieval.
- `app/services/ollama.py`: embedding/generation integration.
- `scripts/ingest.py`: optional command-line ingestion.
- `app/static/`: chat interface.
- `app/core/logging_config.py`: logging configuration added during subsequent development.

### REST API

`POST /api/documents/upload`, `POST /api/chat`, `GET /api/documents`, `GET /api/health`.

### Features and observed behavior

- Four supported file types; persistent vector storage.
- SHA-256 document deduplication and page/chunk citations as documented.
- Local inference without a cloud LLM requirement.
- Automated tests and logging.
- Earlier local manual testing included a TXT document about LangGraph and a PDF resume. TXT retrieval and citations worked; some PDF questions returned incomplete retrieval results.

## 4. Framework decision

FastAPI was chosen instead of Django because the assignment allows alternative frameworks, and FastAPI provides request validation, automatically generated Swagger documentation, and straightforward integration with Python RAG components.

## 5. Logging implementation

Logging was added to both projects using `app/core/logging_config.py` and `setup_logging()` in the FastAPI application. The intended events include application startup, uploads, processing/indexing outcomes, errors, and question-answering operations. Log files are stored separately under each project's `logs/application.log`.

Task 2's application startup message was observed in console output on 2026-11-06. The user subsequently reported logging completed for both tasks. Full event-by-event log verification should be included in final screenshots. Log messages must reflect actual operations; example warnings/errors must not be logged unconditionally.

## 6. Testing and reproducibility

Initial static verification (Linux/Python 3.13, without FAISS, ChromaDB, or Ollama): Python compilation passed; the interview XLSX yielded five expected URLs; five Task 2 chunking tests passed; ZIP CRC check passed. Full API and end-to-end tests could not run in that initial environment.

Subsequent Windows local verification: Task 1 tests reported 5 passed; Task 2 tests reported 9 passed. Both web applications ran locally, and Task 1 Docker image and container startup were tested. These are earlier observations and should be rerun after the latest logging changes, with current evidence captured.

Automated tests that mock Ollama or retrieval components do not prove live model inference or website availability. Manual browser tests remain important.

See `TEST_REPORT.md` for details.

## 7. Bonus criteria status

| Bonus criterion | Current status |
|---|---|
| Docker | Task 1 image built and container started locally; Task 2 Docker not verified |
| Automated testing | 5 Task 1 and 9 Task 2 tests previously passed locally |
| Logging | Added to both projects; startup output observed for Task 2 |
| Deployment | No completed AWS/public deployment |
| Code quality and structure | Modular service layout; independent final review recommended |

## 8. Assumptions

- Python 3.11 and local Ollama models are available on the reviewer's machine.
- Website content may be blocked, unavailable, or JavaScript-rendered; restrictions are respected.
- Model weights are installed separately via Ollama rather than packaged in the ZIP.
- This is a local single-user prototype, not a production service.
- The exact documented source paths, schemas, and routes should be checked against the final ZIP before submission.

## 9. Difficulties and limitations

- External sites may return HTTP 403/404, rate-limit requests, or require client-side rendering.
- Task 1's synchronous ingestion and index rebuilding are not optimized for large-scale processing.
- SSRF mitigation requires more than URL filtering in a production deployment.
- OCR is not included for scanned PDFs.
- Retrieval can miss relevant passages, and LLM answers can be incomplete or inaccurate.
- Local model inference requires sufficient memory and compute.
- Task 2 Docker build was not completed due to local machine memory constraints.
- Public deployment would require authentication, rate limiting, file scanning, and monitoring.

## 10. Development time

The assignment asks for **actual time per task**. No measured times were supplied; do not replace the following with invented numbers.

| Activity | Actual time |
|---|---|
| Task 1 implementation and local verification | 2 Hours |
| Task 2 implementation and local verification | 2 Hours |
| Logging integration and verification | 30 minutes |
| Screenshots and demonstration recording | 30 minutes |
| Total elapsed development/testing time | 1 Hour |

## 11. Other observations

1. Source quality and extractable text strongly affect RAG retrieval.
2. Source snippets and citations help reviewers verify generated statements.
3. FAISS suits lightweight local vector indexing; ChromaDB conveniently stores document vectors with metadata.
4. FastAPI Swagger UI supports independent API evaluation.
5. Background ingestion, incremental indexing, and stronger grounding would be valuable production enhancements.

## 12. Submission notes

Include the two source directories, root README, this report, the test report, dependency files, launchers, Docker files, and real screenshots/video evidence where required. Exclude fabricated results and unnecessary runtime files. Cloud deployment is listed as a bonus rather than a required core feature in the criteria shared.

Copyright © 2026 Jeya Mathesh G. All rights reserved.
