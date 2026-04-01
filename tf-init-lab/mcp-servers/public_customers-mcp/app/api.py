from starlette.requests import Request
from starlette.responses import JSONResponse
from app.server_init import mcp
from app import database
from app.models import CustomerCreate

@mcp.custom_route("/api/customers", methods=["GET"])
async def rest_list_customers(request: Request):
    """REST endpoint to list all customers."""
    customers = database.get_all_customers()
    return JSONResponse([c.model_dump() for c in customers])

@mcp.custom_route("/api/customers/{customer_id}", methods=["GET"])
async def rest_get_customer(request: Request):
    """REST endpoint to get a specific customer."""
    customer_id = request.path_params["customer_id"]
    customer = database.get_customer_by_id(customer_id)
    if customer:
        return JSONResponse(customer.model_dump())
    return JSONResponse({"error": "Customer not found"}, status_code=404)

@mcp.custom_route("/api/customers", methods=["POST"])
async def rest_register_customer(request: Request):
    """REST endpoint to register a new customer."""
    try:
        body = await request.json()
        customer_create = CustomerCreate(**body)
        new_customer = database.add_customer(customer_create)
        return JSONResponse(new_customer.model_dump(), status_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@mcp.custom_route("/api/health", methods=["GET"])
async def health_check(request: Request):
    """Simple health check endpoint."""
    return JSONResponse({"status": "ok", "service": "customers-mcp"})
