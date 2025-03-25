import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DB_HOST = os.getenv("DB_HOST", "database")
DB_NAME = os.getenv("POSTGRES_DB", "jobflow")
DB_USER = os.getenv("POSTGRES_USER", "jobflow")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

# LinkedIn settings
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "Python Developer").split(",")
SCRAPER_INTERVAL_SECONDS = int(os.getenv("SCRAPER_INTERVAL_SECONDS", 21600))

# LLM settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemini-1.5-pro")
EVALUATOR_INTERVAL_SECONDS = int(os.getenv("EVALUATOR_INTERVAL_SECONDS", 3600))

# Selenium settings
HEADLESS = os.getenv("ENVIRONMENT", "development") == "production"