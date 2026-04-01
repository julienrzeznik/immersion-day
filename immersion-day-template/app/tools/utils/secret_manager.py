from google.cloud import secretmanager
from google.auth import default

def access_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
  # Application default credential automatically gets token from MDS using agent identity
  agent_identity_credentials, _ = default()

  # Create the Secret Manager client.
  client = secretmanager.SecretManagerServiceClient(credentials=agent_identity_credentials)

  # Build the resource name of the secret version.
  name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

  # Access the secret version.
  response = client.access_secret_version(request={"name": name})

  # Decode the payload to get the secret string.
  secret_value = response.payload.data.decode("UTF-8")
  return secret_value
