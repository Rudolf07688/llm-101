import os
# from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent

from .prompts import return_instructions_agent



template_agent = Agent(
    model=os.getenv("TEMPLATE_AGENT_MODEL"),
    name="template_agent",
    description="The template agent in the council of elders.",
    instruction=return_instructions_agent(),
)
