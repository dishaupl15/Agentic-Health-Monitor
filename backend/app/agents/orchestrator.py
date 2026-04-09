"""
app/agents/orchestrator.py
Coordinates all LLM agents. Routes call these functions — never agents directly.
"""
import logging
from typing import Dict, List, Optional
from app.schemas.input_schema import SymptomFormInput
from app.schemas.output_schema import (
    AnalyzeResponse,
    FinalAssessmentResponse,
    RagChunk,
    ConditionItem,
)
from app.agents.symptom_agent import summarize_symptoms, interpret_symptoms
from app.agents.clarification_agent import generate_follow_up_questions
from app.agents.risk_agent import assess_risk
from app.agents.recommendation_agent import get_full_recommendation
from app.tools.rag_tool import retrieve_as_dicts

logger = logging.getLogger(__name__)


def analyze_symptoms_workflow(payload: SymptomFormInput) -> AnalyzeResponse:
    print("\n" + "="*60)
    print("[ORCHESTRATOR] analyze_symptoms_workflow CALLED")
    print(f"  patient  : {payload.name} | age={payload.age} | gender={payload.gender}")
    print(f"  symptoms : {payload.symptoms}")
    print(f"  duration : {payload.duration} | severity : {payload.severity}")
    print("="*60)

    # Step 1: Symptom Interpreter
    print("\n[STEP 1] Running Symptom Interpreter Agent...")
    interpretation = interpret_symptoms(
        symptoms=payload.symptoms,
        age=payload.age,
        gender=payload.gender,
    )

    # Step 2: Symptom Summarizer
    print("\n[STEP 2] Running Symptom Summarizer Agent...")
    summary, follow_up_needed, _ = summarize_symptoms(
        symptoms=payload.symptoms,
        duration=payload.duration,
        severity=payload.severity,
        bp=payload.bp,
        sugar=payload.sugar,
        temperature=payload.temperature,
        age=payload.age,
        gender=payload.gender,
        history=payload.history,
    )
    print(f"\n[STEP 2] follow_up_needed={follow_up_needed}")

    # Step 3: Clarification Agent
    questions: List[str] = []
    if follow_up_needed:
        print("\n[STEP 3] Running Clarification Agent...")
        questions = generate_follow_up_questions(
            symptoms=payload.symptoms,
            summary=summary,
            interpretation=interpretation,
        )
        print(f"[STEP 3] {len(questions)} questions generated")
    else:
        print("\n[STEP 3] Clarification Agent SKIPPED — follow_up_needed=False")

    # Step 4: RAG Tool
    print("\n[STEP 4] Running RAG retrieval...")
    raw_chunks = retrieve_as_dicts(payload.symptoms, top_k=3)
    relevant_knowledge = [
        RagChunk(
            id=str(c.get("id", "")),
            source=str(c.get("source", "unknown")),
            text=str(c.get("text", "")),
            score=float(c.get("score", 0.0)),
        )
        for c in raw_chunks
    ]
    print(f"[STEP 4] {len(relevant_knowledge)} RAG chunks retrieved")
    for c in relevant_knowledge:
        print(f"  source={c.source} | score={c.score:.2f}")

    print("\n[ORCHESTRATOR] analyze_symptoms_workflow COMPLETE")
    print("="*60 + "\n")

    return AnalyzeResponse(
        symptom_summary=summary,
        follow_up_needed=follow_up_needed,
        follow_up_questions=questions,
        relevant_knowledge=relevant_knowledge,
    )


def final_assessment_workflow(
    original_data: SymptomFormInput,
    follow_up_answers: Dict[str, str],
    symptom_summary: Optional[str] = None,
) -> FinalAssessmentResponse:
    print("\n" + "="*60)
    print("[ORCHESTRATOR] final_assessment_workflow CALLED")
    print(f"  patient          : {original_data.name}")
    print(f"  symptoms         : {original_data.symptoms}")
    print(f"  follow_up_answers: {follow_up_answers}")
    print("="*60)

    # Step 1: Risk Agent
    print("\n[STEP 1] Running Risk Assessment Agent...")
    conditions, confidence, risk_level, urgency, explanation = assess_risk(
        symptoms=original_data.symptoms,
        duration=original_data.duration,
        severity=original_data.severity,
        follow_up_answers=follow_up_answers,
        summary=symptom_summary or "",
    )
    print(f"[STEP 1] risk={risk_level} | confidence={confidence} | urgency={urgency}")
    print(f"  conditions : {[c.name for c in conditions]}")

    # Step 2: Recommendation Agent
    print("\n[STEP 2] Running Recommendation Agent...")
    rec = get_full_recommendation(
        risk_level=risk_level,
        urgency=urgency,
        explanation=explanation,
        possible_conditions=conditions,
    )
    print(f"[STEP 2] recommendation generated")

    print("\n[ORCHESTRATOR] final_assessment_workflow COMPLETE")
    print("="*60 + "\n")

    return FinalAssessmentResponse(
        possible_conditions=conditions,
        confidence=confidence,
        risk_level=risk_level,
        urgency=urgency,
        explanation=explanation,
        recommendation=rec["recommendation"],
        next_steps=rec.get("next_steps", []),
        disclaimer=rec.get("disclaimer", ""),
        follow_up_answers=follow_up_answers,
    )
