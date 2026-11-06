# Reference-style modular RAG implementation

This edition adapts the **chunking pattern** from the user-provided Banking_Risk_Investigation project, without copying its banking-specific graph, tools, or agents.

## Structure
Both projects expose `app/services/chunking.py`, `embeddings.py`, `ingest.py`, and `retriever.py`, plus their existing storage and API modules.

## Chunking
Uses `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)`; boundaries prefer sentences and spaces. Chunking runs as part of the existing upload/indexing workflows. Source identifiers are retained by the existing storage layer.

## Embeddings
This edition retains the original fully local Ollama embedding pipeline (`nomic-embed-text`) rather than requiring a second HuggingFace model download. Both apps default to your installed `llama3.2:latest` model. The reference project used HuggingFace MiniLM; swapping embedding models requires rebuilding vector indexes.

## Retrieval
Task 1 persists raw HTML and metadata in SQLite, with vectors in FAISS. Task 2 persists document chunks in ChromaDB. Both provide source-grounded answers. The optional `retriever.py` facade defaults to top 3; existing API search settings remain unchanged.

## Run and verify
Follow `README.md` and run the provided Windows scripts. Install updated dependencies first. For Task 1, upload the leadership workbook and check `/api/urls/`. For Task 2, upload a document and ask a question. Check actual retrieval sources and Ollama output before recording.

## Validation
Source code syntax was checked in the build environment. Full end-to-end Ollama, website scraping, and vector database execution must be tested on the Windows computer before submission.
