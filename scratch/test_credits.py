import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test():
    # Login
    response = client.post("/api/v1/auth/token", data={"username": "sejal", "password": "password"})
    if response.status_code != 200:
        print("Login failed:", response.text)
        return
    token = response.json()["access_token"]
    
    # Test credits
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/credits/me", headers=headers)
    print("ME status:", res.status_code)
    print("ME response:", res.text)
    
    res = client.get("/api/v1/credits/history", headers=headers)
    print("HISTORY status:", res.status_code)
    print("HISTORY response:", res.text)

if __name__ == "__main__":
    test()
