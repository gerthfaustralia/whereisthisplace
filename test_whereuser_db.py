import requests
import psycopg2
import json

# Database connection
DATABASE_URL = "postgresql://whereuser:wherepass@localhost:5432/whereisthisplace"
API_URL = "http://localhost:8000"

def test_database():
    print("🗄️ Testing database connection with whereuser...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Set schema
        cursor.execute("SET search_path TO whereisthisplace, public")
        
        # Check photos count
        cursor.execute("SELECT COUNT(*) FROM photos")
        count = cursor.fetchone()[0]
        print(f"✅ Photos in database: {count}")
        
        # Check recent photos
        cursor.execute("SELECT id, scene_label, created_at FROM photos ORDER BY created_at DESC LIMIT 3")
        recent = cursor.fetchall()
        print(f"📸 Recent photos: {recent}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api():
    print("🌐 Testing API...")
    try:
        # Health check
        health = requests.get(f"{API_URL}/health")
        print(f"✅ Health status: {health.status_code}")
        
        # Post image
        try:
            with open('eiffel.jpg', 'rb') as f:
                files = {'photo': f}
                response = requests.post(f"{API_URL}/predict", files=files)
                print(f"✅ Image POST status: {response.status_code}")
                print(f"📋 Response: {response.json()}")
        except FileNotFoundError:
            print("❌ eiffel.jpg not found")
            
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_integration():
    print("🔗 Testing API + Database integration...")
    
    # Get initial count
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SET search_path TO whereisthisplace, public")
    cursor.execute("SELECT COUNT(*) FROM photos")
    initial_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Initial photo count: {initial_count}")
    
    # Post image via API
    try:
        with open('eiffel.jpg', 'rb') as f:
            files = {'photo': f}
            response = requests.post(f"{API_URL}/predict", files=files)
            print(f"🖼️ Posted image, API response: {response.status_code}")
    except:
        print("❌ Could not post image")
        return
    
    # Check if count increased
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SET search_path TO whereisthisplace, public")
    cursor.execute("SELECT COUNT(*) FROM photos")
    final_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Final photo count: {final_count}")
    
    if final_count > initial_count:
        print("✅ Integration working! API stored data in database")
    else:
        print("⚠️ No new data stored - check if API actually saves to DB")

if __name__ == "__main__":
    print("🧪 Running comprehensive whereuser database tests...\n")
    
    db_ok = test_database()
    api_ok = test_api()
    
    if db_ok and api_ok:
        test_integration()
    else:
        print("❌ Basic tests failed, skipping integration test")
