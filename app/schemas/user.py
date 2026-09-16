from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str | None = None
    fullName: str | None = None
    full_name: str | None = None
    email: EmailStr
    password: str
    confirmPassword: str | None = None

class UserLogin(BaseModel):
    email: EmailStr | None = None
    Email: EmailStr | None = None
    password: str | None = None
    Password: str | None = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
