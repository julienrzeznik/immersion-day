from typing import List, Dict, Any, Optional
from app.server_init import mcp
from app import database

@mcp.tool
def list_customers() -> List[Dict[str, Any]]:
    """Lists all customers.
    
    Returns:
        A list of customer objects.
    """
    return [customer.model_dump() for customer in database.get_all_customers()]

@mcp.tool
def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """Gets detailed information about a particular customer.
    
    Args:
        customer_id: The unique identifier (e.g., 'CUST-001').
        
    Returns:
        The customer object if found, or None.
    """
    customer = database.get_customer_by_id(customer_id)
    if customer:
        return customer.model_dump()
    return None

@mcp.tool
def register_customer(
    first_name: str,
    last_name: str,
    city: str
) -> Dict[str, Any]:
    """Registers a new customer.
    
    Args:
        first_name: The first name of the customer.
        last_name: The last name of the customer.
        city: The city where the customer resides.
        
    Returns:
        The newly created customer object.
    """
    from app.models import CustomerCreate
    customer_create = CustomerCreate(
        first_name=first_name,
        last_name=last_name,
        city=city
    )
    new_customer = database.add_customer(customer_create)
    return new_customer.model_dump()
