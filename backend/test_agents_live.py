"""
Live diagnostic — runs the full agent pipeline on two test cases
and prints exactly what each agent returns.
Run: python test_agents_live.py
"""
import traceback
import json

TEST_CASES = [
    {
        "label": "JAUNDICE / LIVER",
        "symptoms": "Yellowish skin and eyes, dark urine, severe itching, abdominal pain",
    },
    {
        "label": "STROKE",
        "symptoms": "Sudden weakness on one side of the body, difficulty speaking, blurred vision in one eye, severe headache",
    },
]


def run():
    # ── 1. Raw LLM health check ──────────────────────────────────────────────
    print("\n" + "="*60)
    print("STEP 0: RAW LLM HEALTH CHECK")
    print("="*60)
    try:
        from app.core.llm import chat_completion
        raw = chat_completion(
            messages=[{"role": "user", "content": 'Return JSON: {"status": "ok"}'}],
            json_mode=True,
        )
        print(f"  LLM response: {raw}")
    except Exception:
        print("  ❌ LLM FAILED:")
        traceback.print_exc()
        print("\n  Cannot continue — fix LLM connection first.")
        return

    # ── 2. Per test case ─────────────────────────────────────────────────────
    for case in TEST_CASES:
        print("\n" + "="*60)
        print(f"TEST CASE: {case['label']}")
        print(f"INPUT:     {case['symptoms']}")
        print("="*60)

        symptoms = case["symptoms"]

        # Step 1: Symptom Interpreter
        print("\n[1] SYMPTOM INTERPRETER AGENT")
        try:
            from app.agents.symptom_agent import interpret_symptoms
            interp = interpret_symptoms(symptoms=symptoms, age=35, gender="unknown")
            print(f"  possible_conditions : {interp.possible_conditions}")
            print(f"  body_system         : {interp.body_system}")
            print(f"  risk_level          : {interp.risk_level}")
            print(f"  symptom_cluster     : {interp.symptom_cluster}")
            print(f"  is_emergency        : {interp.is_emergency}")
        except Exception:
            print("  ❌ FAILED:")
            traceback.print_exc()
            interp = None

        # Step 2: Symptom Summarizer
        print("\n[2] SYMPTOM SUMMARIZER AGENT")
        try:
            from app.agents.symptom_agent import summarize_symptoms
            summary, follow_up_needed, _ = summarize_symptoms(
                symptoms=symptoms, duration="2 days", severity="severe", age=35
            )
            print(f"  follow_up_needed : {follow_up_needed}")
            print(f"  summary          : {summary}")
        except Exception:
            print("  ❌ FAILED:")
            traceback.print_exc()
            summary, follow_up_needed = "", True

        # Step 3: Clarification / Question Generation
        print("\n[3] CLARIFICATION AGENT (QUESTION GENERATION)")
        try:
            from app.agents.clarification_agent import generate_follow_up_questions
            questions = generate_follow_up_questions(
                symptoms=symptoms,
                summary=summary,
                interpretation=interp,
            )
            print(f"  Generated {len(questions)} questions:")
            for i, q in enumerate(questions, 1):
                print(f"    {i}. {q}")
        except Exception:
            print("  ❌ FAILED:")
            traceback.print_exc()

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)


if __name__ == "__main__":
    run()
