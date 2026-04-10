"""
app/agents/recommendation_agent.py
Recommendation Agent - converts risk assessment into actionable patient guidance.
"""
import logging
from typing import List
from pydantic import BaseModel, Field, field_validator
from app.core.llm import chat_structured

logger = logging.getLogger(__name__)


class RecommendationOutput(BaseModel):
    recommendation: str
    next_steps: List[str] = Field(description="3-5 concrete actionable steps.")
    disclaimer: str

    @field_validator("next_steps")
    @classmethod
    def enforce_steps(cls, v):
        return v[:5] if v else ["Consult a healthcare provider."]


_SYSTEM = """\
You are a patient guidance AI. Convert the risk assessment into clear, safe, actionable guidance.

Rules:
- Tailor next_steps to the actual possible conditions, not just the risk level.
- Never prescribe specific medications or claim a definitive diagnosis.
- Emergency: instruct to call emergency services immediately.
- High: advise urgent care or same-day doctor visit.
- Medium: schedule doctor within 2-3 days, monitor symptoms.
- Low: rest, hydration, home care, clear criteria to escalate.

You MUST respond with ONLY this exact JSON structure, no extra text:
{
  "recommendation": "<clear patient-facing recommendation>",
  "next_steps": [
    "<actionable step 1>",
    "<actionable step 2>",
    "<actionable step 3>"
  ],
  "disclaimer": "<medical disclaimer>"
}"""


def get_full_recommendation(
    risk_level: str,
    urgency: str,
    explanation: str,
    possible_conditions: list,
) -> dict:
    conditions_text = ", ".join(
        c.name if hasattr(c, "name") else str(c) for c in possible_conditions
    ) or "unspecified condition"

    user_message = (
        "Risk Level: " + risk_level + "\n"
        "Urgency: " + urgency + "\n"
        "Possible Conditions: " + conditions_text + "\n\n"
        "Clinical Explanation:\n" + explanation + "\n\n"
        "Generate patient guidance and next steps."
    )
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_message},
    ]

    try:
        result: RecommendationOutput = chat_structured(
            messages=messages,
            output_model=RecommendationOutput,
            temperature=0.3,
        )
        logger.info("[RecommendationAgent] recommendation generated for risk=%s", risk_level)
        print("[RECOMMENDATION AGENT] OK - recommendation generated for risk=" + risk_level)
        return {
            "recommendation": result.recommendation,
            "next_steps": result.next_steps,
            "disclaimer": result.disclaimer,
        }
    except Exception as exc:
        logger.warning("[RecommendationAgent] LLM failed (%s) - using fallback.", exc)
        print("[RECOMMENDATION AGENT] FAILED: " + str(exc) + " - fallback used")
        return _fallback_recommendation(risk_level, urgency)


def _fallback_recommendation(risk_level: str, urgency: str) -> dict:
    if risk_level == "Emergency":
        rec = "Call emergency services (911) immediately. Do not drive yourself."
        steps = [
            "Call 911 or your local emergency number immediately.",
            "Do not eat or drink anything.",
            "Stay calm and keep the patient still.",
            "Inform emergency responders of all symptoms.",
        ]
    elif risk_level == "High":
        rec = "Seek urgent medical care today. Do not delay."
        steps = [
            "Go to an urgent care clinic or emergency room today.",
            "Bring a list of your current medications.",
            "Monitor symptoms closely and call 911 if they worsen rapidly.",
        ]
    elif risk_level == "Medium":
        rec = "Schedule a doctor's appointment within 2-3 days."
        steps = [
            "Book a doctor's appointment within 2-3 days.",
            "Rest and stay hydrated.",
            "Monitor symptoms and seek emergency care if they worsen.",
        ]
    else:
        rec = "Rest and monitor your symptoms. Seek care if symptoms worsen."
        steps = [
            "Rest and stay well hydrated.",
            "Take over-the-counter medication as appropriate.",
            "Seek medical attention if symptoms persist beyond 5 days or worsen.",
        ]
    return {
        "recommendation": rec,
        "next_steps": steps,
        "disclaimer": "This is an AI-generated assessment and does not replace professional medical advice.",
    }
