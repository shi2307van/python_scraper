"""
Simple and Effective Job Scraper
Using alternative approaches when main sites are blocked
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import quote, urlencode
from typing import List, Dict, Optional
import re

class SimpleJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
    
    def scrape_indeed_simple(self, keyword: str) -> List[Dict]:
        """Simple Indeed scraping with fallback approaches"""
        jobs = []
        
        try:
            # Try multiple Indeed domains and approaches
            indeed_urls = [
                f"https://in.indeed.com/jobs?q={quote(keyword)}&l=India&start=0",
                f"https://www.indeed.co.in/jobs?q={quote(keyword)}",
                f"https://indeed.com/jobs?q={quote(keyword)}&l=India"
            ]
            
            for url in indeed_urls:
                try:
                    print(f"🔍 Trying Indeed: {url}")
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200 and len(response.text) > 5000:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for job listings using multiple approaches
                        job_containers = []
                        
                        # Approach 1: data-jk attribute
                        job_containers = soup.find_all('div', {'data-jk': True})
                        
                        # Approach 2: class-based selectors
                        if not job_containers:
                            job_containers = soup.find_all('div', class_=re.compile(r'job'))
                        
                        # Approach 3: Look for job titles
                        if not job_containers:
                            job_containers = soup.find_all('h2', string=re.compile(r'developer|engineer|analyst', re.I))
                            job_containers = [elem.parent.parent for elem in job_containers if elem.parent and elem.parent.parent]
                        
                        print(f"Found {len(job_containers)} job containers")
                        
                        for container in job_containers[:10]:
                            try:
                                # Extract title
                                title_elem = (container.find('h2') or 
                                            container.find('a', string=re.compile(r'developer|engineer|analyst', re.I)))
                                
                                if title_elem:
                                    if title_elem.find('a'):
                                        title = title_elem.find('a').get_text(strip=True)
                                    else:
                                        title = title_elem.get_text(strip=True)
                                    
                                    # Extract company
                                    company = "N/A"
                                    company_selectors = [
                                        '[data-testid="company-name"]',
                                        '.companyName',
                                        'span[title]'
                                    ]
                                    
                                    for selector in company_selectors:
                                        company_elem = container.select_one(selector)
                                        if company_elem:
                                            company = company_elem.get_text(strip=True)
                                            break
                                    
                                    # Extract location
                                    location = "India"
                                    location_elem = container.select_one('[data-testid="job-location"], .companyLocation')
                                    if location_elem:
                                        location = location_elem.get_text(strip=True)
                                    
                                    if title and len(title) > 3:
                                        jobs.append({
                                            "title": title,
                                            "company": company,
                                            "location": location,
                                            "source": "indeed"
                                        })
                            
                            except Exception as e:
                                continue
                        
                        if jobs:
                            break
                    
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"❌ Indeed URL failed: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Indeed scraping error: {e}")
        
        return jobs
    
    def scrape_glassdoor_api(self, keyword: str) -> List[Dict]:
        """Try to get jobs from Glassdoor-like sources"""
        jobs = []
        
        try:
            # Glassdoor search (simplified)
            glassdoor_url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={quote(keyword)}"
            
            response = self.session.get(glassdoor_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job listings
                job_elements = soup.find_all('div', class_=re.compile(r'job|listing'))
                
                for job_elem in job_elements[:5]:
                    try:
                        title_elem = job_elem.find('a', string=re.compile(keyword.split()[0], re.I))
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            
                            # Try to find company
                            company_elem = job_elem.find('span', string=re.compile(r'[A-Z][a-z]+'))
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            jobs.append({
                                "title": title,
                                "company": company,
                                "location": "India",
                                "source": "glassdoor"
                            })
                    
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"❌ Glassdoor scraping error: {e}")
        
        return jobs
    
    def scrape_linkedin_jobs(self, keyword: str) -> List[Dict]:
        """Try LinkedIn jobs (public listings)"""
        jobs = []
        
        try:
            # LinkedIn public job search
            linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={quote(keyword)}&location=India"
            
            # Use specific headers for LinkedIn
            linkedin_headers = self.session.headers.copy()
            linkedin_headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
            
            response = self.session.get(linkedin_url, headers=linkedin_headers, timeout=15)
            
            if response.status_code == 200 and len(response.text) > 5000:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job cards
                job_cards = soup.find_all('div', class_=re.compile(r'job.*card|result.*card'))
                
                for card in job_cards[:5]:
                    try:
                        # Extract title
                        title_elem = card.find('h3') or card.find('a', string=re.compile(keyword.split()[0], re.I))
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            
                            # Extract company
                            company_elem = card.find('h4') or card.find('span', string=re.compile(r'[A-Z][a-z]+.*[A-Z]'))
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            jobs.append({
                                "title": title,
                                "company": company,
                                "location": "India",
                                "source": "linkedin"
                            })
                    
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"❌ LinkedIn scraping error: {e}")
        
        return jobs
    
    def create_sample_jobs(self, keyword: str) -> List[Dict]:
        """Create sample jobs when scraping fails"""
        
        sample_companies = [
            "TCS", "Infosys", "Wipro", "HCL", "Accenture", 
            "Cognizant", "IBM", "Microsoft", "Amazon", "Google"
        ]
        
        job_titles = [
            f"Senior {keyword}",
            f"{keyword}",
            f"Lead {keyword}",
            f"Principal {keyword}",
            f"Junior {keyword}"
        ]
        
        locations = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Pune", "Hyderabad"]
        
        jobs = []
        for i in range(5):
            jobs.append({
                "title": random.choice(job_titles),
                "company": random.choice(sample_companies),
                "location": random.choice(locations),
                "source": "sample_data",
                "note": "This is sample data when live scraping is blocked"
            })
        
        return jobs

# Global instance
simple_scraper = SimpleJobScraper()
