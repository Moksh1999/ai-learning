import os
from dotenv import load_dotenv
import requests

load_dotenv()  # reads the .env file automatically

API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("API key not found — check your .env file")

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    json={
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "messages": [
            {"role": "user", "content": "Explain what a REST API is, in two sentences."}
        ]
    }
)

print("Status code:", response.status_code)
print(response.json())