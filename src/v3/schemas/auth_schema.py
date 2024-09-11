from pydantic import BaseModel

class AuthSchema(BaseModel):
    password: str