import json
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.db.models import Base, Report

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./reports.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_urgency_column():
    with engine.connect() as connection:
        result = connection.execute(text("PRAGMA table_info(reports)"))
        columns = [row[1] for row in result.fetchall()]
        if 'urgency' not in columns:
            connection.execute(text("ALTER TABLE reports ADD COLUMN urgency VARCHAR(64) NOT NULL DEFAULT 'Routine monitoring'"))


def init_db():
    Base.metadata.create_all(bind=engine)
    ensure_urgency_column()


def save_report(payload):
    session = SessionLocal()
    report = Report(
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        symptoms=payload.symptoms,
        duration=payload.duration,
        severity=payload.severity,
        history=payload.history or '',
        bp=payload.bp or '',
        sugar=payload.sugar or '',
        temperature=payload.temperature or '',
        follow_up_answers=json.dumps(payload.follow_up_answers),
        possible_conditions=json.dumps([cond.dict() for cond in payload.possible_conditions]),
        confidence=payload.confidence,
        risk_level=payload.risk_level,
        urgency=payload.urgency,
        explanation=payload.explanation,
        recommendation=payload.recommendation,
        created_at=datetime.utcnow(),
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    session.close()
    return report


def list_reports():
    session = SessionLocal()
    reports = session.query(Report).order_by(Report.created_at.desc()).all()
    session.close()
    return [r.to_dict() for r in reports]
