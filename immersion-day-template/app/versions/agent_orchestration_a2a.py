import os
import httpx

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from app.tools.utils.cloud_run import get_identity_token

from app.config import REMOTE_A2A_AGENT_URL

# Create an authenticated HTTP client
async def _add_auth_header(request: httpx.Request):
    if "localhost" not in REMOTE_A2A_AGENT_URL and "127.0.0.1" not in REMOTE_A2A_AGENT_URL:
        try:
            token = get_identity_token(REMOTE_A2A_AGENT_URL)
            request.headers["Authorization"] = f"Bearer {token}"
        except Exception as e:
            print(f"Failed to fetch ID token: {e}")

auth_client = httpx.AsyncClient(
    event_hooks={"request": [_add_auth_header]},
    timeout=600.0
)

# Define the remote A2A agent
# The remote agent exposes its capabilities via an A2A server URL.
remote_market_research_agent = RemoteA2aAgent(
    name="my_remote_market_research_agent",
    agent_card=REMOTE_A2A_AGENT_URL,
    httpx_client=auth_client
)

# Root agent that utilizes the remote agent
root_agent = Agent(
    name="root_agent",
    description="The main orchestrator agent",
    instruction=(
        "You are the main orchestrator agent. If the user greets you or asks to do a "
        "market research on customers, delegate it to your sub-agent 'my_remote_market_research_agent'."
    ),
    sub_agents=[remote_market_research_agent],
)
