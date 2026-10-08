import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Define the tool: name, description, and what arguments it expects
tools = [
    {
        "name": "calculate",
        "description": "Perform a basic arithmetic calculation. Use this whenever the user asks a math question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression to evaluate, e.g. '23 * 47' or '(100 - 15) / 5'"
                }
            },
            "required": ["expression"]
        }
    }
]

def call_claude(messages):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 500,
            "tools": tools,
            "messages": messages
        }
    )
    return response.json()

# Step 1: Ask a question that requires the tool
messages = [
    {"role": "user", "content": "What is 847 multiplied by 293, then add 1500?"}
]

data = call_claude(messages)
print("--- First response from model ---")
print(json.dumps(data, indent=2))

# Step 2: Execute the tool call ourselves
tool_call = data["content"][0]
expression = tool_call["input"]["expression"]
result = eval(expression)  # fine for our own trusted test expressions; never eval() untrusted input in production

print(f"\n--- Executing tool locally ---")
print(f"Expression: {expression}")
print(f"Result: {result}")

# Step 3: Send the result back to the model, linked by tool_use_id
messages.append({"role": "assistant", "content": data["content"]})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_call["id"],
            "content": str(result)
        }
    ]
})

final_data = call_claude(messages)
print("\n--- Final response from model ---")
print(final_data["content"][0]["text"])