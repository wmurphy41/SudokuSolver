#!/usr/bin/env python3
"""
Test script for the session creation endpoint.
Run this to diagnose Redis connection issues.
"""

import requests
import json
import sys

# Test data
test_grid = [
    [5, 0, 0, 4, 3, 0, 1, 0, 0],
    [0, 0, 3, 1, 5, 0, 0, 4, 8],
    [1, 0, 0, 0, 2, 0, 0, 7, 0],
    [7, 0, 0, 6, 0, 0, 5, 1, 0],
    [0, 4, 0, 0, 0, 5, 7, 2, 9],
    [0, 5, 1, 9, 0, 4, 0, 0, 0],
    [6, 2, 0, 7, 0, 8, 0, 0, 1],
    [3, 9, 8, 0, 0, 0, 0, 0, 7],
    [0, 0, 7, 5, 0, 0, 9, 0, 2]
]

def test_redis_connection():
    """Test Redis connection directly."""
    print("=" * 60)
    print("Step 1: Testing Redis connection directly...")
    print("=" * 60)
    try:
        import redis
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        result = r.ping()
        print(f"✅ Redis ping successful: {result}")
        
        # Test write/read
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print(f"✅ Test write/read successful: {value}")
        r.delete("test_key")
        print("✅ Redis connection is working!\n")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {type(e).__name__}: {e}\n")
        return False

def test_backend_health():
    """Test backend health endpoint."""
    print("=" * 60)
    print("Step 2: Testing backend health endpoint...")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:8000/api/healthz", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is running: {response.json()}\n")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}: {response.text}\n")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible on http://localhost:8000")
        print("   Make sure the backend server is started with:")
        print("   python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000\n")
        return False
    except Exception as e:
        print(f"❌ Error checking backend health: {type(e).__name__}: {e}\n")
        return False

def test_session_endpoint():
    """Test session creation endpoint."""
    print("=" * 60)
    print("Step 3: Testing session creation endpoint...")
    print("=" * 60)
    
    data = {
        "grid": test_grid,
        "debug_level": 0
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/sessions",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Session created successfully!")
            print(f"   Session ID: {result.get('session_id', 'N/A')}\n")
            return True
        else:
            print(f"❌ Session creation failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}\n")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 10 seconds")
        print("   This suggests Redis might be slow or unreachable\n")
        return False
    except Exception as e:
        print(f"❌ Error testing session endpoint: {type(e).__name__}: {e}\n")
        return False

if __name__ == "__main__":
    print("\n🔍 Diagnosing Session Endpoint Issues\n")
    
    redis_ok = test_redis_connection()
    backend_ok = test_backend_health()
    
    if redis_ok and backend_ok:
        session_ok = test_session_endpoint()
        if session_ok:
            print("=" * 60)
            print("✅ All tests passed! Session endpoint is working.")
            print("=" * 60)
            sys.exit(0)
        else:
            print("=" * 60)
            print("❌ Session endpoint test failed. Check error details above.")
            print("=" * 60)
            sys.exit(1)
    else:
        print("=" * 60)
        print("❌ Prerequisites failed. Fix Redis or backend issues first.")
        print("=" * 60)
        sys.exit(1)

