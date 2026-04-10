"""
Quick pipeline test — run with:
  .venv\Scripts\activate
  python test_pipeline.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

TEST_CASES = [
    {
        "label": "CARDIAC",
        "symptoms": "Chest pain spreading to left arm, sweating, nausea, shortness of breath",
        "age": 55, "gender": "male",
    },
    {
        "label": "STROKE / NEUROLOGICAL",
        "symptoms": "Sudden weakness on one side of the body, difficulty speaking, blurred vision",
        "age": 62, "gender": "female",
    },
    {
        "label": "LIVER / HEPATIC",
        "symptoms": "Yellowish skin and eyes, dark urine, severe itching, abdominal pain on right side",
        "age": 40, "gender": "male",
    },
]

def run():
    print("\n" + "="*65)
    print("PIPELINE TEST — 3 SYMPTOM CASES")
    print("="*65)

    from app.agents.symptom_agent import interpret_symptoms, summarize_symptoms
    from app.agents.clarification_agent import generate_follow_up_questions

    for case in TEST_CASES:
        print(f"\n{'='*65}")
        print(f"CASE: {case['label']}")
        print(f"INPUT: {case['symptoms']}")
        print("="*65)

        # Step 1: Interpreter
        interp = interpret_symptoms(
            symptoms=case["symptoms"],
            age=case["age"],
            gender=case["gender"],
        )
        print(f"\n[INTERPRETER RESULT]")
        print(f"  body_system : {interp.body_system}")
        print(f"  risk_level  : {interp.risk_level}")
        print(f"  conditions  : {interp.possible_conditions}")
        print(f"  emergency   : {interp.is_emergency}")

        # Step 2: Summarizer
        summary, follow_up_needed, _ = summarize_symptoms(
            symptoms=case["symptoms"],
            duration="2 days",
            severity="severe",
            age=case["age"],
            gender=case["gender"],
        )
        print(f"\n[SUMMARIZER RESULT]")
        print(f"  follow_up_needed : {follow_up_needed}")
        print(f"  summary          : {summary[:120]}...")

        # Step 3: Clarification
        questions = generate_follow_up_questions(
            symptoms=case["symptoms"],
            summary=summary,
            interpretation=interp,
        )
        print(f"\n[CLARIFICATION QUESTIONS] ({len(questions)} generated)")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")

    print(f"\n{'='*65}")
    print("TEST COMPLETE")
    print("="*65)

if __name__ == "__main__":
    run()
