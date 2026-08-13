# AI Interview Platform

This project combines:

- React frontend for the interview UI
- Python FastAPI backend for interview logic and API endpoints
- PostgreSQL-ready database configuration
- Python data / ML / NLP pipeline
- Plotly visualizations
- Streamlit Cloud deployment support

## Stack

- Frontend: React
- Backend: Python, FastAPI
- Database: PostgreSQL
- Data / ML: Python, Pandas, NumPy, scikit-learn, NLTK
- Visualization: Plotly
- Deployment: Streamlit Cloud

## Local setup

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Streamlit analytics dashboard

```bash
streamlit run streamlit_app.py
```

### PostgreSQL

Create a PostgreSQL database named `ai_interview` and set the connection string in your environment:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ai_interview"
```

## Deployment

- Frontend can be deployed to Vercel
- Streamlit dashboard can be deployed to Streamlit Cloud
- FastAPI backend can be deployed to Render, Railway, or a similar service

Local Docker deployment (example)

1. Copy environment file:

```bash
cp .env.example .env
```

2. Start services with Docker Compose:

```bash
docker compose up --build
```

This will start Postgres, the FastAPI backend on port `8000`, and the frontend served via nginx on port `5175`.
