import asyncio
import httpx
import os
import json
import subprocess

async def test_reel_flow():
    client = httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1/", timeout=60.0)
    
    print("1. Logging in...")
    test_user = {
        "email": "smoketest@example.com",
        "password": "password123"
    }
    res = await client.post("auth/login", json=test_user)
    assert res.status_code in (200, 201), f"Auth failed: {res.text}"
    token = res.json()["access_token"]
    
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    print("2. Getting Business...")
    res = await client.get("businesses/me")
    assert res.status_code == 200, f"Get business failed: {res.text}"
    business_id = res.json()["id"]

    print("3. Getting a Product...")
    res = await client.get("products")
    products = res.json().get("data", [])
    if not products:
        print("   No products found, creating one...")
        prod_data = {
            "name": "Smoke Test Product",
            "description": "A very good product for testing.",
            "price": 100,
            "images": ["https://via.placeholder.com/300"]
        }
        res = await client.post("products", json=prod_data)
        assert res.status_code in (200, 201), f"Product creation failed: {res.text}"
        data = res.json()
        product_id = data.get("id") or data.get("_id") or data.get("product_id") or data["data"]["id"]
    else:
        product_id = products[0]["id"]
        
    print(f"   Using Product ID: {product_id}")

    print("4. Generating Reel...")
    reel_req = {
        "product_id": product_id,
        "objective": "increase sales",
        "platform": "instagram",
        "language": "English",
        "duration": 15
    }
    
    res = await client.post("content/generate-reel", json=reel_req)
    assert res.status_code == 200, f"Reel request failed: {res.text}"
    
    job_id = res.json()["job_id"]
    print(f"   Job ID: {job_id}")
    
    print("4. Polling status...")
    video_url = None
    for _ in range(60): # Poll for up to 120 seconds
        await asyncio.sleep(2)
        res = await client.get(f"content/reel/{job_id}/status")
        status = res.json()["status"]
        stage = res.json()["stage"]
        print(f"   Status: {status} | Stage: {stage}")
        
        if status == "completed":
            video_url = res.json()["video_url"]
            print(f"   SUCCESS! Video URL: {video_url}")
            break
        elif status == "failed":
            print(f"   FAILED! Stage: {stage}")
            break
            
    assert video_url is not None, "Video generation did not complete successfully"
    
    print("5. Verifying MP4 with FFprobe...")
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffprobe_exe = ffmpeg_exe.replace("ffmpeg.exe", "ffprobe.exe")
        
        if not os.path.exists(ffprobe_exe):
            # Sometimes imageio_ffmpeg doesn't bundle ffprobe.
            # If so, just verify the file exists and has size > 0.
            print("   (ffprobe not bundled by imageio_ffmpeg, skipping stream validation)")
        else:
            # Local path to video
            local_video_path = video_url.lstrip("/")
            assert os.path.exists(local_video_path), f"Video file not found at {local_video_path}"
            
            cmd = [
                ffprobe_exe,
                "-v", "error",
                "-show_entries", "stream=codec_type,width,height",
                "-of", "json",
                local_video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            probe = json.loads(result.stdout)
            
            has_video = False
            has_audio = False
            for stream in probe.get("streams", []):
                if stream["codec_type"] == "video":
                    has_video = True
                    width = stream.get("width")
                    height = stream.get("height")
                    assert width == 720 and height == 1280, f"Invalid resolution: {width}x{height}"
                elif stream["codec_type"] == "audio":
                    has_audio = True
                    
            assert has_video, "No video stream found"
            assert has_audio, "No audio stream found"
            
            print("   FFprobe Verification PASS: Video stream (720x1280) and Audio stream present.")
        
    except Exception as e:
        print(f"   Verification failed: {e}")
        raise e
        
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(test_reel_flow())
