"""
RAG Tool — reusable retrieval tool for all LLM agents.
Wraps ChromaDB querying with error handling, typed output,
and prompt-ready formatting. Compatible with existing vector_store.
"""
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from app.rag.vector_store import query_similar_chunks

logger = logging.getLogger(__name__)

# Minimum relevance score to include a chunk (0.0-1.0, higher = more relevant)
_MIN_SCORE: float = 0.0


# Typed output model for a single retrieved chunk

class RetrievedChunk(BaseModel):
    id: str
    source: str
    text: str
    score: float = Field(ge=0.0, le=1.0)


def retrieve(
    query: str,
    top_k: int = 3,
    min_score: float = _MIN_SCORE,
) -> List[RetrievedChunk]:
    """
    Query ChromaDB with the given text and return top_k relevant chunks.

    Args:
        query:     Case text or symptom description to search against.
        top_k:     Maximum number of chunks to return.
        min_score: Minimum relevance score threshold (0.0 = no filter).

    Returns:
        List of RetrievedChunk objects ordered by score descending.
        Returns empty list on any error — never raises.
    """
    if not query or not query.strip():
        logger.warning("RAG Tool: empty query received, skipping retrieval.")
        return []

    try:
        raw = query_similar_chunks(query.strip(), top_k=top_k)
    except Exception as exc:
        logger.error("RAG Tool: ChromaDB query failed. Error: %s", exc)
        return []

    chunks: List[RetrievedChunk] = []
    for item in raw:
        try:
            score = float(item.get("score", 0.0))
            if score < min_score:
                continue
            chunks.append(RetrievedChunk(
                id=str(item.get("id", "")),
                source=str(item.get("source", "unknown")),
                text=str(item.get("text", "")),
                score=round(score, 4),
            ))
        except Exception as exc:
            logger.warning("RAG Tool: skipping malformed chunk. Error: %s", exc)
            continue

    return sorted(chunks, key=lambda c: c.score, reverse=True)


def retrieve_as_context(
    query: str,
    top_k: int = 3,
    min_score: float = _MIN_SCORE,
) -> str:
    """
    Retrieve chunks and format them as a single context string
    ready to be injected into an LLM system or user prompt.

    Returns a fallback string if nothing is found or retrieval fails.
    """
    chunks = retrieve(query, top_k=top_k, min_score=min_score)

    if not chunks:
        return "No relevant medical context found in the knowledge base."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Medical Reference {i} | Source: {chunk.source} | Relevance: {chunk.score:.2f}]\n"
            f"{chunk.text}"
        )

    return "\n\n".join(parts)


def retrieve_as_dicts(
    query: str,
    top_k: int = 3,
    min_score: float = _MIN_SCORE,
) -> List[dict]:
    """
    Retrieve chunks and return as plain dicts.
    Used by routes that need to serialize chunks into API responses.
    """
    return [c.model_dump() for c in retrieve(query, top_k=top_k, min_score=min_score)]
