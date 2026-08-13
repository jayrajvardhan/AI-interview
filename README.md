# AI Interview Platform 🎯

An AI-powered mock interview platform with a **React frontend** and **FastAPI backend**. Supports theoretical Q&A with voice input, coding challenges with in-browser execution, real-time scoring, and a full performance report.

> **Live Repo:** https://github.com/jayrajvardhan/AI-interview

---

## Features

- 🎤 Voice-to-text answers (Web Speech API)
- 💻 In-browser JavaScript code execution
- 📊 Auto-scoring with TF-IDF similarity + keyword matching
- 🗄️ SQLite database (zero config, works out of the box)
- 👤 Student + Admin roles
- 📋 12 pre-seeded interview questions (Frontend, Backend, Database, System Design, DevOps, ML, Security)

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 19 + Vite                     |
| Backend    | Python 3.9+, FastAPI, Uvicorn       |
| Database   | SQLite (default) / PostgreSQL       |
| ML / NLP   | scikit-learn, NLTK                  |
| Analytics  | Streamlit, Plotly                   |

---

## Quick Start (Local)

### 1. Clone the repo

```bash
git clone https://github.com/jayrajvardhan/AI-interview.git
cd AI-interview
```

### 2. Start the Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend will be available at: **http://127.0.0.1:8000**
API docs at: **http://127.0.0.1:8000/docs**

> The SQLite database (`ai_interview.db`) is created automatically on first run. No PostgreSQL setup needed.

### 3. Start the Frontend

Open a **new terminal** in the project root:

```bash
npm install
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## Login Credentials

| Role    | Email                  | Password |
|---------|------------------------|----------|
| Student | any email              | any text |
| Admin   | admin@codegian.com     | admin123 |

---

## Environment Variables (Optional)

By default the app uses **SQLite** — no setup needed.

To use **PostgreSQL** instead, copy `.env.example` to `.env` and set:

```bash
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/ai_interview
```

---

## API Endpoints

| Method | Endpoint              | Description                     |
|--------|-----------------------|---------------------------------|
| GET    | /health               | Health check + DB status        |
| POST   | /login                | Login or register a user        |
| GET    | /questions            | Get all questions (auto-seeded) |
| POST   | /evaluate/theory      | Score a theoretical answer      |
| POST   | /run/code             | Execute JavaScript/Python code  |
| POST   | /save-interview       | Save completed interview to DB  |
| GET    | /interviews           | List all completed interviews   |
| GET    | /interview/{id}       | Get detailed interview report   |

---

## Project Structure

```
AI-interview/
├── backend/
│   ├── main.py           # FastAPI app + all routes
│   ├── database.py       # SQLAlchemy models + DB init
│   └── requirements.txt  # Python dependencies
├── src/
│   ├── App.jsx           # Main React component
│   ├── App.css           # Styles
│   └── main.jsx          # Entry point
├── index.html
├── package.json
├── vite.config.js
└── .env.example          # Environment variable template
```

---

## Docker (Optional)

```bash
cp .env.example .env
docker compose up --build
```

This starts PostgreSQL + FastAPI backend (port 8000) + frontend (port 5175).

---

## Deployment

| Service   | Platform             |
|-----------|----------------------|
| Frontend  | Vercel / Netlify     |
| Backend   | Render / Railway     |
| Analytics | Streamlit Cloud      |
