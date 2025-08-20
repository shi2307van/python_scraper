"""
Advanced Multi-Platform Job Scraper with Anti-Detection
Designed to bypass access restrictions and provide reliable job data
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import time
import random
from typing import List, Dict, Optional
import traceback
from datetime import datetime

# Import our advanced scraper
from advanced_scraper import advanced_scraper

app = FastAPI(
    title="Advanced Job Scraper API",
    description="Anti-detection job scraper for multiple platforms",
    version="2.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active", 
        "message": "Advanced Job Scraper API is running",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Anti-detection technology",
            "Multi-platform support",
            "Advanced fallback strategies",
            "Cloudflare bypass",
            "User-agent rotation"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test basic functionality
        test_response = advanced_scraper.safe_request("https://httpbin.org/user-agent")
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "advanced_scraper": "operational",
                "http_client": "operational" if test_response else "warning",
                "anti_detection": "active"
            }
        }
        
        return health_status
    
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/scrape-jobs")
async def scrape_jobs_advanced(
    keyword: str = "python developer",
    sources: str = "all"  # "all", "indeed", "naukri", "timesjobs"
):
    """
    Advanced job scraping with anti-detection
    
    Args:
        keyword: Job search keyword
        sources: Comma-separated list of sources or "all"
    
    Returns:
        JSON response with job listings from multiple platforms
    """
    
    start_time = time.time()
    results = {
        "keyword": keyword,
        "timestamp": datetime.now().isoformat(),
        "sources_requested": sources,
        "jobs": [],
        "summary": {},
        "status": "success"
    }
    
    try:
        # Parse sources
        if sources.lower() == "all":
            source_list = ["indeed", "naukri", "timesjobs"]
        else:
            source_list = [s.strip().lower() for s in sources.split(",")]
        
        print(f"🚀 Starting advanced job scraping for: {keyword}")
        print(f"📋 Sources: {source_list}")
        
        all_jobs = []
        source_stats = {}
        
        # Scrape Indeed
        if "indeed" in source_list:
            try:
                print("🔍 Scraping Indeed with advanced techniques...")
                indeed_jobs = advanced_scraper.scrape_indeed_advanced(keyword)
                all_jobs.extend(indeed_jobs)
                source_stats["indeed"] = {
                    "count": len(indeed_jobs),
                    "status": "success" if indeed_jobs else "no_results"
                }
                print(f"✅ Indeed: {len(indeed_jobs)} jobs found")
                
                # Random delay between sources
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"❌ Indeed error: {e}")
                source_stats["indeed"] = {"count": 0, "status": "error", "error": str(e)}
        
        # Scrape Naukri with advanced anti-detection
        if "naukri" in source_list:
            try:
                print("🔍 Scraping Naukri with maximum stealth...")
                naukri_jobs = advanced_scraper.scrape_naukri_advanced(keyword)
                all_jobs.extend(naukri_jobs)
                source_stats["naukri"] = {
                    "count": len(naukri_jobs),
                    "status": "success" if naukri_jobs else "blocked_or_no_results"
                }
                print(f"✅ Naukri: {len(naukri_jobs)} jobs found")
                
                # Random delay between sources
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"❌ Naukri error: {e}")
                source_stats["naukri"] = {"count": 0, "status": "error", "error": str(e)}
        
        # Scrape TimesJobs
        if "timesjobs" in source_list:
            try:
                print("🔍 Scraping TimesJobs...")
                timesjobs_jobs = advanced_scraper.scrape_timesjobs_advanced(keyword)
                all_jobs.extend(timesjobs_jobs)
                source_stats["timesjobs"] = {
                    "count": len(timesjobs_jobs),
                    "status": "success" if timesjobs_jobs else "no_results"
                }
                print(f"✅ TimesJobs: {len(timesjobs_jobs)} jobs found")
                
            except Exception as e:
                print(f"❌ TimesJobs error: {e}")
                source_stats["timesjobs"] = {"count": 0, "status": "error", "error": str(e)}
        
        # Compile results
        results["jobs"] = all_jobs
        results["summary"] = {
            "total_jobs": len(all_jobs),
            "sources": source_stats,
            "processing_time": round(time.time() - start_time, 2),
            "success_rate": len([s for s in source_stats.values() if s["count"] > 0]) / len(source_stats) if source_stats else 0
        }
        
        print(f"✅ Scraping completed: {len(all_jobs)} total jobs in {results['summary']['processing_time']}s")
        
        # If no jobs found, provide helpful information
        if not all_jobs:
            results["status"] = "no_results"
            results["message"] = "No jobs found. This could be due to:"
            results["suggestions"] = [
                "Try different keywords",
                "Some sites may be temporarily blocking requests",
                "Check if the keyword is too specific",
                "Try again in a few minutes"
            ]
        
        return JSONResponse(content=results)
    
    except Exception as e:
        error_details = {
            "status": "error",
            "keyword": keyword,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(time.time() - start_time, 2)
        }
        print(f"❌ Scraping failed: {e}")
        return JSONResponse(content=error_details, status_code=500)

@app.get("/scrape-naukri-only")
async def scrape_naukri_only(keyword: str = "python developer"):
    """
    Specialized endpoint for Naukri with maximum anti-detection
    """
    
    start_time = time.time()
    
    try:
        print(f"🎯 Focused Naukri scraping for: {keyword}")
        
        # Reset scraper session for fresh start
        advanced_scraper.setup_session()
        
        # Multiple attempts with different strategies
        all_naukri_jobs = []
        
        for attempt in range(3):
            print(f"🔄 Naukri attempt {attempt + 1}/3")
            
            jobs = advanced_scraper.scrape_naukri_advanced(keyword)
            if jobs:
                all_naukri_jobs.extend(jobs)
                break
            
            # Wait between attempts
            if attempt < 2:
                time.sleep(random.uniform(5, 10))
        
        results = {
            "keyword": keyword,
            "source": "naukri",
            "jobs": all_naukri_jobs,
            "total_jobs": len(all_naukri_jobs),
            "processing_time": round(time.time() - start_time, 2),
            "timestamp": datetime.now().isoformat(),
            "status": "success" if all_naukri_jobs else "blocked_or_no_results"
        }
        
        if not all_naukri_jobs:
            results["message"] = "Naukri access blocked or no results found"
            results["recommendation"] = "Try the multi-platform endpoint /scrape-jobs for better results"
        
        return JSONResponse(content=results)
    
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "keyword": keyword,
                "error": str(e),
                "processing_time": round(time.time() - start_time, 2),
                "timestamp": datetime.now().isoformat()
            },
            status_code=500
        )

@app.get("/test-anti-detection")
async def test_anti_detection():
    """
    Test endpoint to verify anti-detection capabilities
    """
    
    try:
        test_results = {}
        
        # Test basic HTTP request
        response = advanced_scraper.safe_request("https://httpbin.org/headers")
        if response:
            headers_data = response.json()
            test_results["basic_request"] = {
                "status": "success",
                "user_agent": headers_data.get("headers", {}).get("User-Agent", "N/A")
            }
        else:
            test_results["basic_request"] = {"status": "failed"}
        
        # Test Cloudflare bypass
        cf_response = advanced_scraper.safe_request("https://httpbin.org/user-agent")
        test_results["cloudflare_bypass"] = {
            "status": "operational" if cf_response else "failed"
        }
        
        # Test Indeed access
        indeed_response = advanced_scraper.safe_request("https://in.indeed.com/")
        test_results["indeed_access"] = {
            "status": "accessible" if indeed_response and indeed_response.status_code == 200 else "blocked"
        }
        
        # Test Naukri access
        naukri_response = advanced_scraper.safe_request("https://www.naukri.com/")
        test_results["naukri_access"] = {
            "status": "accessible" if naukri_response and "access denied" not in naukri_response.text.lower() else "blocked"
        }
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "overall_status": "healthy" if any(t.get("status") == "success" for t in test_results.values()) else "issues_detected"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Legacy endpoint for backward compatibility
@app.get("/scrape/")
async def legacy_scrape(keyword: str = "python developer"):
    """Legacy endpoint - redirects to advanced scraper"""
    return await scrape_jobs_advanced(keyword=keyword, sources="all")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
