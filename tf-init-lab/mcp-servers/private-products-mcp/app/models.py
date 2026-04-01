from pydantic import BaseModel

class Product(BaseModel):
    id: str
    brand: str
    model: str
    storage: str
    color: str
    price: float
    release_date: str

class ProductCreate(BaseModel):
    brand: str
    model: str
    storage: str
    color: str
    price: float
    release_date: str
