"""
Database initialization and models
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./ai_interview.db'
)

# SQLite needs check_same_thread=False; PostgreSQL doesn't need it
connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default='Student')  # Student or Admin
    created_at = Column(DateTime, default=datetime.utcnow)


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # theoretical or coding
    category = Column(String(100), nullable=False)  # Frontend, Backend, etc.
    difficulty = Column(String(50), nullable=False)  # Easy, Medium, Hard
    level = Column(Integer, default=1)
    text = Column(Text, nullable=False)
    accepted_keywords = Column(JSON, default=list)
    starter_code = Column(Text, nullable=True)
    compiler = Column(String(50), nullable=True)  # JavaScript, Python
    expected_output = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Interview(Base):
    __tablename__ = 'interviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # optional: set when user is linked
    student_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    status = Column(String(50), default='in_progress')  # in_progress, completed
    overall_score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class InterviewAnswer(Base):
    __tablename__ = 'interview_answers'

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, nullable=False, index=True)
    question_id = Column(Integer, nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Initialize database with all tables"""
    Base.metadata.create_all(bind=engine)
    print("âœ… Database tables created successfully!")


if __name__ == '__main__':
    init_db()
