import uuid
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[dict]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
        })

        start += chunk_size - overlap

    return chunks
