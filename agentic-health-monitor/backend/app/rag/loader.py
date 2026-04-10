import re
from pathlib import Path
from typing import Dict, List

MEDICAL_DOCS_PATH = Path(__file__).resolve().parents[2] / 'medical_docs'


def chunk_text(text: str, chunk_size: int = 450, overlap: int = 90) -> List[str]:
    text = re.sub(r'\s+', ' ', text.strip())
    if not text:
        return []

    words = text.split(' ')
    chunks: List[str] = []
    current: List[str] = []

    for word in words:
        current.append(word)
        if len(' '.join(current)) >= chunk_size:
            chunks.append(' '.join(current).strip())
            overlap_words = current[-overlap:] if overlap < len(current) else current
            current = overlap_words.copy()

    if current:
        chunks.append(' '.join(current).strip())

    return chunks


def load_documents() -> List[Dict[str, str]]:
    documents: List[Dict[str, str]] = []
    if MEDICAL_DOCS_PATH.exists():
        for path in sorted(MEDICAL_DOCS_PATH.glob('*.txt')):
            if path.is_file():
                raw_text = path.read_text(encoding='utf-8').strip()
                for idx, chunk in enumerate(chunk_text(raw_text)):
                    documents.append({
                        'id': f'{path.stem}_{idx}',
                        'source': path.name,
                        'text': chunk,
                    })
    return documents
