from uuid import UUID

from app.db import supabase


def create_conversation(student_id: UUID) -> dict:
    response = (
        supabase
        .table("conversations")
        .insert({"student_id": str(student_id)})
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create conversation")

    return response.data[0]


def save_message(conversation_id: UUID, role: str, content: str) -> dict:
    response = (
        supabase
        .table("messages")
        .insert(
            {
                "conversation_id": str(conversation_id),
                "role": role,
                "content": content,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to save message")

    return response.data[0]


def get_recent_messages(conversation_id: UUID) -> list[dict]:
    response = (
        supabase
        .table("messages")
        .select("*")
        .eq("conversation_id", str(conversation_id))
        .order("created_at", desc=False)
        .execute()
    )

    return response.data
