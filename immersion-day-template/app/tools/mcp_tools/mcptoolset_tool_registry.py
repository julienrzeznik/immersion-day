import os
from dotenv import load_dotenv

from google.adk.integrations.api_registry import ApiRegistry
from google.adk.tools import McpToolset

from ..utils.cloud_run import create_header_provider

load_dotenv()

import logging

logger = logging.getLogger(__name__)

PROJECT_ID = "immersion-day-master-project"

MCP_SERVER_NAME = f"projects/{PROJECT_ID}/locations/europe-west4/mcpServers/apihub-27888638-6180-4733-aa87-a73b6649d197.c4ae718f-bf0d-40fe-bff4-402f9a47c602.846c3835-8bd9-435e-a78e-aed3c1e4f38d"

LOCATION = "global"



def load_api_registry(project_id, header_provider=None):
    try:
         api_registry = ApiRegistry(
              api_registry_project_id=project_id,
              location="global",
              header_provider=header_provider
         )
         return api_registry
    except Exception as e:
         logger.error(f"Failed to load ApiRegistry for project {project_id}: {e}.")
         raise e


# 1. Fetch the server list to get the URL dynamically
api_registry = load_api_registry(PROJECT_ID)
server = api_registry._mcp_servers.get(MCP_SERVER_NAME)

if not server or not server.get("urls"):
    logger.error(f"MCP server {MCP_SERVER_NAME} not found or has no URLs. Dynamic resolution failed.")
    raise ValueError(f"MCP server {MCP_SERVER_NAME} not found or has no URLs. Dynamic resolution failed.")

mcp_server_url = server["urls"][0]

# Append /mcp if missing
if not mcp_server_url.endswith("/mcp") and not mcp_server_url.endswith("/mcp/"):
    if mcp_server_url.endswith("/"):
        mcp_server_url = mcp_server_url[:-1]
    mcp_server_url += "/mcp"

# 2. Create header provider
from urllib.parse import urlparse
parsed_url = urlparse(mcp_server_url)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

header_provider = create_header_provider(base_url)

# 3. Initialize McpToolset with header provider directly
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
products_mcp_tools = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url,
    ),
    header_provider=header_provider,
)
