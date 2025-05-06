import os
# from google.adk.agents import Agent
from google.adk.agents import ParallelAgent


# Sub Agents
# from ..template_agent.agent import template_agent
from ..web_agent.agent import web_agent
from ..stoic_agent.agent import stoic_agent

council_agent = ParallelAgent(
    name="council_agent",
    description="The Elder Agent that coordinates the Council of Elders.",
    sub_agents=[
        web_agent,
        stoic_agent,
        # science_agent,
        # daoist_agent,
        # abrahamic_agent,
        # buddhist_agent,
    ]
)
