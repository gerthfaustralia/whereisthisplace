#!/bin/bash

# Manual API Test Script for WhereIsThisPlace using curl
# Tests the new bias detection and enhanced API response structure

# Configuration
BASE_URL="https://api.wheretheplaceis.com"
IMAGE_FILE="eiffel.jpg"

echo "🚀 Starting Manual API Tests"
echo "Target: $BASE_URL"
echo "Image: $IMAGE_FILE"
echo "=================================================="

# Test 1: Health endpoint
echo "🔍 Testing Health Endpoint..."
echo "Request: GET $BASE_URL/health"
curl -s -w "Status Code: %{http_code}\n" "$BASE_URL/health" | python3 -m json.tool 2>/dev/null || echo "Response received"
echo "✅ Health endpoint test completed!"
echo "--------------------------------------------------"

# Test 2: Check if image file exists
if [[ ! -f "$IMAGE_FILE" ]]; then
    echo "❌ Image file '$IMAGE_FILE' not found!"
    exit 1
fi

# Test 3: Basic prediction (should trigger bias detection for eiffel.jpg)
echo "🔍 Testing Predict Endpoint..."
echo "Request: POST $BASE_URL/predict (with $IMAGE_FILE)"
echo "Response:"
curl -s -w "\nStatus Code: %{http_code}\n" \
    -X POST \
    -F "photo=@$IMAGE_FILE" \
    "$BASE_URL/predict" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2))
    
    # Analyze the enhanced response
    prediction = data.get('prediction', {})
    print('\n📊 Response Analysis:')
    print(f'  • Coordinates: ({prediction.get(\"lat\")}, {prediction.get(\"lon\")})')
    print(f'  • Score: {prediction.get(\"score\")}')
    print(f'  • Confidence Level: {prediction.get(\"confidence_level\")}')
    print(f'  • Source: {prediction.get(\"source\", \"model\")}')
    print(f'  • Bias Warning: {prediction.get(\"bias_warning\", \"None\")}')
    
    if prediction.get('original_score'):
        print(f'  • Original Score: {prediction.get(\"original_score\")}')
    
    # Check if bias detection worked for Eiffel Tower
    if 'eiffel' in '$IMAGE_FILE'.lower() and prediction.get('bias_warning'):
        print('🎯 Bias detection is working! European landmark detected.')
        
except json.JSONDecodeError:
    print('Response is not valid JSON')
except Exception as e:
    print(f'Error parsing response: {e}')
"
echo "✅ Basic prediction test completed!"
echo "--------------------------------------------------"

# Test 4: OpenAI mode prediction
echo "🔍 Testing Predict Endpoint (OpenAI mode)..."
echo "Request: POST $BASE_URL/predict (with $IMAGE_FILE, mode=openai)"
echo "Response:"
curl -s -w "\nStatus Code: %{http_code}\n" \
    -X POST \
    -F "photo=@$IMAGE_FILE" \
    -F "mode=openai" \
    "$BASE_URL/predict" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2))
    
    # Analyze the enhanced response
    prediction = data.get('prediction', {})
    print('\n📊 OpenAI Mode Analysis:')
    print(f'  • Coordinates: ({prediction.get(\"lat\")}, {prediction.get(\"lon\")})')
    print(f'  • Score: {prediction.get(\"score\")}')
    print(f'  • Confidence Level: {prediction.get(\"confidence_level\")}')
    print(f'  • Source: {prediction.get(\"source\", \"model\")}')
    print(f'  • Bias Warning: {prediction.get(\"bias_warning\", \"None\")}')
    
    if prediction.get('source') == 'openai':
        print('🤖 OpenAI mode is working!')
    else:
        print('⚠️  Still using model prediction (OpenAI might not be configured)')
        
except json.JSONDecodeError:
    print('Response is not valid JSON')
except Exception as e:
    print(f'Error parsing response: {e}')
"
echo "✅ OpenAI mode test completed!"
echo "--------------------------------------------------"

# Test 5: Rate limiting
echo "🔍 Testing Rate Limiting..."
echo "Making multiple requests to trigger rate limiting..."
for i in {1..12}; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
    echo "Request $i: Status $status_code"
    if [[ "$status_code" == "429" ]]; then
        echo "✅ Rate limiting is working!"
        break
    fi
    sleep 0.1  # Small delay between requests
done

if [[ "$status_code" != "429" ]]; then
    echo "⚠️  Rate limiting might not be active or limit is higher than 12"
fi
echo "--------------------------------------------------"

echo "🏁 Manual tests completed!" 