from fastapi import APIRouter, Depends, status
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token, get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate):
    user = await AuthService.create_user(user_in)
    
    # Generate JWT
    access_token = create_access_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin):
    user = await AuthService.authenticate_user(user_in)
    
    # Generate JWT
    access_token = create_access_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email
    )
