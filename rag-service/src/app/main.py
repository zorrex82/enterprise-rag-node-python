from fastapi import FastAPI

app = FastAPI(title="rag-service", version="0.1.0")

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "rag-service",
    }