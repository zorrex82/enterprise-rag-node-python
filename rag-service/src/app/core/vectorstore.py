from __future__ import annotations

import math
from typing import Dict, List, Tuple

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    Returns -1.0 if vectors are invalid or have zero magnitude.
    """

    if not a or not b or len(a) != len(b):
        return -1.0

    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y

    denom = math.sqrt(norm_a) * math.sqrt(norm_b)
    if denom == 0.0:
        return -1.0

    return dot / denom

def top_k_similar(
    store: Dict[str, dict],
    query_embedding: List[float],
    k: int = 5,
) -> List[Tuple[str, float]]:

    """
    Rank items in STORE by cosine similarity and return top-k (chunk_id, score).
    Expects each store item to have an 'embedding' key with a List[float].
    """

    scored: List[Tuple[str, float]] = []

    for chunk_id, item in store.items():
        emb = item.get("embedding")
        if not emb:
            continue

        score = cosine_similarity(query_embedding, emb)
        scored.append((chunk_id, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]