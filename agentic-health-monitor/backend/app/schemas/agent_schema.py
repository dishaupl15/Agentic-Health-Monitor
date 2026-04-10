"""
app/schemas/agent_schema.py
Internal Pydantic models for agent inputs and outputs.
These are used between agents and the orchestrator — not exposed in the API directly.
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ── Symptom Agent ─────────────────────────────────────────────────────────────

class SymptomAgentInput(BaseModel):
    symptoms: str
    duration: str
    severity: str
    age: Optional[int] = None
    gender: Optional[str] = None
    history: Optional[str] = None
    bp: Optional[str] = None
    sugar: Optional[str] = None
    temperature: Optional[str] = None


class SymptomAgentOutput(BaseModel):
    summary: str = Field(description="Concise clinical-style summary of the patient case.")
    concern_level: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"] = Field(
        description="Triage concern level."
    )
    follow_up_needed: bool = Field(
        description="Whether clarifying questions are needed before risk assessment."
    )
    rationale: str = Field(description="Brief reasoning behind the concern level.")


# ── Clarification Agent ───────────────────────────────────────────────────────

class ClarificationAgentInput(BaseModel):
    symptoms: str
    summary: str = ""


class ClarificationQuestion(BaseModel):
    question: str
    priority: Literal["URGENT", "HIGH", "MEDIUM", "LOW"]
    reason: str


class ClarificationAgentOutput(BaseModel):
    questions: List[ClarificationQuestion] = Field(description="4-8 prioritized questions.")
    priority_reason: str = Field(description="Overall questioning strategy explanation.")

    @field_validator("questions")
    @classmethod
    def sort_and_limit(cls, v: List[ClarificationQuestion]) -> List[ClarificationQuestion]:
        order = {"URGENT": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(v, key=lambda q: order.get(q.priority, 4))[:8]


# ── Risk Agent ────────────────────────────────────────────────────────────────

class RiskAgentInput(BaseModel):
    symptoms: str
    duration: str
    severity: str
    follow_up_answers: dict
    summary: str = ""


class PossibleCondition(BaseModel):
    name: str = Field(description="Possible condition name. Not a definitive diagnosis.")
    score: float = Field(ge=0.0, le=1.0, description="Likelihood score 0.0-1.0.")
    reasoning: str = Field(description="One sentence clinical reasoning.")


class RiskAgentOutput(BaseModel):
    possible_conditions: List[PossibleCondition] = Field(description="Top 1-3 conditions.")
    confidence: Literal["Low", "Moderate", "High"]
    risk_level: Literal["Low", "Medium", "High", "Emergency"]
    urgency: Literal["Routine monitoring", "Within 3 days", "Within 24 hours", "Immediate"]
    explanation: str = Field(description="2-3 sentence reasoning with acknowledged uncertainty.")

    @field_validator("possible_conditions")
    @classmethod
    def sort_and_limit(cls, v: List[PossibleCondition]) -> List[PossibleCondition]:
        return sorted(v, key=lambda c: c.score, reverse=True)[:3]


# ── Recommendation Agent ──────────────────────────────────────────────────────

class RecommendationAgentInput(BaseModel):
    risk_level: str
    urgency: str
    explanation: str
    possible_conditions: List[str] = Field(default_factory=list)


class RecommendationAgentOutput(BaseModel):
    recommendation: str = Field(description="1-2 sentence primary recommendation.")
    next_steps: List[str] = Field(description="3-5 concrete actionable steps.")
    disclaimer: str = Field(description="Medical disclaimer.")

    @field_validator("next_steps")
    @classmethod
    def enforce_steps(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("next_steps must not be empty.")
        return v[:5]
