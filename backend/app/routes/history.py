import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.output_schema import HistoryResponse
from app.db.database import list_reports

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK)
def get_history():
    try:
        reports = list_reports()
        return HistoryResponse(reports=reports)
    except Exception as exc:
        logger.error("get_history failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load history. Please try again.",
        )
