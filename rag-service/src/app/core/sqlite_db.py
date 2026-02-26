from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


def _db_path() -> str:
    # Allow override via env var
    env_path = os.getenv("SQLITE_DB_PATH")
    if env_path and env_path.strip():
        return env_path

    # Resolve default path to: <repo_root>/rag-service/data/rag.db
    # This file is: <repo_root>/rag-service/src/app/core/sqlite_db.py
    # We find the "rag-service" directory by walking parents.
    here = Path(__file__).resolve()
    rag_service_dir = None

    for parent in here.parents:
        if parent.name == "rag-service" and (parent / "src").exists():
            rag_service_dir = parent
            break

    if rag_service_dir is None:
        # Fallback: assume 4 levels up lands inside rag-service (last resort)
        rag_service_dir = here.parents[4]

    return str(rag_service_dir / "data" / "rag.db")

def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    path = _db_path()
    _ensure_parent_dir(path)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    # basic pragmas safe defaults
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            embedding_json TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at_utc)")
        conn.commit()


def upsert_chunk(
    *,
    chunk_id: str,
    text: str,
    embedding: List[float],
    created_at_utc: str,
) -> None:
    embedding_json = json.dumps(embedding)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chunks (chunk_id, text, embedding_json, created_at_utc)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chunk_id) DO UPDATE SET
                text = excluded.text,
                embedding_json = excluded.embedding_json,
                created_at_utc = excluded.created_at_utc
            """,
            (chunk_id, text, embedding_json, created_at_utc),
        )
        conn.commit()

def fetch_all_chunks() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT chunk_id, text, embedding_json, created_at_utc FROM chunks ORDER BY created_at_utc ASC"
        ).fetchall()
    
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "chunk_id": r["chunk_id"],
                "text": r["text"],
                "embedding": json.loads(r["embedding_json"]),
                "created_at_utc": r["created_at_utc"],
            }
        )
    return out