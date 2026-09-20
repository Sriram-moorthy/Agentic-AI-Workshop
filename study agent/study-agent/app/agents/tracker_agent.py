"""Tracker Agent: uses Gemini function calling to log a study session from a natural-language message."""

from datetime import date

from google.genai import types

from app.llm.client import client
from app.tools.study_tools import create_study_session

MODEL = "gemini-3.1-flash-lite"

_CREATE_STUDY_SESSION_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="create_study_session",
            description="Logs a completed study session for the student.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "subject": types.Schema(
                        type="STRING", description="The subject that was studied."
                    ),
                    "duration_minutes": types.Schema(
                        type="INTEGER", description="Total minutes spent studying."
                    ),
                    "problems_solved": types.Schema(
                        type="INTEGER",
                        description="Number of problems solved. Use 0 if none were mentioned.",
                    ),
                    "study_date": types.Schema(
                        type="STRING",
                        description="The date studied, in YYYY-MM-DD format. Use today's date if not mentioned.",
                    ),
                },
                required=["subject", "duration_minutes", "problems_solved", "study_date"],
            ),
        )
    ]
)

_CONFIG = types.GenerateContentConfig(tools=[_CREATE_STUDY_SESSION_TOOL])


def run_tracker_agent(student_id: str, message: str) -> str:
    """Send the user's message to Gemini, execute create_study_session() when called, and return the final reply."""
    contents = [types.Content(role="user", parts=[types.Part(text=message)])]

    response = client.models.generate_content(model=MODEL, contents=contents, config=_CONFIG)

    part = response.candidates[0].content.parts[0]
    function_call = part.function_call

    if not function_call:
        return response.text

    args = function_call.args
    print(f"[Tracker Agent] Calling tool: create_study_session({dict(args)})")
    # student_id always comes from the app, never from Gemini's arguments.
    result = create_study_session(
        student_id=student_id,
        subject=args["subject"],
        duration_minutes=int(args["duration_minutes"]),
        problems_solved=int(args["problems_solved"]),
        study_date=date.fromisoformat(args["study_date"]),
    )
    print(f"[Tracker Agent] Tool result: {result}")

    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name, response={"result": result}
                )
            ],
        )
    )

    final_response = client.models.generate_content(model=MODEL, contents=contents, config=_CONFIG)
    return final_response.text
