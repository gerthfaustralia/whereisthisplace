#!/usr/bin/env python3
"""
Test script for OpenAI-Default Feature Branch
This script tests the new behavior where OpenAI is the default prediction method.
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_openai_default_behavior(image_path: str, api_url: str = "http://localhost:8000"):
    """Test the new OpenAI-default behavior"""
    
    print("🧪 Testing OpenAI-Default Feature Branch")
    print("=" * 50)
    print(f"Image: {image_path}")
    print(f"API: {api_url}")
    print()
    
    if not os.path.exists(image_path):
        print(f"❌ Image file '{image_path}' not found")
        return
    
    # Check if OpenAI API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("   Set with: export OPENAI_API_KEY='your-key-here'")
        print("   Without it, requests will fall back to model predictions")
        print()
    else:
        print(f"✅ OpenAI API key found ({len(api_key)} characters)")
        print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Default Mode (should use OpenAI)",
            "params": {},
            "expected": "openai" if api_key else "model"
        },
        {
            "name": "No Mode Specified (should use OpenAI)", 
            "params": {},
            "expected": "openai" if api_key else "model"
        },
        {
            "name": "Explicit Model Mode (should use model)",
            "params": {"mode": "model"},
            "expected": "model"
        },
        {
            "name": "Explicit OpenAI Mode (should use OpenAI)",
            "params": {"mode": "openai"},
            "expected": "openai" if api_key else "model"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"{i}️⃣ {scenario['name']}")
        
        try:
            with open(image_path, 'rb') as img_file:
                files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
                
                if scenario['params']:
                    response = requests.post(f"{api_url}/predict", files=files, data=scenario['params'], timeout=30)
                else:
                    response = requests.post(f"{api_url}/predict", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', {})
                
                source = prediction.get('source')
                score = prediction.get('score', 0)
                original_score = prediction.get('original_score')
                coordinates = (prediction.get('lat'), prediction.get('lon'))
                bias_warning = prediction.get('bias_warning')
                
                print(f"   Source: {source}")
                print(f"   Score: {score:.4f}")
                if original_score:
                    print(f"   Original Model Score: {original_score:.4f}")
                print(f"   Coordinates: ({coordinates[0]:.6f}, {coordinates[1]:.6f})")
                if bias_warning:
                    print(f"   Warning: {bias_warning}")
                
                # Check if result matches expectation
                if source == scenario['expected']:
                    print(f"   ✅ PASS: Used {source} as expected")
                    results.append(True)
                else:
                    print(f"   ❌ FAIL: Expected {scenario['expected']}, got {source}")
                    results.append(False)
                
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)
        
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary:")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI-default mode is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the results above.")
    
    print()
    print("🔍 Feature Branch Behavior:")
    print("• Default: Uses OpenAI (if API key available)")
    print("• mode=model: Forces model prediction")
    print("• mode=openai: Uses OpenAI (same as default)")
    print("• Fallback: Uses model if OpenAI fails")

def compare_predictions(image_path: str, api_url: str = "http://localhost:8000"):
    """Compare OpenAI vs Model predictions side by side"""
    
    print("\n🔄 Prediction Comparison")
    print("=" * 30)
    
    if not os.path.exists(image_path):
        print(f"❌ Image file '{image_path}' not found")
        return
    
    predictions = {}
    
    # Get model prediction
    try:
        with open(image_path, 'rb') as img_file:
            files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
            data = {'mode': 'model'}
            response = requests.post(f"{api_url}/predict", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            predictions['model'] = result.get('prediction', {})
        else:
            print(f"❌ Model prediction failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Model prediction error: {e}")
    
    # Get OpenAI prediction (default mode)
    try:
        with open(image_path, 'rb') as img_file:
            files = {'photo': (os.path.basename(image_path), img_file, 'image/jpeg')}
            response = requests.post(f"{api_url}/predict", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            predictions['openai'] = result.get('prediction', {})
        else:
            print(f"❌ OpenAI prediction failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ OpenAI prediction error: {e}")
    
    # Compare results
    if 'model' in predictions and 'openai' in predictions:
        model_pred = predictions['model']
        openai_pred = predictions['openai']
        
        print("📊 Side-by-Side Comparison:")
        print(f"{'Metric':<20} {'Model':<25} {'OpenAI':<25}")
        print("-" * 70)
        print(f"{'Source':<20} {model_pred.get('source', 'N/A'):<25} {openai_pred.get('source', 'N/A'):<25}")
        print(f"{'Score':<20} {model_pred.get('score', 0):<25.4f} {openai_pred.get('score', 0):<25.4f}")
        print(f"{'Latitude':<20} {model_pred.get('lat', 0):<25.6f} {openai_pred.get('lat', 0):<25.6f}")
        print(f"{'Longitude':<20} {model_pred.get('lon', 0):<25.6f} {openai_pred.get('lon', 0):<25.6f}")
        print(f"{'Confidence':<20} {model_pred.get('confidence_level', 'N/A'):<25} {openai_pred.get('confidence_level', 'N/A'):<25}")
        
        # Calculate distance between predictions
        try:
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lon1, lat1, lon2, lat2):
                """Calculate distance between two points on Earth"""
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # Radius of earth in kilometers
                return c * r
            
            distance = haversine(
                model_pred.get('lon', 0), model_pred.get('lat', 0),
                openai_pred.get('lon', 0), openai_pred.get('lat', 0)
            )
            
            print(f"\n📏 Distance between predictions: {distance:.2f} km")
            
        except Exception as e:
            print(f"\n❌ Could not calculate distance: {e}")

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
    
    # Check if API is running
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API not responding")
            return
    except:
        print(f"❌ Cannot connect to API at {api_url}")
        return
    
    print("✅ API is running")
    print()
    
    # Run tests
    test_openai_default_behavior(image_path, api_url)
    
    # Compare predictions
    compare_predictions(image_path, api_url)
    
    print("\n💡 Usage: python test_openai_default.py [image_path] [api_url]")
    print("   Example: python test_openai_default.py eiffel.jpg http://localhost:8000")

if __name__ == "__main__":
    main() 