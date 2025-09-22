#!/usr/bin/env python3

import requests
import os
import sys

def test_api():
    # Test health endpoint
    try:
        print("🩺 Testing health endpoint...")
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test debug endpoint
    try:
        print("\n🔍 Testing debug endpoint...")
        response = requests.get('http://localhost:5000/api/face/debug', timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"FAISS: {result.get('faiss_index', 'unknown')}")
        print(f"Labels: {result.get('labels', 'unknown')}")
        print(f"Persons: {result.get('registered_persons', 0)}")
        print("✅ Debug check passed")
    except Exception as e:
        print(f"❌ Debug check failed: {e}")
        return False

    # Test with real image
    try:
        print("\n🤖 Testing recognition with real image...")
        dataset_dir = r"f:\face-recognition\dataset"
        image_files = [f for f in os.listdir(dataset_dir) if f.endswith('.jpg')]

        if not image_files:
            print("❌ No images found in dataset")
            return False

        image_path = os.path.join(dataset_dir, image_files[0])
        print(f"📁 Using image: {image_files[0]}")

        with open(image_path, 'rb') as f:
            files = {'image': (image_files[0], f, 'image/jpeg')}
            response = requests.post('http://localhost:5000/api/face/recognize', files=files, timeout=10)

        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Result: {result}")

        if result.get('status') == 'success':
            print("✅ Recognition API working!")
            print(f"👤 Detected: {result.get('name', 'Unknown')}")
            print(f"📊 Distance: {result.get('distance', 'N/A')}")
        else:
            print("❌ Recognition API failed")
            return False

    except Exception as e:
        print(f"❌ Recognition test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 Starting API Test...")
    success = test_api()
    print(f"\n{'✅ ALL TESTS PASSED!' if success else '❌ SOME TESTS FAILED!'}")
    sys.exit(0 if success else 1)
