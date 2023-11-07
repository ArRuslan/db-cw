from pydantic import BaseModel


class CustomerModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: int
