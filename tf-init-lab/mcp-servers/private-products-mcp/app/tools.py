from typing import List, Dict, Any, Optional
from app.server_init import mcp
from app import database

@mcp.tool
def list_products() -> List[Dict[str, Any]]:
    """Lists all products.
    
    Returns:
        A list of product objects.
    """
    return [product.model_dump() for product in database.get_all_products()]

@mcp.tool
def get_product(product_id: str) -> Optional[Dict[str, Any]]:
    """Gets detailed information about a particular product.
    
    Args:
        product_id: The unique identifier (e.g., 'PROD-001').
        
    Returns:
        The product object if found, or None.
    """
    product = database.get_product_by_id(product_id)
    if product:
        return product.model_dump()
    return None

@mcp.tool
def register_product(
    brand: str,
    model: str,
    storage: str,
    color: str,
    price: float,
    release_date: str
) -> Dict[str, Any]:
    """Registers a new product.
    
    Args:
        brand: The brand of the product (e.g., 'TechCo').
        model: The model name (e.g., 'UltraBook').
        storage: Storage capacity (e.g., '512GB').
        color: Color of the product.
        price: Price in USD.
        release_date: Release date (YYYY-MM-DD).
        
    Returns:
        The newly created product object.
    """
    from app.models import ProductCreate
    product_create = ProductCreate(
        brand=brand,
        model=model,
        storage=storage,
        color=color,
        price=price,
        release_date=release_date
    )
    new_product = database.add_product(product_create)
    return new_product.model_dump()
