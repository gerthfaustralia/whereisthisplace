#!/usr/bin/env python3
"""
Manual API Test Script for WhereIsThisPlace
Tests the new bias detection and enhanced API response structure
"""
import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://52.28.72.57"  # Your public IP
IMAGE_FILE = "eiffel.jpg"  # Test image

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ Health endpoint is working!")
        else:
            print(f"❌ Health endpoint failed: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        print("-" * 50)

def test_predict_endpoint(mode=None):
    """Test the predict endpoint with bias detection"""
    mode_str = f" (mode: {mode})" if mode else ""
    print(f"🔍 Testing Predict Endpoint{mode_str}...")
    
    # Check if image file exists
    if not Path(IMAGE_FILE).exists():
        print(f"❌ Image file '{IMAGE_FILE}' not found!")
        return
    
    try:
        # Prepare the request
        with open(IMAGE_FILE, 'rb') as img_file:
            files = {'photo': (IMAGE_FILE, img_file, 'image/jpeg')}
            data = {}
            if mode:
                data['mode'] = mode
            
            response = requests.post(
                f"{BASE_URL}/predict", 
                files=files, 
                data=data,
                timeout=30
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prediction successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Analyze the enhanced response
            prediction = data.get('prediction', {})
            print("\n📊 Response Analysis:")
            print(f"  • Coordinates: ({prediction.get('lat')}, {prediction.get('lon')})")
            print(f"  • Score: {prediction.get('score')}")
            print(f"  • Confidence Level: {prediction.get('confidence_level')}")
            print(f"  • Source: {prediction.get('source', 'model')}")
            print(f"  • Bias Warning: {prediction.get('bias_warning', 'None')}")
            
            if prediction.get('original_score'):
                print(f"  • Original Score: {prediction.get('original_score')}")
            
            # Check if bias detection worked for Eiffel Tower
            if 'eiffel' in IMAGE_FILE.lower() and prediction.get('bias_warning'):
                print("🎯 Bias detection is working! European landmark detected.")
            
        else:
            print(f"❌ Prediction failed: {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Prediction error: {e}")
    
    print("-" * 50)

def test_rate_limiting():
    """Test rate limiting by making multiple requests"""
    print("🔍 Testing Rate Limiting...")
    try:
        for i in range(12):  # Should hit rate limit around 10
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print("✅ Rate limiting is working!")
                break
        else:
            print("⚠️  Rate limiting might not be active or limit is higher")
    except Exception as e:
        print(f"❌ Rate limiting test error: {e}")
    print("-" * 50)

def main():
    """Run all manual tests"""
    print("🚀 Starting Manual API Tests")
    print(f"Target: {BASE_URL}")
    print(f"Image: {IMAGE_FILE}")
    print("=" * 50)
    
    # Test 1: Health endpoint
    test_health_endpoint()
    
    # Test 2: Basic prediction (should trigger bias detection for eiffel.jpg)
    test_predict_endpoint()
    
    # Test 3: OpenAI mode prediction (if API key is configured)
    test_predict_endpoint(mode="openai")
    
    # Test 4: Rate limiting
    test_rate_limiting()
    
    print("🏁 Manual tests completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = f"http://{sys.argv[1]}"
        print(f"Using custom URL: {BASE_URL}")
    
    main() 