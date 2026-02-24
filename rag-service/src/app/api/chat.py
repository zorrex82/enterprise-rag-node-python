import os

from email.policy import default
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.embeddings import embed_text
from app.core.memory_store import STORE
from app.core.vectorstore import top_k_similar

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/v1/chat")
def chat(request: ChatRequest, top_k: int = Query(default=5, ge=1, le=20)) -> dict:
    """
    Retrieve the most relevant chunks from STORE  using cosine similarity.
    """
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # generate embedding for the question
    query_embedding = embed_text(
        text=request.question,
        base_url=ollama_base_url,
        model=embedding_model
        )

    # retrieve top-k similar chunks
    ranked = top_k_similar(STORE, query_embedding, k=top_k)

    # build response with chunk text and score
    results = []
    context_parts = []

    for chunk_id, score in ranked:
        chunk = STORE.get(chunk_id)
        chunk_text  = chunk.get("text") if  chunk else None

        results.append({
            "chunk_id": chunk_id,
            "score": score,
            "text": chunk_text,
        })

        if chunk_text:
            # keep context deterministic and readable
            context_parts.append(f"[{chunk_id}] {chunk_text}")

    context = "\n\n".join(context_parts)        

    return {
        "question": request.question,
        "matches": results,
        "match_count": len(results),
        "context": context,
    }
    