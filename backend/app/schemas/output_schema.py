"""
app/schemas/output_schema.py
Response models for FastAPI routes.
ConditionItem lives here as the single source of truth — imported by input_schema and agents.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ConditionItem(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)


class RagChunk(BaseModel):
    id: str
    source: str
    text: str
    score: float = Field(ge=0.0, le=1.0)


class AnalyzeResponse(BaseModel):
    symptom_summary: str
    follow_up_needed: bool
    follow_up_questions: List[str]
    relevant_knowledge: List[RagChunk] = Field(default_factory=list)


class FinalAssessmentResponse(BaseModel):
    possible_conditions: List[ConditionItem]
    confidence: str
    risk_level: str
    urgency: str
    explanation: str
    recommendation: str
    next_steps: List[str] = Field(default_factory=list)
    disclaimer: str = ""
    follow_up_answers: Optional[Dict[str, str]] = None


class SaveReportResponse(BaseModel):
    success: bool
    message: str


class ReportItem(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    symptoms: str
    duration: str
    severity: str
    history: Optional[str] = None
    bp: Optional[str] = None
    sugar: Optional[str] = None
    temperature: Optional[str] = None
    follow_up_answers: Dict[str, str]
    possible_conditions: List[ConditionItem]
    confidence: str
    risk_level: str
    urgency: str
    explanation: str
    recommendation: str
    created_at: datetime


class HistoryResponse(BaseModel):
    reports: List[ReportItem]


class RagResponse(BaseModel):
    chunks: List[RagChunk]
