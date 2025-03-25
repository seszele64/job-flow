import logging
import time
from src.config import settings
from src.database.operations import DatabaseOperations
from src.database.models import RelevantJob, RejectedJob
from src.evaluators.openrouter import OpenRouterEvaluator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_evaluator():
    """Run the job evaluator"""
    db = DatabaseOperations()
    evaluator = OpenRouterEvaluator()
    
    try:
        # Connect to database
        db.connect()
        
        # Set up evaluator
        if not evaluator.setup():
            logger.error("Failed to set up evaluator")
            return
        
        # Get unevaluated jobs
        unevaluated_jobs = db.get_unevaluated_jobs()
        logger.info(f"Found {len(unevaluated_jobs)} unevaluated jobs")
        
        # Evaluate each job
        for job in unevaluated_jobs:
            try:
                # Evaluate job
                evaluation = evaluator.evaluate(job)
                
                # Save evaluation result
                if evaluation["is_relevant"]:
                    relevant_job = RelevantJob(
                        job_id=job.id,
                        evaluation_score=evaluation["score"],
                        evaluation_summary=evaluation["summary"]
                    )
                    db.save_relevant_job(relevant_job)
                else:
                    rejected_job = RejectedJob(
                        job_id=job.id,
                        reason=evaluation["reason"]
                    )
                    db.save_rejected_job(rejected_job)
                
                # Add a small delay between evaluations
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error evaluating job {job.id}: {e}")
        
    except Exception as e:
        logger.error(f"Error running evaluator: {e}")
    finally:
        # Clean up resources
        evaluator.cleanup()
        db.close()
        logger.info("Evaluator run completed")

if __name__ == "__main__":
    # Run the evaluator periodically
    while True:
        try:
            run_evaluator()
        except Exception as e:
            logger.error(f"Error in evaluator: {e}")
        
        # Sleep for a specified interval
        logger.info(f"Sleeping for {settings.EVALUATOR_INTERVAL_SECONDS} seconds")
        time.sleep(settings.EVALUATOR_INTERVAL_SECONDS)