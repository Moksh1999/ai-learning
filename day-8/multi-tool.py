import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# --- Tool 1: calculator (from Day 8) ---
def calculate(expression):
    return eval(expression)

# --- Tool 2: a mock weather lookup (hardcoded data, no real API needed for this exercise) ---
def get_weather(city):
    fake_weather_db = {
        "delhi": 34,
        "mumbai": 31,
        "bengaluru": 26,
    }
    return fake_weather_db.get(city.lower(), "unknown city")

tools = [
    {
        "name": "calculate",
        "description": "Perform a basic arithmetic calculation. Use this whenever a math computation is needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "A math expression, e.g. '34 * 2'"}
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get the current temperature in Celsius for a given city. Use this whenever the user asks about weather or temperature in a specific place.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Delhi'"}
            },
            "required": ["city"]
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

def execute_tool(name, tool_input):
    if name == "calculate":
        return calculate(tool_input["expression"])
    elif name == "get_weather":
        return get_weather(tool_input["city"])
    else:
        return "unknown tool"

# --- The agent loop ---
messages = [
    {"role": "user", "content": "What's the temperature in Delhi right now, and what would that be if it doubled?"}
]

max_rounds = 5
for round_num in range(max_rounds):
    data = call_claude(messages)
    print(f"\n=== Round {round_num + 1} | stop_reason: {data['stop_reason']} ===")

    if data["stop_reason"] == "tool_use":
        # There may be one or more tool_use blocks in this response
        messages.append({"role": "assistant", "content": data["content"]})

        tool_results = []
        for block in data["content"]:
            if block["type"] == "tool_use":
                print(f"Model wants to call: {block['name']}({block['input']})")
                result = execute_tool(block["name"], block["input"])
                print(f"Tool result: {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": str(result)
                })

        messages.append({"role": "user", "content": tool_results})
        # loop continues - model gets another turn with the new result available

    else:
        # stop_reason == "end_turn" - model is done, this is the final answer
        print(f"\nFinal answer:\n{data['content'][0]['text']}")
        break