import json
import urllib.request
from typing import List

def embed_text(text: str, base_url: str, model: str) -> List[float]:
    payload = {
        "model": model,
        "prompt": text,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url = f"{base_url.rstrip('/')}/api/embeddings",
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
        parsed = json.loads(body)

    return parsed["embedding"]