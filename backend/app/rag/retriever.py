from typing import List, Dict

from app.rag.vector_store import query_similar_chunks


def retrieve_relevant_chunks(symptom_text: str, top_k: int = 3) -> List[Dict[str, object]]:
    return query_similar_chunks(symptom_text, top_k=top_k)
