import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

config = load_config()

# Helper constants for easy importing
VERTEX_AI_SEARCH_DATASTORE = config.get("VERTEX_AI_SEARCH_DATASTORE", "")
SKILLS_URI = config.get("SKILLS_URI", "")

# MCP URLs
CLOUD_RUN_NOAUTH_MCP_URL = config.get("CLOUD_RUN_NOAUTH_MCP_URL", "")
CLOUD_RUN_AUTH_MCP_URL = config.get("CLOUD_RUN_AUTH_MCP_URL", "")

# Remote Agent URLs
REMOTE_A2A_AGENT_URL = config.get("REMOTE_A2A_AGENT_URL", "")

# Secrets
GITHUB_PAT_SECRET = config.get("GITHUB_PAT_SECRET", "")
GITHUB_OAUTH_APP_SECRET = config.get("GITHUB_OAUTH_APP_SECRET", "")
BIGQUERY_TOOLSET_OAUTH_SECRET = config.get("BIGQUERY_TOOLSET_OAUTH_SECRET", "")