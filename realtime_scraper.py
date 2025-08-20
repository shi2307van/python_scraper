"""
Real-Time Multi-Platform Job Scraper
Scrapes live job data from all major platforms simultaneously
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
import random
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode, urljoin
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import re
import cloudscraper
import fake_useragent
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

app = FastAPI(
    title="Real-Time Multi-Platform Job Scraper",
    description="Live job scraping from all major platforms with apply links",
    version="3.0.0"
)

class RealTimeJobScraper:
    def __init__(self):
        self.session = None
        self.user_agent_rotator = fake_useragent.UserAgent()
        self.setup_session()
        self.job_cache = {}
        self.cache_expiry = 300  # 5 minutes cache
        
    def setup_session(self):
        """Setup session with anti-detection"""
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
    
    def get_random_headers(self):
        """Get randomized headers"""
        return {
            'User-Agent': self.user_agent_rotator.random,
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.8'
            ])
        }
    
    def safe_request(self, url: str, max_retries: int = 2) -> Optional[requests.Response]:
        """Make safe request with retries"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(0.5, 1.5))
                self.session.headers.update(self.get_random_headers())
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200 and len(response.text) > 1000:
                    return response
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(1, 3))
                    self.setup_session()
        return None
    
    def scrape_indeed_realtime(self, keyword: str, location: str = "India") -> List[Dict]:
        """Real-time Indeed scraping"""
        jobs = []
        
        try:
            indeed_urls = [
                f"https://in.indeed.com/jobs?q={quote(keyword)}&l={quote(location)}&sort=date",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l={quote(location)}&sort=date",
                f"https://indeed.com/jobs?q={quote(keyword)}&l={quote(location)}&fromage=1"
            ]
            
            for url in indeed_urls:
                print(f"🔍 Scraping Indeed: {url}")
                response = self.safe_request(url)
                
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Multiple job selectors
                    job_cards = (soup.find_all('div', {'data-jk': True}) or
                               soup.find_all('div', class_=re.compile(r'job.*card|result.*item')))
                    
                    print(f"Found {len(job_cards)} Indeed job cards")
                    
                    for card in job_cards[:10]:
                        try:
                            # Title and link
                            title_elem = card.find('h2') or card.find('a', {'data-testid': 'job-title'})
                            if title_elem:
                                title_link = title_elem.find('a') if title_elem.find('a') else title_elem
                                title = title_link.get_text(strip=True)
                                
                                # Apply link
                                apply_link = None
                                if title_link.get('href'):
                                    href = title_link['href']
                                    if href.startswith('/'):
                                        apply_link = urljoin('https://in.indeed.com', href)
                                    elif href.startswith('http'):
                                        apply_link = href
                                    else:
                                        apply_link = f"https://in.indeed.com{href}"
                                
                                # Company
                                company_elem = (card.find('span', {'data-testid': 'company-name'}) or
                                              card.find('a', class_='companyName') or
                                              card.find('span', class_='companyName'))
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                
                                # Location
                                location_elem = (card.find('div', {'data-testid': 'job-location'}) or
                                               card.find('div', class_='companyLocation'))
                                job_location = location_elem.get_text(strip=True) if location_elem else location
                                
                                # Salary
                                salary_elem = card.find('span', class_='salaryText')
                                salary = salary_elem.get_text(strip=True) if salary_elem else "Not disclosed"
                                
                                # Description snippet
                                desc_elem = card.find('div', class_='summary') or card.find('div', class_='job-snippet')
                                description = desc_elem.get_text(strip=True)[:200] + "..." if desc_elem else "No description available"
                                
                                if title and len(title) > 3:
                                    jobs.append({
                                        "id": f"indeed_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": job_location,
                                        "salary": salary,
                                        "description": description,
                                        "apply_link": apply_link,
                                        "source": "indeed",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": "Recent"
                                    })
                        
                        except Exception as e:
                            continue
                    
                    if jobs:
                        break
                        
        except Exception as e:
            print(f"❌ Indeed error: {e}")
        
        return jobs
    
    def scrape_naukri_realtime(self, keyword: str) -> List[Dict]:
        """Real-time Naukri scraping"""
        jobs = []
        
        try:
            naukri_urls = [
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs?sort=1",  # Sort by latest
                f"https://www.naukri.com/jobs-in-india?k={quote(keyword)}&sort=1",
                f"https://www.naukri.com/{quote(keyword)}-jobs-in-india"
            ]
            
            for url in naukri_urls:
                print(f"🔍 Scraping Naukri: {url}")
                
                # Enhanced headers for Naukri
                naukri_headers = self.get_random_headers()
                naukri_headers.update({
                    'Referer': 'https://www.naukri.com/',
                    'Origin': 'https://www.naukri.com'
                })
                
                self.session.headers.update(naukri_headers)
                response = self.safe_request(url)
                
                if response and "access denied" not in response.text.lower():
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Naukri job selectors
                    job_cards = (soup.find_all('article', class_=re.compile(r'jobTuple')) or
                               soup.find_all('div', class_=re.compile(r'jobTuple')))
                    
                    print(f"Found {len(job_cards)} Naukri job cards")
                    
                    for card in job_cards[:8]:
                        try:
                            # Title and link
                            title_elem = card.find('a', class_=re.compile(r'title'))
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                apply_link = urljoin('https://www.naukri.com', title_elem['href']) if title_elem.get('href') else None
                                
                                # Company
                                company_elem = card.find('a', class_=re.compile(r'subTitle'))
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                
                                # Experience
                                exp_elem = card.find('span', class_=re.compile(r'experience'))
                                experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                                
                                # Salary
                                salary_elem = card.find('span', class_=re.compile(r'salary'))
                                salary = salary_elem.get_text(strip=True) if salary_elem else "Not disclosed"
                                
                                # Location
                                location_elem = card.find('span', class_=re.compile(r'location'))
                                location = location_elem.get_text(strip=True) if location_elem else "India"
                                
                                # Skills
                                skills_elems = card.find_all('span', class_=re.compile(r'skill'))
                                skills = [skill.get_text(strip=True) for skill in skills_elems[:5]]
                                
                                if title and len(title) > 3:
                                    jobs.append({
                                        "id": f"naukri_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": location,
                                        "salary": salary,
                                        "experience": experience,
                                        "skills": skills,
                                        "apply_link": apply_link,
                                        "source": "naukri",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": "Recent"
                                    })
                        
                        except Exception as e:
                            continue
                    
                    if jobs:
                        break
                        
        except Exception as e:
            print(f"❌ Naukri error: {e}")
        
        return jobs
    
    def scrape_linkedin_realtime(self, keyword: str) -> List[Dict]:
        """Real-time LinkedIn scraping"""
        jobs = []
        
        try:
            linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={quote(keyword)}&location=India&f_TPR=r86400"  # Last 24 hours
            
            print(f"🔍 Scraping LinkedIn: {linkedin_url}")
            response = self.safe_request(linkedin_url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # LinkedIn job cards
                job_cards = soup.find_all('div', class_=re.compile(r'job.*card|result.*card'))
                
                print(f"Found {len(job_cards)} LinkedIn job cards")
                
                for card in job_cards[:8]:
                    try:
                            # Title and link
                            title_elem = card.find('h3') or card.find('a', string=re.compile(keyword.split()[0], re.I))
                            if title_elem:
                                title_link = title_elem.find('a') if title_elem.find('a') else title_elem
                                title = title_link.get_text(strip=True)
                                
                                apply_link = None
                                if title_link.get('href'):
                                    href = title_link['href']
                                    if href.startswith('/'):
                                        apply_link = urljoin('https://www.linkedin.com', href)
                                    elif href.startswith('http'):
                                        apply_link = href
                                    else:
                                        apply_link = f"https://www.linkedin.com{href}"
                            
                            # Company
                            company_elem = card.find('h4') or card.find('a', class_=re.compile(r'company'))
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            # Location
                            location_elem = card.find('span', string=re.compile(r'[A-Z][a-z]+,'))
                            location = location_elem.get_text(strip=True) if location_elem else "India"
                            
                            if title and len(title) > 3:
                                jobs.append({
                                    "id": f"linkedin_{int(time.time())}_{len(jobs)}",
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "apply_link": apply_link,
                                    "source": "linkedin",
                                    "scraped_at": datetime.now().isoformat(),
                                    "posted_date": "Recent"
                                })
                    
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"❌ LinkedIn error: {e}")
        
        return jobs
    
    def scrape_timesjobs_realtime(self, keyword: str) -> List[Dict]:
        """Real-time TimesJobs scraping"""
        jobs = []
        
        try:
            params = {
                'searchType': 'personalizedSearch',
                'from': 'submit',
                'txtKeywords': keyword,
                'cboWorkExp1': '0',
                'cboWorkExp2': '30',
                'sortBy': '1'  # Sort by latest
            }
            
            url = f"https://www.timesjobs.com/candidate/job-search.html?{urlencode(params)}"
            print(f"🔍 Scraping TimesJobs: {url}")
            
            response = self.safe_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
                print(f"Found {len(job_cards)} TimesJobs cards")
                
                for card in job_cards[:8]:
                    try:
                        # Title and link
                        title_elem = card.find('h2')
                        if title_elem:
                            title_link = title_elem.find('a')
                            if title_link:
                                title = title_link.get_text(strip=True)
                                apply_link = urljoin('https://www.timesjobs.com', title_link['href']) if title_link.get('href') else None
                                
                                # Company
                                company_elem = card.find('h3', class_='joblist-comp-name')
                                company = company_elem.find('a').get_text(strip=True) if company_elem and company_elem.find('a') else "N/A"
                                
                                # Experience
                                exp_elem = card.find('span', string=re.compile(r'\d+.*year'))
                                experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                                
                                # Location
                                location_elem = card.find('span', class_='loc')
                                location = location_elem.get_text(strip=True) if location_elem else "India"
                                
                                # Posted date
                                posted_elem = card.find('span', class_='sim-posted')
                                posted_date = posted_elem.get_text(strip=True) if posted_elem else "Recent"
                                
                                if title and len(title) > 3:
                                    jobs.append({
                                        "id": f"timesjobs_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": location,
                                        "experience": experience,
                                        "apply_link": apply_link,
                                        "source": "timesjobs",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": posted_date
                                    })
                    
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"❌ TimesJobs error: {e}")
        
        return jobs
    
    def scrape_all_platforms_parallel(self, keyword: str, location: str = "India") -> List[Dict]:
        """Scrape all platforms in parallel for real-time data"""
        
        # Check cache first
        cache_key = f"{keyword}_{location}".lower()
        if cache_key in self.job_cache:
            cache_time, cached_jobs = self.job_cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                print(f"📦 Returning cached results for {keyword}")
                return cached_jobs
        
        print(f"🚀 Real-time scraping for: {keyword}")
        all_jobs = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all scraping tasks
            future_to_platform = {
                executor.submit(self.scrape_indeed_realtime, keyword, location): "indeed",
                executor.submit(self.scrape_naukri_realtime, keyword): "naukri",
                executor.submit(self.scrape_linkedin_realtime, keyword): "linkedin",
                executor.submit(self.scrape_timesjobs_realtime, keyword): "timesjobs"
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_platform, timeout=30):
                platform = future_to_platform[future]
                try:
                    jobs = future.result()
                    if jobs:
                        all_jobs.extend(jobs)
                        print(f"✅ {platform}: {len(jobs)} jobs scraped")
                    else:
                        print(f"⚠️ {platform}: No jobs found")
                except Exception as e:
                    print(f"❌ {platform}: {e}")
        
        # Add apply links for jobs that don't have them
        for job in all_jobs:
            if not job.get('apply_link'):
                # Generate search links as fallback
                title_encoded = quote(job['title'])
                company_encoded = quote(job['company'])
                
                if job['source'] == 'indeed':
                    job['apply_link'] = f"https://in.indeed.com/jobs?q={title_encoded}&l={quote(location)}"
                elif job['source'] == 'naukri':
                    job['apply_link'] = f"https://www.naukri.com/jobs-in-india?k={title_encoded}"
                elif job['source'] == 'linkedin':
                    job['apply_link'] = f"https://www.linkedin.com/jobs/search?keywords={title_encoded}&location=India"
                elif job['source'] == 'timesjobs':
                    job['apply_link'] = f"https://www.timesjobs.com/candidate/job-search.html?txtKeywords={title_encoded}"
        
        # Remove duplicates based on title and company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        # Sort by scraped time (most recent first)
        unique_jobs.sort(key=lambda x: x['scraped_at'], reverse=True)
        
        # Cache the results
        self.job_cache[cache_key] = (time.time(), unique_jobs)
        
        print(f"🎯 Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs

# Global scraper instance
realtime_scraper = RealTimeJobScraper()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Real-Time Multi-Platform Job Scraper",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Real-time job scraping",
            "Multi-platform support (Indeed, Naukri, LinkedIn, TimesJobs)",
            "Apply links included",
            "Parallel processing",
            "Cache optimization",
            "Anti-detection technology"
        ]
    }

@app.get("/scrape-realtime")
async def scrape_realtime_jobs(
    keyword: str = "python developer",
    location: str = "India",
    max_jobs: int = 50
):
    """
    Real-time job scraping from all platforms
    
    Args:
        keyword: Job search keyword
        location: Job location
        max_jobs: Maximum number of jobs to return
    
    Returns:
        Real-time job listings with apply links
    """
    
    start_time = time.time()
    
    try:
        print(f"🔥 Starting real-time scraping for: {keyword} in {location}")
        
        # Scrape all platforms in parallel
        all_jobs = realtime_scraper.scrape_all_platforms_parallel(keyword, location)
        
        # Limit results
        jobs = all_jobs[:max_jobs]
        
        # Compile statistics
        platform_stats = {}
        for job in jobs:
            platform = job['source']
            if platform not in platform_stats:
                platform_stats[platform] = 0
            platform_stats[platform] += 1
        
        results = {
            "keyword": keyword,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "jobs": jobs,
            "summary": {
                "total_jobs": len(jobs),
                "platform_breakdown": platform_stats,
                "processing_time": round(time.time() - start_time, 2),
                "data_freshness": "real-time",
                "cache_status": "fresh" if len(all_jobs) > 0 else "cached"
            },
            "status": "success",
            "message": f"Found {len(jobs)} real-time job listings with apply links"
        }
        
        print(f"✅ Real-time scraping completed: {len(jobs)} jobs in {results['summary']['processing_time']}s")
        
        return JSONResponse(content=results)
    
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "keyword": keyword,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "processing_time": round(time.time() - start_time, 2)
            },
            status_code=500
        )

# Legacy endpoints
@app.get("/scrape-jobs")
async def legacy_scrape_jobs(keyword: str = "python developer"):
    """Legacy endpoint redirects to real-time scraper"""
    return await scrape_realtime_jobs(keyword=keyword)

@app.get("/scrape/")  
async def legacy_scrape(keyword: str = "python developer"):
    """Legacy endpoint redirects to real-time scraper"""
    return await scrape_realtime_jobs(keyword=keyword)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
