import ast
import operator
import os
import sqlite3
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "students.db"

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Create a .env file using .env.example."
    )

# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------

def fetch_student(student_id: str) -> tuple[Any, ...] | None:
    """Fetch one student record."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT student_id, name, department,
                   python, database_mark, ai, web
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        )
        return cursor.fetchone()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def get_student_profile(student_id: str) -> str:
    """Get a student's name, department, and marks for all four subjects."""

    student = fetch_student(student_id)

    if student is None:
        return f"No student was found with ID {student_id}."

    (
        student_id,
        name,
        department,
        python_mark,
        database_mark,
        ai_mark,
        web_mark,
    ) = student

    return (
        f"Student ID: {student_id}\n"
        f"Name: {name}\n"
        f"Department: {department}\n"
        f"Python: {python_mark}\n"
        f"Database: {database_mark}\n"
        f"AI: {ai_mark}\n"
        f"Web: {web_mark}"
    )


@tool
def calculate_result(
    python_mark: int,
    database_mark: int,
    ai_mark: int,
    web_mark: int,
) -> str:
    """Calculate total, average, and percentage from four subject marks."""

    marks = [python_mark, database_mark, ai_mark, web_mark]

    if any(mark < 0 or mark > 100 for mark in marks):
        return "Invalid marks. Each mark must be between 0 and 100."

    total = sum(marks)
    average = total / len(marks)
    percentage = (total / 400) * 100

    return (
        f"Total: {total}/400\n"
        f"Average: {average:.2f}\n"
        f"Percentage: {percentage:.2f}%"
    )


@tool
def check_passing_status(
    python_mark: int,
    database_mark: int,
    ai_mark: int,
    web_mark: int,
) -> str:
    """Check whether four subject marks satisfy the university passing rules."""

    marks = {
        "Python": python_mark,
        "Database": database_mark,
        "AI": ai_mark,
        "Web": web_mark,
    }

    if any(mark < 0 or mark > 100 for mark in marks.values()):
        return "Invalid marks. Each mark must be between 0 and 100."

    average = sum(marks.values()) / len(marks)
    minimum_subject_mark = min(marks.values())

    average_rule = average >= 40
    subject_rule = minimum_subject_mark >= 35
    eligible = average_rule and subject_rule

    failed_subjects = [
        subject for subject, mark in marks.items() if mark < 35
    ]

    result = (
        "PASS" if eligible else "NOT ELIGIBLE"
    )

    lines = [
        f"Status: {result}",
        f"Overall average: {average:.2f}% "
        f"({'satisfied' if average_rule else 'not satisfied'})",
        f"Minimum subject mark: {minimum_subject_mark} "
        f"({'satisfied' if subject_rule else 'not satisfied'})",
    ]

    if failed_subjects:
        lines.append(
            "Subjects below 35: " + ", ".join(failed_subjects)
        )

    return "\n".join(lines)


# A restricted calculator rather than raw eval().
_ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float | int:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")

        return _ALLOWED_BIN_OPS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
        return _ALLOWED_UNARY_OPS[type(node.op)](_safe_eval(node.operand))

    raise ValueError("Only basic arithmetic expressions are allowed.")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression safely."""

    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        return str(result)
    except Exception as exc:
        return f"Calculation error: {exc}"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are a university student information assistant.

Your job is to answer questions using the provided tools.

Available tools:

1. get_student_profile
   Retrieves a student's identity, department, and four subject marks.

2. calculate_result
   Calculates total, average, and percentage from four marks.

3. check_passing_status
   Checks the university passing rules using four marks.

4. calculator
   Performs basic arithmetic.

University passing rules:
- Overall average must be at least 40%.
- Every subject mark must be at least 35.

Rules:
- Never invent student information or marks.
- Use get_student_profile whenever student-specific data is required.
- Use calculate_result when the user asks for total, average, or percentage.
- Use check_passing_status when the user asks about passing eligibility.
- You may call multiple tools when the question requires multiple pieces of information.
- Keep the final answer concise and clearly explain the result.
"""

LLM = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0,
    google_api_key=API_KEY,
)

TOOLS = [
    get_student_profile,
    calculate_result,
    check_passing_status,
    calculator,
]

agent = create_agent(
    model=LLM,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
)


def ask_student_agent(question: str) -> str:
    """Send one question to the LangChain agent."""
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content


def main() -> None:
    print("Student Result Agent")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            answer = ask_student_agent(question)
            print(f"\nAgent: {answer}\n")
        except Exception as exc:
            print(f"\nAgent error: {exc}\n")


if __name__ == "__main__":
    main()
