import os
import json
import uuid
from typing import List, Optional, Dict, Any
from app.models import Customer, CustomerCreate

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

def get_all_customers() -> List[Customer]:
    data = load_db()
    return [Customer(**item) for item in data]

def get_customer_by_id(customer_id: str) -> Optional[Customer]:
    customers = get_all_customers()
    for customer in customers:
        if customer.id == customer_id:
            return customer
    return None

def add_customer(customer_create: CustomerCreate) -> Customer:
    customers = load_db()
    new_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
    new_customer = Customer(id=new_id, **customer_create.model_dump())
    customers.append(new_customer.model_dump())
    save_db(customers)
    return new_customer
