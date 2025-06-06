#!/usr/bin/env python3

"""
Test OpenAI API Key Functionality
This script tests if the OpenAI API key works directly before testing the API integration.
"""

import os
import sys
import base64
import requests
import json
from pathlib import Path

def test_openai_key():
    """Test if OpenAI API key works directly"""
    
    print("🔑 Testing OpenAI API Key")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-8:]} ({len(api_key)} chars)")
    
    # Check base URL
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    print(f"🌐 Using base URL: {base_url}")
    
    # Test with a simple text completion first
    print("\n🧪 Testing OpenAI API with simple text request...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Simple text test
    text_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say 'Hello World' and nothing else."}
        ],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=text_payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ Text API works! Response: '{message.strip()}'")
            text_api_works = True
        else:
            print(f"❌ Text API failed: {response.text}")
            text_api_works = False
            
    except Exception as e:
        print(f"❌ Text API error: {e}")
        text_api_works = False
    
    # Test with vision API (what the WhereIsThisPlace API uses)
    print("\n🖼️  Testing OpenAI Vision API...")
    
    # Check if we have a test image
    image_path = "eiffel.jpg"
    if not os.path.exists(image_path):
        print(f"⚠️  Test image '{image_path}' not found")
        print("💡 Using a simple text-based location question instead")
        
        vision_payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user", 
                    "content": "What are the GPS coordinates of the Eiffel Tower in Paris? Respond with just the latitude and longitude numbers."
                }
            ],
            "max_tokens": 50
        }
    else:
        print(f"📸 Using test image: {image_path}")
        
        # Encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        vision_payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What location is shown in this image? Provide GPS coordinates if possible."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 100
        }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=vision_payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ Vision API works! Response:")
            print(f"   {message.strip()}")
            vision_api_works = True
        else:
            print(f"❌ Vision API failed: {response.text}")
            vision_api_works = False
            
    except Exception as e:
        print(f"❌ Vision API error: {e}")
        vision_api_works = False
    
    # Summary
    print("\n📊 OpenAI API Test Summary:")
    print("=" * 30)
    print(f"Text API: {'✅ Working' if text_api_works else '❌ Failed'}")
    print(f"Vision API: {'✅ Working' if vision_api_works else '❌ Failed'}")
    
    if text_api_works and vision_api_works:
        print("\n🎉 OpenAI API key is working correctly!")
        print("💡 If your WhereIsThisPlace API isn't using OpenAI, it's likely because:")
        print("   • Model confidence is too high (> threshold)")
        print("   • OpenAI fallback logic needs adjustment")
        print("   • API server doesn't have the OpenAI key configured")
        return True
    else:
        print("\n❌ OpenAI API key has issues")
        print("🔧 Check:")
        print("   • API key is valid and not expired")
        print("   • Account has sufficient credits")
        print("   • Network connectivity")
        return False

if __name__ == "__main__":
    test_openai_key() 