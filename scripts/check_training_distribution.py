#!/usr/bin/env python3
"""
Training Data Distribution Analyzer for WhereIsThisPlace
Analyzes the geographic distribution of training images to identify potential model bias.

Usage:
    python scripts/check_training_distribution.py
"""

import asyncio
import asyncpg
import json
from collections import defaultdict
from typing import Dict, List, Tuple

async def analyze_training_distribution():
    """Analyze the geographic distribution of training images"""
    
    # Connect to database
    database_url = 'postgresql://whereuser:wherepass@localhost:5432/whereisthisplace'
    
    try:
        pool = await asyncpg.create_pool(database_url)
        
        async with pool.acquire() as conn:
            # Get overall statistics
            total_training = await conn.fetchval('SELECT COUNT(*) FROM training_images')
            total_photos = await conn.fetchval('SELECT COUNT(*) FROM photos')
            
            print(f"📊 DATABASE OVERVIEW")
            print(f"Total training images: {total_training}")
            print(f"Total photos (predictions): {total_photos}")
            print(f"Total entries: {total_training + total_photos}")
            print()
            
            # Analyze training images by source
            sources = await conn.fetch('''
                SELECT source, COUNT(*) as count, 
                       AVG(lat) as avg_lat, AVG(lon) as avg_lon,
                       MIN(lat) as min_lat, MAX(lat) as max_lat,
                       MIN(lon) as min_lon, MAX(lon) as max_lon
                FROM training_images 
                GROUP BY source 
                ORDER BY count DESC
            ''')
            
            print(f"🗂️ TRAINING DATA BY SOURCE")
            print(f"{'Source':<25} {'Count':<8} {'Avg Lat':<10} {'Avg Lon':<10} {'Geographic Range'}")
            print("-" * 80)
            
            city_distribution = defaultdict(int)
            total_by_region = defaultdict(int)
            
            for row in sources:
                source = row['source']
                count = row['count']
                avg_lat = row['avg_lat']
                avg_lon = row['avg_lon']
                lat_range = f"{row['min_lat']:.2f} to {row['max_lat']:.2f}"
                lon_range = f"{row['min_lon']:.2f} to {row['max_lon']:.2f}"
                
                # Identify city/region based on coordinates
                city = identify_city(avg_lat, avg_lon)
                city_distribution[city] += count
                
                # Classify by major region
                region = classify_region(avg_lat, avg_lon)
                total_by_region[region] += count
                
                print(f"{source:<25} {count:<8} {avg_lat:<10.4f} {avg_lon:<10.4f} {city}")
            
            print()
            print(f"🌍 GEOGRAPHIC DISTRIBUTION")
            print(f"{'City/Region':<20} {'Count':<8} {'Percentage':<12}")
            print("-" * 45)
            
            for city, count in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_training) * 100 if total_training > 0 else 0
                print(f"{city:<20} {count:<8} {percentage:>8.1f}%")
            
            print()
            print(f"🌎 REGIONAL DISTRIBUTION")
            print(f"{'Region':<20} {'Count':<8} {'Percentage':<12}")
            print("-" * 45)
            
            for region, count in sorted(total_by_region.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_training) * 100 if total_training > 0 else 0
                print(f"{region:<20} {count:<8} {percentage:>8.1f}%")
            
            # Check for specific landmarks
            await check_landmark_coverage(conn)
            
            # Provide bias analysis and recommendations
            print()
            analyze_bias_and_recommendations(city_distribution, total_by_region, total_training)
            
        await pool.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure your database is running and accessible at:")
        print("postgresql://whereuser:wherepass@localhost:5432/whereisthisplace")

def identify_city(lat: float, lon: float) -> str:
    """Identify city based on coordinates"""
    # Major city coordinate ranges
    cities = {
        'NYC': (40.4, 41.0, -74.5, -73.5),
        'London': (51.2, 51.7, -0.5, 0.3),
        'Paris': (48.7, 49.0, 2.0, 2.6),
        'Berlin': (52.3, 52.7, 13.0, 13.8),
        'Tokyo': (35.4, 35.9, 139.4, 140.0),
        'San Francisco': (37.6, 37.9, -122.7, -122.2),
        'Los Angeles': (33.9, 34.3, -118.7, -118.0),
        'Sydney': (-34.0, -33.7, 150.8, 151.4),
        'Moscow': (55.5, 55.9, 37.3, 38.0),
        'Rome': (41.7, 42.0, 12.3, 12.7)
    }
    
    for city, (min_lat, max_lat, min_lon, max_lon) in cities.items():
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return city
    
    return f"Unknown ({lat:.2f}, {lon:.2f})"

def classify_region(lat: float, lon: float) -> str:
    """Classify coordinates by major world region"""
    if 25 <= lat <= 50 and -130 <= lon <= -60:
        return "North America"
    elif 35 <= lat <= 70 and -10 <= lon <= 40:
        return "Europe"
    elif 20 <= lat <= 50 and 70 <= lon <= 150:
        return "Asia"
    elif -40 <= lat <= -10 and 110 <= lon <= 160:
        return "Australia/Oceania"
    elif -35 <= lat <= 35 and -80 <= lon <= -30:
        return "South America"
    elif -35 <= lat <= 35 and -20 <= lon <= 50:
        return "Africa"
    else:
        return "Other/Unknown"

async def check_landmark_coverage(conn):
    """Check if we have training data near famous landmarks"""
    landmarks = [
        ("Brandenburg Gate", 52.5163, 13.3777, "Berlin"),
        ("Buckingham Palace", 51.5014, -0.1419, "London"), 
        ("Eiffel Tower", 48.8584, 2.2945, "Paris"),
        ("Statue of Liberty", 40.6892, -74.0445, "NYC"),
        ("Times Square", 40.7580, -73.9855, "NYC"),
        ("Tower Bridge", 51.5055, -0.0754, "London"),
        ("Arc de Triomphe", 48.8738, 2.2950, "Paris"),
        ("Central Park", 40.7829, -73.9654, "NYC"),
    ]
    
    print(f"🏛️ LANDMARK COVERAGE ANALYSIS")
    print(f"{'Landmark':<20} {'City':<10} {'Nearest Training':<15} {'Distance (km)'}")
    print("-" * 65)
    
    for name, lat, lon, city in landmarks:
        # Find nearest training image within 5km
        nearest = await conn.fetchrow('''
            SELECT filename, lat, lon, source,
                   ST_Distance(
                       ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                       geom::geography
                   ) / 1000 as distance_km
            FROM training_images 
            WHERE ST_DWithin(
                ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                geom::geography,
                5000
            )
            ORDER BY distance_km 
            LIMIT 1
        ''', lon, lat)
        
        if nearest:
            print(f"{name:<20} {city:<10} {nearest['filename'][:13]:<15} {nearest['distance_km']:.2f}")
        else:
            print(f"{name:<20} {city:<10} {'❌ None < 5km':<15} {'>':<5}")

def analyze_bias_and_recommendations(city_dist: Dict, region_dist: Dict, total: int):
    """Analyze potential bias and provide recommendations"""
    print(f"🔍 BIAS ANALYSIS & RECOMMENDATIONS")
    print("=" * 50)
    
    # Check for heavy bias towards one city/region
    if total == 0:
        print("❌ No training data found! The model has no training examples.")
        return
    
    max_city_count = max(city_dist.values()) if city_dist else 0
    max_city_percent = (max_city_count / total) * 100
    
    if max_city_percent > 60:
        max_city = max(city_dist.keys(), key=lambda x: city_dist[x])
        print(f"⚠️  HIGH BIAS DETECTED: {max_city_percent:.1f}% of training data is from {max_city}")
        print(f"   This explains why images are being misclassified as {max_city} locations.")
        print()
    
    # NYC bias check (common issue)
    nyc_count = city_dist.get('NYC', 0)
    nyc_percent = (nyc_count / total) * 100
    
    if nyc_percent > 40:
        print(f"🗽 NYC BIAS: {nyc_percent:.1f}% of training data is from NYC")
        print("   This is likely why Brandenburg Gate → NYC and Buckingham Palace → NYC")
        print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS TO FIX BIAS:")
    print()
    
    if nyc_percent > 40 or max_city_percent > 60:
        print("1. 🎯 IMMEDIATE ACTION - Add more diverse training data:")
        print("   • Download 1000+ images from Berlin (Brandenburg Gate area)")
        print("   • Download 1000+ images from London (Buckingham Palace area)")
        print("   • Download images from other major European cities")
        print()
        
        print("2. 📍 SUGGESTED BBOX DOWNLOADS:")
        # Berlin Brandenburg Gate area
        print("   Berlin (Brandenburg Gate): --bbox '13.35,52.50,13.40,52.53'")
        # London Buckingham Palace area  
        print("   London (Buckingham Palace): --bbox '-0.16,51.49,-0.12,51.51'")
        # Paris Landmarks
        print("   Paris (Central): --bbox '2.25,48.84,2.35,48.88'")
        print()
        
        print("3. 🔄 RETRAIN MODEL after adding balanced data:")
        print("   Target distribution: ~25% each for NYC, London, Paris, Berlin")
        print()
    
    if total < 1000:
        print("4. 📈 SCALE UP: You need more training data overall")
        print(f"   Current: {total} images | Recommended: 5000+ images")
        print("   More data = better accuracy and less overfitting")
        print()
    
    print("5. 🧪 TEST AFTER REBALANCING:")
    print("   • Upload Brandenburg Gate image → should predict Berlin")
    print("   • Upload Buckingham Palace image → should predict London")
    print("   • Monitor prediction accuracy across different cities")

if __name__ == '__main__':
    asyncio.run(analyze_training_distribution()) 