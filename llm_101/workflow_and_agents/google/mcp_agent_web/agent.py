# ---------------------------------------------------------------------------- #
#                      https://google.github.io/adk-docs/                      #
# ---------------------------------------------------------------------------- #

from google.adk.agents import (
    Agent,
    BaseAgent,
    LlmAgent,
    ParallelAgent,
    RunConfig,
)
from google.adk import Runner
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService
from google.adk.runners import StreamingMode
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.genai import types

from dotenv import load_dotenv, find_dotenv
from typing import AsyncGenerator
import asyncio


MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
# Note: Specific model names might change. Refer to LiteLLM/Provider documentation.
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"


def before_agent_callback(callback_context):
    print(f"This is the before agent callback function: ---\n{callback_context}\n---")

def after_agent_callback(callback_context):
    print(f"This is the after agent callback function: ---\n{callback_context}\n---")

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


async def call_agent_async(query: str, runner: Runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])  # ?? Not needed?

    final_response_text = "Agent did not produce a final response." # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        event: Event  # just for type hinting
        # Check if the event is a final response
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break # Stop processing events once the final response is found
    print(f"<<< Agent Response: {final_response_text}")


async def run_conversation(runner: Runner):
    await call_agent_async("What is the weather like in London?",
                            runner=runner,
                            user_id=USER_ID,
                            session_id=SESSION_ID)

# if __name__ == "__main__":

# define constants
APP_NAME = "llm_101"
USER_ID = "rudolf"
SESSION_ID = "session_101"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters

async def get_mcp_tools():
    """Gets tools from the File System MCP Server."""
    ACCESS_PATH = '/workspaces/devcontainers/llm-101/llm_101/workflow_and_agents/'
    print("Attempting to connect to MCP Filesystem server...")
    fs_tools = await MCPToolset.from_server(
        # Use StdioServerParameters for local process communication
        connection_params=StdioServerParameters(   # or SseServerParams for remote
            command='npx',
            args=["-y",
                    "@modelcontextprotocol/server-filesystem",
                    ACCESS_PATH],                           # <---- Path to the folder to access
        )
        # For remote servers, you would use SseServerParams instead:
        # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
    )

    bq_tools = await MCPToolset.from_server(
        connection_params=StdioServerParameters(   # or SseServerParams for remote
            command='npx',
            args=["-y",
                    "@ergut/mcp-bigquery-server",   #  | git@github.com:ergut/mcp-bigquery-server.git
                    "--project-id",
                    "llm-training-wheels",
                    "--location",
                    "europe-west1",
                    ],
        )
        # For remote servers, you would use SseServerParams instead:
        # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
    )

    print("MCP Toolset created successfully.")
    # MCP requires maintaining a connection to the local MCP Server.
    # exit_stack manages the cleanup of this connection.

    tools = [*fs_tools, *bq_tools]
    return tools, exit_stack

mcp_tools, exit_stack = await get_mcp_tools()
other_tools = [
    GoogleSearchTool(),
    get_weather,
]

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL,   # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly."
                "You can also use the Google Search tool to find information."
                "If you need to access files, use the MCP File System tool."
                "You can also use the BigQuery tool to access data.",
    tools=[*mcp_tools, *other_tools],
    after_agent_callback=after_agent_callback,
    before_agent_callback=before_agent_callback,
)

print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")

# Create a session service
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# Create a runner
runner = Runner(
    agent=weather_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")

# ----------------------------- load environment ----------------------------- #
_env_found: bool = load_dotenv(find_dotenv())


# ----------------- Check if the environment variable is set ----------------- #
if not _env_found:
    print("No .env file found. Please set the GOOGLE_API_KEY environment variable.")
else:
    print("Environment variables loaded successfully.")

# ----------------------------- run the conversation ----------------------------- #
try:
    root_agent = weather_agent
    asyncio.run(run_conversation(runner))
except Exception as e:
    print(f"An error occurred: {e}")
