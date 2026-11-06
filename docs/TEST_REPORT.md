# Test Report — Technical Assignment Round 2

Prepared by: Jeya Mathesh G  
Environment: Windows, Python, FastAPI, Ollama  
Projects: Leadership Knowledge Base Hub and Local Document RAG Chatbot  
Copyright: © 2026 Jeya Mathesh G

---

## 1. Test Overview

This report documents the testing and verification performed for both applications developed as part of Technical Assignment – Round 2.

The applications were initially subjected to static verification in a Linux/Python 3.13 environment. Additional local testing was subsequently performed on Windows with the required dependencies and Ollama.

## 2. Initial Static Verification

| Test | Result |
|---|---|
| Python source compilation using `compileall` | PASS |
| Leadership XLSX parsing — 5 URLs extracted | PASS |
| Task 2 chunking tests | 5 passed |
| ZIP archive CRC validation | PASS |
| Task 1 FastAPI tests in initial Linux environment | Not verified — FAISS unavailable |
| Task 2 FastAPI tests in initial Linux environment | Not verified — ChromaDB unavailable |
| Ollama end-to-end testing in initial Linux environment | Not verified |

These results describe the initial verification environment only.

## 3. Windows Local Testing

### Task 1 — Leadership Knowledge Base Hub

| Test activity | Result |
|---|---|
| FastAPI application execution | PASS |
| Frontend accessible on localhost:8000 | PASS |
| CSV/XLSX ingestion | PASS |
| SQLite data storage | PASS |
| FAISS indexing | PASS |
| Ollama integration | Tested locally |
| Automated tests | 5 passed |
| Docker image build | PASS |
| Docker container startup | PASS |
| Logging | Implemented |

Website ingestion results:

- Total submitted URLs: 5
- Successfully processed URLs: 3
- Failed requests: 2
- Indexed text chunks: 13

HTTP 403 and HTTP 404 errors were recorded for inaccessible URLs.

### Task 2 — Local Document RAG Chatbot

| Test activity | Result |
|---|---|
| FastAPI application execution | PASS |
| Frontend accessible on localhost:8001 | PASS |
| Document upload | PASS |
| ChromaDB integration | Tested locally |
| Document question answering | Tested locally |
| Source citations | Verified with TXT document |
| Automated tests | 9 passed |
| Logging | Implemented |
| Docker deployment | Not completed |

The application was tested using a PDF resume and a TXT document containing LangGraph information.

TXT retrieval and citations worked successfully. Some PDF-related questions returned incomplete retrieval results.

## 4. Automated Test Summary

| Project | Tests passed | Tests failed |
|---|---:|---:|
| Task 1 — Leadership Knowledge Base Hub | 5 | 0 |
| Task 2 — Local Document RAG Chatbot | 9 | 0 |
| Total | 14 | 0 |

These are previously observed local test results. The tests should be rerun after the latest logging changes.

## 5. Commands to Reproduce Testing

### Task 1

Open PowerShell inside `task1_knowledge_hub`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Task 2

Open PowerShell inside `task2_local_rag`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The expected previously observed results are 5 and 9 passing tests, respectively.

## 6. Logging Verification

Logging has been added to both applications using Python's logging module.

Task 1 log location:

`task1_knowledge_hub/logs/application.log`

Task 2 log location:

`task2_local_rag/logs/application.log`

Logging is intended to record application startup, ingestion operations, processing errors, and other significant events.

A Task 2 startup message was observed in the terminal. File logging and the full set of event messages should be confirmed using the generated log files.

## 7. Docker Verification

Task 1 Docker image creation and local container startup were completed successfully.

The following Docker Compose command was used:

```powershell
docker compose up -d --no-deps --no-build knowledge-hub
```

Task 2 Docker deployment was not completed due to local system resource constraints.

## 8. Deployment Status

Both applications were developed for local execution.

- Task 1: localhost:8000
- Task 2: localhost:8001
- AWS EC2 deployment: Paused
- Jenkins CI/CD: Not configured

Deployment is listed as a bonus criterion in the assignment rather than a mandatory requirement.

## 9. Known Testing Limitations

- Some websites block automated requests.
- JavaScript-rendered pages may not provide usable scraped content.
- RAG responses can occasionally be incomplete or unsupported.
- Complex PDF layouts can reduce retrieval accuracy.
- Scanned PDFs require OCR support.
- Automated API tests do not replace full end-to-end model verification.
- The latest changes should be retested before submission.

## 10. Conclusion

Both applications have been implemented and tested locally.

Previously observed automated testing produced 14 passing tests across both projects.

Task 1 additionally demonstrated website ingestion, SQLite persistence, FAISS indexing, and Docker support.

Task 2 demonstrated local document ingestion, ChromaDB retrieval, and Ollama-based question answering.

Logging has been added to both applications. Final regression testing and evidence collection remain necessary before submission.

---

Prepared by: Jeya Mathesh G  
Copyright © 2026 Jeya Mathesh G. All rights reserved.