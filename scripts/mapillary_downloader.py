#!/usr/bin/env python3
"""
Mapillary Dataset Downloader for WhereIsThisPlace
Downloads geolocated images from Mapillary API for training data.

Features:
- Client-side geographic filtering (due to Mapillary API bbox issues)
- Requests 10x more images than needed to account for API filtering problems
- Validates coordinates are actually within specified bounding box
- Progress tracking and statistics

Usage:
    python scripts/mapillary_downloader.py \
        --access-token YOUR_MAPILLARY_TOKEN \
        --bbox "2.2,48.8,2.4,48.9" \
        --output-dir ./datasets/mapillary_paris \
        --max-images 1000
"""

import argparse
import asyncio
import aiohttp
import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple

class MapillaryDownloader:
    def __init__(self, access_token: str, output_dir: str, max_images: int = 1000):
        self.access_token = access_token
        self.output_dir = Path(output_dir)
        self.max_images = max_images
        self.base_url = "https://graph.mapillary.com"
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'api_results': 0,
            'bbox_filtered': 0,
            'downloaded': 0,
            'errors': 0
        }
        
    def is_within_bbox(self, lat: float, lon: float, bbox: Tuple[float, float, float, float]) -> bool:
        """Check if coordinates are within bounding box (client-side validation)"""
        min_lon, min_lat, max_lon, max_lat = bbox
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
        
    async def search_images(self, bbox: Tuple[float, float, float, float]) -> List[Dict]:
        """Search for images within bounding box with client-side filtering"""
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Request 10x more images than needed due to Mapillary API bbox issues
        request_limit = min(self.max_images * 10, 10000)
        
        async with aiohttp.ClientSession() as session:
            images = []
            url = f"{self.base_url}/images"
            params = {
                'access_token': self.access_token,
                'bbox': f"{min_lon},{min_lat},{max_lon},{max_lat}",
                'fields': 'id,thumb_256_url,computed_geometry,captured_at',
                'limit': request_limit
            }
            
            print(f"Searching for images in bbox: {bbox}")
            print(f"Requesting {request_limit} images from API to find {self.max_images} within bbox")
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    api_results = data.get('data', [])
                    self.stats['api_results'] = len(api_results)
                    print(f"API returned {len(api_results)} images")
                    
                    # Client-side filtering for coordinates within bbox
                    filtered_images = []
                    for image_data in api_results:
                        geometry = image_data.get('computed_geometry')
                        if geometry and geometry.get('type') == 'Point':
                            lon, lat = geometry['coordinates']
                            if self.is_within_bbox(lat, lon, bbox):
                                filtered_images.append(image_data)
                                if len(filtered_images) >= self.max_images:
                                    break
                    
                    images = filtered_images
                    self.stats['bbox_filtered'] = len(images)
                    print(f"After client-side bbox filtering: {len(images)} images within target area")
                    
                else:
                    print(f"Error searching images: {response.status}")
                    
            return images
    
    async def download_image(self, session: aiohttp.ClientSession, image_data: Dict, index: int, bbox: Tuple[float, float, float, float]) -> Dict:
        """Download a single image with coordinate validation"""
        try:
            image_id = image_data['id']
            image_url = image_data['thumb_256_url']
            geometry = image_data['computed_geometry']
            
            # Extract coordinates
            if geometry['type'] == 'Point':
                lon, lat = geometry['coordinates']
            else:
                print(f"Skipping non-point geometry: {image_id}")
                return None
            
            # Double-check coordinates are within bbox (redundant but safe)
            if not self.is_within_bbox(lat, lon, bbox):
                print(f"Skipping image outside bbox: {image_id} at {lat:.4f}, {lon:.4f}")
                return None
            
            # Download image
            filename = f"mapillary_{image_id}_{index:06d}.jpg"
            filepath = self.output_dir / filename
            
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await response.read())
                    
                    self.stats['downloaded'] += 1
                    
                    return {
                        'image': filename,
                        'lat': lat,
                        'lon': lon,
                        'description': f"Mapillary image {image_id} within bbox",
                        'mapillary_id': image_id,
                        'captured_at': image_data.get('captured_at', ''),
                        'verified_bbox': True  # Mark as verified within bbox
                    }
                else:
                    print(f"Failed to download {image_id}: {response.status}")
                    self.stats['errors'] += 1
                    return None
                    
        except Exception as e:
            print(f"Error downloading {image_data.get('id', 'unknown')}: {e}")
            self.stats['errors'] += 1
            return None
    
    async def download_dataset(self, bbox: Tuple[float, float, float, float]):
        """Download complete dataset with enhanced filtering"""
        print(f"Starting enhanced Mapillary download to: {self.output_dir}")
        start_time = time.time()
        
        # Search for images with client-side filtering
        images = await self.search_images(bbox)
        if not images:
            print("No images found within the specified bounding box!")
            return
        
        print(f"Downloading {len(images)} verified images...")
        
        # Download images concurrently
        csv_data = []
        semaphore = asyncio.Semaphore(10)  # Limit concurrent downloads
        
        async def download_with_semaphore(session, image_data, index):
            async with semaphore:
                return await self.download_image(session, image_data, index, bbox)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                download_with_semaphore(session, image_data, i) 
                for i, image_data in enumerate(images)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful downloads
            for result in results:
                if result and not isinstance(result, Exception):
                    csv_data.append(result)
        
        # Write CSV file with verification info
        csv_path = self.output_dir / 'mapillary_dataset.csv'
        with open(csv_path, 'w', newline='') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
        
        # Write bbox verification file
        bbox_info_path = self.output_dir / 'bbox_info.json'
        bbox_info = {
            'target_bbox': bbox,
            'bbox_string': f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            'requested_images': self.max_images,
            'api_results': self.stats['api_results'],
            'bbox_filtered': self.stats['bbox_filtered'],
            'successfully_downloaded': len(csv_data),
            'download_errors': self.stats['errors'],
            'filtering_effectiveness': f"{(self.stats['bbox_filtered'] / max(self.stats['api_results'], 1)) * 100:.1f}%",
            'download_time': time.time() - start_time
        }
        
        with open(bbox_info_path, 'w') as f:
            json.dump(bbox_info, f, indent=2)
        
        print(f"""
=== ENHANCED MAPILLARY DOWNLOAD COMPLETE ===
🎯 Target bbox: {bbox}
📊 API returned: {self.stats['api_results']} images
✅ Within bbox: {self.stats['bbox_filtered']} images
💾 Downloaded: {len(csv_data)} images
❌ Errors: {self.stats['errors']}
🔍 Bbox filtering: {(self.stats['bbox_filtered'] / max(self.stats['api_results'], 1)) * 100:.1f}% effective
⏱️  Total time: {time.time() - start_time:.1f}s
📁 Directory: {self.output_dir}
📄 CSV file: {csv_path}
📋 Bbox info: {bbox_info_path}
🎯 Ready for bulk loading!

Next steps:
python scripts/bulk_loader_production.py \\
    --dataset-dir {self.output_dir} \\
    --source mapillary_dataset \\
    --max-concurrent 8
        """)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Mapillary dataset with enhanced geographic filtering')
    parser.add_argument('--access-token', required=True, help='Mapillary API access token')
    parser.add_argument('--bbox', required=True, help='Bounding box: "min_lon,min_lat,max_lon,max_lat"')
    parser.add_argument('--output-dir', required=True, help='Output directory for dataset')
    parser.add_argument('--max-images', type=int, default=1000, help='Maximum images to download')
    
    args = parser.parse_args()
    
    # Parse bounding box
    bbox_parts = args.bbox.split(',')
    if len(bbox_parts) != 4:
        raise ValueError("Bounding box must be 'min_lon,min_lat,max_lon,max_lat'")
    
    bbox = tuple(float(x) for x in bbox_parts)
    
    # Validate bbox format
    min_lon, min_lat, max_lon, max_lat = bbox
    if min_lon >= max_lon or min_lat >= max_lat:
        raise ValueError("Invalid bounding box: min values must be less than max values")
    
    print(f"Target bounding box: {bbox}")
    print(f"Bbox area: {abs(max_lon - min_lon):.4f}° × {abs(max_lat - min_lat):.4f}°")
    
    downloader = MapillaryDownloader(args.access_token, args.output_dir, args.max_images)
    asyncio.run(downloader.download_dataset(bbox)) 