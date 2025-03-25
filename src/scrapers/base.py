from abc import ABC, abstractmethod
from typing import List
from src.database.models import Job

class BaseScraper(ABC):
    """Base class for job scrapers"""
    
    @abstractmethod
    def setup(self):
        """Set up the scraper"""
        pass
    
    @abstractmethod
    def scrape(self, keywords: List[str]) -> List[Job]:
        """Scrape jobs based on keywords"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up resources"""
        pass