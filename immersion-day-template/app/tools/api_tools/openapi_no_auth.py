from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

from app.config import CLOUD_RUN_NOAUTH_MCP_URL

# --- Sample OpenAPI Specification (JSON String) ---
openapi_spec_string = """
openapi: 3.0.0
info:
  title: Customers API
  description: API for managing customers.
  version: 1.0.0
servers:
  - url: CLOUD_RUN_NOAUTH_MCP_URL_PLACEHOLDER
    description: Customers Server
paths:
  /api/customers:
    get:
      summary: Get all customers
      description: Returns a list of all customers.
      responses:
        '200':
          description: A JSON array of customer objects
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Customer'
    post:
      summary: Register a new customer
      description: Registers a new customer and returns the created customer object.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomerCreate'
      responses:
        '201':
          description: A single JSON customer object
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '400':
          description: Bad request
  /api/customers/{customer_id}:
    get:
      summary: Get a single customer by ID
      description: Returns a specific customer based on the provided path parameter.
      parameters:
        - name: customer_id
          in: path
          required: true
          description: The ID of the customer to retrieve.
          schema:
            type: string
      responses:
        '200':
          description: A single JSON customer object
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '404':
          description: Customer not found
  /api/health:
    get:
      summary: Health check
      description: Returns the health status of the service.
      responses:
        '200':
          description: Service is healthy
components:
  schemas:
    Customer:
      type: object
      properties:
        id:
          type: string
          example: CUST-001
        first_name:
          type: string
          example: John
        last_name:
          type: string
          example: Doe
        city:
          type: string
          example: Paris
    CustomerCreate:
      type: object
      required:
        - first_name
        - last_name
        - city
      properties:
        first_name:
          type: string
          example: John
        last_name:
          type: string
          example: Doe
        city:
          type: string
          example: Paris
""".replace("CLOUD_RUN_NOAUTH_MCP_URL_PLACEHOLDER", CLOUD_RUN_NOAUTH_MCP_URL)

# --- Create OpenAPIToolset ---
customers_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='yaml',
)