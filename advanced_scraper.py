"""
Advanced Job Scraper with Anti-Detection
Implements multiple strategies to bypass access restrictions
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import quote, urlencode
from typing import List, Dict, Optional
import cloudscraper  # For Cloudflare bypass
import fake_useragent  # For rotating user agents

class AdvancedJobScraper:
    def __init__(self):
        self.session = None
        self.user_agent_rotator = fake_useragent.UserAgent()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with advanced anti-detection"""
        # Use cloudscraper which handles Cloudflare protection
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Set realistic headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def get_random_headers(self):
        """Get randomized headers for each request"""
        return {
            'User-Agent': self.user_agent_rotator.random,
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.8',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.5'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def safe_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make a safe request with retries and error handling"""
        for attempt in range(max_retries):
            try:
                # Random delay to appear human-like
                time.sleep(random.uniform(1, 3))
                
                # Update headers for each request
                self.session.headers.update(self.get_random_headers())
                
                response = self.session.get(url, timeout=15)
                
                # Check for common blocking indicators
                if (response.status_code == 200 and 
                    "access denied" not in response.text.lower() and
                    "blocked" not in response.text.lower() and
                    "bot" not in response.text.lower() and
                    "captcha" not in response.text.lower() and
                    len(response.text) > 1000):  # Ensure we got actual content
                    return response
                else:
                    print(f"⚠️ Attempt {attempt + 1} failed for {url} - Status: {response.status_code}, Content length: {len(response.text)}")
                    if attempt < max_retries - 1:
                        # Reset session and try again
                        self.setup_session()
                        time.sleep(random.uniform(3, 8))
                    
            except Exception as e:
                print(f"❌ Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 8))
        
        return None
    
    def scrape_indeed_advanced(self, keyword: str, location: str = "India") -> List[Dict]:
        """Advanced Indeed scraping with multiple strategies"""
        jobs = []
        
        # Multiple Indeed URL patterns
        url_patterns = [
            f"https://in.indeed.com/jobs?q={quote(keyword)}&l={quote(location)}",
            f"https://www.indeed.co.in/jobs?q={quote(keyword)}&l={quote(location)}",
            f"https://in.indeed.com/jobs?q={quote(keyword)}&sort=date",
            f"https://www.indeed.com/jobs?q={quote(keyword)}&l={quote(location)}"
        ]
        
        for url in url_patterns:
            try:
                print(f"🔍 Trying Indeed URL: {url}")
                response = self.safe_request(url)
                
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Multiple selectors for Indeed job cards
                    job_selectors = [
                        'div[data-jk]',
                        '.job_seen_beacon',
                        '.jobsearch-SerpJobCard',
                        'div[class*="job"]',
                        'article'
                    ]
                    
                    job_elements = []
                    for selector in job_selectors:
                        job_elements = soup.select(selector)
                        if job_elements:
                            print(f"✅ Found {len(job_elements)} jobs with selector: {selector}")
                            break
                    
                    for job_elem in job_elements[:5]:
                        try:
                            # Extract job data with multiple fallbacks
                            title_elem = (job_elem.select_one('h2 a span') or
                                        job_elem.select_one('h2 a') or
                                        job_elem.select_one('[data-testid="job-title"]') or
                                        job_elem.select_one('.jobTitle'))
                            
                            company_elem = (job_elem.select_one('[data-testid="company-name"]') or
                                          job_elem.select_one('.companyName') or
                                          job_elem.select_one('span[title]'))
                            
                            location_elem = (job_elem.select_one('[data-testid="job-location"]') or
                                           job_elem.select_one('.companyLocation'))
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                location = location_elem.get_text(strip=True) if location_elem else "N/A"
                                
                                # Get job link
                                link_elem = job_elem.select_one('h2 a')
                                link = None
                                if link_elem and link_elem.get('href'):
                                    link = f"https://in.indeed.com{link_elem['href']}"
                                
                                jobs.append({
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "link": link,
                                    "source": "indeed"
                                })
                        
                        except Exception as e:
                            continue
                    
                    if jobs:
                        break
                        
            except Exception as e:
                print(f"❌ Indeed scraping error: {e}")
                continue
        
        return jobs
    
    def scrape_naukri_advanced(self, keyword: str) -> List[Dict]:
        """Advanced Naukri scraping with maximum stealth"""
        jobs = []
        
        # Multiple Naukri URL strategies
        url_patterns = [
            f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs",
            f"https://www.naukri.com/jobs-in-india?k={quote(keyword)}",
            f"https://www.naukri.com/{keyword.replace(' ', '%20')}-jobs-in-india",
            f"https://www.naukri.com/jobs-in-india?k={quote(keyword)}&l=",
        ]
        
        for i, url in enumerate(url_patterns):
            try:
                print(f"🔍 Trying Naukri URL {i+1}: {url}")
                
                # Add specific headers for Naukri
                naukri_headers = self.get_random_headers()
                naukri_headers.update({
                    'Referer': 'https://www.naukri.com/',
                    'Origin': 'https://www.naukri.com',
                    'Sec-Fetch-Site': 'same-origin'
                })
                
                self.session.headers.update(naukri_headers)
                response = self.safe_request(url)
                
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check if we're on a valid job listing page  
                    page_text = response.text.lower()
                    if ("jobs" in page_text and 
                        ("found" in page_text or "results" in page_text or "developer" in page_text)):
                        print("✅ Successfully accessed Naukri job page")
                        
                        # Multiple selectors for Naukri
                        job_selectors = [
                            'article[class*="jobTuple"]',
                            'div[class*="jobTuple"]',
                            '.srp-jobtuple-wrapper',
                            '[data-job-id]',
                            '.jobTupleHeader'
                        ]
                        
                        job_elements = []
                        for selector in job_selectors:
                            job_elements = soup.select(selector)
                            if job_elements:
                                print(f"✅ Found {len(job_elements)} jobs with selector: {selector}")
                                break
                        
                        for job_elem in job_elements[:5]:
                            try:
                                # Extract with multiple strategies
                                title_elem = (job_elem.select_one('a[class*="title"]') or
                                            job_elem.select_one('.title a') or
                                            job_elem.select_one('h2 a'))
                                
                                company_elem = (job_elem.select_one('a[class*="subTitle"]') or
                                              job_elem.select_one('.subTitle') or
                                              job_elem.select_one('[class*="company"]'))
                                
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                    
                                    link = None
                                    if title_elem.get('href'):
                                        link = title_elem['href']
                                        if not link.startswith('http'):
                                            link = f"https://www.naukri.com{link}"
                                    
                                    jobs.append({
                                        "title": title,
                                        "company": company,
                                        "link": link,
                                        "source": "naukri"
                                    })
                            
                            except Exception as e:
                                continue
                        
                        if jobs:
                            break
                    else:
                        print(f"⚠️ Naukri URL {i+1}: Not a valid job page")
                
            except Exception as e:
                print(f"❌ Naukri URL {i+1} error: {e}")
                continue
        
        return jobs
    
    def scrape_timesjobs_advanced(self, keyword: str) -> List[Dict]:
        """Advanced TimesJobs scraping"""
        jobs = []
        
        try:
            # TimesJobs search URL
            params = {
                'searchType': 'personalizedSearch',
                'from': 'submit',
                'txtKeywords': keyword,
                'cboWorkExp1': '0',
                'cboWorkExp2': '30'
            }
            
            url = f"https://www.timesjobs.com/candidate/job-search.html?{urlencode(params)}"
            print(f"🔍 Trying TimesJobs: {url}")
            
            response = self.safe_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # TimesJobs job selectors
                job_elements = soup.select('li[class*="clearfix job-bx"]')
                
                if not job_elements:
                    job_elements = soup.select('div[class*="job"]')
                
                print(f"✅ Found {len(job_elements)} TimesJobs listings")
                
                for job_elem in job_elements[:5]:
                    try:
                        title_elem = job_elem.select_one('h2 a, h3 a, .jobTitle')
                        company_elem = job_elem.select_one('h3[class*="joblist-comp-name"] a, .compName')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            link = None
                            if title_elem.get('href'):
                                link = title_elem['href']
                                if not link.startswith('http'):
                                    link = f"https://www.timesjobs.com{link}"
                            
                            jobs.append({
                                "title": title,
                                "company": company,
                                "link": link,
                                "source": "timesjobs"
                            })
                    
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"❌ TimesJobs error: {e}")
        
        return jobs

# Global scraper instance
advanced_scraper = AdvancedJobScraper()
