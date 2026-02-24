from typing import Dict, List

# Simple in-memory store (temporary, for local dev)
# key: chunk_id
# value: {"text": str, "embedding": List[float]}
STORE: Dict[str, dict] = {}