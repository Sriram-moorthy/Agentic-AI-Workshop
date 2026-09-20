import os
from uuid import UUID
from dotenv import load_dotenv

from app.agents.tracker_agent import run_tracker_agent

load_dotenv()

student_id = UUID(os.getenv("STUDENT_ID") or os.getenv("STUDENT_UUID"))

message = "I studied Java for 2 hours and solved 5 problems."

result = run_tracker_agent(
    student_id=student_id,
    message=message,
)

print(result)