from datetime import date
from uuid import UUID

from app.db import supabase


def create_study_session(
    student_id: UUID,
    subject: str,
    duration_minutes: int,
    problems_solved: int,
    study_date: date,
) -> dict:
    payload = {
        "student_id": str(student_id),
        "subject": subject,
        "duration_minutes": duration_minutes,
        "problems_solved": problems_solved,
        "study_date": study_date.isoformat(),
    }

    try:
        response = supabase.table("study_sessions").insert(payload).execute()
    except Exception as exc:
        raise RuntimeError(f"Failed to create study session: {exc}") from exc

    if not response.data:
        raise RuntimeError("Failed to create study session")

    return response.data[0]
