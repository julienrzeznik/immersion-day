import time
import shutil
import threading
import subprocess
import google.auth
import google.auth.transport.requests
from google.oauth2 import id_token
from google.oauth2 import credentials as user_creds
from google.auth import jwt

# --- Configuration ---
# Safety buffer: Refresh token if it expires in less than this many seconds.
EXPIRY_BUFFER_SECONDS = 30 

# Cache storage: { "service_url": {"token": "...", "expiry": 1234567890} }
_TOKEN_CACHE = {}
_CACHE_LOCK = threading.Lock()

def get_identity_token(service_url):
    """
    Returns a valid ID token for the given service URL (audience).
    
    Features:
    - Auto-detects environment (Cloud Run vs Local Developer).
    - Caches tokens to minimize latency and API calls.
    - Thread-safe.
    """
    # 1. Check Cache (Thread-safe read)
    with _CACHE_LOCK:
        if _is_token_valid(service_url):
            return _TOKEN_CACHE[service_url]["token"]

    # 2. Generate New Token (if cache missed or expired)
    # Note: We generate outside the lock to avoid blocking other threads 
    # if generation takes time, though a double-check pattern could be added for strictness.
    token = _generate_new_token(service_url)
    
    # 3. Cache the new result (Thread-safe write)
    _cache_token(service_url, token)
    
    return token

def _is_token_valid(audience):
    """Checks if we have a non-expired token in memory."""
    cached_data = _TOKEN_CACHE.get(audience)
    if not cached_data:
        return False
    
    now = time.time()
    # Check if token is still valid (current time < expiry - buffer)
    if now < (cached_data["expiry"] - EXPIRY_BUFFER_SECONDS):
        return True
    
    return False

def _cache_token(audience, token_str):
    """Decodes token to find expiry, then stores it safely."""
    try:
        # Decode without verifying signature to extract 'exp'.
        # We trust the source (Google) and only need the timestamp.
        decoded = jwt.decode(token_str, verify=False)
        expiry = decoded.get("exp")
        
        with _CACHE_LOCK:
            _TOKEN_CACHE[audience] = {
                "token": token_str,
                "expiry": expiry
            }
    except Exception as e:
        # If decoding fails, we just return the token without caching
        # so the immediate request succeeds.
        print(f"Warning: Could not decode token for caching: {e}")

def _generate_new_token(audience):
    """
    Internal logic to generate a token based on environment.
    """
    creds, _ = google.auth.default()

    # Scenario A: Local User Credentials
    # identified by checking the credentials object type.
    if isinstance(creds, user_creds.Credentials):
        return _get_token_from_gcloud_cli()

    # Scenario B: Service Account / Cloud Run / Agent Engine
    # Uses the standard, efficient library method.
    auth_req = google.auth.transport.requests.Request()
    return id_token.fetch_id_token(auth_req, audience)

def _get_token_from_gcloud_cli():
    """
    Fallback for local user accounts using the gcloud CLI.
    
    CRITICAL NOTE: We do NOT pass the '--audiences' flag here.
    User credentials cannot sign tokens with custom audiences.
    We generate a standard Google-audience token, which Cloud Run 
    accepts for developers (Authorization: Bearer <token>).
    """
    if not shutil.which("gcloud"):
        raise EnvironmentError("gcloud CLI not found. Required for local user authentication.")

    try:
        # The simple command generates a token with audience set to Google's CLI Client ID.
        # Cloud Run recognizes this audience for User credentials.
        cmd = ["gcloud", "auth", "print-identity-token"]
        
        # 'strip()' removes the trailing newline
        return subprocess.check_output(cmd, text=True).strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to generate token via gcloud: {e}")


def create_header_provider(audience):
    """
    Factory that creates a header_provider specific to one audience.
    """
    def _provider(context):
        token = get_identity_token(audience)
        return {"Authorization": f"Bearer {token}"}
        
    return _provider
