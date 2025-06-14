#!/usr/bin/env python3
"""
Debug OpenAI Integration Script
This script helps you test what OpenAI returns for your images
and understand why the API might not be using OpenAI fallback.
"""

import os
import sys
import base64
import json
import requests
from pathlib import Path

def test_openai_direct(image_path: str):
    """Test OpenAI vision API directly"""
    print("🤖 Testing OpenAI Vision API directly...")
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Set it with: export OPENAI_API_KEY='your-key-here'")
        return None
    
    print(f"✅ OpenAI API key found ({len(api_key)} characters)")
    
    # Read and encode image
    try:
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
        
        b64_image = base64.b64encode(image_data).decode()
        print(f"📷 Image encoded: {len(b64_image)} characters")
        
        # Determine content type
        if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
            content_type = "image/jpeg"
        elif image_path.lower().endswith('.png'):
            content_type = "image/png"
        else:
            content_type = "image/jpeg"  # default
        
        print(f"📋 Content type: {content_type}")
        
    except Exception as e:
        print(f"❌ Error reading image: {e}")
        return None
    
    # Make OpenAI API request
    try:
        print("🔄 Making OpenAI API request...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Where was this photo taken? Reply with ONLY the city and country name, like 'Paris, France' or 'New York, USA'. If you cannot identify the location, reply with 'Unknown'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{b64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📡 OpenAI API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response
            message_content = result['choices'][0]['message']['content'].strip()
            usage = result.get('usage', {})
            
            print("✅ OpenAI Response:")
            print(f"   Location: '{message_content}'")
            print(f"   Tokens used: {usage.get('total_tokens', 'unknown')}")
            
            return message_content
            
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return None

def test_nominatim_geocoding(place_name: str):
    """Test geocoding the place name using Nominatim"""
    print(f"\n🌍 Testing geocoding for: '{place_name}'")
    
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": place_name,
                "format": "json",
                "limit": 1
            },
            headers={
                "User-Agent": "WhereIsThisPlace/1.0 (https://github.com/whereisthisplace)"
            },
            timeout=10
        )
        
        print(f"📡 Nominatim response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and data:
                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                display_name = result.get("display_name", "Unknown")
                
                print("✅ Geocoding result:")
                print(f"   Coordinates: ({lat:.6f}, {lon:.6f})")
                print(f"   Full name: {display_name}")
                
                return lat, lon
            else:
                print("❌ No geocoding results found")
                return None, None
        else:
            print(f"❌ Geocoding error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error geocoding: {e}")
        return None, None

def test_api_decision_logic(image_path: str, api_url: str = "http://localhost:8000"):
    """Test the API and understand why it made its decision"""
    print(f"\n🔍 Testing API decision logic...")
    print(f"API URL: {api_url}")
    
    try:
        # Test normal mode first
        print("\n1️⃣ Testing normal mode (no OpenAI)...")
        with open(image_path, 'rb') as img_file:
            files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
            response = requests.post(f"{api_url}/predict", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction', {})
            
            print("📊 Normal mode result:")
            print(f"   Source: {prediction.get('source')}")
            print(f"   Score: {prediction.get('score')}")
            print(f"   Confidence: {prediction.get('confidence_level')}")
            print(f"   Coordinates: ({prediction.get('lat')}, {prediction.get('lon')})")
            print(f"   Bias warning: {prediction.get('bias_warning')}")
            
            # Analyze why OpenAI wasn't used
            score = prediction.get('score', 0)
            bias_warning = prediction.get('bias_warning')
            
            print("\n🧠 Decision analysis:")
            if score >= 0.8:
                print(f"   ✅ High confidence ({score:.3f}) - OpenAI not needed")
            elif score >= 0.4:
                print(f"   ⚠️  Medium confidence ({score:.3f}) - might use OpenAI")
            else:
                print(f"   ❌ Low confidence ({score:.3f}) - should use OpenAI")
            
            if bias_warning:
                print(f"   ⚠️  Bias detected: {bias_warning}")
                print("   📝 This should trigger OpenAI fallback")
            else:
                print("   ✅ No bias detected")
        
        # Test OpenAI mode
        print("\n2️⃣ Testing OpenAI mode...")
        with open(image_path, 'rb') as img_file:
            files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
            data = {'mode': 'openai'}
            response = requests.post(f"{api_url}/predict", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction', {})
            
            print("📊 OpenAI mode result:")
            print(f"   Source: {prediction.get('source')}")
            print(f"   Score: {prediction.get('score')}")
            print(f"   Confidence: {prediction.get('confidence_level')}")
            print(f"   Coordinates: ({prediction.get('lat')}, {prediction.get('lon')})")
            print(f"   Original score: {prediction.get('original_score')}")
            
            if prediction.get('source') == 'openai':
                print("   🎯 SUCCESS: OpenAI was used!")
            else:
                print("   📝 Model was still used (high confidence)")
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def main():
    """Main debugging function"""
    print("🔧 OpenAI Integration Debugger")
    print("=" * 50)
    
    # Get image path from command line or use default
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "eiffel.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image file '{image_path}' not found")
        print("💡 Usage: python debug_openai.py [image_path]")
        return
    
    print(f"📷 Testing with image: {image_path}")
    
    # Test 1: Direct OpenAI API call
    openai_result = test_openai_direct(image_path)
    
    # Test 2: Geocoding if OpenAI worked
    if openai_result:
        test_nominatim_geocoding(openai_result)
    
    # Test 3: API decision logic
    test_api_decision_logic(image_path)
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("=" * 50)
    
    if openai_result:
        print(f"✅ OpenAI identified location as: '{openai_result}'")
        print("✅ OpenAI integration is working")
        print("📝 If API still uses model, it's because model confidence is high")
        print("💡 This is optimal behavior - saves API costs when model is confident")
    else:
        print("❌ OpenAI integration failed")
        print("🔧 Check your OPENAI_API_KEY environment variable")
    
    print("\n💡 To force OpenAI usage, try:")
    print("   • Images with unclear or ambiguous landmarks")
    print("   • Blurry or low-quality images")
    print("   • Images that might confuse the model")
    print("   • Lower the confidence threshold in the API code")

if __name__ == "__main__":
    main() 