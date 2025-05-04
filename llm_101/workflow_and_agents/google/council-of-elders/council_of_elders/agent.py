

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""
import os
from datetime import date

# from google.genai import types

from google.adk.agents import LoopAgent
# from google.adk.agents.callback_context import CallbackContext
# from google.adk.tools import load_artifacts

from .sub_agents.council_agent.agent import council_agent
from .prompts import return_instructions_root
# from .sub_agents.bigquery.tools import (
#     get_database_settings as get_bq_database_settings,
# )
# from .tools import call_db_agent, call_ds_agent

date_today = date.today()


# def setup_before_agent_call(callback_context: CallbackContext):
#     """Setup the agent."""

#     # setting up database settings in session.state
#     if "database_settings" not in callback_context.state:
#         db_settings = dict()
#         db_settings["use_database"] = "BigQuery"
#         callback_context.state["all_db_settings"] = db_settings

#     # setting up schema in instruction
#     if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
#         callback_context.state["database_settings"] = get_bq_database_settings()
#         schema = callback_context.state["database_settings"]["bq_ddl_schema"]

#         callback_context._invocation_context.agent.instruction = (
#             return_instructions_root()
#             + f"""

#     --------- The BigQuery schema of the relevant data with a few sample rows. ---------
#     {schema}

#     """
#         )



root_agent = LoopAgent(
    name="gateway_agent",
    description="The entry point for all user interactions in a multi-agent system built with Google ADK.",
    model=os.getenv("ROOT_AGENT_MODEL"),
    instruction=return_instructions_root(),
    global_instruction=(
        f"""
        You are an agentic system called the Council of Elders that each bring your own specific context to
        the table and try to construct a holistic and unbiased answer.
        Todays date: {date_today}
        """
    ),
    sub_agents=[
        council_agent,
    ],
    tools=[
        # call_db_agent,
        # call_ds_agent,
        # load_artifacts,
    ],
    # before_agent_callback=setup_before_agent_call,
    # generate_content_config=types.GenerateContentConfig(temperature=0.01),
    max_iterations=5,
)
