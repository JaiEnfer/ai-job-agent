# AI Job Application Agent

Germany-focused AI job application agent that can:

- ingest jobs manually or from URLs
- parse job descriptions
- manage candidate profiles
- match jobs to profiles
- generate tailored CV drafts
- generate cover letters
- score ATS readiness
- save application packages
- track applications through workflow stages

## Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Playwright
- Gemini API

### Frontend
- React
- Vite
- Axios
- React Router

## Features

- Job ingestion
- JD parsing
- Candidate profile management
- Match scoring
- Tailored CV generation
- Cover letter generation
- ATS scoring
- Application package generation
- Application tracking
- Site-aware scraping foundation

## Run backend

```bash
uvicorn app.main:app --reload
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

## Run with Docker
```bash 
docker compose -f docker-compose.full.yml up --build
```

## Environment variables

Create a .env file with:

```text
APP_NAME=AI Job Application Agent
APP_ENV=dev
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_job_agent
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3-flash
```

## MVP Goal

1. Create candidate profile

2. Create or ingest a job

3. Generate application package

4. Save and view package

5. Create application record

6. Track application status

## Goal 

Build a full-stack AI job application agent for Germany that goes from job ingestion to application package generation and tracking.