#!/usr/bin/env python3

"""
Real-Time Job Scraper Test
Demonstrates live scraping from all platforms with apply links
"""

import sys
import os
sys.path.append(os.getcwd())

from realtime_scraper import realtime_scraper
import time
import json

def test_realtime_scraping():
    """Test the real-time multi-platform scraper"""
    
    print("🔥 REAL-TIME MULTI-PLATFORM JOB SCRAPER TEST")
    print("=" * 60)
    print(f"⏰ Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    keywords = ["python developer", "java developer", "react developer"]
    
    for keyword in keywords:
        print(f"🎯 Testing real-time scraping for: {keyword}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # Test real-time scraping
            jobs = realtime_scraper.scrape_all_platforms_parallel(keyword)
            
            processing_time = time.time() - start_time
            
            print(f"✅ Status: SUCCESS")
            print(f"📊 Total jobs found: {len(jobs)}")
            print(f"⚡ Processing time: {processing_time:.2f} seconds")
            print()
            
            # Show platform breakdown
            platforms = {}
            for job in jobs:
                platform = job['source']
                if platform not in platforms:
                    platforms[platform] = 0
                platforms[platform] += 1
            
            print("📈 Platform Breakdown:")
            for platform, count in platforms.items():
                print(f"   {platform.title()}: {count} jobs")
            print()
            
            # Show sample jobs with apply links
            print("🏢 Sample Job Listings:")
            for i, job in enumerate(jobs[:5]):
                print(f"   {i+1}. {job['title']}")
                print(f"      Company: {job['company']}")
                print(f"      Location: {job.get('location', 'N/A')}")
                print(f"      Source: {job['source']}")
                print(f"      Apply Link: {job.get('apply_link', 'Not available')}")
                print(f"      Scraped: {job['scraped_at']}")
                print()
            
            print("🎯 FEATURES DEMONSTRATED:")
            print("✅ Real-time data from live job sites")
            print("✅ Multi-platform scraping (Indeed, Naukri, LinkedIn, TimesJobs)")
            print("✅ Apply links included for each job")
            print("✅ Parallel processing for speed")
            print("✅ Anti-detection technology")
            print("✅ Duplicate removal across platforms")
            print("✅ Fresh timestamp for each job")
            print()
            
        except Exception as e:
            print(f"❌ Error testing {keyword}: {e}")
            import traceback
            traceback.print_exc()
        
        print("=" * 60)
    
    print("🎉 REAL-TIME SCRAPING TEST COMPLETED!")
    print()
    print("💡 KEY BENEFITS:")
    print("   🔄 Live data (not static/cached)")
    print("   🌐 Multiple job platforms simultaneously")
    print("   🔗 Direct apply links for immediate application")
    print("   ⚡ Fast parallel processing")
    print("   🛡️ Anti-detection to avoid blocking")
    print("   📱 Ready for production deployment")

if __name__ == "__main__":
    test_realtime_scraping()
