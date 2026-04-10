"""
app/agents/risk_agent.py
Risk Assessment Agent - reasons over symptoms + follow-up answers + RAG context.
"""
import logging
from typing import Dict, List, Literal, Tuple
from pydantic import BaseModel, Field, field_validator
from app.core.llm import chat_structured
from app.tools.rag_tool import retrieve_as_context
from app.schemas.output_schema import ConditionItem

logger = logging.getLogger(__name__)


class PossibleCondition(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str


class RiskAssessmentOutput(BaseModel):
    possible_conditions: List[PossibleCondition]
    confidence: Literal["Low", "Moderate", "High"]
    risk_level: Literal["Low", "Medium", "High", "Emergency"]
    urgency: Literal["Routine monitoring", "Within 3 days", "Within 24 hours", "Immediate"]
    explanation: str

    @field_validator("possible_conditions")
    @classmethod
    def sort_and_limit(cls, v):
        return sorted(v, key=lambda c: c.score, reverse=True)[:3]


_SYSTEM = """\
You are a clinical risk assessment AI. Reason over the full patient case.

Rules:
- Never state a definitive diagnosis. Use: may suggest, consistent with, could indicate.
- Acknowledge overlapping symptoms and uncertainty in the explanation.
- When information is incomplete, lean toward higher risk.
- Use retrieved medical context to ground your reasoning.
- Over-triage rather than under-triage.

Risk levels: Emergency=life-threatening, High=24h, Medium=3 days, Low=home care.

You MUST respond with ONLY this exact JSON structure, no extra text:
{
  "possible_conditions": [
    {"name": "<condition name>", "score": <0.0-1.0>, "reasoning": "<why this condition fits>"},
    {"name": "<condition name>", "score": <0.0-1.0>, "reasoning": "<why this condition fits>"}
  ],
  "confidence": "<Low|Moderate|High>",
  "risk_level": "<Low|Medium|High|Emergency>",
  "urgency": "<Routine monitoring|Within 3 days|Within 24 hours|Immediate>",
  "explanation": "<2-3 sentence clinical explanation>"
}"""


def assess_risk(
    symptoms: str,
    duration: str,
    severity: str,
    follow_up_answers: Dict[str, str],
    summary: str = "",
) -> Tuple[List[ConditionItem], str, str, str, str]:
    rag_context = retrieve_as_context(symptoms, top_k=3)

    answers_text = "\n".join(
        "  Q: " + q + "\n  A: " + a for q, a in follow_up_answers.items()
    ) or "None provided."

    user_message = (
        "Symptoms: " + symptoms + "\n"
        "Duration: " + duration + " | Severity: " + severity + "\n\n"
        "Follow-up Answers:\n" + answers_text + "\n\n"
        "Clinical Summary:\n" + (summary or "Not available.") + "\n\n"
        "Relevant Medical Context:\n" + rag_context + "\n\n"
        "Assess the full case and return the risk JSON."
    )
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_message},
    ]

    try:
        result: RiskAssessmentOutput = chat_structured(
            messages=messages,
            output_model=RiskAssessmentOutput,
            temperature=0.2,
        )
        conditions = [ConditionItem(name=c.name, score=c.score) for c in result.possible_conditions]
        logger.info("[RiskAgent] risk=%s | confidence=%s | urgency=%s", result.risk_level, result.confidence, result.urgency)
        print("[RISK AGENT] risk=" + result.risk_level + " | confidence=" + result.confidence + " | urgency=" + result.urgency)
        print("  conditions : " + str([c.name for c in conditions]))
        return conditions, result.confidence, result.risk_level, result.urgency, result.explanation

    except Exception as exc:
        logger.warning("[RiskAgent] LLM failed (%s) - using safe fallback.", exc)
        print("[RISK AGENT] FAILED: " + str(exc) + " - fallback used")
        return (
            [ConditionItem(name="Unspecified condition", score=0.5)],
            "Low",
            "High",
            "Within 24 hours",
            "Unable to complete automated risk assessment. Symptoms reported: " + symptoms + ". "
            "Please consult a healthcare provider promptly.",
        )
