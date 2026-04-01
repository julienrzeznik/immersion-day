# Customers MCP Server

A Model Context Protocol (MCP) server that helps manage **Generic Customers**.

It allows you to:
- List all customers.
- Get details of a specific customer.
- Register new customers.

It supports both MCP (stdio/SSE) and REST HTTP endpoints.

## Tools

1. `list_customers`: List all customers in the database.
2. `get_customer`: Get details of a specific customer by ID.
3. `register_customer`: Register a new customer.

## REST Endpoints

- `GET /api/customers`: List all customers.
- `GET /api/customers/{customer_id}`: Get details of a specific customer.
- `POST /api/customers`: Register a new customer (JSON body required).
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