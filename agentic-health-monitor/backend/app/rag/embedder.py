import re
from collections import Counter
from math import sqrt
from typing import Dict, List, Union

from openai import OpenAI
from app.core.config import get_settings


def _get_client() -> OpenAI | None:
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def normalize_text(text: str) -> str:
    return re.sub(r'[^a-z0-9\s]', ' ', text.lower()).strip()


def simple_text_embedding(text: str) -> Dict[str, int]:
    tokens = normalize_text(text).split()
    return dict(Counter(tokens))


def _dicts_to_float_vectors(dicts: List[Dict[str, int]]) -> List[List[float]]:
    """Convert bag-of-words dicts to fixed-length float vectors using a shared vocab."""
    vocab = sorted({k for d in dicts for k in d})
    if not vocab:
        return [[0.0] for _ in dicts]
    return [[float(d.get(word, 0)) for word in vocab] for d in dicts]


def create_embeddings(texts: List[str]) -> List[List[float]]:
    client = _get_client()
    if client:
        try:
            model = get_settings().openai_embedding_model
            response = client.embeddings.create(model=model, input=texts)
            return [item.embedding for item in response.data]
        except Exception:
            pass

    # Fallback: bag-of-words converted to fixed-length float vectors
    bow_dicts = [simple_text_embedding(text) for text in texts]
    return _dicts_to_float_vectors(bow_dicts)


def cosine_similarity(vec_a: Union[List[float], Dict[str, int]], vec_b: Union[List[float], Dict[str, int]]) -> float:
    if isinstance(vec_a, dict) and isinstance(vec_b, dict):
        dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in vec_a)
        norm_a = sqrt(sum(v * v for v in vec_a.values()))
        norm_b = sqrt(sum(v * v for v in vec_b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    if isinstance(vec_a, list) and isinstance(vec_b, list):
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sqrt(sum(a * a for a in vec_a))
        norm_b = sqrt(sum(b * b for b in vec_b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    return 0.0
