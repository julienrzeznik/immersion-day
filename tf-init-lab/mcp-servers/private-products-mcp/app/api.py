from starlette.requests import Request
from starlette.responses import JSONResponse
from app.server_init import mcp
from app import database
from app.models import ProductCreate

@mcp.custom_route("/api/products", methods=["GET"])
async def rest_list_products(request: Request):
    """REST endpoint to list all products."""
    products = database.get_all_products()
    return JSONResponse([p.model_dump() for p in products])

@mcp.custom_route("/api/products/{product_id}", methods=["GET"])
async def rest_get_product(request: Request):
    """REST endpoint to get a specific product."""
    product_id = request.path_params["product_id"]
    product = database.get_product_by_id(product_id)
    if product:
        return JSONResponse(product.model_dump())
    return JSONResponse({"error": "Product not found"}, status_code=404)

@mcp.custom_route("/api/products", methods=["POST"])
async def rest_register_product(request: Request):
    """REST endpoint to register a new product."""
    try:
        body = await request.json()
        product_create = ProductCreate(**body)
        new_product = database.add_product(product_create)
        return JSONResponse(new_product.model_dump(), status_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@mcp.custom_route("/api/health", methods=["GET"])
async def health_check(request: Request):
    """Simple health check endpoint."""
    return JSONResponse({"status": "ok", "service": "products-mcp"})
