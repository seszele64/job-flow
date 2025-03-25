import logging
import json
import requests
from src.config import settings
from src.database.models import Job
from src.evaluators.base import BaseEvaluator

logger = logging.getLogger(__name__)

class OpenRouterEvaluator(BaseEvaluator):
    """OpenRouter job evaluator implementation"""
    
    def __init__(self):
        """Initialize the OpenRouter evaluator"""
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.LLM_MODEL
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def setup(self):
        """Set up the OpenRouter evaluator"""
        if not self.api_key:
            logger.error("OpenRouter API key not provided in .env file")
            return False
        return True
    
    def evaluate(self, job: Job) -> dict:
        """Evaluate a job"""
        if not self.api_key:
            if not self.setup():
                return {"is_relevant": False, "reason": "Evaluator not set up properly"}
        
        try:
            # Form the evaluation prompt
            prompt = self._create_evaluation_prompt(job)
            
            # Call the LLM API
            result = self._call_llm_api(prompt)
            
            # Parse the result
            return self._parse_evaluation_result(result)
        except Exception as e:
            logger.error(f"Error evaluating job: {e}")
            return {
                "is_relevant": False,
                "score": 0,
                "reason": f"Error during evaluation: {str(e)}",
                "summary": "Error occurred during evaluation"
            }
    
    def _create_evaluation_prompt(self, job: Job) -> str:
        """Create an evaluation prompt for the job"""
        # Get user profile from environment variables
        user_skills = settings.get("USER_SKILLS", "Python, Data Science")
        user_experience = settings.get("USER_EXPERIENCE", "5+ years in software development")
        user_preferences = settings.get("USER_PREFERENCES", "Remote work")
        
        prompt = f"""
        Please evaluate this job offer against my profile and provide a JSON response.

        JOB DETAILS:
        Title: {job.title}
        Company: {job.company}
        Location: {job.location}
        Description: {job.description}

        MY PROFILE:
        Skills: {user_skills}
        Experience: {user_experience}
        Preferences: {user_preferences}

        Analyze the job description and determine how well it matches my skills, experience, and preferences. 
        Consider technical requirements, experience level, and work arrangements (remote/on-site).

        Return a JSON object with the following structure:
        {{
          "is_relevant": true/false,
          "score": 0-100,
          "reason": "Brief explanation why this job is or isn't a good match",
          "summary": "Summary of the key points of this job and why it's a good match (if relevant)",
          "skills_match": ["list", "of", "matching", "skills"],
          "missing_skills": ["list", "of", "required", "skills", "I", "don't", "have"]
        }}

        Ensure your response can be parsed as valid JSON.
        """
        
        return prompt
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call the OpenRouter API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that evaluates job offers."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _parse_evaluation_result(self, result: str) -> dict:
        """Parse the evaluation result from the LLM"""
        try:
            evaluation = json.loads(result)
            return evaluation
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return {
                "is_relevant": False,
                "score": 0,
                "reason": "Failed to parse LLM response",
                "summary": "Error evaluating job"
            }
    
    def cleanup(self):
        """Clean up resources"""
        # No cleanup needed for API-based evaluator
        pass