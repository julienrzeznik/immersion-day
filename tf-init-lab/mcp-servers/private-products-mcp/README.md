# Products MCP Server

A Model Context Protocol (MCP) server that helps manage **Generic Products**.

It allows you to:
- List all products.
- Get details of a specific product.
- Register new products.

It supports both MCP (stdio/SSE) and REST HTTP endpoints.

## Tools

1. `list_products`: List all products in the database.
2. `get_product`: Get details of a specific product by ID.
3. `register_product`: Register a new product.

## REST Endpoints

- `GET /api/products`: List all products.
- `GET /api/products/{product_id}`: Get details of a specific product.
- `POST /api/products`: Register a new product (JSON body required).
- `GET /api/health`: Health check.

## MCP Protocol Path

When running in HTTP mode, the MCP protocol is served at:
- `/mcp`: The MCP endpoint (supporting SSE or Streamable HTTP).

## Running

### Stdio Mode (Default for MCP)

```bash
uv run python mcp_server.py --transport stdio
```

### HTTP Mode (REST)

```bash
uv run python mcp_server.py --transport http --port 8080
```