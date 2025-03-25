from abc import ABC, abstractmethod
from src.database.models import Job

class BaseEvaluator(ABC):
    """Base class for job evaluators"""
    
    @abstractmethod
    def setup(self):
        """Set up the evaluator"""
        pass
    
    @abstractmethod
    def evaluate(self, job: Job) -> dict:
        """Evaluate a job"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up resources"""
        pass