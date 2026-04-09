import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.input_schema import ReportCreate
from app.schemas.output_schema import SaveReportResponse
from app.db.database import save_report

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/save-report", response_model=SaveReportResponse, status_code=status.HTTP_201_CREATED)
def save_report_endpoint(payload: ReportCreate):
    try:
        save_report(payload)
        return SaveReportResponse(success=True, message="Report saved successfully.")
    except Exception as exc:
        logger.error("save_report failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save report. Please try again.",
        )
