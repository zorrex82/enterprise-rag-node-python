import os
from datetime import datetime, timezone

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.chunking import chunk_text
from app.core.embeddings import embed_text
from app.core.memory_store import STORE
from app.core.sqlite_db import init_db, upsert_chunk

router = APIRouter()

class IngestRequest(BaseModel):
    text: str

@router.post("/v1/ingest")
def ingest(
    request: IngestRequest,
    verbose: bool = Query(default=False)
) -> dict:
    init_db()

    chunks = chunk_text(request.text)
    chunk_ids = [c["id"] for c in chunks]

    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    embedding_dim = None
    created_at_utc = datetime.now(timezone.utc).isoformat()

    for c in chunks:
        chunk_id = c["id"]
        chunk_text_value = c["text"]

        vec = embed_text(chunk_text_value, base_url=ollama_base_url, model=embedding_model)
        
        # In-memory store (current behavior)
        STORE[chunk_id] = {"text": chunk_text_value, "embedding": vec}

        # SQLite persistence (new behavior)
        upsert_chunk(
            chunk_id=chunk_id,
            text=chunk_text_value,
            embedding=vec,
            created_at_utc=created_at_utc,
        )

        if embedding_dim is None:
            embedding_dim = len(vec)

    response = {
        "status": "accepted",
        "chunks_created": len(chunks),
        "chunk_ids": chunk_ids,
        "embedding_dim": embedding_dim,
        "embedding_model": embedding_model,
    }

    if verbose:
        response["chunks_preview"] = [
            {
                "id": cid,
                "text_preview": STORE[cid]["text"][:80],
                "embedding_preview": STORE[cid]["embedding"][:5],
            }
            for cid in chunk_ids
        ]

    return response
