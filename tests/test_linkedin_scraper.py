import pytest
from unittest.mock import MagicMock, patch
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.database.models import Job

@pytest.fixture
def mock_driver():
    """Create a mock web driver"""
    return MagicMock()

@pytest.fixture
def mock_job_search():
    """Create a mock job search"""
    search = MagicMock()
    job_listing = MagicMock()
    job_listing.title = "Software Engineer"
    job_listing.company = "Test Company"
    job_listing.location = "Remote"
    job_listing.description = "A test job description"
    job_listing.linkedin_url = "https://linkedin.com/jobs/1"
    search.search.return_value = [job_listing]
    return search

@patch('src.scrapers.linkedin_scraper.setup_chrome_driver')
@patch('src.scrapers.linkedin_scraper.actions')
@patch('src.scrapers.linkedin_scraper.JobSearch')
def test_setup_success(mock_job_search_class, mock_actions, mock_setup_driver, mock_driver):
    """Test successful setup of LinkedIn scraper"""
    mock_setup_driver.return_value = mock_driver
    mock_job_search_class.return_value = MagicMock()
    
    with patch('src.scrapers.linkedin_scraper.settings') as mock_settings:
        mock_settings.LINKEDIN_USERNAME = "test@example.com"
        mock_settings.LINKEDIN_PASSWORD = "password"
        
        scraper = LinkedInScraper()
        result = scraper.setup()
        
        assert result is True
        mock_setup_driver.assert_called_once()
        mock_actions.login.assert_called_once_with(mock_driver, "test@example.com", "password")
        mock_job_search_class.assert_called_once()

@patch('src.scrapers.linkedin_scraper.setup_chrome_driver')
def test_setup_missing_credentials(mock_setup_driver, mock_driver):
    """Test setup failure when credentials are missing"""
    mock_setup_driver.return_value = mock_driver
    
    with patch('src.scrapers.linkedin_scraper.settings') as mock_settings:
        mock_settings.LINKEDIN_USERNAME = None
        mock_settings.LINKEDIN_PASSWORD = None
        
        scraper = LinkedInScraper()
        result = scraper.setup()
        
        assert result is False

@patch('src.scrapers.linkedin_scraper.actions')
def test_setup_login_exception(mock_actions, mock_driver):
    """Test setup failure when login raises an exception"""
    mock_actions.login.side_effect = Exception("Login failed")
    
    with patch('src.scrapers.linkedin_scraper.setup_chrome_driver', return_value=mock_driver):
        with patch('src.scrapers.linkedin_scraper.settings') as mock_settings:
            mock_settings.LINKEDIN_USERNAME = "test@example.com"
            mock_settings.LINKEDIN_PASSWORD = "password"
            
            scraper = LinkedInScraper()
            result = scraper.setup()
            
            assert result is False

def test_scrape_with_setup_needed(mock_job_search):
    """Test scraping when setup is needed first"""
    scraper = LinkedInScraper()
    
    # Mock the setup method
    scraper.setup = MagicMock(return_value=True)
    scraper.job_search = mock_job_search
    
    with patch('src.scrapers.linkedin_scraper.settings') as mock_settings:
        mock_settings.SEARCH_KEYWORDS = ["python"]
        
        jobs = scraper.scrape()
        
        scraper.setup.assert_called_once()
        mock_job_search.search.assert_called_once_with("python")
        assert len(jobs) == 1
        assert jobs[0].title == "Software Engineer"
        assert jobs[0].company == "Test Company"
        assert jobs[0].source == "linkedin"

def test_scrape_with_explicit_keywords(mock_job_search):
    """Test scraping with explicitly provided keywords"""
    scraper = LinkedInScraper()
    scraper.driver = MagicMock()
    scraper.job_search = mock_job_search
    
    jobs = scraper.scrape(keywords=["java", "c++"]) 
    
    # Should have called search twice, once for each keyword
    assert mock_job_search.search.call_count == 2
    assert len(jobs) == 2  # One job per keyword

def test_convert_to_job():
    """Test converting a LinkedIn job listing to a Job object"""
    scraper = LinkedInScraper()
    
    job_listing = MagicMock()
    job_listing.title = "Developer"
    job_listing.company = "Tech Corp"
    job_listing.location = "New York, NY"
    job_listing.description = "Building great software"
    job_listing.linkedin_url = "https://linkedin.com/jobs/123"
    
    job = scraper._convert_to_job(job_listing)
    
    assert job.title == "Developer"
    assert job.company == "Tech Corp"
    assert job.location == "New York, NY"
    assert job.description == "Building great software"
    assert job.link == "https://linkedin.com/jobs/123"
    assert job.source == "linkedin"

def test_convert_to_job_handles_missing_attributes():
    """Test that job conversion gracefully handles missing attributes"""
    scraper = LinkedInScraper()
    
    # Create a more specific mock that only has the title attribute
    job_listing = MagicMock(spec=['title'])
    job_listing.title = "Developer"
    
    # When accessing company, location, description, etc., it will raise AttributeError
    
    job = scraper._convert_to_job(job_listing)
    
    assert job.title == "Developer"
    assert job.company == "Unknown Company"
    assert job.location == "Unknown Location"
    assert job.description == ""
    assert job.link == ""
    assert job.source == "linkedin"

def test_cleanup():
    """Test cleanup of resources"""
    scraper = LinkedInScraper()
    scraper.driver = MagicMock()
    
    # Store a reference to the driver before cleanup
    driver = scraper.driver
    
    scraper.cleanup()
    
    # Assert on the stored reference
    driver.quit.assert_called_once()
    assert scraper.driver is None
    assert scraper.job_search is None
