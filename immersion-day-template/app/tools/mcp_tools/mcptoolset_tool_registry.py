import os
from dotenv import load_dotenv

from google.adk.integrations.api_registry import ApiRegistry
from google.adk.tools import McpToolset

from ..utils.cloud_run import create_header_provider

load_dotenv()

import logging

logger = logging.getLogger(__name__)

from app.config import PRODUCTS_MCP_TOOL_REGISTRY_URL

# Get the project ID by parsing the PRODUCTS_MCP_TOOL_REGISTRY_URL
PROJECT_ID = PRODUCTS_MCP_TOOL_REGISTRY_URL.split("/")[1]

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
server = api_registry._mcp_servers.get(PRODUCTS_MCP_TOOL_REGISTRY_URL)

if not server or not server.get("urls"):
    logger.error(f"MCP server {PRODUCTS_MCP_TOOL_REGISTRY_URL} not found or has no URLs. Dynamic resolution failed.")
    raise ValueError(f"MCP server {PRODUCTS_MCP_TOOL_REGISTRY_URL} not found or has no URLs. Dynamic resolution failed.")

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
