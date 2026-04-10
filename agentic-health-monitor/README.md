# Agentic Health Monitor

An AI-powered health assessment system built with FastAPI, React, and Groq LLM.

## Features

- Multi-agent LLM pipeline for symptom analysis
- Symptom-specific follow-up questions (cardiac, neurological, hepatic, etc.)
- Risk assessment and recommendations
- Patient report history
- RAG-based medical knowledge retrieval

## Tech Stack

**Backend:** FastAPI, Groq (llama-3.3-70b-versatile), ChromaDB, SQLite, Pydantic  
**Frontend:** React, Vite, Tailwind CSS

## Project Structure

```
agentic-health-monitor/
├── backend/
│   ├── app/
│   │   ├── agents/        # LLM agents (symptom, clarification, risk, recommendation)
│   │   ├── core/          # LLM client, config
│   │   ├── routes/        # FastAPI routes
│   │   ├── schemas/       # Pydantic models
│   │   ├── rag/           # Embedder and vector store
│   │   └── tools/         # RAG tool
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/         # SymptomForm, FollowUp, Report, History
    │   ├── components/
    │   └── services/      # API calls
    └── package.json
```

## Setup

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # Add your GROQ_API_KEY
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at: https://console.groq.com

## Usage

1. Open http://localhost:5173
2. Enter patient name, age, symptoms, duration, severity
3. AI analyzes symptoms and generates targeted follow-up questions
4. Answer questions to get full risk assessment and recommendations
5. View and save reports in history

## Agents

| Agent | Role |
|-------|------|
| SymptomInterpreter | Identifies body system and risk level |
| SymptomSummarizer | Generates clinical summary |
| ClarificationAgent | Generates symptom-specific follow-up questions |
| RiskAgent | Assesses risk and possible conditions |
| RecommendationAgent | Provides actionable recommendations |
