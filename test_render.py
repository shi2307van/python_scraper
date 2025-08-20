"""
Test the deployed enhanced scraper on Render
"""
import requests
import json

def test_render_deployment():
    base_url = "https://python-scraper-84ov.onrender.com"
    
    print("🚀 Testing Enhanced Scraper on Render")
    print("=" * 50)
    
    try:
        # Test health check
        print("1. Health Check...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📋 Version: {data['version']}")
            print("Features:")
            for feature in data['features']:
                print(f"   • {feature}")
        
        print("\n" + "="*50)
        
        # Test scraping
        print("2. Testing Job Scraping...")
        response = requests.get(
            f"{base_url}/scrape-realtime",
            params={"keyword": "python developer", "max_jobs": 15},
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total jobs: {data['total_jobs']}")
            print(f"⏱️ Response time: {data['response_time_seconds']}s")
            
            # Platform breakdown
            platform_counts = {}
            for job in data['jobs']:
                source = job['source']
                platform_counts[source] = platform_counts.get(source, 0) + 1
            
            print("\n📊 Platform Results:")
            for platform, count in platform_counts.items():
                status = "✅" if count > 0 else "❌"
                print(f"   {status} {platform.title()}: {count} jobs")
            
            if data['jobs']:
                print(f"\n📝 Sample job: {data['jobs'][0]['title']}")
                print(f"   Company: {data['jobs'][0]['company']}")
                print(f"   Apply: {data['jobs'][0]['apply_link']}")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_render_deployment()
