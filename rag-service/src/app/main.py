from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.core.memory_store import STORE
from app.core.sqlite_db import fetch_all_chunks, init_db

app = FastAPI(title="rag-service", version="0.1.0")

app.include_router(ingest_router)
app.include_router(chat_router)

@app.on_event("startup")
def on_startup() -> None:
    init_db()

    items = fetch_all_chunks()

    # Reset in-memory store and repopulate from SQLite
    STORE.clear()
    for item in items:
        STORE[item["chunk_id"]] = {
            "text": item["text"],
            "embedding": item["embedding"],
        }

    print(f"Loaded {len(items)} chunks from SQLite into in-memory STORE.")

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "rag-service",
        "store_size": len(STORE),
    }

