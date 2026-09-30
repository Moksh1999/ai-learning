import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("API key not found - check your .env file")

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    json={
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "system": "You are a strict technical reviewer. You always respond in valid JSON only, with no extra text before or after. Never include markdown code fences.",
        "messages": [
            # --- few-shot example 1 ---
            {"role": "user", "content": "Review this code comment: '// loop through stuff'"},
            {"role": "assistant", "content": '{"issue": "vague comment", "severity": "low", "suggestion": "Describe what is being looped and why"}'},
            # --- few-shot example 2 ---
            {"role": "user", "content": "Review this code comment: '// TODO: fix this later maybe'"},
            {"role": "assistant", "content": '{"issue": "unclear TODO with no owner or ticket reference", "severity": "medium", "suggestion": "Link a ticket ID and describe the actual defect"}'},
            # --- the real question ---
            {"role": "user", "content": "Review this code comment: '// this works dont touch it'"}
        ]
    }
)

data = response.json()
model_reply = data["content"][0]["text"]

# Strip markdown code fences if present
cleaned = model_reply.strip()
if cleaned.startswith("```"):
    cleaned = cleaned.split("\n", 1)[1]  # remove first line (```json)
    cleaned = cleaned.rsplit("```", 1)[0]  # remove trailing ```
cleaned = cleaned.strip()

print("--- Cleaned output ---")
print(cleaned)

print("\n--- Parsed as JSON ---")
parsed = json.loads(cleaned)
print(parsed)
print("Issue:", parsed["issue"])