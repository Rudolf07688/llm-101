# ./adk_agent_samples/mcp_agent/agent.py
import asyncio
import os
from dotenv import find_dotenv, load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters

# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys
found_env = load_dotenv(find_dotenv('.env'))
if not found_env:
    print("No .env file found. Ensure your environment variables are set correctly.")


access_path = os.getcwd()
print(f"Accessing folder: {access_path}")

# --- Step 1: Import Tools from MCP Server ---
async def get_tools_async():
  """Gets tools from the File System MCP Server."""
  print("Attempting to connect to MCP Filesystem server...")
  tools, exit_stack = await MCPToolset.from_server(
      # Use StdioServerParameters for local process communication
      connection_params=StdioServerParameters(
          command='npx', # Command to run the server
          args=["-y",    # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                access_path],                           # <---- Path to the folder to access
      )
      # For remote servers, you would use SseServerParams instead:
      # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
  )
  print("MCP Toolset created successfully.")
  # MCP requires maintaining a connection to the local MCP Server.
  # exit_stack manages the cleanup of this connection.
  return tools, exit_stack

# --- Step 2: Agent Definition ---
async def get_agent_async():
  """Creates an ADK Agent equipped with tools from the MCP Server."""
  tools, exit_stack = await get_tools_async()
  print(f"Fetched {len(tools)} tools from MCP server.")
  root_agent = LlmAgent(
      model='gemini-2.0-flash', # Adjust model name if needed based on availability
      name='filesystem_assistant',
      instruction='Help user interact with the local filesystem using available tools.',
      tools=tools, # Provide the MCP tools to the ADK agent
  )
  return root_agent, exit_stack

# --- Step 3: Main Execution Logic ---
async def async_main():
  session_service = InMemorySessionService()
  # Artifact service might not be needed for this example
  artifacts_service = InMemoryArtifactService()

  session = session_service.create_session(
      state={}, app_name='mcp_filesystem_app', user_id='user_fs'
  )

  # TODO: Change the query to be relevant to YOUR specified folder.
  # e.g., "list files in the 'documents' subfolder" or "read the file 'notes.txt'"
  query = "Please list all of the contents in the root directory './'"
  print(f"User Query: '{query}'")
  content = types.Content(role='user', parts=[types.Part(text=query)])

  root_agent, exit_stack = await get_agent_async()

  runner = Runner(
      app_name='mcp_filesystem_app',
      agent=root_agent,
      artifact_service=artifacts_service, # Optional
      session_service=session_service,
  )

  final_response_text = "Agent did not produce a final response." # Default
  print("Running agent...")
  async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
    # Optional: Print events for debugging if needed
    # print()
    # print(f"Event received: \n{event}")
    if event.is_final_response():
      print("-- FINAL RESPONSE RECEIVED --")
      # Ensure the content is fully loaded (though often not strictly needed for text)
      if event.content and event.content.parts and event.content.parts[0].text:
          final_response_text = event.content.parts[0].text
      else:
          final_response_text = "Agent produced a final response, but it was empty."

      if event.actions and event.actions.escalate: # Handle potential errors/escalations
        final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
      break # Stop processing events once the final response is found
    # Removed intermediate print from here

  # Print the final result after the loop finishes
  print("\n--- Agent Execution Complete ---")
  print(f"Final Response: {final_response_text}")

  # Crucial Cleanup: Ensure the MCP server process connection is closed.
  print("Closing MCP server connection...")
  await exit_stack.aclose()
  print("Cleanup complete.")

if __name__ == '__main__':
  try:
    asyncio.run(async_main())
  except Exception as e:
    print(f"An error occurred: {e}")