import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def call_haiku(system_prompt: str, user_message: str) -> str:
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    return response.content[0].text #type: ignore