#!/usr/bin/env python3
"""
Test script for the improved job scraper
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import fake_useragent
import time

def test_indeed():
    """Test Indeed scraping"""
    print("🔍 Testing Indeed...")
    
    try:
        ua = fake_useragent.UserAgent()
        session = requests.Session()
        session.headers.update({
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
        })
        
        keyword = "python developer"
        url = f"https://in.indeed.com/jobs?q={quote(keyword)}&l=India&sort=date"
        
        response = session.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors
            selectors = [
                'div[data-jk]',
                '.job_seen_beacon',
                'td.resultContent',
                '.jobsearch-SerpJobCard'
            ]
            
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    print(f"✅ Found {len(cards)} job cards with selector: {selector}")
                    
                    # Extract first job
                    if cards:
                        first_card = cards[0]
                        title_elem = (first_card.select_one('h2 a span[title]') or 
                                    first_card.select_one('h2 a') or 
                                    first_card.select_one('[data-testid="job-title"]'))
                        
                        if title_elem:
                            title = title_elem.get('title') or title_elem.get_text(strip=True)
                            print(f"First job title: {title}")
                        
                    return len(cards)
            
            print("❌ No job cards found with any selector")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return 0

def test_naukri():
    """Test Naukri scraping"""
    print("\n🔍 Testing Naukri...")
    
    try:
        ua = fake_useragent.UserAgent()
        session = requests.Session()
        session.headers.update({
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.naukri.com/',
        })
        
        keyword = "python developer"
        url = f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs"
        
        response = session.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors
            selectors = [
                'article.jobTuple',
                'div.jobTuple',
                '.srp-jobtuple-wrapper',
                'article[class*="jobTuple"]'
            ]
            
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    print(f"✅ Found {len(cards)} job cards with selector: {selector}")
                    
                    # Extract first job
                    if cards:
                        first_card = cards[0]
                        title_elem = (first_card.select_one('.title a') or
                                    first_card.select_one('h3 a'))
                        
                        if title_elem:
                            title = title_elem.get('title') or title_elem.get_text(strip=True)
                            print(f"First job title: {title}")
                        
                    return len(cards)
            
            print("❌ No job cards found with any selector")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return 0

if __name__ == "__main__":
    print("🚀 Testing job scraper components...")
    
    indeed_count = test_indeed()
    naukri_count = test_naukri()
    
    print(f"\n📊 Results:")
    print(f"Indeed: {indeed_count} jobs")
    print(f"Naukri: {naukri_count} jobs")
    print(f"Total: {indeed_count + naukri_count} jobs")
