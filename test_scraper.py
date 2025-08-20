#!/usr/bin/env python3

"""
Test script for the advanced job scraper
"""

from advanced_scraper import advanced_scraper
import json

def test_scraper():
    print("🧪 Testing Advanced Job Scraper")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    response = advanced_scraper.safe_request('https://httpbin.org/user-agent')
    if response:
        print("✅ Basic HTTP request working")
        data = response.json()
        print(f"   User-Agent: {data.get('headers', {}).get('User-Agent', 'N/A')[:80]}...")
    else:
        print("❌ Basic HTTP request failed")
    
    # Test 2: Indeed scraping
    print("\n2. Testing Indeed scraping...")
    try:
        indeed_jobs = advanced_scraper.scrape_indeed_advanced('python developer')
        print(f"✅ Indeed jobs found: {len(indeed_jobs)}")
        for i, job in enumerate(indeed_jobs[:3]):
            print(f"   {i+1}. {job['title']} at {job['company']}")
            if job.get('location'):
                print(f"      Location: {job['location']}")
    except Exception as e:
        print(f"❌ Indeed scraping failed: {e}")
    
    # Test 3: Naukri scraping
    print("\n3. Testing Naukri scraping...")
    try:
        naukri_jobs = advanced_scraper.scrape_naukri_advanced('python developer')
        if naukri_jobs:
            print(f"✅ Naukri jobs found: {len(naukri_jobs)}")
            for i, job in enumerate(naukri_jobs[:3]):
                print(f"   {i+1}. {job['title']} at {job['company']}")
        else:
            print("⚠️ Naukri: No jobs found (possibly blocked)")
    except Exception as e:
        print(f"❌ Naukri scraping failed: {e}")
    
    # Test 4: TimesJobs scraping
    print("\n4. Testing TimesJobs scraping...")
    try:
        timesjobs_jobs = advanced_scraper.scrape_timesjobs_advanced('python developer')
        print(f"✅ TimesJobs jobs found: {len(timesjobs_jobs)}")
        for i, job in enumerate(timesjobs_jobs[:3]):
            print(f"   {i+1}. {job['title']} at {job['company']}")
    except Exception as e:
        print(f"❌ TimesJobs scraping failed: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_scraper()
