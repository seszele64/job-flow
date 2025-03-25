# Job Offer Filtering System

An automated system that scrapes job offers, evaluates them against your skills and expectations using an LLM, and stores relevant matches in a database.

## Architecture

The system follows a three-stage pipeline:

1. **Scraper** - Collects job offers from various sources
2. **LLM Evaluator** - Filters offers based on skills/expectations match 
3. **Database** - Stores both relevant offers and rejected offers

```
Scraper → Database → LLM Evaluator → Database
```

## Components

### Scraper

The system scrapes job offers from:
- LinkedIn (using [linkedin_scraper](https://github.com/joeyism/linkedin_scraper))

*Note: jina.ai/reader was considered but can't read behind login*

### LLM Evaluator

The LLM component evaluates if job offers match your skills and expectations:
- Uses OpenRouter.com for structured JSON responses
- Considering Gemini as the model
    - because of reasonable price per 1m tokens and big context 
- Prompt engineering to be established (possibly using LangChain)

### Database

PostgreSQL database running in a separate container with tables for:
- All scraped offers
- Rejected offers (to avoid re-processing)
- Relevant/interesting offers that match your criteria

## Container Structure

- **Database Container**
  - PostgreSQL instance
  - Tables for all offers, relevant offers, and rejected offers
  
- **LLM Container**
  - API interface
  - Prompt management
  
- **Scraper Container**
  - LinkedIn scraper
  - Additional sources can be added later

## Getting Started

*[To be added: setup and installation instructions]*

## Configuration

*[To be added: configuration options]*

## Usage

*[To be added: usage examples]*

## Structure

```
job-flow/
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── src/
│   ├── config/
│   │   └── settings.py         # Centralized settings management
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py             # Base scraper interface
│   │   └── linkedin_scraper.py # LinkedIn implementation
│   ├── evaluators/
│   │   ├── __init__.py
│   │   ├── base.py             # Base evaluator interface
│   │   └── openrouter.py       # OpenRouter implementation
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # Database schema definition
│   │   └── operations.py       # Database operations
│   └── utils/
│       ├── __init__.py
│       └── webdriver.py        # Browser utilities
├── docker/
│   ├── database/
│   │   ├── Dockerfile
│   │   └── init.sql
│   ├── scraper/
│   │   └── Dockerfile
│   └── evaluator/
│       └── Dockerfile
└── tests/
    ├── test_scrapers.py
    ├── test_evaluators.py
    └── test_database.py
```