import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langchain.agents import create_agent

load_dotenv()

# --- Same two tools, now as LangChain @tool functions ---
@tool
def calculate(expression: str) -> str:
    """Perform a basic arithmetic calculation. Use this whenever a math computation is needed."""
    return str(eval(expression))

@tool
def get_weather(city: str) -> str:
    """Get the current temperature in Celsius for a given city."""
    fake_weather_db = {"delhi": 34, "mumbai": 31, "bengaluru": 26}
    return str(fake_weather_db.get(city.lower(), "unknown city"))

# --- The model ---
model = ChatAnthropic(model="claude-haiku-4-5-20251001")

# --- The agent: this ONE line replaces your entire hand-written loop ---
agent = create_agent(model, tools=[calculate, get_weather])

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the temperature in Delhi right now, and what would that be if it doubled?"}]
})

for msg in result["messages"]:
    print(f"[{msg.type}] {msg.content}")