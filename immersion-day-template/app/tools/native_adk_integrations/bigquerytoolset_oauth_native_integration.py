import json

from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode


from google.adk.auth.auth_credential import AuthCredentialTypes
import google.auth

# Define an appropriate credential type
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2

from ..utils.secret_manager import access_secret

from app.config import BIGQUERY_TOOLSET_OAUTH_SECRET

def _get_oauth_secret():
    project_id = BIGQUERY_TOOLSET_OAUTH_SECRET.get("project")
    secret_name = BIGQUERY_TOOLSET_OAUTH_SECRET.get("name")
    return json.loads(access_secret(project_id, secret_name))


# Write modes define BigQuery access control of agent:
# ALLOWED: Tools will have full write capabilites.
# BLOCKED: Default mode. Effectively makes the tool read-only.
# PROTECTED: Only allows writes on temporary data for a given BigQuery session.


tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

if CREDENTIALS_TYPE == AuthCredentialTypes.OAUTH2:
  # Initiaze the tools to do interactive OAuth
  sec = _get_oauth_secret()
  credentials_config = BigQueryCredentialsConfig(
      client_id=sec["client_id"],
      client_secret=sec["client_secret"],
  )
elif CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
  # Initialize the tools to use the credentials in the service account key.
  creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
  credentials_config = BigQueryCredentialsConfig(credentials=creds)
else:
  # Initialize the tools to use the application default credentials.
  application_default_credentials, _ = google.auth.default()
  credentials_config = BigQueryCredentialsConfig(
      credentials=application_default_credentials
  )

bigquery_toolset = BigQueryToolset(
  credentials_config=credentials_config,   
  tool_filter=[
    'list_dataset_ids',
    'get_dataset_info',
    'list_table_ids',
    'get_table_info',
    'execute_sql',
  ])