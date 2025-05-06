import os
# from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool

from .prompts import return_instructions_agent


web_agent = Agent(
    model=os.getenv("WEB_AGENT_MODEL"),
    name="web_agent",
    description="The web searching agent in the council of elders.",
    instruction=return_instructions_agent(),
    tools=[GoogleSearchTool()],
)
