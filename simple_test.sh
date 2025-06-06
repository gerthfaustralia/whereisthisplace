#!/bin/bash

# Simple API Test - Single Request
BASE_URL="http://52.28.72.57:8000"
IMAGE_FILE="eiffel.jpg"

echo "🚀 Testing WhereIsThisPlace API"
echo "Target: $BASE_URL"
echo "Image: $IMAGE_FILE"
echo "=================================="

echo "📱 Making single prediction request..."
echo "Request: POST $BASE_URL/predict"
echo ""

# Make the request and capture response
response=$(curl -s -X POST -F "photo=@$IMAGE_FILE" "$BASE_URL/predict" 2>/dev/null)
status_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -F "photo=@$IMAGE_FILE" "$BASE_URL/predict" 2>/dev/null)

echo "Status Code: $status_code"
echo "Response:"
echo "$response"

# Try to parse as JSON if successful
if [[ "$status_code" == "200" ]]; then
    echo ""
    echo "📊 Parsing JSON response..."
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('✅ Valid JSON response!')
    print(json.dumps(data, indent=2))
    
    # Analyze the enhanced response
    prediction = data.get('prediction', {})
    print('\n🔍 Enhanced API Analysis:')
    print(f'  • Coordinates: ({prediction.get(\"lat\")}, {prediction.get(\"lon\")})')
    print(f'  • Score: {prediction.get(\"score\")}')
    print(f'  • Confidence Level: {prediction.get(\"confidence_level\")}')
    print(f'  • Source: {prediction.get(\"source\", \"model\")}')
    print(f'  • Bias Warning: {prediction.get(\"bias_warning\", \"None\")}')
    
    if prediction.get('original_score'):
        print(f'  • Original Score: {prediction.get(\"original_score\")}')
    
    # Check bias detection for Eiffel Tower
    if 'eiffel' in '$IMAGE_FILE'.lower():
        if prediction.get('bias_warning'):
            print('\n🎯 ✅ Bias detection is working! European landmark detected.')
        else:
            print('\n⚠️  Bias detection might not be triggered (depends on model prediction)')
            
    # Check for enhanced response fields
    expected_fields = ['confidence_level', 'source']
    missing_fields = [field for field in expected_fields if field not in prediction]
    if missing_fields:
        print(f'\n⚠️  Missing expected fields: {missing_fields}')
        print('   This might indicate the old API version is still deployed.')
    else:
        print('\n✅ All expected enhanced API fields are present!')
        
except json.JSONDecodeError:
    print('❌ Response is not valid JSON')
    print('Raw response:', repr(sys.stdin.read()))
except Exception as e:
    print(f'❌ Error parsing response: {e}')
"
else
    echo "❌ Request failed with status $status_code"
    if [[ "$status_code" == "429" ]]; then
        echo "💡 Tip: Wait a few minutes before retrying due to rate limiting"
    fi
fi

echo ""
echo "�� Test completed!" 