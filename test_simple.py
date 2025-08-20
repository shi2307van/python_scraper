from simple_scraper import simple_scraper

print("Testing simple scraper...")
jobs = simple_scraper.scrape_indeed_simple('python developer')
print(f'Simple scraper found {len(jobs)} jobs')

for i, job in enumerate(jobs[:3]):
    print(f"  {i+1}. {job['title']} at {job['company']}")

# Test sample data
print("\nTesting sample data...")
sample_jobs = simple_scraper.create_sample_jobs('python developer')
print(f'Sample jobs: {len(sample_jobs)}')
for job in sample_jobs[:3]:
    print(f"  - {job['title']} at {job['company']}")
