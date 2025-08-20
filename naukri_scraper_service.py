from fastapi import FastAPI
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import shutil
import os
import subprocess
import urllib.parse

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "API is running", "message": "Python Scraper Service"}

@app.get("/health")
def health():
    chrome_available = os.path.exists("/usr/bin/google-chrome") or bool(shutil.which("google-chrome"))
    return {
        "status": "healthy", 
        "chrome_available": chrome_available,
        "chrome_paths": {
            "google-chrome": shutil.which("google-chrome"),
            "usr_bin_google_chrome": "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None,
            "google-chrome-stable": shutil.which("google-chrome-stable"),
            "chromium": shutil.which("chromium"),
            "chromium-browser": shutil.which("chromium-browser")
        },
        "chromedriver_paths": {
            "chromedriver": shutil.which("chromedriver"),
            "usr_bin_chromedriver": "/usr/bin/chromedriver" if os.path.exists("/usr/bin/chromedriver") else None
        }
    }

@app.get("/debug")
def debug_info():
    """Debug endpoint to check browser availability"""
    import subprocess
    try:
        # Try to get Chrome version
        chrome_version = subprocess.run(
            ["google-chrome", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        chrome_version_output = chrome_version.stdout.strip() if chrome_version.returncode == 0 else f"Error: {chrome_version.stderr}"
    except Exception as e:
        chrome_version_output = f"Exception: {str(e)}"
    
    try:
        # Try to get ChromeDriver version
        chromedriver_version = subprocess.run(
            ["chromedriver", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        chromedriver_version_output = chromedriver_version.stdout.strip() if chromedriver_version.returncode == 0 else f"Error: {chromedriver_version.stderr}"
    except Exception as e:
        chromedriver_version_output = f"Exception: {str(e)}"
    
    return {
        "environment_variables": dict(os.environ),
        "chrome_version": chrome_version_output,
        "chromedriver_version": chromedriver_version_output,
        "working_directory": os.getcwd(),
        "python_version": os.sys.version
    }

# ✅ Helper function for creating driver with multiple fallback strategies
def get_driver():
    print("🚀 Starting Chrome driver creation...")
    
    # Strategy 1: Let undetected_chromedriver handle everything automatically
    try:
        print("📍 Strategy 1: Auto-detection by undetected_chromedriver")
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Let undetected_chromedriver auto-detect everything
        driver = uc.Chrome(options=options, version_main=None)
        print("✅ Strategy 1 successful: Auto-detection worked")
        return driver
        
    except Exception as e1:
        print(f"❌ Strategy 1 failed: {e1}")
    
    # Strategy 2: Use system Chrome with explicit paths
    try:
        print("📍 Strategy 2: System Chrome with explicit paths")
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        
        # Try to find Chrome binary
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/google-chrome"
        ]
        
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                print(f"✅ Found Chrome binary: {chrome_binary}")
                break
        
        if chrome_binary:
            options.binary_location = chrome_binary
        
        # Try to find ChromeDriver
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver"
        ]
        
        chromedriver_binary = None
        for path in chromedriver_paths:
            if os.path.exists(path):
                chromedriver_binary = path
                print(f"✅ Found ChromeDriver: {chromedriver_binary}")
                break
        
        driver = uc.Chrome(
            options=options,
            driver_executable_path=chromedriver_binary
        )
        print("✅ Strategy 2 successful: System Chrome worked")
        return driver
        
    except Exception as e2:
        print(f"❌ Strategy 2 failed: {e2}")
    
    # Strategy 3: Minimal options fallback
    try:
        print("� Strategy 3: Minimal options fallback")
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = uc.Chrome(options=options)
        print("✅ Strategy 3 successful: Minimal options worked")
        return driver
        
    except Exception as e3:
        print(f"❌ Strategy 3 failed: {e3}")
    
    # Strategy 4: Use regular Selenium WebDriver as last resort
    try:
        print("📍 Strategy 4: Regular Selenium WebDriver")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Try to find ChromeDriver
        chromedriver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
        if os.path.exists(chromedriver_path):
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Strategy 4 successful: Regular Selenium worked")
            return driver
        else:
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ Strategy 4 successful: Regular Selenium with auto-detection worked")
            return driver
            
    except Exception as e4:
        print(f"❌ Strategy 4 failed: {e4}")
    
    # If all strategies fail
    raise Exception(f"All driver creation strategies failed. Errors: Strategy1={str(e1)[:100]}, Strategy2={str(e2)[:100]}, Strategy3={str(e3)[:100]}, Strategy4={str(e4)[:100]}")


@app.get("/debug-page")
def debug_page_content(keyword: str = "python"):
    """Debug endpoint to see what Naukri page content looks like"""
    driver = None
    try:
        driver = get_driver()
        encoded_keyword = urllib.parse.quote(keyword.replace(" ", "-"))
        search_url = f"https://www.naukri.com/{encoded_keyword}-jobs"
        
        driver.get(search_url)
        time.sleep(8)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        return {
            "url": driver.current_url,
            "title": soup.find("title").text if soup.find("title") else "No title",
            "page_source_length": len(page_source),
            "page_source_preview": page_source[:2000] + "..." if len(page_source) > 2000 else page_source,
            "article_elements": len(soup.find_all("article")),
            "div_elements_with_job": len(soup.find_all("div", string=lambda text: text and "job" in text.lower())),
            "all_classes": list(set([cls for elem in soup.find_all(class_=True) for cls in elem.get("class", [])]))[:50]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if driver:
            driver.quit()

@app.get("/scrape/")
def scrape_data(keyword: str):
    driver = None
    try:
        print(f"🔍 Starting scrape for keyword: {keyword}")
        
        naukri_jobs = []
        glassdoor_jobs = []
        foundit_jobs = []
        linkedin_jobs = []

        # Create driver
        driver = get_driver()
        print("✅ Driver created successfully")
        
        # Scrape Naukri with proper URL encoding
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword.replace(" ", "-"))
        search_url = f"https://www.naukri.com/{encoded_keyword}-jobs"
        print(f"📍 Navigating to: {search_url}")
        
        driver.get(search_url)
        print("⏳ Waiting for page to load...")
        
        # Smart wait for content to load
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for any job-related content to appear
            wait = WebDriverWait(driver, 15)
            wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, "article, .jobTuple, [data-job-id], .job") or 
                      "No jobs found" in driver.page_source or 
                      "Sorry" in driver.page_source)
            
        except Exception as e:
            print(f"⚠️ Smart wait failed, using basic wait: {e}")
            time.sleep(8)
        
        # Additional wait to ensure full content load
        time.sleep(3)
        
        # Try to handle any popups or overlays
        try:
            # Check for and close any modal/popup
            close_buttons = driver.find_elements("css selector", "[class*='close'], [class*='dismiss'], .crossIcon")
            for button in close_buttons:
                try:
                    if button.is_displayed():
                        button.click()
                        time.sleep(1)
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Popup handling: {e}")
        
        print("📄 Parsing page content...")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Try multiple selectors for job listings
        job_selectors = [
            "article[class*='jobTuple']",
            ".jobTuple",
            "[class*='job-tuple']",
            ".srp-jobtuple-wrapper",
            ".jobTupleHeader",
            "[data-job-id]"
        ]
        
        jobs = []
        for selector in job_selectors:
            jobs = soup.select(selector)
            if jobs:
                print(f"✅ Found jobs using selector: {selector}")
                break
        
        print(f"🎯 Found {len(jobs)} job listings")
        
        # If no jobs found, let's debug what we can see
        if len(jobs) == 0:
            print("🔍 Debug: Checking page content...")
            
            # Check if page loaded correctly
            page_title = soup.find("title")
            print(f"📄 Page title: {page_title.text if page_title else 'Not found'}")
            
            # Check for any job-related content
            job_indicators = soup.find_all(text=lambda text: text and any(word in text.lower() for word in ["job", "position", "vacancy", "opening"]))
            print(f"📊 Job-related content found: {len(job_indicators)} items")
            
            # Check if we're on the right page
            if "naukri" in driver.current_url.lower():
                print("✅ On Naukri website")
            else:
                print(f"⚠️ Redirected to: {driver.current_url}")
            
            # Try alternative selectors
            alt_selectors = [".jobTuple", "[data-job-id]", ".job", ".position", ".vacancy"]
            for alt_sel in alt_selectors:
                alt_jobs = soup.select(alt_sel)
                if alt_jobs:
                    print(f"🔍 Alternative selector '{alt_sel}' found {len(alt_jobs)} elements")
                    jobs = alt_jobs
                    break

        for i, job in enumerate(jobs[:5]):
            try:
                # Try multiple selectors for job title and company
                title_selectors = ["a.title", ".title", "[class*='title']", "h2 a", "h3 a", ".jobTitle"]
                company_selectors = ["a.subTitle", ".subTitle", "[class*='subTitle']", ".companyName", ".org"]
                
                title_elem = None
                for title_sel in title_selectors:
                    title_elem = job.select_one(title_sel)
                    if title_elem:
                        break
                
                company_elem = None
                for company_sel in company_selectors:
                    company_elem = job.select_one(company_sel)
                    if company_elem:
                        break
                
                # Extract job data
                title_text = title_elem.get_text(strip=True) if title_elem else "N/A"
                company_text = company_elem.get_text(strip=True) if company_elem else "N/A"
                
                # Extract link
                link = None
                if title_elem and title_elem.get("href"):
                    link = title_elem["href"]
                    if link and not link.startswith("http"):
                        link = f"https://www.naukri.com{link}"
                
                # Only add if we have meaningful data
                if title_text != "N/A" or company_text != "N/A":
                    job_data = {
                        "title": title_text,
                        "company": company_text,
                        "link": link
                    }
                    naukri_jobs.append(job_data)
                    print(f"✅ Job {i+1}: {job_data['title']} - {job_data['company']}")
                else:
                    print(f"⚠️ Job {i+1}: No meaningful data found")
                
            except Exception as job_error:
                print(f"❌ Error processing job {i+1}: {job_error}")
                continue

        print(f"🎉 Successfully scraped {len(naukri_jobs)} jobs")
        
        return {
            "success": True,
            "keyword": keyword,
            "naukri": naukri_jobs,
            "glassdoor": glassdoor_jobs,
            "foundit": foundit_jobs,
            "linkedin": linkedin_jobs,
            "total_jobs": len(naukri_jobs)
        }

    except Exception as e:
        error_msg = f"Scraping error: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "keyword": keyword,
            "naukri": [],
            "glassdoor": [],
            "foundit": [],
            "linkedin": []
        }
    
    finally:
        if driver:
            try:
                driver.quit()
                print("🔧 Driver closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing driver: {e}")
