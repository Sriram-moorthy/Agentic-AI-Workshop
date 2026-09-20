from fastapi import FastAPI, HTTPException

from app.db import supabase
from app.schemas.study_session import StudySessionCreate
from app.tools.study_tools import create_study_session

app = FastAPI(
    title="AI Study Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/study-sessions")
def create_study_session_endpoint(session: StudySessionCreate):
    try:
        return create_study_session(
            student_id=session.student_id,
            subject=session.subject,
            duration_minutes=session.duration_minutes,
            problems_solved=session.problems_solved,
            study_date=session.study_date,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/test-supabase")
def test_supabase():
    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return response.data