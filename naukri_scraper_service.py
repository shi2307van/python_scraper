from fastapi import FastAPI
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import shutil
import os
import subprocess

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

# ✅ Helper function for creating driver
def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")   # Headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # ✅ Detect environment and set Chrome binary path
    chrome_path = None
    driver_path = None
    
    # Try to find Chrome in various locations
    possible_chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable", 
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium-browser"),
        shutil.which("chromium")
    ]
    
    # Find the first valid Chrome path
    for path in possible_chrome_paths:
        if path and os.path.exists(path):
            chrome_path = path
            print(f"✅ Found Chrome at: {chrome_path}")
            break
    
    # Set binary location only if we found a valid Chrome path
    if chrome_path:
        options.binary_location = chrome_path
    else:
        print("⚠️ No Chrome binary found, letting undetected_chromedriver handle it")
    
    # Try to find ChromeDriver
    possible_driver_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        shutil.which("chromedriver")
    ]
    
    for path in possible_driver_paths:
        if path and os.path.exists(path):
            driver_path = path
            print(f"✅ Found ChromeDriver at: {driver_path}")
            break

    try:
        driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path
        )
        return driver
    except Exception as e:
        print(f"❌ Error creating driver: {e}")
        print("🔄 Trying fallback method...")
        # Fallback - let undetected_chromedriver handle everything
        fallback_options = uc.ChromeOptions()
        fallback_options.add_argument("--headless=new")
        fallback_options.add_argument("--no-sandbox")
        fallback_options.add_argument("--disable-dev-shm-usage")
        try:
            return uc.Chrome(options=fallback_options)
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise Exception(f"Could not create Chrome driver: {e}. Fallback error: {fallback_error}")


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
        
        # Scrape Naukri
        search_url = f"https://www.naukri.com/{keyword}-jobs"
        print(f"📍 Navigating to: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)  # Increased wait time
        
        print("📄 Parsing page content...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("article", class_="jobTuple")
        
        print(f"🎯 Found {len(jobs)} job listings")

        for i, job in enumerate(jobs[:5]):
            try:
                title = job.find("a", class_="title")
                company = job.find("a", class_="subTitle")
                link = title["href"] if title else None
                
                if link and not link.startswith("http"):
                    link = f"https://www.naukri.com{link}"

                job_data = {
                    "title": title.text.strip() if title else "N/A",
                    "company": company.text.strip() if company else "N/A",
                    "link": link
                }
                naukri_jobs.append(job_data)
                print(f"✅ Job {i+1}: {job_data['title']} - {job_data['company']}")
                
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
