import pytest
from abc import ABC
from src.scrapers.base import BaseScraper
from src.database.models import Job
from typing import List

def test_base_scraper_is_abstract():
    """Test that BaseScraper is an abstract class"""
    assert issubclass(BaseScraper, ABC)

def test_base_scraper_cannot_be_instantiated():
    """Test that BaseScraper cannot be instantiated directly"""
    with pytest.raises(TypeError):
        BaseScraper()

def test_concrete_class_must_implement_abstract_methods():
    """Test that concrete classes must implement all abstract methods"""
    
    # Create a concrete class that doesn't implement all methods
    class IncompleteImplementation(BaseScraper):
        def setup(self):
            pass
        
        def scrape(self, keywords: List[str]) -> List[Job]:
            pass
        
        # Missing cleanup method
    
    # Should raise TypeError when instantiated
    with pytest.raises(TypeError):
        IncompleteImplementation()
    
    # Create a complete implementation
    class CompleteImplementation(BaseScraper):
        def setup(self):
            pass
        
        def scrape(self, keywords: List[str]) -> List[Job]:
            return []
        
        def cleanup(self):
            pass
    
    # Should be instantiable
    instance = CompleteImplementation()
    assert isinstance(instance, BaseScraper)
