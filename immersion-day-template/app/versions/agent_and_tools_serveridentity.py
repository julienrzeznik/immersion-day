import os
from dotenv import load_dotenv

import google.auth

from google.genai import types

from google.adk.agents import Agent
from google.adk.models import Gemini

from google.adk.tools.agent_tool import AgentTool


# PYTHON TOOLS
from ..tools.python_tools.python_tool import generate_excuse

# NATIVE LLM INTEGRATIONS
from ..tools.native_llm_tools.google_search_native import google_search_agent
from ..tools.native_llm_tools.google_maps_native import google_maps_agent
from ..tools.native_llm_tools.code_execution import coding_agent

# LANGCHAIN AND 3RD PARTY TOOLS
from ..tools.third_party_tools.langchain_tool import langchain_tool

# NATIVE ADK INTEGRATIONS
from ..tools.native_adk_integrations.vertex_ai_search import rag_tool

# API TOOLS
from ..tools.api_tools.openapi_no_auth import customers_toolset
from ..tools.api_tools.openapi_tool_id_token import products_toolset

# MCP TOOLS
from ..tools.mcp_tools.mcptoolset_agentidentity_github import mcp_github_toolset_pat


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are a helpful assistant. You are designed to provide accurate and useful information.
    """,
    tools=[
        ### PYTHON TOOLS ###
        generate_excuse,

        ### LANGCHAIN TOOLS ###
        langchain_tool,
        
        ### NATIVE LLM TOOLS ###
        AgentTool(agent=google_search_agent), # Workaround until gemini 3.1 is released
        AgentTool(agent=google_maps_agent), # Workaround until gemini 3.1 is released
        AgentTool(agent=coding_agent), # Workaround until gemini 3.1 is released

        ### NATIVE ADK INTEGRATIONS ###
        rag_tool,

        ### API TOOLS ###
        customers_toolset,
        products_toolset,

        ### MCP TOOLS ###
        mcp_github_toolset_pat,
    ],
)
