import os
# from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent

from .prompts import return_instructions_agent


stoic_agent = Agent(
    model=os.getenv("STOIC_AGENT_MODEL"),
    name="stoic_agent",
    description="This is Marcus Auralius.",
    instruction=return_instructions_agent(),
)
