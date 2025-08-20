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
        """Setup session with enhanced anti-detection"""
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=random.uniform(1, 3)
        )
        
        # More realistic headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
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
    
    def safe_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Enhanced safe request with better retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                # Random delay between requests
                time.sleep(random.uniform(1, 3))
                
                # Rotate user agent and headers
                self.session.headers.update(self.get_random_headers())
                self.session.headers['User-Agent'] = self.ua.random
                
                # Make request with longer timeout
                response = self.session.get(url, timeout=15, allow_redirects=True)
                
                # Check for successful response
                if response.status_code == 200:
                    # Validate response content
                    if len(response.text) > 1000 and not any(blocked in response.text.lower() for blocked in [
                        'access denied', 'blocked', 'captcha', 'robot', 'bot detection',
                        'please verify', 'security check', 'unusual traffic'
                    ]):
                        return response
                    else:
                        print(f"⚠️ Response may be blocked or invalid (length: {len(response.text)})")
                
                elif response.status_code == 403:
                    print(f"❌ Access forbidden (403) for {url}")
                elif response.status_code == 429:
                    print(f"❌ Rate limited (429) for {url}")
                    time.sleep(random.uniform(5, 10))  # Longer wait for rate limiting
                else:
                    print(f"❌ HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt + 1} for {url}")
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error on attempt {attempt + 1} for {url}")
            except Exception as e:
                print(f"❌ Request error on attempt {attempt + 1}: {e}")
                
            # If not the last attempt, wait and recreate session
            if attempt < max_retries - 1:
                wait_time = random.uniform(2, 5) * (attempt + 1)  # Exponential backoff
                print(f"⏳ Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
                self.setup_session()  # Fresh session
                
        print(f"❌ All {max_retries} attempts failed for {url}")
        return None
    
    def scrape_indeed_realtime(self, keyword: str, location: str = "India") -> List[Dict]:
        """Enhanced real-time Indeed scraping with better anti-detection"""
        jobs = []
        
        try:
            # Multiple Indeed domains and URL patterns
            indeed_urls = [
                f"https://in.indeed.com/jobs?q={quote(keyword)}&l={quote(location)}&sort=date",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l={quote(location)}&sort=date",
                f"https://indeed.com/jobs?q={quote(keyword)}&l={quote(location)}&fromage=1",
                f"https://in.indeed.com/jobs?q={quote(keyword)}&l=India&fromage=1&sort=date",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l=Mumbai&sort=date",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l=Bangalore&sort=date",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l=Delhi&sort=date"
            ]
            
            for url in indeed_urls:
                try:
                    print(f"🔍 Scraping Indeed: {url}")
                    
                    # Enhanced headers specifically for Indeed
                    indeed_headers = self.get_random_headers()
                    indeed_headers.update({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'Referer': 'https://www.google.com/',
                        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Windows"'
                    })
                    
                    self.session.headers.update(indeed_headers)
                    
                    # Random delay
                    time.sleep(random.uniform(3, 6))
                    
                    response = self.safe_request(url)
                    
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Multiple job card selectors to try
                        job_selectors = [
                            'div[data-jk]',
                            '.jobsearch-SerpJobCard',
                            '.result',
                            'div[class*="job"]',
                            '.jobsearch-result',
                            'div[class*="result"]'
                        ]
                        
                        job_cards = []
                        for selector in job_selectors:
                            cards = soup.select(selector)
                            if cards:
                                print(f"✅ Found {len(cards)} job cards with selector: {selector}")
                                job_cards = cards
                                break
                        
                        print(f"📝 Processing {len(job_cards)} Indeed job cards")
                        
                        for i, card in enumerate(job_cards[:10]):
                            try:
                                # Multiple title selectors
                                title_elem = None
                                apply_link = None
                                
                                title_selectors = [
                                    'h2 a[data-testid="job-title"]',
                                    'h2 a',
                                    'a[data-testid="job-title"]',
                                    '.jobTitle a',
                                    'h3 a',
                                    'a[title]'
                                ]
                                
                                for t_sel in title_selectors:
                                    elem = card.select_one(t_sel)
                                    if elem and elem.get_text(strip=True):
                                        title_elem = elem
                                        apply_link = elem.get('href', '')
                                        if apply_link and apply_link.startswith('/'):
                                            apply_link = urljoin('https://in.indeed.com', apply_link)
                                        elif apply_link and not apply_link.startswith('http'):
                                            apply_link = f"https://in.indeed.com{apply_link}"
                                        break
                                
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                
                                # Company selectors
                                company_elem = None
                                company_selectors = [
                                    'span[data-testid="company-name"]',
                                    '.companyName',
                                    'a.companyName',
                                    'span.companyName',
                                    '.company',
                                    'div[data-testid="company-name"]'
                                ]
                                
                                for c_sel in company_selectors:
                                    elem = card.select_one(c_sel)
                                    if elem and elem.get_text(strip=True):
                                        company_elem = elem
                                        break
                                
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                
                                # Location selectors
                                location_elem = None
                                location_selectors = [
                                    'div[data-testid="job-location"]',
                                    '.companyLocation',
                                    '.locationsContainer',
                                    'div[data-testid="companyLocation"]'
                                ]
                                
                                for l_sel in location_selectors:
                                    elem = card.select_one(l_sel)
                                    if elem and elem.get_text(strip=True):
                                        location_elem = elem
                                        break
                                
                                job_location = location_elem.get_text(strip=True) if location_elem else location
                                
                                # Salary selectors
                                salary_elem = None
                                salary_selectors = [
                                    '.salaryText',
                                    'span[data-testid="salary-snippet"]',
                                    '.salary-snippet',
                                    '.salary'
                                ]
                                
                                for s_sel in salary_selectors:
                                    elem = card.select_one(s_sel)
                                    if elem and elem.get_text(strip=True):
                                        salary_elem = elem
                                        break
                                
                                salary = salary_elem.get_text(strip=True) if salary_elem else "Not disclosed"
                                
                                # Description selectors
                                desc_elem = None
                                desc_selectors = [
                                    '.summary',
                                    '.job-snippet',
                                    'div[data-testid="job-snippet"]',
                                    '.jobDescription'
                                ]
                                
                                for d_sel in desc_selectors:
                                    elem = card.select_one(d_sel)
                                    if elem and elem.get_text(strip=True):
                                        desc_elem = elem
                                        break
                                
                                description = desc_elem.get_text(strip=True)[:200] + "..." if desc_elem else "No description available"
                                
                                if title and len(title) > 3:
                                    job_data = {
                                        "id": f"indeed_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": job_location,
                                        "salary": salary,
                                        "description": description,
                                        "apply_link": apply_link or f"https://in.indeed.com/jobs?q={quote(keyword)}",
                                        "source": "indeed",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": "Recent"
                                    }
                                    jobs.append(job_data)
                                    print(f"✅ Added Indeed job: {title}")
                            
                            except Exception as e:
                                print(f"❌ Error processing Indeed job card {i}: {e}")
                                continue
                        
                        if jobs:
                            print(f"✅ Successfully scraped {len(jobs)} jobs from Indeed")
                            break
                    else:
                        print(f"❌ Indeed request failed for {url}")
                        
                except Exception as e:
                    print(f"❌ Error with Indeed URL {url}: {e}")
                    continue
                        
        except Exception as e:
            print(f"❌ Indeed error: {e}")
        
        return jobs
    
    def scrape_naukri_realtime(self, keyword: str) -> List[Dict]:
        """Enhanced real-time Naukri scraping with multiple fallbacks"""
        jobs = []
        
        try:
            # Multiple URL patterns for better coverage
            naukri_urls = [
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs?sort=1",  # Sort by latest
                f"https://www.naukri.com/jobs-in-india?k={quote(keyword)}&sort=1",
                f"https://www.naukri.com/{quote(keyword)}-jobs-in-india",
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-bangalore",
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-delhi",
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-mumbai",
                f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-hyderabad"
            ]
            
            for url in naukri_urls:
                try:
                    print(f"🔍 Scraping Naukri: {url}")
                    
                    # Enhanced headers for Naukri with session rotation
                    naukri_headers = self.get_random_headers()
                    naukri_headers.update({
                        'Referer': 'https://www.naukri.com/',
                        'Origin': 'https://www.naukri.com',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Windows"'
                    })
                    
                    self.session.headers.update(naukri_headers)
                    
                    # Add random delay
                    time.sleep(random.uniform(2, 5))
                    
                    response = self.safe_request(url)
                    
                    if response and response.status_code == 200 and "access denied" not in response.text.lower():
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Multiple job card selectors to try
                        job_selectors = [
                            'article[class*="jobTuple"]',
                            'div[class*="jobTuple"]',
                            '.srp-jobtuple-wrapper',
                            'article.jobTuple',
                            '.job-tuple',
                            '[data-job-id]',
                            '.jobTupleHeader'
                        ]
                        
                        job_cards = []
                        for selector in job_selectors:
                            cards = soup.select(selector)
                            if cards:
                                print(f"✅ Found {len(cards)} job cards with selector: {selector}")
                                job_cards = cards
                                break
                        
                        print(f"📝 Processing {len(job_cards)} Naukri job cards")
                        
                        for i, card in enumerate(job_cards[:10]):  # Limit to 10 jobs
                            try:
                                # Multiple title selectors
                                title_elem = None
                                apply_link = None
                                
                                # Try different title selectors
                                title_selectors = [
                                    'a[class*="title"]',
                                    '.title a',
                                    'h3 a',
                                    'a[title]',
                                    '.jobTitle a',
                                    'h2 a'
                                ]
                                
                                for t_sel in title_selectors:
                                    elem = card.select_one(t_sel)
                                    if elem and elem.get_text(strip=True):
                                        title_elem = elem
                                        apply_link = elem.get('href', '')
                                        if apply_link and not apply_link.startswith('http'):
                                            apply_link = urljoin('https://www.naukri.com', apply_link)
                                        break
                                
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                
                                # Company selectors
                                company_elem = None
                                company_selectors = [
                                    'a[class*="subTitle"]',
                                    '.companyInfo a',
                                    '.company-name',
                                    '.subTitle a',
                                    '.comp-name'
                                ]
                                
                                for c_sel in company_selectors:
                                    elem = card.select_one(c_sel)
                                    if elem and elem.get_text(strip=True):
                                        company_elem = elem
                                        break
                                
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                
                                # Experience selectors
                                exp_elem = None
                                exp_selectors = [
                                    'span[class*="experience"]',
                                    '.experience',
                                    '.exp',
                                    '.expwdth'
                                ]
                                
                                for e_sel in exp_selectors:
                                    elem = card.select_one(e_sel)
                                    if elem and elem.get_text(strip=True):
                                        exp_elem = elem
                                        break
                                
                                experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                                
                                # Salary selectors
                                salary_elem = None
                                salary_selectors = [
                                    'span[class*="salary"]',
                                    '.salary',
                                    '.sal'
                                ]
                                
                                for s_sel in salary_selectors:
                                    elem = card.select_one(s_sel)
                                    if elem and elem.get_text(strip=True):
                                        salary_elem = elem
                                        break
                                
                                salary = salary_elem.get_text(strip=True) if salary_elem else "Not disclosed"
                                
                                # Location selectors
                                location_elem = None
                                location_selectors = [
                                    'span[class*="location"]',
                                    '.location',
                                    '.locationsContainer span',
                                    '.jobTupleFooter .location'
                                ]
                                
                                for l_sel in location_selectors:
                                    elem = card.select_one(l_sel)
                                    if elem and elem.get_text(strip=True):
                                        location_elem = elem
                                        break
                                
                                location = location_elem.get_text(strip=True) if location_elem else "India"
                                
                                # Skills selectors
                                skills_elems = card.select('span[class*="skill"]') or card.select('.skill')
                                skills = [skill.get_text(strip=True) for skill in skills_elems[:5]]
                                
                                if title and len(title) > 3:
                                    job_data = {
                                        "id": f"naukri_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": location,
                                        "salary": salary,
                                        "experience": experience,
                                        "skills": skills,
                                        "apply_link": apply_link or f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs",
                                        "source": "naukri",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": "Recent"
                                    }
                                    jobs.append(job_data)
                                    print(f"✅ Added Naukri job: {title}")
                            
                            except Exception as e:
                                print(f"❌ Error processing Naukri job card {i}: {e}")
                                continue
                        
                        if jobs:
                            print(f"✅ Successfully scraped {len(jobs)} jobs from Naukri")
                            break
                    else:
                        print(f"❌ Naukri request failed for {url}")
                        
                except Exception as e:
                    print(f"❌ Error with Naukri URL {url}: {e}")
                    continue
                        
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
        """Enhanced real-time TimesJobs scraping with multiple fallbacks"""
        jobs = []
        
        try:
            # Multiple URL patterns for TimesJobs
            timesjobs_urls = [
                # Basic search with sorting
                f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={quote(keyword)}&cboWorkExp1=0&cboWorkExp2=30&sortBy=1",
                # Alternative search patterns
                f"https://www.timesjobs.com/candidate/job-search.html?searchType=Home_Search&from=submit&txtKeywords={quote(keyword)}&sortBy=1",
                # Location-specific searches
                f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={quote(keyword)}&txtLocation=India&sortBy=1",
                f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={quote(keyword)}&txtLocation=Mumbai&sortBy=1",
                f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={quote(keyword)}&txtLocation=Bangalore&sortBy=1"
            ]
            
            for url in timesjobs_urls:
                try:
                    print(f"🔍 Scraping TimesJobs: {url}")
                    
                    # Enhanced headers for TimesJobs
                    timesjobs_headers = self.get_random_headers()
                    timesjobs_headers.update({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'Referer': 'https://www.timesjobs.com/',
                        'Origin': 'https://www.timesjobs.com'
                    })
                    
                    self.session.headers.update(timesjobs_headers)
                    
                    # Random delay
                    time.sleep(random.uniform(2, 5))
                    
                    response = self.safe_request(url)
                    
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Multiple job card selectors
                        job_selectors = [
                            'li.clearfix.job-bx.wht-shd-bx',
                            '.job-bx',
                            'li[class*="job-bx"]',
                            '.clearfix.job-bx',
                            'li.clearfix'
                        ]
                        
                        job_cards = []
                        for selector in job_selectors:
                            cards = soup.select(selector)
                            if cards:
                                print(f"✅ Found {len(cards)} job cards with selector: {selector}")
                                job_cards = cards
                                break
                        
                        print(f"📝 Processing {len(job_cards)} TimesJobs cards")
                        
                        for i, card in enumerate(job_cards[:10]):
                            try:
                                # Multiple title selectors
                                title_elem = None
                                apply_link = None
                                
                                title_selectors = [
                                    'h2 a',
                                    '.joblist-comp-dtls h2 a',
                                    'h3 a',
                                    '.job-title a'
                                ]
                                
                                for t_sel in title_selectors:
                                    elem = card.select_one(t_sel)
                                    if elem and elem.get_text(strip=True):
                                        title_elem = elem
                                        apply_link = elem.get('href', '')
                                        if apply_link and not apply_link.startswith('http'):
                                            apply_link = urljoin('https://www.timesjobs.com', apply_link)
                                        break
                                
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                
                                # Company selectors
                                company_elem = None
                                company_selectors = [
                                    'h3.joblist-comp-name a',
                                    '.joblist-comp-name a',
                                    '.company-name a',
                                    'h3 a'
                                ]
                                
                                for c_sel in company_selectors:
                                    elem = card.select_one(c_sel)
                                    if elem and elem.get_text(strip=True):
                                        company_elem = elem
                                        break
                                
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                
                                # Experience selectors
                                exp_elem = None
                                exp_selectors = [
                                    'span[title*="experience"]',
                                    'li[title*="experience"]',
                                    '.rec-detail span'
                                ]
                                
                                for e_sel in exp_selectors:
                                    elem = card.select_one(e_sel)
                                    if elem and "year" in elem.get_text().lower():
                                        exp_elem = elem
                                        break
                                
                                experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                                
                                # Location selectors
                                location_elem = None
                                location_selectors = [
                                    'span.loc',
                                    '.location',
                                    'span[title*="location"]',
                                    'li[title*="location"]'
                                ]
                                
                                for l_sel in location_selectors:
                                    elem = card.select_one(l_sel)
                                    if elem and elem.get_text(strip=True):
                                        location_elem = elem
                                        break
                                
                                location = location_elem.get_text(strip=True) if location_elem else "India"
                                
                                # Posted date selectors
                                posted_elem = None
                                posted_selectors = [
                                    'span.sim-posted',
                                    '.posted-date',
                                    'span[title*="posted"]'
                                ]
                                
                                for p_sel in posted_selectors:
                                    elem = card.select_one(p_sel)
                                    if elem and elem.get_text(strip=True):
                                        posted_elem = elem
                                        break
                                
                                posted_date = posted_elem.get_text(strip=True) if posted_elem else "Recent"
                                
                                # Skills selectors
                                skills_elems = card.select('.rec-detail span') or card.select('.skills span')
                                skills = [skill.get_text(strip=True) for skill in skills_elems[:5] if skill.get_text(strip=True)]
                                
                                if title and len(title) > 3:
                                    job_data = {
                                        "id": f"timesjobs_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": location,
                                        "experience": experience,
                                        "skills": skills,
                                        "apply_link": apply_link or f"https://www.timesjobs.com/candidate/job-search.html?txtKeywords={quote(keyword)}",
                                        "source": "timesjobs",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": posted_date
                                    }
                                    jobs.append(job_data)
                                    print(f"✅ Added TimesJobs job: {title}")
                            
                            except Exception as e:
                                print(f"❌ Error processing TimesJobs job card {i}: {e}")
                                continue
                        
                        if jobs:
                            print(f"✅ Successfully scraped {len(jobs)} jobs from TimesJobs")
                            break
                    else:
                        print(f"❌ TimesJobs request failed for {url}")
                        
                except Exception as e:
                    print(f"❌ Error with TimesJobs URL {url}: {e}")
                    continue
                        
        except Exception as e:
            print(f"❌ TimesJobs error: {e}")
        
        return jobs
    
    def scrape_glassdoor_realtime(self, keyword: str) -> List[Dict]:
        """Enhanced real-time Glassdoor scraping"""
        jobs = []
        
        try:
            # Multiple Glassdoor URL patterns
            glassdoor_urls = [
                f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={quote(keyword)}&locT=N&locId=115&sc.sortBy=1",
                f"https://www.glassdoor.com/Job/india-{keyword.replace(' ', '-')}-jobs-SRCH_IL.0,5_IN115_KO6,{6+len(keyword)}.htm",
                f"https://www.glassdoor.co.in/Job/india-{keyword.replace(' ', '-')}-jobs-SRCH_IL.0,5_IN115_KO6,{6+len(keyword)}.htm",
                f"https://www.glassdoor.co.in/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={quote(keyword)}&sc.keyword={quote(keyword)}&locT=N&locId=115"
            ]
            
            for url in glassdoor_urls:
                try:
                    print(f"🔍 Scraping Glassdoor: {url}")
                    
                    # Enhanced headers for Glassdoor
                    glassdoor_headers = self.get_random_headers()
                    glassdoor_headers.update({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'Referer': 'https://www.glassdoor.co.in/',
                        'Origin': 'https://www.glassdoor.co.in'
                    })
                    
                    self.session.headers.update(glassdoor_headers)
                    
                    # Random delay
                    time.sleep(random.uniform(3, 6))
                    
                    response = self.safe_request(url)
                    
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Multiple job card selectors for Glassdoor
                        job_selectors = [
                            'li[data-adv-type="GENERAL"]',
                            '.react-job-listing',
                            'li[data-test="jobListing"]',
                            '.jobContainer',
                            'li.jl',
                            'article[data-test="jobListing"]'
                        ]
                        
                        job_cards = []
                        for selector in job_selectors:
                            cards = soup.select(selector)
                            if cards:
                                print(f"✅ Found {len(cards)} job cards with selector: {selector}")
                                job_cards = cards
                                break
                        
                        print(f"📝 Processing {len(job_cards)} Glassdoor job cards")
                        
                        for i, card in enumerate(job_cards[:10]):
                            try:
                                # Multiple title selectors
                                title_elem = None
                                apply_link = None
                                
                                title_selectors = [
                                    'a[data-test="job-link"]',
                                    '.jobTitle a',
                                    'h3 a',
                                    'a[data-test="job-title"]',
                                    '.jobLink'
                                ]
                                
                                for t_sel in title_selectors:
                                    elem = card.select_one(t_sel)
                                    if elem and elem.get_text(strip=True):
                                        title_elem = elem
                                        apply_link = elem.get('href', '')
                                        if apply_link and not apply_link.startswith('http'):
                                            apply_link = urljoin('https://www.glassdoor.co.in', apply_link)
                                        break
                                
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                
                                # Company selectors
                                company_elem = None
                                company_selectors = [
                                    'span[data-test="employer-name"]',
                                    '.employerName',
                                    'div[data-test="employer-short-name"]',
                                    '.companyName'
                                ]
                                
                                for c_sel in company_selectors:
                                    elem = card.select_one(c_sel)
                                    if elem and elem.get_text(strip=True):
                                        company_elem = elem
                                        break
                                
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                
                                # Location selectors
                                location_elem = None
                                location_selectors = [
                                    'span[data-test="job-location"]',
                                    '.location',
                                    'div[data-test="job-location"]'
                                ]
                                
                                for l_sel in location_selectors:
                                    elem = card.select_one(l_sel)
                                    if elem and elem.get_text(strip=True):
                                        location_elem = elem
                                        break
                                
                                location = location_elem.get_text(strip=True) if location_elem else "India"
                                
                                # Salary selectors
                                salary_elem = None
                                salary_selectors = [
                                    'span[data-test="detailSalary"]',
                                    '.salaryText',
                                    'div[data-test="detailSalary"]'
                                ]
                                
                                for s_sel in salary_selectors:
                                    elem = card.select_one(s_sel)
                                    if elem and elem.get_text(strip=True):
                                        salary_elem = elem
                                        break
                                
                                salary = salary_elem.get_text(strip=True) if salary_elem else "Not disclosed"
                                
                                # Rating selectors
                                rating_elem = None
                                rating_selectors = [
                                    'span[data-test="rating"]',
                                    '.rating'
                                ]
                                
                                for r_sel in rating_selectors:
                                    elem = card.select_one(r_sel)
                                    if elem and elem.get_text(strip=True):
                                        rating_elem = elem
                                        break
                                
                                rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
                                
                                if title and len(title) > 3:
                                    job_data = {
                                        "id": f"glassdoor_{int(time.time())}_{len(jobs)}",
                                        "title": title,
                                        "company": company,
                                        "location": location,
                                        "salary": salary,
                                        "rating": rating,
                                        "apply_link": apply_link or f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={quote(keyword)}",
                                        "source": "glassdoor",
                                        "scraped_at": datetime.now().isoformat(),
                                        "posted_date": "Recent"
                                    }
                                    jobs.append(job_data)
                                    print(f"✅ Added Glassdoor job: {title}")
                            
                            except Exception as e:
                                print(f"❌ Error processing Glassdoor job card {i}: {e}")
                                continue
                        
                        if jobs:
                            print(f"✅ Successfully scraped {len(jobs)} jobs from Glassdoor")
                            break
                    else:
                        print(f"❌ Glassdoor request failed for {url}")
                        
                except Exception as e:
                    print(f"❌ Error with Glassdoor URL {url}: {e}")
                    continue
                        
        except Exception as e:
            print(f"❌ Glassdoor error: {e}")
        
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
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all scraping tasks including Glassdoor
            future_to_platform = {
                executor.submit(self.scrape_indeed_realtime, keyword, location): "indeed",
                executor.submit(self.scrape_naukri_realtime, keyword): "naukri",
                executor.submit(self.scrape_linkedin_realtime, keyword): "linkedin",
                executor.submit(self.scrape_timesjobs_realtime, keyword): "timesjobs",
                executor.submit(self.scrape_glassdoor_realtime, keyword): "glassdoor"
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
                elif job['source'] == 'glassdoor':
                    job['apply_link'] = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={title_encoded}"
        
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
            "Multi-platform support (Indeed, Naukri, LinkedIn, TimesJobs, Glassdoor)",
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
