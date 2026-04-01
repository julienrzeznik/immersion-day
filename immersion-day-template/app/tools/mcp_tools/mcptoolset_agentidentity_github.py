

from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from ..utils.secret_manager import access_secret

from app.config import GITHUB_PAT_SECRET

def create_github_pat_provider():
    def _provider(context):
        project_id = GITHUB_PAT_SECRET.get("project")
        secret_name = GITHUB_PAT_SECRET.get("name")
        pat = access_secret(project_id, secret_name)
        return {"Authorization": f"Bearer {pat}"}
    return _provider

mcp_github_toolset_pat = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/"
    ),
    header_provider=create_github_pat_provider(),
    tool_filter=[
        'list_issues',
        'search_issues'
    ]
)