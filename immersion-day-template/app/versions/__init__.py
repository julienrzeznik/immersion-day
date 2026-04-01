import os
import importlib
import json
from google.adk.agents import Agent
from app.config import config

def get_agent() -> Agent:
    """ Load the agent based on the version specified in app/config.json. """
    version = config.get("version", "agent_and_tools_serveridentity")
    
    try:
        # Dynamically import the module
        module = importlib.import_module(f".{version}", package="app.versions")
        # Expect the module to have a 'root_agent' object or a 'get_agent' function
        if hasattr(module, "get_agent"):
            return module.get_agent()
        elif hasattr(module, "root_agent"):
            return module.root_agent
        else:
            raise AttributeError(f"Module {version} does not have 'root_agent' or 'get_agent'")
    except ImportError as e:
        print(f"Error importing agent version '{version}': {e}")
        print("Falling back to default 'agent_and_tools_serveridentity'")
        # Fallback to agent_and_tools_serveridentity if import fails
        from . import agent_and_tools_serveridentity
        if hasattr(agent_and_tools_serveridentity, "get_agent"):
            return agent_and_tools_serveridentity.get_agent()
        return agent_and_tools_serveridentity.root_agent
