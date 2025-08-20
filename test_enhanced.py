#!/usr/bin/env python3
"""
Quick test for enhanced multi-platform job scraper
"""
import requests
import json
from datetime import datetime

def test_enhanced_scraper():
    """Test the enhanced scraper locally"""
    
    # Test data
    test_keywords = ["python developer", "data scientist", "software engineer"]
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enhanced Multi-Platform Job Scraper")
    print("=" * 60)
    
    try:
        # Test health check
        print("1. Testing Health Check...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Service Status: {health_data.get('status')}")
            print(f"📋 Features: {len(health_data.get('features', []))}")
            for feature in health_data.get('features', []):
                print(f"   • {feature}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
            
        print("\n" + "="*60)
        
        # Test real-time scraping
        for keyword in test_keywords:
            print(f"\n2. Testing Real-time Scraping: '{keyword}'")
            print("-" * 40)
            
            try:
                response = requests.get(
                    f"{base_url}/scrape-realtime",
                    params={
                        "keyword": keyword,
                        "location": "India",
                        "max_jobs": 20
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    total_jobs = data.get('total_jobs', 0)
                    platforms = data.get('platforms_scraped', [])
                    jobs = data.get('jobs', [])
                    
                    print(f"✅ Total Jobs Found: {total_jobs}")
                    print(f"📊 Platforms Scraped: {len(platforms)}")
                    
                    # Platform breakdown
                    platform_counts = {}
                    for job in jobs:
                        source = job.get('source', 'unknown')
                        platform_counts[source] = platform_counts.get(source, 0) + 1
                    
                    for platform, count in platform_counts.items():
                        print(f"   • {platform.title()}: {count} jobs")
                    
                    # Show sample jobs
                    if jobs:
                        print(f"\n📝 Sample Jobs:")
                        for i, job in enumerate(jobs[:3]):
                            print(f"   {i+1}. {job.get('title', 'N/A')}")
                            print(f"      Company: {job.get('company', 'N/A')}")
                            print(f"      Source: {job.get('source', 'N/A')}")
                            print(f"      Apply: {job.get('apply_link', 'N/A')[:60]}...")
                            
                    print(f"⏱️ Response time: {data.get('response_time_seconds', 'N/A')}s")
                    
                    # Check for successful platforms
                    working_platforms = [p for p, c in platform_counts.items() if c > 0]
                    failed_platforms = [p for p in ['indeed', 'naukri', 'linkedin', 'timesjobs', 'glassdoor'] 
                                      if p not in working_platforms]
                    
                    if working_platforms:
                        print(f"✅ Working platforms: {', '.join(working_platforms)}")
                    if failed_platforms:
                        print(f"⚠️ Failed platforms: {', '.join(failed_platforms)}")
                        
                else:
                    print(f"❌ Scraping failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                    
            except requests.exceptions.Timeout:
                print("⏰ Request timeout (>30s)")
            except Exception as e:
                print(f"❌ Test error: {e}")
                
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Test suite error: {e}")

if __name__ == "__main__":
    test_enhanced_scraper()
