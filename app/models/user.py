from pydantic import EmailStr
from app.models.base import MongoBaseModel


class User(MongoBaseModel):
    name: str
    email: EmailStr
    hashed_password: str
