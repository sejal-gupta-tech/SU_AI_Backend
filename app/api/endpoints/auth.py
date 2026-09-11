from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from datetime import timedelta

from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.database import get_database

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
async def register(data: dict, db=Depends(get_database)):
    # Basic mock registration
    existing_user = await db["users"].find_one({"email": data.get("email")})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(data.get("password", "password"))
    user = {
        "name": data.get("name", "Test User"),
        "email": data.get("email"),
        "hashed_password": hashed_password
    }
    result = await db["users"].insert_one(user)
    user_id = str(result.inserted_id)
    
    # Auto-create a business for this user
    business = {
        "owner_id": user_id,
        "name": f"{user['name']}'s Business",
        "category": "Retail",
        "target_customer": "Everyone"
    }
    await db["businesses"].insert_one(business)
    
    return {"success": True, "message": "User registered successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_database)):
    # Find user
    user = await db["users"].find_one({"email": form_data.username})
    
    # If no user exists yet in the whole database (first run), let's auto-create one for testing
    if not user:
        if await db["users"].count_documents({}) == 0:
            hashed_password = get_password_hash(form_data.password)
            user = {
                "name": "Test User",
                "email": form_data.username,
                "hashed_password": hashed_password
            }
            result = await db["users"].insert_one(user)
            user["_id"] = result.inserted_id
            
            business = {
                "owner_id": str(user["_id"]),
                "name": "Test Business",
                "category": "Retail"
            }
            await db["businesses"].insert_one(business)
        else:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
    else:
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
            
    access_token = create_access_token(subject=str(user["_id"]))
    
    return {"access_token": access_token, "token_type": "bearer"}
