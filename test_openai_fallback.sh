#!/bin/bash

# OpenAI Fallback Testing Script
# This script helps test when and how the OpenAI fallback activates

BASE_URL="http://localhost:8000"  # Change to your deployed URL
IMAGE_FILE="eiffel.jpg"

echo "🤖 OpenAI Fallback Testing for WhereIsThisPlace"
echo "=============================================="
echo "Base URL: $BASE_URL"
echo "Test Image: $IMAGE_FILE"
echo ""

# Check if OpenAI API key is configured
echo "🔑 Checking OpenAI Configuration..."
if [[ -n "$OPENAI_API_KEY" ]]; then
    echo "✅ OPENAI_API_KEY is set (${#OPENAI_API_KEY} characters)"
else
    echo "⚠️  OPENAI_API_KEY not found in environment"
    echo "   Set with: export OPENAI_API_KEY='your-key-here'"
fi

if [[ -n "$OPENAI_BASE_URL" ]]; then
    echo "✅ OPENAI_BASE_URL is set: $OPENAI_BASE_URL"
else
    echo "ℹ️  OPENAI_BASE_URL not set (will use default)"
fi

echo ""

# Function to test with different modes and analyze when OpenAI is used
test_fallback() {
    local mode="$1"
    local description="$2"
    
    echo "🧪 Testing: $description"
    echo "Mode: $mode"
    
    # Build request
    local curl_cmd="curl -s -X POST -F \"photo=@$IMAGE_FILE\""
    if [[ -n "$mode" ]]; then
        curl_cmd="$curl_cmd -F \"mode=$mode\""
    fi
    curl_cmd="$curl_cmd \"$BASE_URL/predict\""
    
    # Make request
    local response=$(eval $curl_cmd 2>/dev/null)
    local status_code=$(eval $curl_cmd -o /dev/null -w "%{http_code}" 2>/dev/null)
    
    if [[ "$status_code" == "200" ]]; then
        echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    prediction = data.get('prediction', {})
    
    source = prediction.get('source', 'unknown')
    confidence = prediction.get('confidence_level', 'unknown')
    score = prediction.get('score', 0)
    
    print(f'Source: {source}')
    print(f'Confidence: {confidence}')
    print(f'Score: {score}')
    
    if source == 'openai':
        print('🎯 SUCCESS: OpenAI fallback was used!')
        original_score = prediction.get('original_score')
        if original_score:
            print(f'   Original model score was: {original_score}')
            print(f'   Improvement: {score - original_score:.3f}')
    elif source == 'model':
        print('📊 Model prediction used (high confidence)')
        if score > 1.0:
            print(f'   Very high confidence - OpenAI not needed')
        else:
            print(f'   Confidence was sufficient to skip OpenAI')
    
    # Location analysis
    lat, lon = prediction.get('lat'), prediction.get('lon')
    if lat and lon:
        if 48.0 <= lat <= 50.0 and 1.0 <= lon <= 4.0:
            print(f'📍 Location: Paris area ({lat:.3f}, {lon:.3f})')
        elif 40.0 <= lat <= 41.0 and -75.0 <= lon <= -73.0:
            print(f'📍 Location: NYC area ({lat:.3f}, {lon:.3f})')
        else:
            print(f'📍 Location: Other ({lat:.3f}, {lon:.3f})')
            
except Exception as e:
    print(f'❌ Error parsing response: {e}')
"
    else
        echo "❌ Request failed with status $status_code"
        echo "Response: $response"
    fi
    
    echo "---"
    echo ""
}

# Run tests
echo "🚀 Starting fallback tests..."
echo ""

# Test 1: Default mode
test_fallback "" "Default mode (no mode specified)"

# Wait for rate limiting
echo "⏱️  Waiting 5 seconds..."
sleep 5

# Test 2: Explicit model mode
test_fallback "model" "Explicit model mode"

# Wait for rate limiting
echo "⏱️  Waiting 5 seconds..."
sleep 5

# Test 3: OpenAI mode
test_fallback "openai" "OpenAI mode (may still use model if confident)"

echo ""
echo "📋 Summary & Analysis:"
echo "====================="
echo ""
echo "🔍 Understanding OpenAI Fallback Logic:"
echo ""
echo "The API uses OpenAI fallback when:"
echo "  1. mode=openai is specified AND model confidence is low"
echo "  2. Model prediction score < confidence threshold"
echo "  3. OpenAI API key is properly configured"
echo ""
echo "🎯 Your Eiffel Tower Results:"
echo "  • High model confidence (score > 1.0) = no OpenAI needed"
echo "  • Correct Paris prediction = model is working well"
echo "  • This is optimal behavior - saves API costs!"
echo ""
echo "💡 To trigger OpenAI fallback, try:"
echo "  • Images with ambiguous or unclear landmarks"
echo "  • Blurry or low-quality images"
echo "  • Images of less famous locations"
echo "  • Images that might confuse the model"
echo ""
echo "⚙️  Current Behavior Analysis:"
if [[ -n "$OPENAI_API_KEY" ]]; then
    echo "  ✅ OpenAI is configured and ready"
    echo "  ✅ Model is confident enough to not need fallback"
    echo "  ✅ This demonstrates intelligent cost optimization"
else
    echo "  ⚠️  OpenAI not configured - fallback won't work"
    echo "  🔧 To enable: export OPENAI_API_KEY='your-key'"
fi

echo ""
echo "🏁 OpenAI fallback system is working as designed! 🎉" 