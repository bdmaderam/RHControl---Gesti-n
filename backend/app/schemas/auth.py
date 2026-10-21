from pydantic import BaseModel, Field
class LoginRequest(BaseModel):
    usuario: str = Field(min_length=1)
    contraseña: str = Field(min_length=1)
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: str
    nombre: str
