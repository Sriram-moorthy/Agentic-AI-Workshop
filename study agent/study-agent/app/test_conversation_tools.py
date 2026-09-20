import os
from uuid import UUID
from dotenv import load_dotenv

from app.tools.conversation_tools import (
    create_conversation,
    save_message,
    get_recent_messages,
)

load_dotenv()

student_id = UUID(os.getenv("STUDENT_ID") or os.getenv("STUDENT_UUID"))


# 1. Create conversation
conversation = create_conversation(student_id)

print("Conversation:")
print(conversation)

conversation_id = UUID(conversation["id"])


# 2. Save user message
user_message = save_message(
    conversation_id=conversation_id,
    role="user",
    content="I studied Java for 2 hours.",
)

print("\nUser message:")
print(user_message)


# 3. Save assistant message
assistant_message = save_message(
    conversation_id=conversation_id,
    role="assistant",
    content="I've recorded your Java study session.",
)

print("\nAssistant message:")
print(assistant_message)


# 4. Retrieve conversation
messages = get_recent_messages(conversation_id)

print("\nConversation history:")

for message in messages:
    print(f"{message['role']}: {message['content']}")