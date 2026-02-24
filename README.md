# Enterprise RAG (Node + FastAPI + Ollama)

A lightweight Retrieval-Augmented Generation (RAG) system built from scratch using:

* FastAPI for the RAG service
* Node.js (Express) as an API gateway
* Ollama for local embeddings and LLM inference
* In-memory vector store (planned migration to SQLite)

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
* Stores embeddings in memory
* Executes cosine similarity retrieval
* Returns ranked matches and context

### 3. Ollama (Local LLM Runtime)

* Generates embeddings (e.g., nomic-embed-text)
* Will be used for answer generation (LLM step)

---

## Current Features

* Text ingestion endpoint
* Character-based chunking
* Embedding generation via Ollama
* In-memory vector storage
* Cosine similarity retrieval
* Gateway proxy with query param forwarding
* Local development script (dev.sh) to manage services

---

## Roadmap

* [x] Ingestion pipeline
* [x] Embeddings integration
* [x] Cosine similarity retrieval
* [x] API Gateway integration
* [ ] LLM answer generation in /v1/chat
* [ ] SQLite persistence layer
* [ ] Document-level filtering (doc_id)
* [ ] Basic evaluation / smoke tests
* [ ] Docker support

---

## Requirements

* Python 3.11+ (recommended 3.11 or 3.12)
* Node.js 20+
* Ollama installed locally
* Git

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

This will create a local virtual environment and install all required Python dependencies.

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

---

## Important Notes

* The `dev.sh` script expects the Python virtual environment to exist at `rag-service/venv`.
* If the RAG service fails to start, ensure the virtual environment is properly created and dependencies are installed.
* Ollama must be installed and accessible in your system PATH.

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

The response currently includes:

* Ranked matches
* Similarity scores
* Aggregated context

LLM-based answer generation will be added in the next milestone.

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
* Provide a foundation for evolving toward persistent storage and production-ready patterns

---

## Future Direction

The next major evolution will replace the in-memory store with SQLite while keeping vector search logic explicit and understandable.

This repository serves as a reference implementation and experimentation ground before building a more structured version intended for teaching purposes.
