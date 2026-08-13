import os
from typing import List, Optional
import subprocess
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import engine, SessionLocal, Base, User, Question, Interview, InterviewAnswer, init_db

app = FastAPI(title='AI Interview API', version='1.0.0')

# Initialize database tables on startup
@app.on_event('startup')
def startup():
    """Create database tables on startup"""
    try:
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database already initialized or error: {e}")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    compiler: Optional[str] = None


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
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    if not payload.name or not payload.email:
        raise HTTPException(status_code=400, detail='Name and email are required.')

    # Check if user exists, if not create
    user = db.query(User).filter(User.email == payload.email).first()
    
    if not user:
        # Create new user
        user = User(
            name=payload.name,
            email=payload.email,
            password='default_password',  # In production, hash this
            role=payload.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] New user created: {payload.email}")
    else:
        print(f"[OK] User logged in: {payload.email}")

    return {
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
        },
    }


@app.get('/questions')
def get_questions(db: Session = Depends(get_db)):
    """Get all questions from database, or seed with sample questions if empty"""
    
    # Check if questions exist in database
    existing_questions = db.query(Question).count()
    
    if existing_questions == 0:
        # Seed database with sample questions
        sample_questions_data = [
            {
                'id': 1,
                'type': 'theoretical',
                'category': 'Frontend',
                'level': 1,
                'difficulty': 'Medium',
                'text': 'Explain the difference between props and state in React and when you would use each.',
                'accepted_keywords': ['props', 'state', 'props are', 'state is', 'immutable', 'component'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 2,
                'type': 'coding',
                'category': 'Frontend',
                'level': 2,
                'difficulty': 'Medium',
                'text': 'Write a JavaScript function that reverses a string without using the reverse() method.',
                'accepted_keywords': ['function', 'reverse', 'string'],
                'compiler': 'JavaScript',
                'expected_output': 'olleh',
            },
            {
                'id': 3,
                'type': 'theoretical',
                'category': 'Backend',
                'level': 3,
                'difficulty': 'Medium',
                'text': 'How would you design a REST API endpoint for user login with security best practices?',
                'accepted_keywords': ['rest', 'endpoint', 'authentication', 'token', 'https', 'validation'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 4,
                'type': 'coding',
                'category': 'Backend',
                'level': 4,
                'difficulty': 'Medium',
                'text': 'Write a function to check whether a number is prime in JavaScript.',
                'accepted_keywords': ['prime', 'function', 'check'],
                'compiler': 'JavaScript',
                'expected_output': 'true',
            },
            {
                'id': 5,
                'type': 'theoretical',
                'category': 'Database',
                'level': 5,
                'difficulty': 'Hard',
                'text': 'Compare relational and distributed data modeling. How would you choose a schema for a system with 10M events per day?',
                'accepted_keywords': ['relational', 'denormal', 'shard', 'partition', 'schema'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 6,
                'type': 'theoretical',
                'category': 'System Design',
                'level': 6,
                'difficulty': 'Hard',
                'text': 'Design a scalable interview evaluation platform that captures live speech, stores answers, scores them, and serves actionable analytics in real time.',
                'accepted_keywords': ['scale', 'stream', 'real time', 'kafka', 'storage', 'analytics'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 7,
                'type': 'coding',
                'category': 'Frontend',
                'level': 7,
                'difficulty': 'Medium',
                'text': 'Write a function to flatten a nested array by one level in JavaScript.',
                'accepted_keywords': ['flatten', 'array', 'nested'],
                'compiler': 'JavaScript',
                'expected_output': '1 2 3 4',
            },
            {
                'id': 8,
                'type': 'theoretical',
                'category': 'DevOps',
                'level': 8,
                'difficulty': 'Hard',
                'text': 'Explain the CI/CD pipeline and why automated testing is important in deployment.',
                'accepted_keywords': ['ci', 'cd', 'pipeline', 'testing', 'automated', 'deploy'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 9,
                'type': 'coding',
                'category': 'Algorithms',
                'level': 9,
                'difficulty': 'Hard',
                'text': 'Write a function that returns the nth Fibonacci number efficiently.',
                'accepted_keywords': ['fibonacci', 'efficient', 'function'],
                'compiler': 'JavaScript',
                'expected_output': '13',
            },
            {
                'id': 10,
                'type': 'theoretical',
                'category': 'Security',
                'level': 10,
                'difficulty': 'Hard',
                'text': 'What is XSS and how do you prevent it in web applications?',
                'accepted_keywords': ['xss', 'sanitize', 'escape', 'input', 'content security policy'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 11,
                'type': 'theoretical',
                'category': 'ML',
                'level': 11,
                'difficulty': 'Hard',
                'text': 'Describe the difference between supervised and unsupervised learning.',
                'accepted_keywords': ['supervised', 'unsupervised', 'labels', 'clustering', 'regression'],
                'compiler': None,
                'expected_output': None,
            },
            {
                'id': 12,
                'type': 'coding',
                'category': 'Data',
                'level': 12,
                'difficulty': 'Hard',
                'text': 'Given an array of integers, return the index of the first repeated value.',
                'accepted_keywords': ['repeated', 'index', 'array'],
                'compiler': 'JavaScript',
                'expected_output': '0',
            },
        ]
        
        # Create and add questions to database
        for q_data in sample_questions_data:
            question = Question(**q_data)
            db.add(question)
        
        db.commit()
        print("[OK] Database seeded with 12 sample questions!")
    
    # Get all questions from database
    questions = db.query(Question).all()
    
    return [
        {
            'id': q.id,
            'type': q.type,
            'category': q.category,
            'difficulty': q.difficulty,
            'level': q.level,
            'text': q.text,
            'compiler': q.compiler,
            'acceptedKeywords': q.accepted_keywords,
            'expectedOutput': q.expected_output,
        }
        for q in questions
    ]



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


@app.post('/save-interview')
def save_interview(payload: InterviewSubmission, db: Session = Depends(get_db)):
    """Save completed interview and answers to database"""
    
    if not payload.student_name or not payload.email:
        raise HTTPException(status_code=400, detail='Student name and email are required.')
    
    try:
        # Create interview record
        interview = Interview(
            student_name=payload.student_name,
            email=payload.email,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.add(interview)
        db.flush()  # Get the interview ID
        
        # Calculate overall score
        total_score = 0
        answer_count = 0
        
        # Save all answers
        for answer_data in payload.answers:
            answer = InterviewAnswer(
                interview_id=interview.id,
                question_id=answer_data.get('question_id', 0),
                answer_text=answer_data.get('answer', ''),
                is_correct=answer_data.get('is_correct', False),
                score=answer_data.get('score', 0),
                feedback=answer_data.get('feedback', '')
            )
            db.add(answer)
            total_score += answer_data.get('score', 0)
            answer_count += 1
        
        # Update interview score
        interview.overall_score = total_score / answer_count if answer_count > 0 else 0
        
        db.commit()
        db.refresh(interview)
        
        print(f"[OK] Interview saved! ID: {interview.id}, Score: {interview.overall_score}")
        
        return {
            'message': 'Interview saved successfully',
            'interview_id': interview.id,
            'student_name': payload.student_name,
            'overall_score': round(interview.overall_score, 2),
            'answers_saved': answer_count,
        }
    
    except Exception as e:
        db.rollback()
        print(f"[ERR] Error saving interview: {e}")
        raise HTTPException(status_code=500, detail=f'Error saving interview: {str(e)}')


@app.get('/interviews')
def get_interviews(db: Session = Depends(get_db)):
    """Get all completed interviews"""
    
    interviews = db.query(Interview).filter(Interview.status == 'completed').all()
    
    return [
        {
            'id': interview.id,
            'student_name': interview.student_name,
            'email': interview.email,
            'overall_score': interview.overall_score,
            'completed_at': interview.completed_at.isoformat() if interview.completed_at else None,
        }
        for interview in interviews
    ]


@app.get('/interview/{interview_id}')
def get_interview_details(interview_id: int, db: Session = Depends(get_db)):
    """Get detailed report for a specific interview"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail='Interview not found')
    
    answers = db.query(InterviewAnswer).filter(InterviewAnswer.interview_id == interview_id).all()
    
    return {
        'interview_id': interview.id,
        'student_name': interview.student_name,
        'email': interview.email,
        'overall_score': interview.overall_score,
        'completed_at': interview.completed_at.isoformat() if interview.completed_at else None,
        'answers': [
            {
                'question_id': answer.question_id,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'score': answer.score,
                'feedback': answer.feedback,
            }
            for answer in answers
        ]
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
