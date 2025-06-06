#!/bin/bash

# Test OpenAI API Key with curl
# This avoids Python import issues

echo "🔑 Testing OpenAI API Key with curl"
echo "=================================="

# Check if API key is set
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "❌ OPENAI_API_KEY not found in environment variables"
    echo "💡 Set it with: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo "✅ API Key found: ${OPENAI_API_KEY:0:8}...${OPENAI_API_KEY: -8} (${#OPENAI_API_KEY} chars)"

# Check base URL
OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
echo "🌐 Using base URL: $OPENAI_BASE_URL"

echo ""

# Test 1: Simple text completion
echo "🧪 Test 1: Simple text completion"
echo "================================"

text_response=$(curl -s -X POST "$OPENAI_BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say \"Hello World\" and nothing else."}],
    "max_tokens": 10
  }')

echo "Response:"
echo "$text_response"

# Check if response contains expected fields
if echo "$text_response" | grep -q '"content"'; then
    echo "✅ Text API works!"
    text_works=true
else
    echo "❌ Text API failed"
    text_works=false
fi

echo ""
echo "----------------------------------------"
echo ""

# Test 2: Vision API with base64 image
echo "🖼️  Test 2: Vision API with image"
echo "================================"

if [[ -f "eiffel.jpg" ]]; then
    echo "📸 Using test image: eiffel.jpg"
    
    # Encode image to base64
    image_base64=$(base64 -i eiffel.jpg)
    
    vision_response=$(curl -s -X POST "$OPENAI_BASE_URL/chat/completions" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -d "{
                 \"model\": \"gpt-4o\",
        \"messages\": [
          {
            \"role\": \"user\",
            \"content\": [
              {
                \"type\": \"text\",
                \"text\": \"What location is shown in this image? Provide GPS coordinates if possible.\"
              },
              {
                \"type\": \"image_url\",
                \"image_url\": {
                  \"url\": \"data:image/jpeg;base64,$image_base64\"
                }
              }
            ]
          }
        ],
        \"max_tokens\": 100
      }")
    
    echo "Response:"
    echo "$vision_response"
    
    # Check if response contains expected fields
    if echo "$vision_response" | grep -q '"content"'; then
        echo "✅ Vision API works!"
        vision_works=true
    else
        echo "❌ Vision API failed"
        vision_works=false
    fi
else
    echo "⚠️  Test image 'eiffel.jpg' not found"
    echo "💡 Testing with text-only vision question..."
    
         vision_response=$(curl -s -X POST "$OPENAI_BASE_URL/chat/completions" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer $OPENAI_API_KEY" \
       -d '{
         "model": "gpt-4o",
         "messages": [{"role": "user", "content": "What are the GPS coordinates of the Eiffel Tower in Paris? Respond with just the latitude and longitude numbers."}],
         "max_tokens": 50
       }')
    
    echo "Response:"
    echo "$vision_response"
    
    if echo "$vision_response" | grep -q '"content"'; then
        echo "✅ Vision API works!"
        vision_works=true
    else
        echo "❌ Vision API failed"
        vision_works=false
    fi
fi

echo ""
echo "📊 OpenAI API Test Summary:"
echo "=========================="
echo "Text API: $([ "$text_works" = true ] && echo "✅ Working" || echo "❌ Failed")"
echo "Vision API: $([ "$vision_works" = true ] && echo "✅ Working" || echo "❌ Failed")"

if [[ "$text_works" = true && "$vision_works" = true ]]; then
    echo ""
    echo "🎉 OpenAI API key is working correctly!"
    echo ""
    echo "💡 If your WhereIsThisPlace API isn't using OpenAI, it's likely because:"
    echo "   • Model confidence is too high (> threshold)"
    echo "   • OpenAI fallback logic needs adjustment"
    echo "   • API server doesn't have the OpenAI key configured"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Check if your API server has OPENAI_API_KEY set"
    echo "   2. Test with a lower-confidence image to trigger fallback"
    echo "   3. Check the confidence threshold in your API code"
else
    echo ""
    echo "❌ OpenAI API key has issues"
    echo "🔧 Common fixes:"
    echo "   • Check if API key is valid and not expired"
    echo "   • Verify account has sufficient credits"
    echo "   • Check network connectivity"
    echo "   • Try regenerating the API key"
fi 