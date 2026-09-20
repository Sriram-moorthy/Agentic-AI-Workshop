import os
from uuid import UUID
from dotenv import load_dotenv

from app.agents.orchestrator import run_orchestrator

load_dotenv()

student_id = UUID(os.getenv("STUDENT_ID") or os.getenv("STUDENT_UUID"))


messages = [
    "I studied Java for 2 hours and solved 5 problems.",
    "How much did I study recently?",
    "How many problems have I solved?",
    "I studied Python for 90 minutes.",
]


for message in messages:
    print(f"\nUser: {message}")

    result = run_orchestrator(
        student_id=student_id,
        message=message,
    )

    print(f"Assistant: {result}")