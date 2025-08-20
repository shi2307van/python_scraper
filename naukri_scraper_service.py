from fastapi import FastAPI
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

app = FastAPI()

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
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )

    # ✅ Render installs Chromium in /usr/bin
    options.binary_location = "/usr/bin/chromium-browser"

    # ✅ Explicit chromedriver path on Render
    driver = uc.Chrome(
        options=options,
        driver_executable_path="/usr/bin/chromedriver"
    )
    return driver


@app.get("/scrape/")
def scrape_data(keyword: str):
    try:
        # Initialize job lists
        naukri_jobs = []
        glassdoor_jobs = []
        foundit_jobs = []
        linkedin_jobs = []

        # Example: Scraping Naukri
        driver = get_driver()
        search_url = f"https://www.naukri.com/{keyword}-jobs"
        driver.get(search_url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("article", class_="jobTuple")

        for job in jobs[:5]:  # Limiting results for demo
            title = job.find("a", class_="title")
            company = job.find("a", class_="subTitle")
            link = title["href"] if title else None

            naukri_jobs.append({
                "title": title.text.strip() if title else "N/A",
                "company": company.text.strip() if company else "N/A",
                "link": link
            })

        driver.quit()

        # TODO: Add Glassdoor, Foundit, LinkedIn scrapers (same logic with get_driver)

        return {
            "naukri": naukri_jobs,
            "glassdoor": glassdoor_jobs,
            "foundit": foundit_jobs,
            "linkedin": linkedin_jobs
        }

    except Exception as e:
        return {"error": str(e)}
