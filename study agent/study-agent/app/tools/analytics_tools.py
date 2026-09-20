from uuid import UUID

from app.db import supabase


def get_study_sessions(student_id: UUID) -> list[dict]:
    response = (
        supabase
        .table("study_sessions")
        .select("*")
        .eq("student_id", str(student_id))
        .order("study_date", desc=True)
        .execute()
    )

    return response.data
