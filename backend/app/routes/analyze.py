import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.input_schema import SymptomFormInput
from app.schemas.output_schema import AnalyzeResponse
from app.agents.orchestrator import analyze_symptoms_workflow

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze-symptoms", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
def analyze_symptoms(payload: SymptomFormInput):
    try:
        return analyze_symptoms_workflow(payload)
    except Exception as exc:
        logger.error("analyze_symptoms failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Symptom analysis failed. Please try again.",
        )
