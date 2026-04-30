# Agentic Health Monitor — Full Project Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [How the App Works — End to End](#4-how-the-app-works--end-to-end)
5. [AI Agents — Detailed Explanation](#5-ai-agents--detailed-explanation)
6. [RAG System](#6-rag-system)
7. [Backend API Routes](#7-backend-api-routes)
8. [Frontend Pages](#8-frontend-pages)
9. [Supabase Integration](#9-supabase-integration)
10. [Database Schema](#10-database-schema)
11. [Authentication Flow](#11-authentication-flow)
12. [Environment Variables](#12-environment-variables)
13. [Setup & Running Locally](#13-setup--running-locally)

---w

## 1. Project Overview

Agentic Health Monitor is an AI-powered health assessment web application. A user logs in, enters their symptoms, answers AI-generated follow-up questions, and receives a full medical risk report with possible conditions, risk level, urgency, and actionable recommendations.

The "agentic" part means the backend uses a **pipeline of multiple AI agents**, each with a specific role, working together in sequence to produce a medically grounded assessment. It is not a single prompt — it is a multi-step reasoning pipeline.

The app also stores every assessment per user in Supabase so users can view their full history after login.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | FastAPI (Python) |
| LLM | Groq API — llama-3.3-70b-versatile |
| Vector Store | ChromaDB |
| Embeddings | OpenAI text-embedding-3-small |
| Auth | Supabase Auth (email + password) |
| Database | Supabase PostgreSQL |
| Local DB | SQLite (legacy, kept for backup) |
| Routing | React Router v6 |

---

## 3. Project Structure

```
Hospital_mgmt_project/
└── agentic-health-monitor/
    ├── backend/
    │   ├── app/
    │   │   ├── agents/
    │   │   │   ├── orchestrator.py        ← coordinates all agents
    │   │   │   ├── symptom_agent.py       ← Agent 1 + Agent 2
    │   │   │   ├── clarification_agent.py ← Agent 3
    │   │   │   ├── risk_agent.py          ← Agent 4
    │   │   │   └── recommendation_agent.py← Agent 5
    │   │   ├── core/
    │   │   │   ├── config.py              ← env settings
    │   │   │   ├── llm.py                 ← Groq LLM client
    │   │   │   └── supabase_client.py     ← Supabase backend client
    │   │   ├── db/
    │   │   │   ├── database.py            ← SQLite operations
    │   │   │   ├── models.py              ← SQLAlchemy models
    │   │   │   └── supabase_db.py         ← Supabase insert helper
    │   │   ├── rag/
    │   │   │   ├── embedder.py            ← text embeddings
    │   │   │   ├── loader.py              ← loads medical docs
    │   │   │   ├── retriever.py           ← similarity search
    │   │   │   └── vector_store.py        ← ChromaDB interface
    │   │   ├── routes/
    │   │   │   ├── analyze.py             ← POST /analyze-symptoms
    │   │   │   ├── assess.py              ← POST /final-assessment
    │   │   │   ├── save_report.py         ← POST /save-report
    │   │   │   ├── history.py             ← GET /history
    │   │   │   └── rag.py                 ← GET /rag-query
    │   │   ├── schemas/
    │   │   │   ├── input_schema.py        ← request models
    │   │   │   └── output_schema.py       ← response models
    │   │   └── main.py                    ← FastAPI app entry point
    │   ├── .env                           ← backend secrets
    │   └── requirements.txt
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── PageShell.jsx          ← layout + navbar
    │   │   │   └── ProtectedRoute.jsx     ← auth guard
    │   │   ├── context/
    │   │   │   └── AuthContext.jsx        ← global session state
    │   │   ├── lib/
    │   │   │   └── supabaseClient.js      ← Supabase frontend client
    │   │   ├── pages/
    │   │   │   ├── Login.jsx
    │   │   │   ├── Signup.jsx
    │   │   │   ├── Home.jsx
    │   │   │   ├── SymptomForm.jsx
    │   │   │   ├── FollowUp.jsx
    │   │   │   ├── Report.jsx
    │   │   │   └── History.jsx
    │   │   ├── services/
    │   │   │   └── api.js                 ← backend API calls
    │   │   ├── App.jsx                    ← routes
    │   │   └── main.jsx                   ← app entry point
    │   └── .env                           ← frontend secrets
    └── medical_docs/                      ← RAG knowledge base
        ├── chest_pain_guidelines.txt
        ├── diabetes_warning.txt
        ├── fever_guidelines.txt
        └── hypertension_warning.txt
```

---

## 4. How the App Works — End to End

```
User opens app
  → Not logged in → redirected to /login
  → Logs in with email + password (Supabase Auth)
  → Lands on Home page

User clicks "Start Assessment"
  → Fills SymptomForm: name, age, gender, symptoms, duration, severity, vitals
  → Clicks "Analyze Symptoms"
  → Frontend calls POST /analyze-symptoms

Backend Pipeline 1 — Analyze Symptoms:
  → Agent 1 (Symptom Interpreter): identifies body system + risk level
  → Agent 2 (Symptom Summarizer): writes clinical summary, decides if follow-up needed
  → Agent 3 (Clarification Agent): generates 5 targeted follow-up questions
  → RAG Tool: retrieves relevant medical knowledge chunks
  → Returns: summary + questions to frontend

User sees FollowUp page
  → Answers the 5 AI-generated questions
  → Clicks "Get Final Report"
  → Frontend calls POST /final-assessment

Backend Pipeline 2 — Final Assessment:
  → Agent 4 (Risk Agent): assesses risk level, possible conditions, urgency
  → Agent 5 (Recommendation Agent): generates patient-facing guidance + next steps
  → Returns: full report to frontend

User sees Report page
  → Report auto-saves to Supabase assessments table
  → User can click "View History" to see all past reports
```

---

## 5. AI Agents — Detailed Explanation

The backend uses **5 AI agents** powered by the Groq LLM (llama-3.3-70b-versatile). Each agent has a specific system prompt, a specific input, and a specific structured JSON output. They are coordinated by the **Orchestrator**.

---

### Agent 1 — Symptom Interpreter

**File:** `backend/app/agents/symptom_agent.py` → `interpret_symptoms()`

**What it does:**
Takes the patient's raw symptoms, age, and gender and identifies the dominant body system being affected, the risk level, and whether it is an emergency.

**Input:**
- symptoms (free text)
- age
- gender

**Output (structured JSON):**
```json
{
  "possible_conditions": ["Angina", "GERD", "Costochondritis"],
  "body_system": "cardiac",
  "risk_level": "high",
  "symptom_cluster": "Chest pressure with radiation suggesting possible cardiac origin",
  "is_emergency": false
}
```

**Body systems it can identify:**
cardiac, neurological, hepatic, respiratory, gastrointestinal, endocrine, musculoskeletal, general

**Why it matters:**
This agent's output is passed directly to Agent 3 (Clarification Agent) so the follow-up questions are specific to the correct body system — not generic questions.

**Fallback:**
If the LLM fails, it returns `body_system=general`, `risk_level=moderate`, `is_emergency=False` so the pipeline never crashes.

---

### Agent 2 — Symptom Summarizer

**File:** `backend/app/agents/symptom_agent.py` → `summarize_symptoms()`

**What it does:**
Takes the full patient case (symptoms, duration, severity, vitals, medical history) and writes a 2-3 sentence clinical-style summary. It also decides whether follow-up questions are needed.

**Input:**
- symptoms, duration, severity
- blood pressure, blood sugar, temperature (optional)
- age, gender, medical history
- RAG context (relevant medical knowledge retrieved automatically)

**Output (structured JSON):**
```json
{
  "summary": "Patient presents with chest tightness and shortness of breath lasting 2 days...",
  "concern_level": "HIGH",
  "follow_up_needed": true,
  "rationale": "Cardiac symptoms with moderate severity warrant further clarification"
}
```

**Concern levels:**
- `LOW` — mild, self-limiting, follow-up may not be needed
- `MODERATE` — needs doctor visit within days, follow-up always needed
- `HIGH` — needs attention within 24 hours, follow-up always needed
- `CRITICAL` — potential life-threatening emergency, follow-up always needed

**Important rule:**
`follow_up_needed` is forced to `true` for anything above LOW, regardless of what the LLM returns. This is a safety override in the code.

**Why it matters:**
The summary is shown to the user on the FollowUp page as "AI Symptom Summary". It is also passed to Agent 4 (Risk Agent) as context.

---

### Agent 3 — Clarification Agent

**File:** `backend/app/agents/clarification_agent.py` → `generate_follow_up_questions()`

**What it does:**
Generates exactly 5 targeted follow-up questions based on the body system identified by Agent 1. Questions are clinically specific — not generic.

**Input:**
- symptoms
- clinical summary (from Agent 2)
- interpretation object (from Agent 1) — body system, conditions, risk level

**Output:**
```json
[
  "Does the chest pain spread to your left arm, jaw, neck, or back?",
  "Are you experiencing shortness of breath along with the chest pain?",
  "Are you sweating, feeling nauseous, or lightheaded right now?",
  "Do you feel pressure or squeezing in your chest rather than sharp pain?",
  "Have you ever been diagnosed with heart disease or had a heart attack before?"
]
```

**Body system question mapping:**

| Body System | Question Focus |
|---|---|
| cardiac | pain radiation, shortness of breath, sweating, pressure/tightness, heart history |
| neurological | FAST signs (face droop, arm weakness, speech), sudden onset, severe headache |
| hepatic | jaundice, urine/stool color, right-side pain, alcohol use, hepatitis exposure |
| respiratory | breathing at rest, cough color, wheezing, fever, lung conditions |
| gastrointestinal | pain location, blood in stool/vomit, bowel changes, pain after eating |
| endocrine | blood sugar readings, thirst/urination, weight changes, diabetes history |
| musculoskeletal | injury/trauma, joint swelling, movement limitation, pain at rest vs movement |

**Retry logic:**
The agent tries up to 3 times if the LLM returns malformed JSON. It also strips markdown code blocks if the LLM wraps the output in them.

**Fallback:**
If all 3 LLM attempts fail, it uses hardcoded body-system-specific questions from `_body_system_fallback()`. The pipeline never returns empty questions.

**Why it matters:**
This is what makes the app "agentic" — the questions adapt to the patient's specific condition, not a fixed questionnaire.

---

### Agent 4 — Risk Agent

**File:** `backend/app/agents/risk_agent.py` → `assess_risk()`

**What it does:**
Takes the full patient case including the follow-up answers and performs a comprehensive risk assessment. Returns possible conditions with confidence scores, overall risk level, urgency, and a clinical explanation.

**Input:**
- symptoms, duration, severity
- follow-up answers (from the patient)
- clinical summary (from Agent 2)
- RAG context (retrieved automatically)

**Output (structured JSON):**
```json
{
  "possible_conditions": [
    {"name": "Unstable Angina", "score": 0.75, "reasoning": "Chest pressure with radiation..."},
    {"name": "GERD", "score": 0.45, "reasoning": "Burning sensation after meals..."},
    {"name": "Anxiety", "score": 0.30, "reasoning": "Stress-related symptoms..."}
  ],
  "confidence": "Moderate",
  "risk_level": "High",
  "urgency": "Within 24 hours",
  "explanation": "The symptom pattern is consistent with possible cardiac involvement..."
}
```

**Risk levels:**
- `Emergency` — life-threatening, call 911
- `High` — urgent care within 24 hours
- `Medium` — doctor visit within 3 days
- `Low` — home care, monitor symptoms

**Urgency levels:**
- `Immediate` — emergency services now
- `Within 24 hours` — urgent care today
- `Within 3 days` — schedule appointment
- `Routine monitoring` — self-care

**Safety rule:**
The agent is instructed to over-triage rather than under-triage. When information is incomplete, it leans toward higher risk.

**Why it matters:**
This is the core diagnostic reasoning step. It uses both the patient's answers AND retrieved medical knowledge to ground its assessment.

---

### Agent 5 — Recommendation Agent

**File:** `backend/app/agents/recommendation_agent.py` → `get_full_recommendation()`

**What it does:**
Takes the risk assessment output and converts it into clear, patient-friendly guidance with specific next steps and a medical disclaimer.

**Input:**
- risk level
- urgency
- clinical explanation
- possible conditions list

**Output (structured JSON):**
```json
{
  "recommendation": "Seek urgent medical care today. Your symptoms may indicate a cardiac condition that requires immediate evaluation.",
  "next_steps": [
    "Go to an emergency room or urgent care clinic immediately.",
    "Do not drive yourself — ask someone to take you or call an ambulance.",
    "Bring a list of all current medications.",
    "Avoid physical exertion until evaluated.",
    "If symptoms worsen suddenly, call 911."
  ],
  "disclaimer": "This is an AI-generated assessment and does not replace professional medical advice."
}
```

**Guidance by risk level:**
- `Emergency` → call 911 immediately, do not drive
- `High` → urgent care or ER today
- `Medium` → doctor appointment within 2-3 days, monitor symptoms
- `Low` → rest, hydration, home care, escalate if worsens

**Why it matters:**
Translates clinical language into plain patient-facing instructions. Always includes a disclaimer.

---

### The Orchestrator

**File:** `backend/app/agents/orchestrator.py`

The orchestrator is not an agent itself — it is the **coordinator** that calls all agents in the correct order and passes outputs between them.

**Pipeline 1 — `analyze_symptoms_workflow()`** (called by `/analyze-symptoms`):
```
Step 1: Agent 1 (Symptom Interpreter)  → body system, risk level
Step 2: Agent 2 (Symptom Summarizer)   → clinical summary, follow_up_needed
Step 3: Agent 3 (Clarification Agent)  → 5 targeted questions  [only if follow_up_needed=True]
Step 4: RAG Tool                        → relevant medical knowledge chunks
→ Returns to frontend: summary + questions + knowledge
```

**Pipeline 2 — `final_assessment_workflow()`** (called by `/final-assessment`):
```
Step 1: Agent 4 (Risk Agent)            → conditions, risk level, urgency, explanation
Step 2: Agent 5 (Recommendation Agent) → patient guidance, next steps, disclaimer
→ Returns to frontend: full assessment report
```

---

## 6. RAG System

RAG stands for Retrieval-Augmented Generation. It allows the LLM agents to reference real medical knowledge instead of relying purely on training data.

**How it works:**
1. Medical documents in `medical_docs/` are loaded and split into chunks
2. Each chunk is embedded using OpenAI `text-embedding-3-small`
3. Embeddings are stored in ChromaDB (local vector database)
4. When a patient submits symptoms, the top 3 most relevant chunks are retrieved
5. These chunks are injected into the prompts of Agent 2 (Summarizer) and Agent 4 (Risk Agent)

**Medical documents included:**
- `chest_pain_guidelines.txt` — cardiac triage guidelines
- `diabetes_warning.txt` — diabetic emergency signs
- `fever_guidelines.txt` — fever assessment criteria
- `hypertension_warning.txt` — hypertension warning signs

**Why it matters:**
Without RAG, the LLM might hallucinate or give outdated information. RAG grounds the agents in actual medical reference material.

---

## 7. Backend API Routes

| Method | Route | Description |
|---|---|---|
| POST | `/analyze-symptoms` | Runs Pipeline 1 — returns summary + follow-up questions |
| POST | `/final-assessment` | Runs Pipeline 2 — returns full risk report |
| POST | `/save-report` | Saves report to SQLite + Supabase assessments |
| GET | `/history` | Returns all reports from SQLite |
| GET | `/rag-query` | Direct RAG knowledge base query |

---

## 8. Frontend Pages

| Route | Page | Description |
|---|---|---|
| `/login` | Login.jsx | Email + password login via Supabase |
| `/signup` | Signup.jsx | Create account + insert profile into Supabase |
| `/` | Home.jsx | Dashboard with features and how-it-works |
| `/symptom-form` | SymptomForm.jsx | Patient details + symptom input form |
| `/follow-up` | FollowUp.jsx | AI-generated follow-up questions |
| `/report` | Report.jsx | Full assessment report + auto-save to Supabase |
| `/history` | History.jsx | All past assessments for logged-in user |

All routes except `/login` and `/signup` are protected by `ProtectedRoute.jsx` — unauthenticated users are redirected to `/login`.

---

## 9. Supabase Integration

### Frontend (`src/lib/supabaseClient.js`)
- Initialised with `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
- Used for: signup, login, logout, session management, direct DB inserts/queries

### Backend (`app/core/supabase_client.py`)
- Initialised with `SUPABASE_URL` and `SUPABASE_KEY` (service role key)
- Used for: inserting assessment records server-side via `/save-report`
- Lazy initialisation — client is only created when first used, so server starts even without credentials

### Auth flow
- Signup → `supabase.auth.signUp()` → inserts row into `public.profiles`
- Login → `supabase.auth.signInWithPassword()` → sets session cookie
- Session → `supabase.auth.getSession()` → returns JWT with `user.id`
- Logout → `supabase.auth.signOut()` → clears session → redirects to `/login`

---

## 10. Database Schema

### `public.profiles`
Stores user profile information linked to Supabase Auth.

| Column | Type | Description |
|---|---|---|
| id | uuid | Primary key, references auth.users(id) |
| full_name | text | User's full name |
| age | int | User's age |
| gender | text | User's gender |
| created_at | timestamptz | Account creation time |

### `public.assessments`
Stores every health assessment per user.

| Column | Type | Description |
|---|---|---|
| id | bigint | Auto-increment primary key |
| user_id | uuid | References auth.users(id) |
| symptoms | text | Patient's reported symptoms |
| summary | text | AI clinical summary (from Agent 2) |
| risk_level | text | Low / Medium / High / Emergency |
| possible_conditions | jsonb | Array of conditions with scores |
| follow_up_questions | jsonb | Follow-up answers submitted by patient |
| created_at | timestamptz | Assessment timestamp |

Both tables have **Row Level Security (RLS)** enabled. Users can only read and write their own rows using `auth.uid() = id/user_id`.

---

## 11. Authentication Flow

```
Signup:
  User fills name, age, email, password
    → supabase.auth.signUp({ email, password })
        → Supabase creates user in auth.users
            → Insert profile into public.profiles { id, full_name, age }
                → Success banner → redirect to /login after 2.5s

Login:
  User fills email, password
    → supabase.auth.signInWithPassword({ email, password })
        → Supabase returns session with JWT
            → AuthContext stores session globally
                → ProtectedRoute allows access to all app pages
                    → Redirect to /

Logout:
  User clicks "Log out" in navbar
    → supabase.auth.signOut()
        → Session cleared
            → Redirect to /login

Session persistence:
  On every page load, AuthContext calls getSession()
    → If valid session exists → user stays logged in
    → If no session → ProtectedRoute redirects to /login
```

---

## 12. Environment Variables

### `backend/.env`
```
GROQ_API_KEY=           # Groq API key for LLM calls
DATABASE_URL=           # SQLite path (sqlite:///./reports.db)
SUPABASE_URL=           # Supabase project URL (https://xxx.supabase.co)
SUPABASE_KEY=           # Supabase service_role key (server-side only)
```

### `frontend/.env`
```
VITE_API_BASE_URL=      # Backend URL (http://localhost:8000)
VITE_SUPABASE_URL=      # Supabase project URL
VITE_SUPABASE_ANON_KEY= # Supabase anon/public key (NOT service_role)
```

> **Security note:** The `service_role` key bypasses all RLS policies. It must never be used in the frontend. The frontend only uses the `anon` key.

---

## 13. Setup & Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Supabase project (free tier works)
- A Groq API key (free at console.groq.com)

### Backend Setup
```bash
cd agentic-health-monitor/backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Fill in .env with your keys
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd agentic-health-monitor/frontend
npm install
# Fill in .env with your Supabase URL and anon key
npm run dev
```

### Supabase Setup
Run these SQL scripts in your Supabase SQL Editor:

```sql
-- Profiles table
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text, age int, gender text,
  created_at timestamptz default now()
);
alter table public.profiles enable row level security;
create policy "select own" on public.profiles for select using (auth.uid() = id);
create policy "insert own" on public.profiles for insert with check (auth.uid() = id);
create policy "update own" on public.profiles for update using (auth.uid() = id);

-- Assessments table
create table if not exists public.assessments (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  symptoms text, summary text, risk_level text,
  possible_conditions jsonb default '[]'::jsonb,
  follow_up_questions jsonb default '[]'::jsonb,
  created_at timestamptz default now()
);
alter table public.assessments enable row level security;
create policy "select own" on public.assessments for select using (auth.uid() = user_id);
create policy "insert own" on public.assessments for insert with check (auth.uid() = user_id);
```

### Open the app
```
http://localhost:5173
```
