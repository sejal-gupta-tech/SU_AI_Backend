import sys
import os
import asyncio
import getpass

# Add backend root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import connect_to_mongo, get_database, close_mongo_connection
from app.core.security import get_password_hash
from app.models.user import User

async def create_admin():
    print("=== Create Admin Account ===")
    email = input("Enter admin email: ").strip()
    if not email:
        print("Email is required.")
        return

    password = getpass.getpass("Enter admin password: ")
    confirm_password = getpass.getpass("Confirm admin password: ")

    if password != confirm_password:
        print("Passwords do not match. Aborting.")
        return
        
    if not password:
        print("Password cannot be empty. Aborting.")
        return

    print("Connecting to database...")
    connect_to_mongo()
    db = get_database()
    users_collection = db["users"]

    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        print(f"User with email {email} already exists. Updating role to admin...")
        await users_collection.update_one(
            {"email": email},
            {"$set": {"role": "admin"}}
        )
        print("Admin privileges granted successfully.")
    else:
        print(f"Creating new admin user: {email}")
        hashed_password = get_password_hash(password)
        user = User(
            name="Admin",
            email=email,
            hashed_password=hashed_password,
            role="admin"
        )
        doc = user.model_dump(by_alias=True, exclude={"id"})
        await users_collection.insert_one(doc)
        print("Admin user created successfully.")

    close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_admin())
