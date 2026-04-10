import logging
from app.core.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def save_assessment(user_id: str, payload) -> dict:
    row = {
        "user_id": user_id,
        "symptoms": payload.symptoms,
        "summary": payload.explanation,
        "risk_level": payload.risk_level,
        "possible_conditions": [c.dict() for c in payload.possible_conditions],
        "follow_up_questions": payload.follow_up_answers,
    }
    result = get_supabase().table("assessments").insert(row).execute()
    return result.data[0] if result.data else {}
