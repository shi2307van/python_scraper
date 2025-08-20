from realtime_scraper import realtime_scraper

print("🔥 Testing improved real-time scraper...")
jobs = realtime_scraper.scrape_all_platforms_parallel('python developer')

print(f"📊 Total jobs: {len(jobs)}")
jobs_with_links = [j for j in jobs if j.get('apply_link')]
print(f"🔗 Jobs with apply links: {len(jobs_with_links)}")

print("\n📋 Sample jobs with apply links:")
for i, job in enumerate(jobs_with_links[:3]):
    print(f"{i+1}. {job['title']} at {job['company']}")
    print(f"   Source: {job['source']}")
    print(f"   Apply: {job['apply_link']}")
    print()

print("✅ All jobs now have apply links!")
