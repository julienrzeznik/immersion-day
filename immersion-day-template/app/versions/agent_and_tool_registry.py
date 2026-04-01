import os
from dotenv import load_dotenv

import google.auth

from google.genai import types

from google.adk.agents import Agent
from google.adk.models import Gemini

# MCP TOOLS WITH OAUTH
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
    You are a helpful assistant. You are designed to provide accurate and useful information.
    """,
    tools=[
        products_mcp_tools,
    ],
)
