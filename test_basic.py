#!/usr/bin/env python3

"""
Simple Test for Real-Time Scraper
"""

import time
import sys
import os

# Test import
try:
    from realtime_scraper import realtime_scraper
    print("✅ Real-time scraper imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_scraping():
    """Test basic scraping functionality"""
    
    print("🧪 Testing basic real-time scraping...")
    
    try:
        # Test Indeed scraping
        print("📋 Testing Indeed scraping...")
        indeed_jobs = realtime_scraper.scrape_indeed_realtime("python developer")
        print(f"   Indeed: {len(indeed_jobs)} jobs found")
        
        # Show sample job with apply link
        if indeed_jobs:
            job = indeed_jobs[0]
            print(f"   Sample: {job['title']} at {job['company']}")
            print(f"   Apply Link: {job.get('apply_link', 'Not available')}")
        
        # Test Naukri scraping
        print("📋 Testing Naukri scraping...")
        naukri_jobs = realtime_scraper.scrape_naukri_realtime("python developer")
        print(f"   Naukri: {len(naukri_jobs)} jobs found")
        
        # Test parallel scraping
        print("📋 Testing parallel scraping...")
        start_time = time.time()
        all_jobs = realtime_scraper.scrape_all_platforms_parallel("python developer")
        processing_time = time.time() - start_time
        
        print(f"✅ Parallel scraping completed!")
        print(f"📊 Total jobs: {len(all_jobs)}")
        print(f"⚡ Time: {processing_time:.2f} seconds")
        
        # Show platform breakdown
        platforms = {}
        for job in all_jobs:
            platform = job['source']
            platforms[platform] = platforms.get(platform, 0) + 1
        
        print("📈 Platform breakdown:")
        for platform, count in platforms.items():
            print(f"   {platform}: {count} jobs")
        
        # Show jobs with apply links
        print("\n🔗 Jobs with apply links:")
        jobs_with_links = [job for job in all_jobs if job.get('apply_link')]
        print(f"   {len(jobs_with_links)} out of {len(all_jobs)} jobs have apply links")
        
        for job in jobs_with_links[:3]:
            print(f"   - {job['title']} ({job['source']})")
            print(f"     Link: {job['apply_link']}")
        
        print("\n🎯 SUCCESS: Real-time scraping is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_scraping()
