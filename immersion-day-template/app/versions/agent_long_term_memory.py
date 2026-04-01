import os
from dotenv import load_dotenv

import google.auth

from google.genai import types


async def auto_save_session_to_memory_callback(callback_context):
   await callback_context._invocation_context.memory_service.add_session_to_memory(
       callback_context._invocation_context.session)


from google.adk.agents import Agent
from google.adk.models import Gemini
from google import adk
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# PYTHON TOOLS
from ..tools.python_tools.python_tool import generate_excuse

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.memory import VertexAiMemoryBankService


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)


async def auto_save_session_to_memory_callback(callback_context):
   await callback_context._invocation_context.memory_service.add_session_to_memory(
       callback_context._invocation_context.session)

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
        ### PYTHON TOOLS ###
        generate_excuse,
        PreloadMemoryTool()
    ],
    after_agent_callback=auto_save_session_to_memory_callback,
)
