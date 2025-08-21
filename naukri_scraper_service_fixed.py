"""
Improved Multi-Platform Job Scraper with Better Reliability
Fixed version addressing timeout and platform detection issues
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
import random
import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode, urljoin
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import fake_useragent

app = FastAPI(
    title="Improved Multi-Platform Job Scraper",
    description="Reliable job scraping from major platforms with faster response times",
    version="4.0.0"
)

class ImprovedJobScraper:
    def __init__(self):
        self.ua = fake_useragent.UserAgent()
        self.job_cache = {}
        self.cache_expiry = 300  # 5 minutes cache
        self.timeout = 10  # Reduced timeout for better performance
        
    def get_session(self) -> requests.Session:
        """Create a new session with random headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        })
        return session
    
    def safe_request(self, url: str, headers: dict = None) -> Optional[str]:
        """Make a safe HTTP request with error handling"""
        try:
            session = self.get_session()
            if headers:
                session.headers.update(headers)
            
            # Add small random delay
            time.sleep(random.uniform(0.5, 1.5))
            
            response = session.get(url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ HTTP {response.status_code} for {url}")
                return None
                
        except Exception as e:
            print(f"❌ Request error for {url}: {e}")
            return None
    
    def scrape_indeed(self, keyword: str, location: str = "India") -> List[Dict]:
        """Scrape Indeed with simplified approach"""
        jobs = []
        
        try:
            # Try multiple Indeed URLs
            indeed_urls = [
                f"https://in.indeed.com/jobs?q={quote(keyword)}&l={quote(location)}&sort=date",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l={quote(location)}",
                f"https://indeed.com/jobs?q={quote(keyword)}&l={quote(location)}"
            ]
            
            for url in indeed_urls:
                print(f"🔍 Trying Indeed: {url}")
                
                content = self.safe_request(url, {
                    'Referer': 'https://www.google.com/',
                    'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"'
                })
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Multiple selectors for job cards
                    job_cards = []
                    selectors = [
                        'div[data-jk]',
                        '.job_seen_beacon',
                        'td.resultContent',
                        '.jobsearch-SerpJobCard'
                    ]
                    
                    for selector in selectors:
                        cards = soup.select(selector)
                        if cards:
                            job_cards = cards[:8]
                            print(f"✅ Found {len(job_cards)} Indeed jobs with {selector}")
                            break
                    
                    for i, card in enumerate(job_cards):
                        try:
                            # Title and link
                            title_elem = (card.select_one('h2 a span[title]') or 
                                        card.select_one('h2 a') or 
                                        card.select_one('[data-testid="job-title"]') or
                                        card.select_one('.jobTitle a'))
                            
                            if title_elem:
                                if title_elem.get('title'):
                                    title = title_elem['title']
                                else:
                                    title = title_elem.get_text(strip=True)
                                
                                # Get apply link
                                link_elem = title_elem if title_elem.name == 'a' else title_elem.find_parent('a')
                                apply_link = None
                                if link_elem and link_elem.get('href'):
                                    href = link_elem['href']
                                    if href.startswith('/'):
                                        apply_link = f"https://in.indeed.com{href}"
                                    elif href.startswith('http'):
                                        apply_link = href
                            else:
                                continue
                            
                            # Company
                            company_elem = (card.select_one('[data-testid="company-name"]') or
                                          card.select_one('.companyName') or
                                          card.select_one('span.companyName'))
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            # Location
                            location_elem = (card.select_one('[data-testid="job-location"]') or
                                           card.select_one('.companyLocation'))
                            job_location = location_elem.get_text(strip=True) if location_elem else location
                            
                            # Salary
                            salary_elem = card.select_one('.salaryText') or card.select_one('[data-testid="salary-snippet"]')
                            salary = salary_elem.get_text(strip=True) if salary_elem else "Not disclosed"
                            
                            if title and len(title) > 3:
                                jobs.append({
                                    "id": f"indeed_{int(time.time())}_{i}",
                                    "title": title,
                                    "company": company,
                                    "location": job_location,
                                    "salary": salary,
                                    "apply_link": apply_link or f"https://in.indeed.com/jobs?q={quote(keyword)}",
                                    "source": "indeed",
                                    "scraped_at": datetime.now().isoformat(),
                                    "posted_date": "Recent"
                                })
                                print(f"✅ Added Indeed job: {title}")
                        
                        except Exception as e:
                            print(f"❌ Error processing Indeed job {i}: {e}")
                            continue
                    
                    if jobs:
                        break  # If we got jobs, don't try other URLs
                        
        except Exception as e:
            print(f"❌ Indeed scraping error: {e}")
        
        return jobs
    
    def scrape_naukri(self, keyword: str) -> List[Dict]:
        """Scrape Naukri with simplified approach"""
        jobs = []
        
        try:
            # Try multiple Naukri URLs
            naukri_urls = [
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs",
                f"https://www.naukri.com/jobs-in-india?k={quote(keyword)}",
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-bangalore"
            ]
            
            for url in naukri_urls:
                print(f"🔍 Trying Naukri: {url}")
                
                content = self.safe_request(url, {
                    'Referer': 'https://www.naukri.com/',
                    'Origin': 'https://www.naukri.com'
                })
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Multiple selectors for job cards
                    job_cards = []
                    selectors = [
                        'article.jobTuple',
                        'div.jobTuple',
                        '.srp-jobtuple-wrapper',
                        'article[class*="jobTuple"]'
                    ]
                    
                    for selector in selectors:
                        cards = soup.select(selector)
                        if cards:
                            job_cards = cards[:8]
                            print(f"✅ Found {len(job_cards)} Naukri jobs with {selector}")
                            break
                    
                    for i, card in enumerate(job_cards):
                        try:
                            # Title and link
                            title_elem = (card.select_one('.title a') or
                                        card.select_one('h3 a') or
                                        card.select_one('a[title]'))
                            
                            if title_elem:
                                title = title_elem.get('title') or title_elem.get_text(strip=True)
                                apply_link = title_elem.get('href', '')
                                if apply_link and not apply_link.startswith('http'):
                                    apply_link = f"https://www.naukri.com{apply_link}"
                            else:
                                continue
                            
                            # Company
                            company_elem = (card.select_one('.subTitle a') or
                                          card.select_one('.companyInfo a'))
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            # Location
                            location_elem = card.select_one('.location') or card.select_one('[class*="location"]')
                            location = location_elem.get_text(strip=True) if location_elem else "India"
                            
                            # Experience
                            exp_elem = card.select_one('.experience') or card.select_one('[class*="experience"]')
                            experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                            
                            if title and len(title) > 3:
                                jobs.append({
                                    "id": f"naukri_{int(time.time())}_{i}",
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "experience": experience,
                                    "apply_link": apply_link or f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs",
                                    "source": "naukri",
                                    "scraped_at": datetime.now().isoformat(),
                                    "posted_date": "Recent"
                                })
                                print(f"✅ Added Naukri job: {title}")
                        
                        except Exception as e:
                            print(f"❌ Error processing Naukri job {i}: {e}")
                            continue
                    
                    if jobs:
                        break  # If we got jobs, don't try other URLs
                        
        except Exception as e:
            print(f"❌ Naukri scraping error: {e}")
        
        return jobs
    
    def scrape_linkedin(self, keyword: str) -> List[Dict]:
        """Scrape LinkedIn with simplified approach"""
        jobs = []
        
        try:
            linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={quote(keyword)}&location=India&f_TPR=r86400"
            
            print(f"🔍 Trying LinkedIn: {linkedin_url}")
            
            content = self.safe_request(linkedin_url, {
                'Referer': 'https://www.linkedin.com/',
                'Origin': 'https://www.linkedin.com'
            })
            
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for job cards
                job_cards = soup.find_all('div', class_=re.compile(r'job.*card|result.*card'))
                
                print(f"✅ Found {len(job_cards)} LinkedIn jobs")
                
                for i, card in enumerate(job_cards[:8]):
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
                            continue
                        
                        # Company
                        company_elem = card.find('h4') or card.find('a', class_=re.compile(r'company'))
                        company = company_elem.get_text(strip=True) if company_elem else "N/A"
                        
                        # Location
                        location_elem = card.find('span', string=re.compile(r'[A-Z][a-z]+,'))
                        location = location_elem.get_text(strip=True) if location_elem else "India"
                        
                        if title and len(title) > 3:
                            jobs.append({
                                "id": f"linkedin_{int(time.time())}_{i}",
                                "title": title,
                                "company": company,
                                "location": location,
                                "apply_link": apply_link or f"https://www.linkedin.com/jobs/search?keywords={quote(keyword)}",
                                "source": "linkedin",
                                "scraped_at": datetime.now().isoformat(),
                                "posted_date": "Recent"
                            })
                            print(f"✅ Added LinkedIn job: {title}")
                    
                    except Exception as e:
                        print(f"❌ Error processing LinkedIn job {i}: {e}")
                        continue
                        
        except Exception as e:
            print(f"❌ LinkedIn scraping error: {e}")
        
        return jobs
    
    def scrape_timesjobs(self, keyword: str) -> List[Dict]:
        """Scrape TimesJobs with simplified approach"""
        jobs = []
        
        try:
            # Try multiple TimesJobs URLs
            timesjobs_urls = [
                f"https://www.timesjobs.com/candidate/job-search.html?txtKeywords={quote(keyword)}",
                f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&txtKeywords={quote(keyword)}"
            ]
            
            for url in timesjobs_urls:
                print(f"🔍 Trying TimesJobs: {url}")
                
                content = self.safe_request(url, {
                    'Referer': 'https://www.timesjobs.com/',
                    'Origin': 'https://www.timesjobs.com'
                })
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Multiple selectors for job cards
                    job_cards = []
                    selectors = [
                        'li.clearfix.job-bx',
                        '.job-bx',
                        'li[class*="job-bx"]',
                        'li.clearfix'
                    ]
                    
                    for selector in selectors:
                        cards = soup.select(selector)
                        if cards:
                            job_cards = cards[:6]
                            print(f"✅ Found {len(job_cards)} TimesJobs jobs with {selector}")
                            break
                    
                    for i, card in enumerate(job_cards):
                        try:
                            # Title and link
                            title_elem = (card.select_one('h2 a') or
                                        card.select_one('h3 a') or
                                        card.select_one('.joblist-comp-dtls h2 a'))
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                apply_link = title_elem.get('href', '')
                                if apply_link and not apply_link.startswith('http'):
                                    apply_link = f"https://www.timesjobs.com{apply_link}"
                            else:
                                continue
                            
                            # Company
                            company_elem = (card.select_one('.joblist-comp-name a') or
                                          card.select_one('h3 a'))
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            # Location
                            location_elem = card.select_one('.loc') or card.select_one('[title*="location"]')
                            location = location_elem.get_text(strip=True) if location_elem else "India"
                            
                            # Experience
                            exp_elem = card.select_one('[title*="experience"]')
                            experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                            
                            if title and len(title) > 3:
                                jobs.append({
                                    "id": f"timesjobs_{int(time.time())}_{i}",
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "experience": experience,
                                    "apply_link": apply_link or f"https://www.timesjobs.com/candidate/job-search.html?txtKeywords={quote(keyword)}",
                                    "source": "timesjobs",
                                    "scraped_at": datetime.now().isoformat(),
                                    "posted_date": "Recent"
                                })
                                print(f"✅ Added TimesJobs job: {title}")
                        
                        except Exception as e:
                            print(f"❌ Error processing TimesJobs job {i}: {e}")
                            continue
                    
                    if jobs:
                        break  # If we got jobs, don't try other URLs
                        
        except Exception as e:
            print(f"❌ TimesJobs scraping error: {e}")
        
        return jobs
    
    def scrape_all_platforms(self, keyword: str, location: str = "India") -> List[Dict]:
        """Scrape all platforms with improved reliability"""
        
        # Check cache first
        cache_key = f"{keyword}_{location}".lower()
        if cache_key in self.job_cache:
            cache_time, cached_jobs = self.job_cache[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                print(f"📦 Returning cached results for {keyword}")
                return cached_jobs
        
        print(f"🚀 Scraping jobs for: {keyword}")
        all_jobs = []
        
        # Use ThreadPoolExecutor with reduced timeout for faster response
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit scraping tasks
            future_to_platform = {
                executor.submit(self.scrape_indeed, keyword, location): "indeed",
                executor.submit(self.scrape_naukri, keyword): "naukri",
                executor.submit(self.scrape_linkedin, keyword): "linkedin",
                executor.submit(self.scrape_timesjobs, keyword): "timesjobs"
            }
            
            # Collect results with timeout
            for future in as_completed(future_to_platform, timeout=25):
                platform = future_to_platform[future]
                try:
                    jobs = future.result(timeout=12)
                    if jobs:
                        all_jobs.extend(jobs)
                        print(f"✅ {platform}: {len(jobs)} jobs scraped")
                    else:
                        print(f"⚠️ {platform}: No jobs found")
                except Exception as e:
                    print(f"❌ {platform}: {e}")
        
        # Add fallback apply links
        for job in all_jobs:
            if not job.get('apply_link') or job['apply_link'] == 'N/A':
                title_encoded = quote(job['title'])
                
                if job['source'] == 'indeed':
                    job['apply_link'] = f"https://in.indeed.com/jobs?q={title_encoded}&l={quote(location)}"
                elif job['source'] == 'naukri':
                    job['apply_link'] = f"https://www.naukri.com/jobs-in-india?k={title_encoded}"
                elif job['source'] == 'linkedin':
                    job['apply_link'] = f"https://www.linkedin.com/jobs/search?keywords={title_encoded}&location=India"
                elif job['source'] == 'timesjobs':
                    job['apply_link'] = f"https://www.timesjobs.com/candidate/job-search.html?txtKeywords={title_encoded}"
        
        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        # Sort by scraped time
        unique_jobs.sort(key=lambda x: x['scraped_at'], reverse=True)
        
        # Cache results
        self.job_cache[cache_key] = (time.time(), unique_jobs)
        
        print(f"🎯 Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs

# Global scraper instance
scraper = ImprovedJobScraper()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Improved Multi-Platform Job Scraper",
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Reliable job scraping",
            "4 major platforms (Indeed, Naukri, LinkedIn, TimesJobs)",
            "Faster response times (10-20s)",
            "Apply links included",
            "Parallel processing",
            "Cache optimization"
        ]
    }

@app.get("/scrape-realtime")
async def scrape_realtime_jobs(
    keyword: str = "python developer",
    location: str = "India",
    max_jobs: int = 50
):
    """
    Improved real-time job scraping
    
    Args:
        keyword: Job search keyword
        location: Job location
        max_jobs: Maximum number of jobs to return
    
    Returns:
        Job listings with apply links
    """
    
    start_time = time.time()
    
    try:
        print(f"🔥 Starting improved scraping for: {keyword} in {location}")
        
        # Scrape all platforms
        all_jobs = scraper.scrape_all_platforms(keyword, location)
        
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
                "success_rate": f"{len(platform_stats)}/4 platforms"
            },
            "status": "success",
            "message": f"Found {len(jobs)} job listings with apply links"
        }
        
        print(f"✅ Scraping completed: {len(jobs)} jobs in {results['summary']['processing_time']}s")
        
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
    """Legacy endpoint redirects to improved scraper"""
    return await scrape_realtime_jobs(keyword=keyword)

@app.get("/scrape/")  
async def legacy_scrape(keyword: str = "python developer"):
    """Legacy endpoint redirects to improved scraper"""
    return await scrape_realtime_jobs(keyword=keyword)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
