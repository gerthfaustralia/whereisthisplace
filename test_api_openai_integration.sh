#!/bin/bash

# Test WhereIsThisPlace API OpenAI Integration
# This tests if the deployed API can use OpenAI fallback

API_URL="http://52.28.72.57:8000"  # Your deployed API
IMAGE_FILE="eiffel.jpg"

echo "🤖 Testing WhereIsThisPlace API OpenAI Integration"
echo "================================================"
echo "API URL: $API_URL"
echo "Test Image: $IMAGE_FILE"
echo ""

# Function to test API with different scenarios
test_api_openai() {
    local test_name="$1"
    local mode="$2"
    local description="$3"
    
    echo "🧪 Test: $test_name"
    echo "Mode: $mode"
    echo "Expected: $description"
    echo ""
    
    # Build curl command
    local curl_cmd="curl -s -X POST -F \"photo=@$IMAGE_FILE\""
    if [[ -n "$mode" ]]; then
        curl_cmd="$curl_cmd -F \"mode=$mode\""
    fi
    curl_cmd="$curl_cmd \"$API_URL/predict\""
    
    # Make request
    local response=$(eval $curl_cmd 2>/dev/null)
    local status_code=$(eval $curl_cmd -o /dev/null -w "%{http_code}" 2>/dev/null)
    
    echo "Status: $status_code"
    
    if [[ "$status_code" == "200" ]]; then
        echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    prediction = data.get('prediction', {})
    
    source = prediction.get('source', 'unknown')
    confidence = prediction.get('confidence_level', 'unknown')  
    score = prediction.get('score', 0)
    original_score = prediction.get('original_score')
    
    print(f'📊 Source: {source}')
    print(f'📊 Confidence: {confidence}')
    print(f'📊 Score: {score}')
    
    if original_score:
        print(f'📊 Original Score: {original_score}')
        print(f'📊 Score Improvement: {score - original_score:.3f}')
    
    # Analysis
    if source == 'openai':
        print('🎯 SUCCESS: OpenAI fallback was used!')
        print('✅ Your API can access OpenAI successfully')
        if original_score:
            print(f'   Model was low confidence ({original_score:.3f})')
            print(f'   OpenAI provided better result ({score:.3f})')
    elif source == 'model':
        print('🧠 Model prediction used')
        if '$mode' == 'openai':
            print('⚠️  OpenAI mode requested but model used instead')
            print('   This means model confidence was above threshold')
            print(f'   Score {score:.3f} was high enough to skip OpenAI')
        else:
            print('✅ Normal model prediction (no OpenAI requested)')
    
    # Coordinates
    lat, lon = prediction.get('lat'), prediction.get('lon')
    if lat and lon:
        print(f'📍 Coordinates: ({lat:.4f}, {lon:.4f})')
        
except Exception as e:
    print(f'❌ Error parsing response: {e}')
    print(f'Raw response: {repr(sys.stdin.read())}')
"
    else
        echo "❌ Request failed: $status_code"
        echo "Response: $response"
    fi
    
    echo "---"
    echo ""
}

# Check if image exists
if [[ ! -f "$IMAGE_FILE" ]]; then
    echo "❌ Test image '$IMAGE_FILE' not found"
    echo "💡 Please ensure you have a test image file"
    exit 1
fi

echo "🚀 Starting OpenAI integration tests..."
echo ""

# Test 1: Default mode (baseline)
test_api_openai "Baseline Test" "" "Normal model prediction"

# Wait for rate limiting
echo "⏱️  Waiting 5 seconds..."
sleep 5

# Test 2: Explicit OpenAI mode
test_api_openai "OpenAI Mode Test" "openai" "Should try OpenAI but might use model if confident"

# Wait for rate limiting
echo "⏱️  Waiting 5 seconds..."
sleep 5

# Test 3: Explicit model mode
test_api_openai "Model Mode Test" "model" "Should force model prediction only"

echo ""
echo "📋 OpenAI Integration Analysis:"
echo "=============================="
echo ""
echo "🔍 What these results tell us:"
echo ""
echo "✅ If source=model even with mode=openai:"
echo "   • Model confidence was too high to need OpenAI"
echo "   • This is GOOD - saves API costs when model is confident"
echo "   • OpenAI integration is ready but not needed"
echo ""
echo "🎯 If source=openai:"
echo "   • OpenAI fallback is working!"
echo "   • API server has access to OpenAI"
echo "   • Model confidence was low enough to trigger fallback"
echo ""
echo "❌ If requests fail:"
echo "   • Check if API server has OPENAI_API_KEY configured"
echo "   • Verify network connectivity to OpenAI"
echo "   • Check API server logs for errors"
echo ""
echo "💡 To force OpenAI fallback, try:"
echo "   • Blurry or unclear images"
echo "   • Images of less famous landmarks"
echo "   • Images that might confuse the model"
echo "   • Lower the confidence threshold in your API code"
echo ""
echo "🏁 OpenAI integration test complete!" 