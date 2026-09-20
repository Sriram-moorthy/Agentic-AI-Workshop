import os
from uuid import UUID
from dotenv import load_dotenv

from app.agents.analyst_agent import run_analyst_agent

load_dotenv()

student_id = UUID(os.getenv("STUDENT_ID") or os.getenv("STUDENT_UUID"))

questions = [
    "How much did I study recently?",
    "How many problems have I solved?",
    "What subjects have I been studying?",
    "How much time did I spend studying Java?",
]

for question in questions:
    print(f"\nUser: {question}")

    result = run_analyst_agent(
        student_id=student_id,
        message=question,
    )

    print(f"Agent: {result}")