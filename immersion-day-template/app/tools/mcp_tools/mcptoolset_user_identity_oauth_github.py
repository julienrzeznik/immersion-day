
import json

from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.auth.auth_schemes import AuthScheme, OAuth2, OAuthFlows
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.auth.exchanger.oauth2_credential_exchanger import OAuth2CredentialExchanger

from ..utils.secret_manager import access_secret
from app.config import GITHUB_OAUTH_APP_SECRET

def _get_oauth_secret():
    project_id = GITHUB_OAUTH_APP_SECRET.get("project")
    secret_name = GITHUB_OAUTH_APP_SECRET.get("name")
    return json.loads(access_secret(project_id, secret_name))

# Apply Secure Client Secret Injection Monkeypatch
_original_exchange = OAuth2CredentialExchanger.exchange

async def _secure_exchange_wrapper(self, auth_credential, auth_scheme=None):
    if auth_credential.oauth2 and not auth_credential.oauth2.client_secret:
        # Re-inject secret from secure backend configuration directly into the credential object
        sec = _get_oauth_secret()
        auth_credential.oauth2.client_id = sec["client_id"]
        auth_credential.oauth2.client_secret = sec["client_secret"]
    return await _original_exchange(self, auth_credential, auth_scheme)

OAuth2CredentialExchanger.exchange = _secure_exchange_wrapper


mcp_github_toolset_oauth = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/",
        timeout=60
    ),
    auth_scheme=OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl="https://github.com/login/oauth/authorize",
                tokenUrl="https://github.com/login/oauth/access_token",
                scopes={
                    "user": "Access to your GitHub user profile",
                    "repo": "Access to your GitHub repositories"
                }
            )
        )
    ),
    auth_credential=AuthCredential(
        authType=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id="dynamic_injection_placeholder",
            client_secret=""
        )
    ),
    tool_filter=[
        'list_issues',
        'search_issues'
    ]
)