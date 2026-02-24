from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.chat import router as chat_router

app = FastAPI(title="rag-service", version="0.1.0")

app.include_router(ingest_router)
app.include_router(chat_router)

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "rag-service",
    }

