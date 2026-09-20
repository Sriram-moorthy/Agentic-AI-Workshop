import os
from uuid import UUID
from dotenv import load_dotenv

from app.agents.orchestrator import run_orchestrator

load_dotenv()

student_id = UUID(os.getenv("STUDENT_ID") or os.getenv("STUDENT_UUID"))

conversation_history = [
{
"role": "user",
"content": "I studied Java for 2 hours.",
},
{
"role": "assistant",
"content": "I've recorded your Java study session.",
},
]

current_message = "How much did I study?"

response = run_orchestrator(
student_id=student_id,
message=current_message,
conversation_history=conversation_history,
)

print("\nAssistant response:")
print(response)
