import json
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(32), nullable=False)
    symptoms = Column(Text, nullable=False)
    duration = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    history = Column(Text, nullable=True)
    bp = Column(String(32), nullable=True)
    sugar = Column(String(32), nullable=True)
    temperature = Column(String(32), nullable=True)
    follow_up_answers = Column(Text, nullable=False)
    possible_conditions = Column(Text, nullable=False)
    confidence = Column(String(64), nullable=False)
    risk_level = Column(String(64), nullable=False)
    urgency = Column(String(64), nullable=False, default='Routine monitoring')
    explanation = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'symptoms': self.symptoms,
            'duration': self.duration,
            'severity': self.severity,
            'history': self.history,
            'bp': self.bp,
            'sugar': self.sugar,
            'temperature': self.temperature,
            'follow_up_answers': json.loads(self.follow_up_answers or '{}'),
            'possible_conditions': json.loads(self.possible_conditions or '[]'),
            'confidence': self.confidence,
            'risk_level': self.risk_level,
            'urgency': self.urgency,
            'explanation': self.explanation,
            'recommendation': self.recommendation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
