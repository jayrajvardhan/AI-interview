import os
from typing import List, Optional
import tempfile
import subprocess
import shlex
import uuid
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/ai_interview',
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app = FastAPI(title='AI Interview API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class UserLogin(BaseModel):
    name: str
    email: str
    role: str = 'Student'


class QuestionItem(BaseModel):
    id: int
    type: str
    category: str
    difficulty: str
    text: str
    compiler: str | None = None


class InterviewSubmission(BaseModel):
    student_name: str
    email: str
    answers: List[dict] = Field(default_factory=list)


class TheoryEvalRequest(BaseModel):
    question_id: int
    question_text: str
    accepted_keywords: List[str] = []
    reference_answers: Optional[List[str]] = None
    student_answer: str


class TheoryEvalResponse(BaseModel):
    similarity: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    is_correct: bool
    score: int
    feedback: str


class CodeRunRequest(BaseModel):
    language: str
    code: str
    tests: Optional[List[dict]] = None  # [{"input":"...","expected":"..."}]


class CodeRunResult(BaseModel):
    passed: bool
    stdout: str
    stderr: str
    tests: Optional[List[dict]] = None


@app.get('/health')
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return {'status': 'ok', 'database': 'connected'}
    except Exception:
        return {'status': 'ok', 'database': 'offline'}


@app.post('/login')
def login_user(payload: UserLogin):
    if not payload.name or not payload.email:
        raise HTTPException(status_code=400, detail='Name and email are required.')

    return {
        'message': 'Login successful',
        'user': {
            'name': payload.name,
            'email': payload.email,
            'role': payload.role,
        },
    }


@app.get('/questions')
def get_questions():
    sample_questions = [
        {
            'id': 1,
            'type': 'theoretical',
            'category': 'Frontend',
            'difficulty': 'Medium',
            'text': 'Explain the difference between props and state in React and when you would use each.',
            'compiler': None,
        },
        {
            'id': 2,
            'type': 'coding',
            'category': 'Frontend',
            'difficulty': 'Medium',
            'text': 'Write a JavaScript function that reverses a string without using reverse().',
            'compiler': 'JavaScript',
        },
        {
            'id': 3,
            'type': 'theoretical',
            'category': 'Backend',
            'difficulty': 'Medium',
            'text': 'How would you design a REST API endpoint for user login with security best practices?',
            'compiler': None,
        },
    ]
    return sample_questions



@app.post('/evaluate/theory', response_model=TheoryEvalResponse)
def evaluate_theory(payload: TheoryEvalRequest):
    student = (payload.student_answer or '').strip()
    if not student:
        raise HTTPException(status_code=400, detail='Student answer is required.')

    # Keyword matching
    matched = [k for k in payload.accepted_keywords if k.lower() in student.lower()]
    missing = [k for k in payload.accepted_keywords if k.lower() not in student.lower()]

    # TF-IDF similarity against the question text and any references
    corpus = [payload.question_text]
    if payload.reference_answers:
        corpus.extend(payload.reference_answers)
    corpus.append(student)

    try:
        vect = TfidfVectorizer().fit_transform(corpus)
        sims = cosine_similarity(vect[-1], vect[:-1])[0]
        similarity = float(sims.max()) if len(sims) > 0 else 0.0
    except Exception:
        similarity = 0.0

    # heuristic for correctness
    is_correct = False
    score = 0
    feedback = ''
    # strong if keywords present or similarity above threshold
    if matched or similarity >= 0.35:
        is_correct = True
        score = int(min(100, 60 + similarity * 40))
        feedback = 'Good answer: covers key points.'
    else:
        score = int(min(100, similarity * 100))
        feedback = 'Answer is incomplete or missing important concepts.'

    return TheoryEvalResponse(
        similarity=round(similarity, 3),
        matched_keywords=matched,
        missing_keywords=missing,
        is_correct=is_correct,
        score=score,
        feedback=feedback,
    )


def _run_code_safely(language: str, code: str, timeout_s: int = 5):
    # supports Python and JavaScript (node) if available in container
    if language.lower().startswith('python'):
        ext = '.py'
        cmd = ['python', 'file']
    else:
        ext = '.js'
        cmd = ['node', 'file']

    fname = f"/tmp/{uuid.uuid4().hex}{ext}"
    try:
        with open(fname, 'w', encoding='utf-8') as fh:
            fh.write(code)
        # run with subprocess
        proc = subprocess.Popen([cmd[0], fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            return False, '', 'Execution timed out.'

        passed = proc.returncode == 0
        return passed, stdout, stderr
    except Exception as e:
        return False, '', str(e)
    finally:
        try:
            if os.path.exists(fname):
                os.remove(fname)
        except Exception:
            pass


@app.post('/run/code', response_model=CodeRunResult)
def run_code(payload: CodeRunRequest):
    if not payload.code:
        raise HTTPException(status_code=400, detail='Code is required')

    passed, stdout, stderr = _run_code_safely(payload.language, payload.code, timeout_s=8)

    test_results = []
    if payload.tests:
        for t in payload.tests:
            expected = str(t.get('expected', '')).strip()
            inp = t.get('input')
            ok = expected in stdout
            test_results.append({'input': inp, 'expected': expected, 'passed': ok})

    return CodeRunResult(passed=passed, stdout=stdout or '', stderr=stderr or '', tests=test_results or None)


@app.post('/interviews/submit')
def submit_interview(payload: InterviewSubmission):
    if not payload.student_name:
        raise HTTPException(status_code=400, detail='Student name is required.')

    score = 0
    for answer in payload.answers:
        response = (answer.get('answer') or '').strip()
        if response:
            score += min(35, len(response.split()) // 3)

    return {
        'message': 'Interview submitted successfully',
        'student_name': payload.student_name,
        'score': min(score, 100),
        'answers_received': len(payload.answers),
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
