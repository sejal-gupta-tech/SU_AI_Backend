from fastapi import HTTPException, status
from app.core.database import get_database
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password

class AuthService:
    @staticmethod
    async def get_collection():
        db = get_database()
        return db["users"]

    @staticmethod
    async def get_user_by_email(email: str) -> User | None:
        collection = await AuthService.get_collection()
        doc = await collection.find_one({"email": email})
        if doc:
            return User(**doc)
        return None

    @staticmethod
    async def create_user(user_in: UserCreate) -> User:
        existing_user = await AuthService.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists."
            )

        hashed_password = get_password_hash(user_in.password)
        collection = await AuthService.get_collection()
        
        user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password
        )
        
        doc = user.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    @staticmethod
    async def authenticate_user(user_login: UserLogin) -> User:
        user = await AuthService.get_user_by_email(user_login.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        
        if not verify_password(user_login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
            
        return user
