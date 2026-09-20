from app.llm.client import client

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Say hello in one sentence."
)

print(response.text)