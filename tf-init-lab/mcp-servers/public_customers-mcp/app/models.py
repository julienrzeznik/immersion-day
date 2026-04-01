from pydantic import BaseModel

class Customer(BaseModel):
    id: str
    first_name: str
    last_name: str
    city: str

class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    city: str
