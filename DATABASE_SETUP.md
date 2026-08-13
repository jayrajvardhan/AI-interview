# 🗄️ Database Integration Guide

## Overview
Your AI Interview platform is now fully integrated with PostgreSQL database. All user data, questions, and interview results are automatically saved to the database.

---

## 🚀 Quick Start (Recommended - Docker)

### Prerequisites
- Docker Desktop installed (Download from https://www.docker.com/products/docker-desktop)
- PowerShell or Command Prompt

### Step 1: Run Setup Script
```powershell
cd "d:\AI interview\AI interview"
.\setup-db.ps1
```

This will:
✅ Start PostgreSQL database
✅ Initialize database tables
✅ Seed sample questions
✅ Start backend API
✅ Start frontend server

### Step 2: Access the Application
- 🌐 **Frontend**: http://localhost:5175
- 🔌 **Backend API**: http://localhost:8000
- 🗄️ **Database**: localhost:5432

---

## 📊 Database Schema

### Tables Created:

#### 1. **users** - Store user accounts
```sql
id (PRIMARY KEY)
name (VARCHAR)
email (UNIQUE)
password (VARCHAR)
role (Student/Admin)
created_at (TIMESTAMP)
```

#### 2. **questions** - Interview question bank
```sql
id (PRIMARY KEY)
type (theoretical/coding)
category (Frontend, Backend, etc.)
difficulty (Easy/Medium/Hard)
level (1-12)
text (TEXT)
accepted_keywords (JSON)
starter_code (TEXT)
compiler (JavaScript/Python)
expected_output (VARCHAR)
created_at (TIMESTAMP)
```

#### 3. **interviews** - Interview sessions
```sql
id (PRIMARY KEY)
student_name (VARCHAR)
email (VARCHAR)
status (in_progress/completed)
overall_score (FLOAT)
started_at (TIMESTAMP)
completed_at (TIMESTAMP)
```

#### 4. **interview_answers** - Individual answers
```sql
id (PRIMARY KEY)
interview_id (FOREIGN KEY)
question_id (FOREIGN KEY)
answer_text (TEXT)
is_correct (BOOLEAN)
score (FLOAT)
feedback (TEXT)
created_at (TIMESTAMP)
```

---

## 🔗 API Endpoints

### User Management
```
POST /login
  Request: { name, email, role }
  Response: { message, user }
  Action: Creates user if doesn't exist, logs in if exists
```

### Questions
```
GET /questions
  Response: List of all 12 questions from database
  Action: Auto-seeds database on first call
```

### Save Interview
```
POST /save-interview
  Request: { student_name, email, answers[] }
  Response: { interview_id, overall_score, answers_saved }
  Action: Saves complete interview to database
```

### View Interviews
```
GET /interviews
  Response: List of all completed interviews
  
GET /interview/{interview_id}
  Response: Detailed interview report with all answers
```

### Health Check
```
GET /health
  Response: { status, database }
  Check if backend and database are connected
```

---

## 📝 Features Enabled

✅ **User Tracking** - Each login creates/updates user record
✅ **Question Banking** - All 12 questions stored in database
✅ **Interview History** - Every interview saved with timestamp
✅ **Score Tracking** - Overall score and per-question scores
✅ **Answer Storage** - All answers with feedback stored
✅ **Progress Analytics** - Track user performance over time

---

## 🔧 Manual Setup (Without Docker)

If you prefer to run locally without Docker:

### 1. Install PostgreSQL
- Download from https://www.postgresql.org/download/windows/
- Install with default settings
- Note credentials (default: postgres/postgres)

### 2. Create Database
```sql
CREATE DATABASE ai_interview;
```

### 3. Setup Backend
```powershell
cd "d:\AI interview\AI interview\backend"
pip install -r requirements.txt

# Create .env
@"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_interview
"@ | Out-File .env

# Initialize database
python database.py
```

### 4. Start Backend
```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Configure Frontend
```powershell
cd "d:\AI interview\AI interview"
@"
VITE_API_URL=http://localhost:8000
"@ | Out-File .env

npm run dev
```

---

## ✅ Verification Checklist

Run these commands to verify everything is connected:

```powershell
# 1. Check Docker containers
docker-compose ps
# Should show: db, backend, frontend as "running"

# 2. Test database connection
curl http://localhost:8000/health
# Should return: {"status":"ok","database":"connected"}

# 3. Test questions endpoint
curl http://localhost:8000/questions
# Should return: Array of 12 questions

# 4. Test frontend
curl http://localhost:5175
# Should return: HTML of the app
```

---

## 🐛 Troubleshooting

### Issue: Database connection refused
**Solution:**
```powershell
# Restart services
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 30
curl http://localhost:8000/health
```

### Issue: Port already in use
**Solution:**
```powershell
# Kill existing services
docker-compose down --volumes

# Or change ports in docker-compose.yml
# Then restart
docker-compose up -d
```

### Issue: Questions not loading
**Solution:**
```powershell
# Verify database is running
docker-compose ps db
# Should be "Up"

# Check logs
docker-compose logs backend
```

### Issue: EBUSY .env file error
**Solution:**
```powershell
# Close any files or editors accessing .env
# Then restart
docker-compose restart
```

---

## 📊 View Database Data

### Option 1: Using pgAdmin (GUI)
```powershell
# Access pgAdmin at: http://localhost:5050
# Default: admin@pgadmin.org / admin
```

### Option 2: Using psql (CLI)
```powershell
# Connect to database
psql -U postgres -d ai_interview -h localhost

# View all interviews
SELECT * FROM interviews;

# View all questions
SELECT id, category, type, text FROM questions;

# View specific interview answers
SELECT * FROM interview_answers WHERE interview_id = 1;
```

### Option 3: Using DBeaver (GUI)
- Download from https://dbeaver.io/
- Connect to: localhost:5432, postgres/postgres, database: ai_interview

---

## 🚀 Next Steps

1. **Login** with any credentials - user auto-created
2. **View Questions** - Browse all 12 questions from database
3. **Complete Interview** - Answers automatically saved
4. **View Analytics** - Check `/interviews` endpoint for results
5. **Admin Features** - Manage questions (coming soon)

---

## 📞 Support

For issues:
1. Check logs: `docker-compose logs backend`
2. Verify ports: `netstat -ano | findstr :5173 :8000 :5432`
3. Restart services: `docker-compose restart`

---

**✨ Your database is now fully integrated and ready to use!**
