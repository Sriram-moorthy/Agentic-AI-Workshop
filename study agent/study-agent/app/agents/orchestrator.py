"""Orchestrator: uses Gemini to route a user message to the Tracker Agent or the Analyst Agent."""

from google.genai import types

from app.agents.analyst_agent import run_analyst_agent
from app.agents.tracker_agent import run_tracker_agent
from app.llm.client import client

MODEL = "gemini-3.1-flash-lite"

_ROUTING_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="route_to_tracker",
            description="Choose this when the user is reporting/recording study activity they just did "
            "(e.g. subjects studied, time spent, problems solved).",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
        types.FunctionDeclaration(
            name="route_to_analyst",
            description="Choose this when the user is asking a question about or wants analysis of their "
            "past study history (e.g. totals, trends, summaries).",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
    ]
)

_CONFIG = types.GenerateContentConfig(
    tools=[_ROUTING_TOOL],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode="ANY")
    ),
)


def run_orchestrator(
    student_id: str, message: str, conversation_history: list[dict] | None = None
) -> str:
    """Classify the message intent with Gemini, then delegate to the Tracker or Analyst agent."""
    contents = _build_contents(conversation_history, message)
    response = client.models.generate_content(model=MODEL, contents=contents, config=_CONFIG)

    route = response.candidates[0].content.parts[0].function_call.name

    if route == "route_to_tracker":
        print("[Orchestrator] Decision: route_to_tracker -> Tracker Agent")
        return run_tracker_agent(student_id, message)

    print("[Orchestrator] Decision: route_to_analyst -> Analyst Agent")
    return run_analyst_agent(student_id, message)


def _build_contents(
    conversation_history: list[dict] | None, message: str
) -> list[types.Content]:
    contents = []

    for entry in conversation_history or []:
        role = "model" if entry["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=entry["content"])]))

    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    return contents
