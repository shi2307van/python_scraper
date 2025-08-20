from fastapi import FastAPI
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import shutil
import os

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "API is running", "message": "Python Scraper Service"}

@app.get("/health")
def health():
    return {"status": "healthy", "chrome_available": os.path.exists("/usr/bin/google-chrome") or bool(shutil.which("google-chrome"))}

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

    # ✅ Detect environment (local vs deployed)
    if os.environ.get('RENDER'):
        # On Render - use Google Chrome installed by build script
        chrome_path = shutil.which("google-chrome") or "/usr/bin/google-chrome"
        if os.path.exists(chrome_path):
            options.binary_location = chrome_path
        driver_path = "/usr/bin/chromedriver"
    elif os.path.exists("/usr/bin/chromium-browser"):
        # Other Linux deployment with chromium
        options.binary_location = "/usr/bin/chromium-browser"
        driver_path = "/usr/bin/chromedriver"
    else:
        # On Local (let uc auto-download chromedriver)
        chrome_path = shutil.which("chrome") or shutil.which("chromium") or shutil.which("google-chrome")
        if chrome_path:
            options.binary_location = chrome_path
        driver_path = None  # uc handles it

    try:
        driver = uc.Chrome(
            options=options,
            driver_executable_path=driver_path if driver_path and os.path.exists(driver_path) else None
        )
        return driver
    except Exception as e:
        print(f"Error creating driver: {e}")
        # Fallback - let undetected_chromedriver handle everything
        fallback_options = uc.ChromeOptions()
        fallback_options.add_argument("--headless=new")
        fallback_options.add_argument("--no-sandbox")
        fallback_options.add_argument("--disable-dev-shm-usage")
        return uc.Chrome(options=fallback_options)


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
