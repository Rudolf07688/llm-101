import os
from google.adk.code_executors import VertexAiCodeExecutor
# from google.adk.agents import Agent
from google.adk.agents import ParallelAgent
from google.adk.agents import LoopAgent

from .prompts import return_instructions_agent

# Sub Agents
# from ..template_agent.agent import template_agent
from ..web_agent.agent import web_agent
from ..stoic_agent.agent import stoic_agent

elder_agent = LoopAgent(
    model=os.getenv("COUNCIL_AGENT_MODEL"),
    name="council_agent",
    description="The Elder Agent that coordinates the Council of Elders.",
    instruction=return_instructions_agent(),
    sub_agents=[
        web_agent,
        stoic_agent,
        # science_agent,
        # daoist_agent,
        # abrahamic_agent,
        # buddhist_agent,
    ]
    # code_executor=VertexAiCodeExecutor(
    #     optimize_data_file=True,
    #     stateful=True,
    # ),
)
