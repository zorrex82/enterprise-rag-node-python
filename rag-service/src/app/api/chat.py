from __future__ import annotations

import os

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.embeddings import embed_text
from app.core.llm import generate_answer
from app.core.memory_store import STORE
from app.core.vectorstore import top_k_similar


router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/v1/chat")
def chat(request: ChatRequest, top_k: int = Query(default=5, ge=1, le=20)) -> dict:
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    chat_model = os.getenv("CHAT_MODEL", "llama3.1")

    question = request.question

    # 1 - Embed the question
    query_embedding = embed_text(
        text=question,
        base_url=ollama_base_url,
        model=embedding_model,
    )

    # 2 - Retrieve top-k similar chunks from the store
    ranked = top_k_similar(STORE, query_embedding, k=top_k)

    # 3 - Build matches + context
    matches = []
    context_parts = []

    for chunk_id, score in ranked:
        chunk = STORE.get(chunk_id)
        chunk_text = chunk.get("text") if chunk else None

        matches.append(
            {
                "chunk_id": chunk_id,
                "score": score,
                "text": chunk_text,
            }
        )

        if chunk_text:
            context_parts.append(f"[{chunk_id}] {chunk_text}")

    # avoid call llm without context
    if not context_parts:
        return {
            "question": question,
            "answer": "I don't know based on the provided context.",
            "chat_model": chat_model,
            "matches": matches,
            "match_count": len(matches),
            "context": "",
        }

    context = "\n\n".join(context_parts)

    # Protection against large context
    max_context_chars = 4000
    if len(context) > max_context_chars:
        context = context[:max_context_chars]

    # 4 - Generate a grounded answer using Ollama chat model
    answer = generate_answer(
        question=question,
        context=context,
        base_url=ollama_base_url,
        model=chat_model,
    )

    return {
        "question": question,
        "answer": answer,
        "chat_model": chat_model,
        "matches": matches,
        "match_count": len(matches),
        "context": context,
    }
