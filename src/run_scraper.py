import logging
import time
from src.config import settings
from src.database.operations import DatabaseOperations
from src.database.models import Job
from src.scrapers.linkedin_scraper import LinkedInScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scraper():
    """Run the job scraper"""
    db = DatabaseOperations()
    scraper = LinkedInScraper()
    
    try:
        # Connect to database
        db.connect()
        
        # Set up scraper
        if not scraper.setup():
            logger.error("Failed to set up scraper")
            return
        
        # Get jobs
        jobs = scraper.scrape()
        logger.info(f"Scraped {len(jobs)} jobs")
        
        # Save jobs to database
        saved_count = 0
        for job in jobs:
            # Check if job already exists
            if db.job_exists(job.link):
                logger.info(f"Job already exists: {job.title} at {job.company}")
                continue
            
            # Save job
            if db.save_job(job):
                saved_count += 1
                
            # Add a small delay between saving jobs
            time.sleep(0.5)
        
        logger.info(f"Saved {saved_count} new jobs to database")
        
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
    finally:
        # Clean up resources
        scraper.cleanup()
        db.close()
        logger.info("Scraper run completed")

if __name__ == "__main__":
    # Run the scraper periodically
    while True:
        try:
            run_scraper()
        except Exception as e:
            logger.error(f"Error in scraper: {e}")
        
        # Sleep for a specified interval
        logger.info(f"Sleeping for {settings.SCRAPER_INTERVAL_SECONDS} seconds")
        time.sleep(settings.SCRAPER_INTERVAL_SECONDS)