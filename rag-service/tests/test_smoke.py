from socket import timeout
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

BASE_URL = "http://localhost:8000"

@retry(stop=stop_after_attempt(10), wait=wait_fixed(1))
def wait_for_service():
    """
    Wait until the rag-service health endpoint responds successfully.
    Retries up to 10 times, waiting 1 second between attempts.
    """

    r = httpx.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200


def test_ingest_and_chat_with_doc_id():
    """
    Smoke test:
    1. Wait for service
    2. Ingest a document with a specific doc_id
    3. Query using the same doc_id
    4. Validate that we get at least one match
    """

    wait_for_service()

    doc_id = "test_doc_smoke"

    # 1 - Ingest
    ingest_response = httpx.post(
        f"{BASE_URL}/v1/ingest",
        json={
            "doc_id": doc_id,
            "text": "FastAPI is a modern Python web framework for building APIs."
        },
        timeout=30,
    )

    assert ingest_response.status_code == 200
    ingest_data = ingest_response.json()
    assert ingest_data["doc_id"] == doc_id
    assert ingest_data["chunks_created"] >= 1

    # 2 - Chat
    chat_response = httpx.post(
        f"{BASE_URL}/v1/chat?doc_id={doc_id}&top_k=3",
        json={
            "question": "what is FastAPI?"
        },
        timeout=30,
    )

    assert chat_response.status_code == 200
    chat_data = chat_response.json()

    assert chat_data["doc_id"] == doc_id
    assert chat_data["match_count"] >= 1
    assert "framework" in chat_data["answer"].lower()