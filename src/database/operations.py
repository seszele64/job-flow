import logging
import psycopg2
from datetime import datetime
from typing import List, Optional
from src.config import settings
from src.database.models import Job, RelevantJob, RejectedJob

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Database operations for job management"""
    
    def __init__(self, host=None, database=None, user=None, password=None):
        """Initialize database connection"""
        self.host = host or settings.DB_HOST
        self.database = database or settings.DB_NAME
        self.user = user or settings.DB_USER
        self.password = password or settings.DB_PASSWORD
        self.conn = None
    
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info("Connected to database")
            return self.conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def save_job(self, job: Job) -> Optional[int]:
        """Save a job to the database"""
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO scraped_jobs (title, company, location, description, link, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (job.title, job.company, job.location, job.description, job.link, job.source)
            )
            job_id = cursor.fetchone()[0]
            self.conn.commit()
            logger.info(f"Saved job {job_id} to database")
            return job_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving job to database: {e}")
            return None
    
    def job_exists(self, job_link: str) -> bool:
        """Check if a job with the given link already exists in the database"""
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id FROM scraped_jobs WHERE link = %s",
                (job_link,)
            )
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if job exists: {e}")
            return False
    
    def get_unevaluated_jobs(self) -> List[Job]:
        """Get jobs that haven't been evaluated yet"""
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT j.id, j.title, j.company, j.location, j.description, j.link, j.source, j.scraped_at
                FROM scraped_jobs j
                LEFT JOIN relevant_jobs r ON j.id = r.job_id
                LEFT JOIN rejected_jobs x ON j.id = x.job_id
                WHERE r.id IS NULL AND x.id IS NULL
                """
            )
            jobs = []
            for row in cursor.fetchall():
                job = Job(
                    id=row[0],
                    title=row[1],
                    company=row[2],
                    location=row[3],
                    description=row[4],
                    link=row[5],
                    source=row[6],
                    scraped_at=row[7]
                )
                jobs.append(job)
            logger.info(f"Found {len(jobs)} unevaluated jobs")
            return jobs
        except Exception as e:
            logger.error(f"Error getting unevaluated jobs: {e}")
            return []
    
    def save_relevant_job(self, relevant_job: RelevantJob) -> Optional[int]:
        """Save a relevant job to the database"""
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO relevant_jobs (job_id, evaluation_score, evaluation_summary)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (relevant_job.job_id, relevant_job.evaluation_score, relevant_job.evaluation_summary)
            )
            relevant_job_id = cursor.fetchone()[0]
            self.conn.commit()
            logger.info(f"Job {relevant_job.job_id} marked as relevant")
            return relevant_job_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving relevant job: {e}")
            return None
    
    def save_rejected_job(self, rejected_job: RejectedJob) -> Optional[int]:
        """Save a rejected job to the database"""
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO rejected_jobs (job_id, reason)
                VALUES (%s, %s)
                RETURNING id
                """,
                (rejected_job.job_id, rejected_job.reason)
            )
            rejected_job_id = cursor.fetchone()[0]
            self.conn.commit()
            logger.info(f"Job {rejected_job.job_id} marked as rejected")
            return rejected_job_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving rejected job: {e}")
            return None