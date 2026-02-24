import os

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from app.core.chunking import chunk_text
from app.core.embeddings import embed_text
from app.core.memory_store import STORE

router = APIRouter()

class IngestRequest(BaseModel):
    text: str

@router.post("/v1/ingest")
def ingest(
    request: IngestRequest,
    verbose: bool = Query(default=False)
) -> dict:

    chunks = chunk_text(request.text)
    chunk_ids = [c["id"] for c in chunks]

    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    embedding_dim = None

    for c in chunks:
        vec = embed_text(c["text"], base_url=ollama_base_url, model=embedding_model)
        STORE[c["id"]] = {"text": c["text"], "embedding": vec}
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
