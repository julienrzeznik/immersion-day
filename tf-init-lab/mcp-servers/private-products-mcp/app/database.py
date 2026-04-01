import os
import json
import uuid
from typing import List, Optional, Dict, Any
from app.models import Product, ProductCreate

DB_FILE = os.path.join(os.path.dirname(__file__), "db.json")

def load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_db(data: List[Dict[str, Any]]):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_products() -> List[Product]:
    data = load_db()
    return [Product(**item) for item in data]

def get_product_by_id(product_id: str) -> Optional[Product]:
    products = get_all_products()
    for product in products:
        if product.id == product_id:
            return product
    return None

def add_product(product_create: ProductCreate) -> Product:
    products = load_db()
    new_id = f"PROD-{uuid.uuid4().hex[:8].upper()}"
    new_product = Product(id=new_id, **product_create.model_dump())
    products.append(new_product.model_dump())
    save_db(products)
    return new_product
