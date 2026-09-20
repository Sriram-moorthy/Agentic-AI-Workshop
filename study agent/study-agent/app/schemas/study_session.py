from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class StudySessionCreate(BaseModel):
    student_id: UUID
    subject: str = Field(..., min_length=1, max_length=100)
    duration_minutes: int = Field(..., gt=0)
    problems_solved: int = Field(..., ge=0)
    study_date: date
