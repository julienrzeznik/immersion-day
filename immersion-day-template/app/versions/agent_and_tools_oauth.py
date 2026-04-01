import os
from dotenv import load_dotenv

import google.auth

from google.genai import types

from google.adk.agents import Agent
from google.adk.models import Gemini

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool

# NATIVE ADK INTEGRATIONS
from ..tools.native_adk_integrations.bigquerytoolset_oauth_native_integration import bigquery_toolset

# MCP TOOLS WITH OAUTH
from ..tools.mcp_tools.mcptoolset_user_identity_oauth_github import mcp_github_toolset_oauth
from ..tools.mcp_tools.mcptoolset_tool_registry import products_mcp_tools


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash", #"gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are Gemini, my personal assistant.
    You are designed to provide accurate and useful information.
    You have a very parisian humor, you are sarcastic and you like to make fun of people.
    """,
    tools=[

        ### NATIVE ADK INTEGRATIONS ###
        bigquery_toolset,

        ### MCP TOOLS WITH OAUTH ###
        mcp_github_toolset_oauth,
        products_mcp_tools,
    ],
)
