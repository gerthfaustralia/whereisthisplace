#!/bin/bash

# Bias Detection Testing Script
# Tests the European landmark -> NYC bias detection system

BASE_URL="http://localhost:8000"  # Change to your deployed URL

echo "⚠️  Bias Detection Testing for WhereIsThisPlace"
echo "=============================================="
echo "Base URL: $BASE_URL"
echo ""

# Function to test bias detection with different images
test_bias_detection() {
    local image_file="$1"
    local expected_bias="$2"
    
    if [[ ! -f "$image_file" ]]; then
        echo "❌ Image file not found: $image_file"
        return
    fi
    
    echo "🧪 Testing Bias Detection"
    echo "Image: $image_file"
    echo "Expected bias behavior: $expected_bias"
    echo ""
    
    # Make prediction request
    local response=$(curl -s -X POST -F "photo=@$image_file" "$BASE_URL/predict" 2>/dev/null)
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -F "photo=@$image_file" "$BASE_URL/predict" 2>/dev/null)
    
    if [[ "$status_code" == "200" ]]; then
        echo "$response" | python3 -c "
import sys, json, os

try:
    data = json.load(sys.stdin)
    prediction = data.get('prediction', {})
    
    # Extract key information
    lat = prediction.get('lat')
    lon = prediction.get('lon')
    bias_warning = prediction.get('bias_warning')
    filename = '$image_file'
    
    print(f'📍 Predicted Location: ({lat}, {lon})')
    
    # Analyze coordinates
    if lat and lon:
        if 40.0 <= lat <= 41.0 and -75.0 <= lon <= -73.0:
            location_type = 'NYC area'
            print('🗽 Predicted as NYC area')
        elif 48.0 <= lat <= 50.0 and 1.0 <= lon <= 4.0:
            location_type = 'Paris area'
            print('🗼 Predicted as Paris area')
        elif 51.0 <= lat <= 52.0 and -1.0 <= lon <= 1.0:
            location_type = 'London area' 
            print('🏰 Predicted as London area')
        else:
            location_type = 'Other location'
            print(f'🌍 Predicted as other location')
    
    # Check for European landmark indicators in filename
    european_keywords = ['eiffel', 'tower', 'london', 'big ben', 'colosseum', 
                        'rome', 'berlin', 'madrid', 'barcelona', 'amsterdam',
                        'prague', 'vienna', 'paris', 'europe']
    
    has_european_keyword = any(keyword in filename.lower() for keyword in european_keywords)
    
    print(f'🏷️  Filename suggests European landmark: {has_european_keyword}')
    
    # Analyze bias detection
    if bias_warning:
        print(f'⚠️  BIAS WARNING DETECTED: {bias_warning}')
        print('✅ Bias detection system is active!')
        
        # Check if this makes sense
        if has_european_keyword and location_type == 'NYC area':
            print('🎯 CORRECT: European landmark predicted as NYC - bias likely!')
        else:
            print('🤔 Unexpected bias warning scenario')
            
    else:
        print('✅ No bias warning')
        
        # Check if we expected one
        if has_european_keyword and location_type == 'NYC area':
            print('⚠️  MISSING: Expected bias warning for European landmark -> NYC')
        else:
            print('✅ Correct: No bias warning needed')
    
    # Summary
    print(f'')
    print(f'📊 Analysis Summary:')
    print(f'  • European filename: {has_european_keyword}')
    print(f'  • Predicted location: {location_type}')
    print(f'  • Bias warning: {\"Yes\" if bias_warning else \"No\"}')
    
    # Recommendations
    if has_european_keyword and location_type == 'NYC area' and not bias_warning:
        print(f'')
        print(f'🔧 Recommendation: Bias detection should trigger!')
        print(f'   Check the bias detection logic in the API')
    elif bias_warning and (not has_european_keyword or location_type != 'NYC area'):
        print(f'')
        print(f'🔧 Note: Unexpected bias warning scenario')
        print(f'   This might be a false positive or different bias type')
    else:
        print(f'')
        print(f'✅ Bias detection behavior looks correct!')
        
except Exception as e:
    print(f'❌ Error analyzing response: {e}')
    print(f'Raw response: {sys.stdin.read()}')
"
    else
        echo "❌ Request failed with status $status_code"
        echo "Response: $response"
    fi
    
    echo "---"
    echo ""
}

# Check available test images
echo "🔍 Checking for test images..."
test_images=()

if [[ -f "eiffel.jpg" ]]; then
    test_images+=("eiffel.jpg")
    echo "✅ Found: eiffel.jpg (European landmark)"
fi

# Look for other potential test images
for img in *.jpg *.jpeg *.png; do
    if [[ -f "$img" && "$img" != "eiffel.jpg" ]]; then
        test_images+=("$img")
        echo "✅ Found: $img"
    fi
done

if [[ ${#test_images[@]} -eq 0 ]]; then
    echo "❌ No test images found!"
    echo "💡 Add some test images (.jpg, .jpeg, .png) to test bias detection"
    exit 1
fi

echo ""
echo "🚀 Starting bias detection tests..."
echo ""

# Test each available image
for img in "${test_images[@]}"; do
    test_bias_detection "$img" "Check if European landmark predicted as NYC"
    
    # Wait between requests for rate limiting
    if [[ "${#test_images[@]}" -gt 1 ]]; then
        echo "⏱️  Waiting 5 seconds for rate limiting..."
        sleep 5
    fi
done

echo ""
echo "📋 Bias Detection System Analysis:"
echo "=================================="
echo ""
echo "🎯 How Bias Detection Works:"
echo "  1. Checks if filename suggests European landmark"
echo "  2. Checks if prediction is in NYC area (40-41°N, 73-75°W)"
echo "  3. If both true → triggers bias warning"
echo "  4. Warning suggests the model may have US bias"
echo ""
echo "🔍 Expected Behaviors:"
echo "  ✅ European landmark + Paris prediction = No warning"
echo "  ✅ Non-European image + NYC prediction = No warning"  
echo "  ⚠️  European landmark + NYC prediction = Bias warning"
echo "  ✅ Any other combination = No warning"
echo ""
echo "💡 To trigger bias detection:"
echo "  • Use images with European landmark filenames"
echo "  • That get predicted as NYC coordinates"
echo "  • This indicates potential model bias toward US locations"
echo ""
echo "🏁 Bias detection system analysis complete!" 