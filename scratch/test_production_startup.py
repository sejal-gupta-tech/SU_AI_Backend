import os
import subprocess
import httpx
import time

def test_startup():
    # Set environment variables for production test
    env = os.environ.copy()
    env["ENVIRONMENT"] = "production"
    env["JWT_SECRET_KEY"] = "your-super-secret-key-here"
    # Don't set a valid JWT_SECRET_KEY, it should fail
    
    print("Testing startup without JWT_SECRET_KEY...")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    process.poll()
    if process.returncode is None:
        process.kill()
        print("FAIL: Server started successfully without JWT_SECRET_KEY in production!")
    else:
        out, err = process.communicate()
        if b"JWT_SECRET_KEY must be set" in err or b"JWT_SECRET_KEY must be set" in out:
            print("PASS: Server failed to start without JWT_SECRET_KEY.")
        else:
            print("FAIL: Server failed but not for the expected reason.")
            print(err.decode())

    # Now test with JWT_SECRET_KEY
    env["JWT_SECRET_KEY"] = "real-production-secret-12345"
    env["CORS_ORIGINS"] = "https://frontend.com"
    env["MONGO_URI"] = "mongodb://localhost:27017"
    
    print("Testing startup WITH JWT_SECRET_KEY...")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    process.poll()
    if process.returncode is None:
        print("PASS: Server started successfully with proper env vars.")
        
        # Test Health endpoint
        try:
            import httpx
            res = httpx.get("http://127.0.0.1:8001/")
            if res.status_code == 200:
                print("PASS: Health endpoint is reachable.")
            else:
                print(f"FAIL: Health endpoint returned {res.status_code}")
                
            # Test CORS headers (Optionally, send Origin header)
            res = httpx.options("http://127.0.0.1:8001/api/v1/auth/login", headers={"Origin": "https://frontend.com", "Access-Control-Request-Method": "POST"})
            if "https://frontend.com" in res.headers.get("access-control-allow-origin", ""):
                print("PASS: CORS is correctly configured.")
            else:
                print("FAIL: CORS did not return expected allow-origin.")
                print(res.headers)
                
            # Test invalid CORS
            res = httpx.options("http://127.0.0.1:8001/api/v1/auth/login", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "POST"})
            if "https://evil.com" not in res.headers.get("access-control-allow-origin", ""):
                print("PASS: CORS rejected invalid origin.")
            else:
                print("FAIL: CORS allowed invalid origin.")
                
        except Exception as e:
            print(f"FAIL: Exception making request: {e}")
            
        process.kill()
    else:
        out, err = process.communicate()
        print("FAIL: Server failed to start with proper env vars.")
        print(err.decode())

if __name__ == "__main__":
    test_startup()
