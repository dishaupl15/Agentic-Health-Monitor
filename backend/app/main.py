from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes.analyze import router as analyze_router
from app.routes.assess import router as assess_router
from app.routes.save_report import router as save_report_router
from app.routes.history import router as history_router
from app.routes.rag import router as rag_router
from app.db.database import init_db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print("[SERVER] Hospital AI Health Monitor starting up")
    print("[SERVER] Routes: /analyze-symptoms | /final-assessment")
    print("[SERVER] All agents loaded and ready")
    print("="*60 + "\n")
    init_db()
    yield
    print("\n[SERVER] Shutting down.")


app = FastAPI(
    title='Hospital AI Health Monitor API',
    version='0.1.0',
    description='FastAPI backend for symptom analysis, follow-up generation, assessment, and history tracking.',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(analyze_router)
app.include_router(assess_router)
app.include_router(save_report_router)
app.include_router(history_router)
app.include_router(rag_router)

@app.get('/')
def read_root():
    return {'message': 'Hospital AI Health Monitor backend is running.'}
