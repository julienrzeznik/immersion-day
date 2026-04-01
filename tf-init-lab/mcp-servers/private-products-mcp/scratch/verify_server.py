import sys
import os
from starlette.testclient import TestClient

# Add local directory to path
sys.path.append(os.getcwd())

# Mock transport env vars
os.environ["FASTMCP_STATELESS_HTTP"] = "true"
os.environ["FASTMCP_JSON_RESPONSE"] = "true"

# Import from app package
from app.server_init import mcp
from app import tools
from app import api

def test_routes():
    app = mcp.http_app(path="/mcp")
    client = TestClient(app)
    
    print("Testing /api/health...")
    response = client.get("/api/health")
    print(f"Status: {response.status_code}, Body: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    print("Testing /api/products...")
    response = client.get("/api/products")
    print(f"Status: {response.status_code}, Body: {response.json()}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    try:
        test_routes()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
