from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_database

def run_tests():
    with TestClient(app) as client:
        # Test 1: New user signup
        signup_data = {
            "name": "Test User",
            "email": "testcredit3@example.com",
            "password": "Password123"
        }
        res = client.post("/api/v1/auth/signup", json=signup_data)
        assert res.status_code in [200, 201], f"Signup failed: {res.text}"
        
        login_data = {
            "email": "testcredit3@example.com",
            "password": "Password123"
        }
        res = client.post("/api/v1/auth/login", json=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 2: Credit balance
        res = client.get("/api/v1/credits/me", headers=headers)
        assert res.status_code == 200
        balance = res.json()
        assert balance["plan"] == "FREE"
        assert balance["credits_total"] == 5
        assert balance["credits_remaining"] == 5
        print("PASS: New user signup -> 5 free credits")
        
        # Test 3: Get subscription
        res = client.get("/api/v1/subscription/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["plan"] == "FREE"
        print("PASS: Subscription API")
        
        # We need a business and product to test generation
        # Let's bypass full endpoints and just use CreditService directly to test atomic deductions
        db = get_database()
        user_id = res.json()["user_id"]
        from app.services.credit_service import CreditService
        import asyncio
        
        loop = asyncio.get_event_loop()
        
        # Test 4: Deduct for Post
        loop.run_until_complete(CreditService.deduct_credits(db, user_id, "post_generation")) # -1
        history = loop.run_until_complete(CreditService.get_history(db, user_id))
        assert len(history) == 1
        assert history[0]["balance_after"] == 4
        print("PASS: Post credit deduction")
        
        # Test 5: Deduct for Photoshoot
        loop.run_until_complete(CreditService.deduct_credits(db, user_id, "photoshoot")) # -2
        history = loop.run_until_complete(CreditService.get_history(db, user_id))
        assert len(history) == 2
        assert history[0]["balance_after"] == 2
        print("PASS: Photoshoot credit deduction")
        
        # Test 6: Insufficient balance
        try:
            loop.run_until_complete(CreditService.deduct_credits(db, user_id, "reel_generation")) # Needs 3, has 2
            assert False, "Should have raised 402"
        except Exception as e:
            assert "Insufficient credits" in str(e) or getattr(e, "status_code", 0) == 402
            print("PASS: Insufficient credits rejected")
            
        # Check history to ensure no negative transaction
        history = loop.run_until_complete(CreditService.get_history(db, user_id))
        assert len(history) == 2
        assert history[0]["balance_after"] == 2
        print("PASS: No negative balance")
        
        # Test 7: Refund
        loop.run_until_complete(CreditService.refund_credits(db, user_id, "reel_generation")) # +3
        history = loop.run_until_complete(CreditService.get_history(db, user_id))
        assert history[0]["balance_after"] == 5
        print("PASS: Refund failed job")

if __name__ == "__main__":
    run_tests()
