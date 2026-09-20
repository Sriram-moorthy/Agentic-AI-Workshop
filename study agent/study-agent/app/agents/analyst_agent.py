"""Analyst Agent: uses Gemini function calling to answer questions about a student's study history."""

from google.genai import types

from app.llm.client import client
from app.tools.analytics_tools import get_study_sessions

MODEL = "gemini-3.1-flash-lite"

_GET_STUDY_SESSIONS_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_study_sessions",
            description="Retrieves the student's past study sessions, ordered by study_date descending.",
            parameters=types.Schema(type="OBJECT", properties={}),
        )
    ]
)

_CONFIG = types.GenerateContentConfig(tools=[_GET_STUDY_SESSIONS_TOOL])


def run_analyst_agent(student_id: str, message: str) -> str:
    """Send the user's message to Gemini, execute get_study_sessions() when called, and return the final reply."""
    contents = [types.Content(role="user", parts=[types.Part(text=message)])]

    response = client.models.generate_content(model=MODEL, contents=contents, config=_CONFIG)

    part = response.candidates[0].content.parts[0]
    function_call = part.function_call

    if not function_call:
        return response.text

    print("[Analyst Agent] Calling tool: get_study_sessions()")
    # student_id always comes from the app, never from Gemini's arguments.
    result = get_study_sessions(student_id=student_id)
    print(f"[Analyst Agent] Tool result: {result}")

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
