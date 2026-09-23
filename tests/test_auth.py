import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_database
from app.core.security import get_password_hash
from unittest.mock import patch
import random
import string

pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
def mock_email_service():
    with patch("app.services.email_service.EmailService.send_otp_email") as mock_send:
        yield mock_send

@pytest.fixture(autouse=True)
async def setup_db():
    from app.core.database import connect_to_mongo, close_mongo_connection
    connect_to_mongo()
    db = get_database()
    # DO NOT DELETE USERS IN TEARDOWN/SETUP
    
    # Ensure admin user exists for tests
    admin_user = await db["users"].find_one({"email": "admin@example.com"})
    if not admin_user:
        admin_data = {
            "name": "Admin",
            "email": "admin@example.com",
            "hashed_password": get_password_hash("Admin@123"),
            "role": "admin",
            "email_verified": True
        }
        await db["users"].insert_one(admin_data)
        
    yield
    close_mongo_connection()

async def test_user_signup_and_otp():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # A. User signup
        response = await ac.post("/api/v1/auth/signup", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123"
        })
        assert response.status_code == 201
        data = response.json()
        assert "detail" in data
        
        # Verify NO user exists in active users collection yet
        db = get_database()
        active_user = await db["users"].find_one({"email": "test@example.com"})
        assert active_user is None
        
        # J. Unverified user login -> rejected (401 because user doesn't exist yet)
        login_response = await ac.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Password@123"
        })
        assert login_response.status_code == 401
        
        # Verify OTP
        db = get_database()
        otp_doc = await db["otps"].find_one({"email": "test@example.com"})
        assert otp_doc is not None
        
        # Let's override the OTP for testing
        test_otp = "123456"
        await db["otps"].update_one(
            {"email": "test@example.com"},
            {"$set": {"otp_hash": get_password_hash(test_otp)}}
        )
        
        # E. OTP success
        verify_response = await ac.post("/api/v1/auth/verify-otp", json={
            "email": "test@example.com",
            "otp": test_otp
        })
        assert verify_response.status_code == 200
        assert "access_token" in verify_response.json()
        
        # I. Verified user login -> succeeds
        login_response_2 = await ac.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Password@123"
        })
        assert login_response_2.status_code == 200
        assert login_response_2.json()["user"]["email_verified"] is True
        token = login_response_2.json()["access_token"]
        
        # L. User attempting admin endpoint -> 403
        admin_res = await ac.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert admin_res.status_code == 403
        
        # M. /auth/me returns correct role
        me_res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["role"] == "user"
        assert me_res.json()["email_verified"] is True

async def test_weak_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/signup", json={
            "name": "Weak Pass",
            "email": "weak@example.com",
            "password": "weak",
            "confirmPassword": "weak"
        })
        assert response.status_code == 422

async def test_invalid_email():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/signup", json={
            "name": "Invalid Email",
            "email": "invalid-email",
            "password": "Password@123",
            "confirmPassword": "Password@123"
        })
        assert response.status_code == 422

async def test_duplicate_email():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First create an active user directly
        db = get_database()
        await db["users"].insert_one({
            "name": "User 1",
            "email": "dup@example.com",
            "hashed_password": "123",
            "role": "user",
            "email_verified": True
        })
        
        response = await ac.post("/api/v1/auth/signup", json={
            "name": "User 2",
            "email": "dup@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123"
        })
        assert response.status_code == 409

async def test_otp_failure_and_resend():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/api/v1/auth/signup", json={
            "name": "OTP Test",
            "email": "otp@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123"
        })
        
        # F. Wrong OTP
        res = await ac.post("/api/v1/auth/verify-otp", json={
            "email": "otp@example.com",
            "otp": "000000"
        })
        assert res.status_code == 400
        
        # H. Resend cooldown
        resend_res = await ac.post("/api/v1/auth/resend-otp", json={
            "email": "otp@example.com"
        })
        assert resend_res.status_code == 429 # Too many requests due to cooldown

async def test_admin_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@example.com",
            "password": "Admin@123"
        })
        assert login_res.status_code == 200
        assert login_res.json()["user"]["role"] == "admin"
        token = login_res.json()["access_token"]
        
        admin_dash = await ac.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert admin_dash.status_code == 200

async def test_smtp_failure(mock_email_service):
    from fastapi import HTTPException
    mock_email_service.side_effect = HTTPException(status_code=500, detail="SMTP Failed")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/signup", json={
            "name": "SMTP Fail",
            "email": "smtpfail@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123"
        })
        assert response.status_code == 500
        
        db = get_database()
        # Ensure no active user
        user = await db["users"].find_one({"email": "smtpfail@example.com"})
        assert user is None
        
        # Ensure no pending record because SMTP failed before saving
        pending = await db["otps"].find_one({"email": "smtpfail@example.com"})
        assert pending is None
