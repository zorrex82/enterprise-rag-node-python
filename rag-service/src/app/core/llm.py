from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, Optional


def generate_answer(
    *,
    question: str,
    context: str,
    base_url: str,
    model: str,
    system_prompt: Optional[str] = None,
    timeout_seconds: int = 60,
) -> str:
    """
    Generate an answer using Ollama /api/chat, grounded on provided context.
    Local-first: no external services.
    """
    base_url = (base_url or "http://localhost:11434").rstrip("/")

    if not model or not model.strip():
        raise ValueError("model must be a non-empty string.")

    system_prompt = system_prompt or (
        "You are a helpful assistant. Use ONLY the provided context to answer. "
        "If the context does not contain the answer, say you don't know."
    )

    user_prompt = (
        "CONTEXT:\n"
        f"{context}\n\n"
        "QUESTION:\n"
        f"{question}\n\n"
        "INSTRUCTIONS:\n"
        "- Answer using only the context.\n"
        '- If the answer is not in the context, reply: "I don\'t know based on the provided context."'
    )

    payload: Dict[str, Any] = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    
    req = urllib.request.Request(
        url=f"{base_url}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
            out = json.loads(raw)
    except Exception as exc:  # pragma: no cover - network errors are environment-dependent
        raise RuntimeError(f"Failed to call Ollama /api/chat: {exc}") from exc

    # Ollama /api/chat returns {"message": {"role": "...", "content": "..."}, ...}
    message = out.get("message", {}) if isinstance(out, dict) else {}
    content = message.get("content", "") if isinstance(message, dict) else ""

    return (content or "").strip()
