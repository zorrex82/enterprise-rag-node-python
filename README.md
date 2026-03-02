# Enterprise RAG (Node + FastAPI + Ollama)

A lightweight Retrieval-Augmented Generation (RAG) system built from scratch using:

* FastAPI for the RAG service
* Node.js (Express) as an API gateway
* Ollama for local embeddings and LLM inference
* SQLite for persistence
* In-memory vector store for fast cosine retrieval

This project is designed as a local-first, educational and experimental RAG implementation. It focuses on understanding the full pipeline instead of relying on external managed vector databases or cloud services.

---

## Architecture

The system is composed of three main components:

### 1. api-gateway (Node.js)

* Acts as the public API layer
* Forwards requests to the RAG service
* Keeps the architecture modular and closer to real-world setups

### 2. rag-service (FastAPI)

* Handles ingestion
* Performs chunking
* Generates embeddings using Ollama
* Persists chunks and embeddings in SQLite
* Loads data into memory on startup
* Executes cosine similarity retrieval
* Generates grounded answers using an LLM
* Returns ranked matches, context, and final answer

### 3. Ollama (Local LLM Runtime)

* Generates embeddings (e.g., `nomic-embed-text`)
* Generates answers using a chat model (e.g., `llama3.1`)

---

## Current Features

* Text ingestion endpoint
* Character-based chunking
* Embedding generation via Ollama
* SQLite persistence layer
* Automatic reload of stored chunks on service startup
* In-memory cosine similarity retrieval
* Grounded answer generation in `/v1/chat`
* Gateway proxy with query param forwarding
* Local development script (`dev.sh`) to manage services

---

## Roadmap

* [x] Ingestion pipeline
* [x] Embeddings integration
* [x] Cosine similarity retrieval
* [x] API Gateway integration
* [x] LLM answer generation in `/v1/chat`
* [x] SQLite persistence layer
* [ ] Document-level filtering (`doc_id`)
* [ ] Basic evaluation / smoke tests
* [ ] Docker support

---

## Requirements

* Python 3.11+ (recommended 3.11 or 3.12)
* Node.js 20+
* Ollama installed locally
* Git

---

## Environment Variables

Optional environment variables:

* `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
* `EMBEDDING_MODEL` (default: `nomic-embed-text`)
* `CHAT_MODEL` (default: `llama3.1`)
* `SQLITE_DB_PATH` (optional override for database location)

Example:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export EMBEDDING_MODEL="nomic-embed-text"
export CHAT_MODEL="llama3.1"
```

---

## Initial Setup (First Time Only)

After cloning the repository, you must set up the Python virtual environment and install dependencies.

### 1. Setup the RAG Service (Python)

```bash
cd rag-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup the API Gateway (Node.js)

```bash
cd ../api-gateway
npm install
```

---

## Running the System

After completing the setup steps above, return to the project root and start all services:

```bash
cd ..
./dev.sh start
```

Check status:

```bash
./dev.sh status
```

Run health checks:

```bash
./dev.sh health
```

Stop services:

```bash
./dev.sh stop
```

Restart services:

```bash
./dev.sh restart
```

---

## Persistence Model

* Chunks and embeddings are stored in SQLite (`rag-service/data/rag.db` by default).
* On startup, the RAG service:

  * Initializes the database (if needed)
  * Loads all stored chunks into memory
* Cosine similarity search is performed in memory for simplicity and clarity.

This approach keeps the architecture understandable while still providing durability across restarts.

---

## Example Usage

### Ingest Text

```bash
curl -X POST http://localhost:3000/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern Python web framework. Python is widely used."
  }'
```

### Query

```bash
curl -X POST "http://localhost:3000/v1/chat?top_k=2" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is FastAPI?"
  }'
```

The response includes:

* `answer` (LLM-generated, grounded in context)
* Ranked matches
* Similarity scores
* Aggregated context
* Model used for generation

---

## Design Philosophy

This project intentionally avoids:

* External vector databases
* Managed cloud AI services
* Heavy frameworks

The goal is to:

* Understand embeddings and retrieval mechanics
* Control the full pipeline
* Keep everything runnable locally
* Provide a clean foundation for evolving toward production-ready patterns

---

## Data Files

The SQLite database is local-only and ignored by Git:

```
rag-service/data/
*.db
*.db-wal
*.db-shm
```

---

## Future Direction

The next major evolution will introduce:

* Document-level filtering via `doc_id`
* Structured document ingestion
* Evaluation utilities
* Docker support

This repository serves as a reference implementation and experimentation ground before building a more structured version intended for teaching purposes.
