#!/usr/bin/env python3
"""
Force OpenAI Test Script
This script temporarily modifies the API to force OpenAI usage for testing.
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_with_forced_openai(image_path: str, api_url: str = "http://localhost:8000"):
    """Test API with different scenarios to force OpenAI usage"""
    
    print("🔧 Force OpenAI Testing")
    print("=" * 40)
    print(f"Image: {image_path}")
    print(f"API: {api_url}")
    print()
    
    if not os.path.exists(image_path):
        print(f"❌ Image file '{image_path}' not found")
        return
    
    # Test 1: Normal request to see baseline
    print("1️⃣ Baseline test (normal mode)...")
    try:
        with open(image_path, 'rb') as img_file:
            files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
            response = requests.post(f"{api_url}/predict", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction', {})
            print(f"   Source: {prediction.get('source')}")
            print(f"   Score: {prediction.get('score'):.4f}")
            print(f"   Confidence: {prediction.get('confidence_level')}")
            baseline_score = prediction.get('score', 0)
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print()
    
    # Test 2: OpenAI mode request
    print("2️⃣ OpenAI mode test...")
    try:
        with open(image_path, 'rb') as img_file:
            files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
            data = {'mode': 'openai'}
            response = requests.post(f"{api_url}/predict", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction', {})
            print(f"   Source: {prediction.get('source')}")
            print(f"   Score: {prediction.get('score'):.4f}")
            print(f"   Confidence: {prediction.get('confidence_level')}")
            
            if prediction.get('source') == 'openai':
                print("   🎯 SUCCESS: OpenAI was used!")
                print(f"   Original score: {prediction.get('original_score', 'N/A')}")
            else:
                print("   📝 Model still used (confidence too high)")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Rename file to trigger bias detection
    print("3️⃣ Testing with bias-triggering filename...")
    
    # Create a temporary file with a name that should trigger bias detection
    temp_names = [
        "suspicious_nyc_photo.jpg",
        "definitely_not_europe.jpg", 
        "american_landmark.jpg"
    ]
    
    for temp_name in temp_names:
        print(f"   Testing with filename: {temp_name}")
        try:
            with open(image_path, 'rb') as img_file:
                files = {'photo': (temp_name, img_file, 'image/jpeg')}
                response = requests.post(f"{api_url}/predict", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', {})
                
                bias_warning = prediction.get('bias_warning')
                source = prediction.get('source')
                
                if bias_warning:
                    print(f"      ⚠️  Bias detected: {bias_warning}")
                    if source == 'openai':
                        print("      🎯 OpenAI fallback triggered!")
                        break
                    else:
                        print("      📝 Bias detected but OpenAI not used")
                else:
                    print("      ✅ No bias detected")
            else:
                print(f"      ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print()
    
    # Analysis and recommendations
    print("📊 Analysis & Recommendations:")
    print("=" * 40)
    
    if baseline_score > 0.8:
        print(f"🔍 Your model is very confident ({baseline_score:.3f}) about this image")
        print("   This is why OpenAI fallback isn't triggered - it's working as designed!")
        print()
        print("💡 To test OpenAI fallback, try:")
        print("   • Blurry or unclear images")
        print("   • Images of less famous landmarks")
        print("   • Images that might confuse the model")
        print("   • Artificially lower the confidence threshold")
    elif baseline_score > 0.4:
        print(f"🔍 Model has medium confidence ({baseline_score:.3f})")
        print("   OpenAI might be used depending on other factors")
    else:
        print(f"🔍 Model has low confidence ({baseline_score:.3f})")
        print("   OpenAI should be triggered automatically")
    
    print()
    print("🔧 Current OpenAI Trigger Conditions:")
    print("   • Score < 0.4 (very low confidence)")
    print("   • Bias warning detected")
    print("   • NYC prediction with score < 0.7")
    print("   • mode=openai explicitly requested")

def create_test_scenarios():
    """Suggest test scenarios that would trigger OpenAI"""
    print("\n🎯 Test Scenarios to Trigger OpenAI:")
    print("=" * 40)
    
    scenarios = [
        {
            "name": "Blurry Image Test",
            "description": "Use a blurry or low-quality image",
            "reason": "Model confidence should be lower"
        },
        {
            "name": "Obscure Location Test", 
            "description": "Use image of lesser-known landmark",
            "reason": "Model might not recognize it well"
        },
        {
            "name": "Bias Trigger Test",
            "description": "Rename European landmark with American filename",
            "reason": "Should trigger bias detection"
        },
        {
            "name": "Threshold Modification",
            "description": "Temporarily lower confidence threshold in API code",
            "reason": "Force OpenAI usage for testing"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Method: {scenario['description']}")
        print(f"   Why: {scenario['reason']}")
        print()

def main():
    """Main function"""
    # Get image path from command line or use default
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "eiffel.jpg"
    
    # Get API URL from command line or use default
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    else:
        api_url = "http://localhost:8000"
    
    # Run tests
    test_with_forced_openai(image_path, api_url)
    
    # Show test scenarios
    create_test_scenarios()
    
    print("\n💡 Usage: python force_openai_test.py [image_path] [api_url]")
    print("   Example: python force_openai_test.py eiffel.jpg http://localhost:8000")

if __name__ == "__main__":
    main() 