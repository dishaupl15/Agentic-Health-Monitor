from fastapi import APIRouter
from app.schemas.input_schema import RagQueryRequest
from app.schemas.output_schema import RagResponse
from app.rag.retriever import retrieve_relevant_chunks

router = APIRouter()

@router.post('/rag-retrieve', response_model=RagResponse)
def rag_retrieve(payload: RagQueryRequest):
    chunks = retrieve_relevant_chunks(payload.query, top_k=payload.top_k)
    return RagResponse(chunks=chunks)
