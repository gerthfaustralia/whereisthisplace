#!/usr/bin/env python3
import openai
import os
import base64
import requests

def test_openai_flow():
    """Test the complete OpenAI + Nominatim flow"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found")
        return
    
    client = openai.OpenAI(api_key=api_key)
    
    # Read the test image
    image_path = 'datasets/mapillary_cairo/mapillary_2395120600634439_000000.jpg'
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
    except FileNotFoundError:
        print(f"❌ Image not found: {image_path}")
        return
    
    b64 = base64.b64encode(image_data).decode()
    print('🔍 Testing OpenAI vision...')
    
    try:
        resp = client.chat.completions.create(
            model='gpt-4o',
            messages=[{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Where was this photo taken? Reply with a location name.'},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
                ],
            }],
            max_tokens=100
        )
        place = resp.choices[0].message.content
        print(f'✅ OpenAI result: "{place}"')
        
        # Test Nominatim geocoding
        print(f'🌍 Testing Nominatim geocoding for: "{place}"')
        g = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': place, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'WhereIsThisPlace/1.0 (https://github.com/whereisthisplace)'},
            timeout=10,
        )
        print(f'🌍 Nominatim status: {g.status_code}')
        if g.status_code == 200:
            data = g.json()
            if data:
                print(f'✅ Geocoded to: lat={data[0]["lat"]}, lon={data[0]["lon"]}')
                print(f'📍 Full result: {data[0]}')
                return True
            else:
                print('❌ No geocoding results found')
                return False
        else:
            print(f'❌ Nominatim failed: {g.text[:100]}')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    test_openai_flow() 