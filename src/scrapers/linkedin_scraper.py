import logging
import time
from typing import List, Optional
from linkedin_scraper import JobSearch, actions
from src.config import settings
from src.database.models import Job
from src.scrapers.base import BaseScraper
from src.utils.webdriver import setup_chrome_driver

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper implementation"""
    
    def __init__(self):
        """Initialize the LinkedIn scraper"""
        self.driver = None
        self.job_search = None
    
    def setup(self):
        """Set up the LinkedIn scraper"""
        logger.info("Setting up LinkedIn scraper")
        self.driver = setup_chrome_driver()
        
        # Login to LinkedIn
        email = settings.LINKEDIN_USERNAME
        password = settings.LINKEDIN_PASSWORD
        
        if not email or not password:
            logger.error("LinkedIn credentials not provided in .env file")
            return False
            
        try:
            logger.info("Logging in to LinkedIn...")
            actions.login(self.driver, email, password)
            logger.info("Login successful")
            
            # Initialize job search
            self.job_search = JobSearch(driver=self.driver, close_on_complete=False, scrape=False)
            return True
        except Exception as e:
            logger.error(f"Error setting up LinkedIn scraper: {e}")
            return False
    
    def scrape(self, keywords: List[str] = None) -> List[Job]:
        """Scrape LinkedIn jobs based on keywords"""
        if not self.driver or not self.job_search:
            if not self.setup():
                return []
        
        if not keywords:
            keywords = settings.SEARCH_KEYWORDS
        
        all_jobs = []
        for keyword in keywords:
            try:
                logger.info(f"Searching for jobs with keyword: {keyword}")
                job_listings = self.job_search.search(keyword)
                logger.info(f"Found {len(job_listings)} job listings for keyword: {keyword}")
                
                for listing in job_listings:
                    job = self._convert_to_job(listing)
                    if job:
                        all_jobs.append(job)
                
                # Add a delay between searches to avoid rate limiting
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error searching for jobs with keyword '{keyword}': {e}")
        
        return all_jobs
    
    def _convert_to_job(self, job_listing) -> Optional[Job]:
        """Convert a LinkedIn job listing to a Job object"""
        try:
            return Job(
                title=job_listing.title if hasattr(job_listing, 'title') else "Unknown Title",
                company=job_listing.company if hasattr(job_listing, 'company') else "Unknown Company",
                location=job_listing.location if hasattr(job_listing, 'location') else "Unknown Location",
                description=job_listing.description if hasattr(job_listing, 'description') else "",
                link=job_listing.linkedin_url if hasattr(job_listing, 'linkedin_url') else "",
                source="linkedin"
            )
        except Exception as e:
            logger.error(f"Error converting job listing: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            logger.info("Closing browser")
            self.driver.quit()
            self.driver = None
            self.job_search = None