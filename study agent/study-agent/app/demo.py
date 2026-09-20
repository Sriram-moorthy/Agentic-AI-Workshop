"""Simple CLI demo of the multi-agent study assistant (Orchestrator -> Tracker/Analyst)."""

import os
from dotenv import load_dotenv

from app.agents.orchestrator import run_orchestrator

load_dotenv()

STUDENT_ID = os.getenv("STUDENT_ID") or os.getenv("STUDENT_UUID")


def run_demo_request(message: str) -> None:
    print(f"User request: {message}")
    response = run_orchestrator(STUDENT_ID, message)
    print(f"Final assistant response: {response}")
    print("-" * 60)


def main() -> None:
    run_demo_request("I studied Java for 2 hours and solved 5 problems.")
    run_demo_request("How much Java have I studied?")


if __name__ == "__main__":
    main()
