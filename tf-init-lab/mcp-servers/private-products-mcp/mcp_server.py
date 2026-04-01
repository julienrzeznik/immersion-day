import argparse
import os
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from app.server_init import mcp
from app import tools  # Ensure tools are registered
from app import api    # Ensure api is registered

def main():
    """Main function to run the FastMCP server."""
    parser = argparse.ArgumentParser(description="Products MCP Server")
    parser.get_default("transport")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="The transport to use for the server (stdio or http).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8080)),
        help="The port to use for the HTTP server. Defaults to $PORT or 8080.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="The host to bind the server to.",
    )
    args = parser.parse_args()

    if args.transport == "http":
        os.environ["FASTMCP_STATELESS_HTTP"] = "true"
        os.environ["FASTMCP_JSON_RESPONSE"] = "true"

        starlette_app = mcp.http_app(path="/mcp")
        starlette_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id"],
        )
        uvicorn.run(starlette_app, host=args.host, port=args.port)
    else:
        mcp.run(transport=args.transport)

if __name__ == "__main__":
    main()