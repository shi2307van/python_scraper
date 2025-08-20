#!/usr/bin/env python3

"""
Direct test of the FastAPI service
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from naukri_scraper_service import app, scrape_jobs_advanced

async def test_service():
    print("🧪 Testing FastAPI Service Directly")
    print("=" * 50)
    
    try:
        # Test the main scraping endpoint
        print("\n1. Testing scrape_jobs_advanced endpoint...")
        result = await scrape_jobs_advanced(keyword="python developer", sources="all")
        
        # Extract the response content
        if hasattr(result, 'body'):
            import json
            response_data = json.loads(result.body.decode())
        else:
            response_data = result
        
        print(f"✅ Service responded successfully")
        print(f"📊 Total jobs found: {response_data.get('summary', {}).get('total_jobs', 0)}")
        
        # Show first few jobs
        jobs = response_data.get('jobs', [])
        for i, job in enumerate(jobs[:3]):
            print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} ({job.get('source', 'N/A')})")
        
        print(f"\n📈 Processing time: {response_data.get('summary', {}).get('processing_time', 'N/A')}s")
        print(f"🎯 Success rate: {response_data.get('summary', {}).get('success_rate', 0):.1%}")
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
