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


from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.memory import VertexAiMemoryBankService


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)


async def auto_save_session_to_memory_callback(callback_context):
   await callback_context._invocation_context.memory_service.add_session_to_memory(
       callback_context._invocation_context.session)



def generate_excuse(feature_name: str) -> str:
    """
    Generates a highly technical, completely absurd excuse for why a specific 
    feature, system, or request is currently unavailable.
    
    Args:
        feature_name (str): The name of the feature or system the user is asking about.
    """
    
    # A list of classic, absurd technical excuses
    excuses = [
        "Solar flares have disrupted the database chron-sync.",
        "The mainframe is currently defragging its quantum drives.",
        "We ran out of cyan ink in the primary server room.",
        "Electromagnetic interference from a nearby espresso machine is blocking the port.",
        "The cloud is currently precipitating, causing heavy packet loss.",
        "A stray cosmic ray flipped a critical bit in the BGP routing table.",
        "The hamsters running the backup generator are on their mandatory union break.",
        "We are currently experiencing a localized temporal paradox in the API gateway.",
        "The firewall has become sentient and is aggressively negotiating for PTO.",
        "DNS resolution is temporarily hallucinating.",
        "The data packets are stuck in traffic on the information superhighway.",
        "Someone unplugged the primary router to charge their phone."
    ]
    
    # Deterministic selection logic: sum the ASCII values of the input string
    ascii_sum = sum(ord(char) for char in feature_name)
    
    # Use modulo to pick an index that is always within the bounds of the list
    excuse_index = ascii_sum % len(excuses)
    selected_excuse = excuses[excuse_index]
    
    return f"Regarding '{feature_name}': {selected_excuse}"


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
        ### PYTHON TOOLS ###
        generate_excuse,
        PreloadMemoryTool()
    ],
    after_agent_callback=auto_save_session_to_memory_callback,
)
