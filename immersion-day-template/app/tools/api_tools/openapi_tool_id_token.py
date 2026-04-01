import os
from dotenv import load_dotenv

from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

from ..utils.cloud_run import create_header_provider

from app.config import CLOUD_RUN_AUTH_MCP_URL

# --- Sample OpenAPI Specification (JSON String) ---
# A basic Pet Store API example using httpbin.org as a mock server
openapi_spec_string = """
{
  "openapi": "3.0.0",
  "info": {
    "title": "Product management MCP server",
    "version": "1.0.0",
    "description": "An API to get and manage products"
  },
  "servers": [
    {
      "url": "CLOUD_RUN_AUTH_MCP_URL_PLACEHOLDER",
      "description": "Product management MCP server"
    }
  ],
  "paths": {
    "/api/products": {
      "get": {
        "summary": "List products",
        "operationId": "listProducts",
        "description": "List the current products",
        "responses": {
          "200": {
            "description": "A list of products.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Product"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "summary": "Register a new product",
        "operationId": "registerProduct",
        "description": "Register a new product",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ProductCreate"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "description": "The registered product.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Product"
                }
              }
            }
          },
          "400": {
            "description": "Bad Request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Error"
                }
              }
            }
          }
        }
      }
    },
    "/api/products/{product_id}": {
      "get": {
        "summary": "Get a specific product",
        "operationId": "getProduct",
        "description": "Get a specific product by ID",
        "parameters": [
          {
            "name": "product_id",
            "in": "path",
            "description": "The ID of the product to retrieve",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "The requested product.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Product"
                }
              }
            }
          },
          "404": {
            "description": "Product not found",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Error"
                }
              }
            }
          }
        }
      }
    },
    "/api/health": {
      "get": {
        "summary": "Simple health check endpoint",
        "operationId": "healthCheck",
        "description": "Simple health check endpoint",
        "responses": {
          "200": {
            "description": "Health status",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "status": {
                      "type": "string"
                    },
                    "service": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Product": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "brand": {
            "type": "string"
          },
          "model": {
            "type": "string"
          },
          "storage": {
            "type": "string"
          },
          "color": {
            "type": "string"
          },
          "price": {
            "type": "number"
          },
          "release_date": {
            "type": "string"
          }
        },
        "required": [
          "id",
          "brand",
          "model",
          "storage",
          "color",
          "price",
          "release_date"
        ]
      },
      "ProductCreate": {
        "type": "object",
        "properties": {
          "brand": {
            "type": "string"
          },
          "model": {
            "type": "string"
          },
          "storage": {
            "type": "string"
          },
          "color": {
            "type": "string"
          },
          "price": {
            "type": "number"
          },
          "release_date": {
            "type": "string"
          }
        },
        "required": [
          "brand",
          "model",
          "storage",
          "color",
          "price",
          "release_date"
        ]
      },
      "Error": {
        "type": "object",
        "properties": {
          "error": {
            "type": "string"
          }
        },
        "required": [
          "error"
        ]
      }
    }
  }
}
""".replace("CLOUD_RUN_AUTH_MCP_URL_PLACEHOLDER", CLOUD_RUN_AUTH_MCP_URL)

# --- Create OpenAPIToolset ---
products_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type='json',
    header_provider=create_header_provider(CLOUD_RUN_AUTH_MCP_URL)
)