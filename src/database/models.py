from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Job:
    """Data model representing a job in the database"""
    id: Optional[int] = None
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    link: str = ""
    source: str = ""
    scraped_at: datetime = None

@dataclass
class RelevantJob:
    """Data model representing a relevant job in the database"""
    id: Optional[int] = None
    job_id: int = None
    evaluation_score: float = 0.0
    evaluation_summary: str = ""
    evaluated_at: datetime = None

@dataclass
class RejectedJob:
    """Data model representing a rejected job in the database"""
    id: Optional[int] = None
    job_id: int = None
    reason: str = ""
    evaluated_at: datetime = None