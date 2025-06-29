"""Enhanced LLM service optimized for local LLMs with robust error handling."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
import json
import aiohttp
from datetime import datetime
import re

from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Enhanced service for interacting with local Ollama LLM with robust error handling."""
    
    def __init__(self):
        self.base_url = settings.ollama_host
        self.model = settings.default_model
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_available = False
        self.max_retries = 3
        self.timeout = 30  # seconds
    
    async def initialize(self):
        """Initialize the LLM service with connection testing."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Test connection and model availability
            await self._test_connection()
            await self._ensure_model_available()
            
            self.is_available = True
            logger.info(f"LLM service initialized successfully with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self.is_available = False
            # Don't raise - allow system to work without LLM
    
    async def _test_connection(self):
        """Test connection to Ollama with retries."""
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        models = await response.json()
                        available_models = [m['name'] for m in models.get('models', [])]
                        logger.info(f"Connected to Ollama. Available models: {available_models}")
                        return
                    else:
                        raise Exception(f"Ollama returned status: {response.status}")
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to connect to Ollama after {self.max_retries} attempts: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _ensure_model_available(self):
        """Ensure the specified model is available, pull if necessary."""
        try:
            # Check if model exists
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    models = await response.json()
                    available_models = [m['name'] for m in models.get('models', [])]
                    
                    if self.model not in available_models:
                        logger.warning(f"Model {self.model} not found. Attempting to pull...")
                        await self._pull_model()
                else:
                    raise Exception(f"Failed to check available models: {response.status}")
        except Exception as e:
            logger.error(f"Error ensuring model availability: {e}")
            raise
    
    async def _pull_model(self):
        """Pull the specified model if not available."""
        try:
            payload = {"name": self.model}
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully pulled model: {self.model}")
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to pull model: {error_text}")
        except Exception as e:
            logger.error(f"Error pulling model {self.model}: {e}")
            raise
    
    async def generate_simple_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a simple response with minimal context - optimized for local LLMs."""
        if not self.is_available:
            return "LLM service is not available. Please check Ollama connection."
        
        # Keep prompts short and focused for local LLMs
        simplified_prompt = self._simplify_prompt(prompt, max_tokens)
        
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": self.model,
                    "prompt": simplified_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.3,  # Lower temperature for more consistent results
                        "top_p": 0.9,
                        "stop": ["\n\n", "###", "---"]  # Stop tokens to prevent rambling
                    }
                }
                
                async with self.session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response", "").strip()
                        
                        if response_text:
                            logger.debug(f"LLM response generated successfully (attempt {attempt + 1})")
                            return response_text
                        else:
                            raise Exception("Empty response from LLM")
                    else:
                        error_text = await response.text()
                        raise Exception(f"LLM generation failed: {error_text}")
                        
            except Exception as e:
                logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All LLM generation attempts failed: {e}")
                    return f"Error generating response: {str(e)}"
                await asyncio.sleep(1)  # Brief pause before retry
        
        return "Failed to generate response after multiple attempts."
    
    def _simplify_prompt(self, prompt: str, max_tokens: int) -> str:
        """Simplify prompts for better local LLM performance."""
        # Remove excessive whitespace and newlines
        simplified = re.sub(r'\s+', ' ', prompt.strip())
        
        # Truncate if too long (leave room for response)
        max_prompt_length = 1000  # Conservative limit for local LLMs
        if len(simplified) > max_prompt_length:
            simplified = simplified[:max_prompt_length] + "..."
        
        # Add clear instruction format
        if not simplified.endswith('.') and not simplified.endswith('?'):
            simplified += "."
        
        return simplified
    
    async def parse_email_content_simple(self, email_content: str) -> Dict[str, Any]:
        """Parse email content with simple, structured approach for local LLMs."""
        if not self.is_available:
            return self._fallback_email_parsing(email_content)
        
        # Truncate email content to manageable size
        content = email_content[:800] if len(email_content) > 800 else email_content
        
        prompt = f"""Extract task information from this email. Respond with ONLY a JSON object:

Email: {content}

Required JSON format:
{{
  "task_title": "brief task name",
  "status": "todo|in_progress|review|done|blocked",
  "priority": "low|medium|high|urgent",
  "description": "brief description"
}}

JSON:"""
        
        try:
            response = await self.generate_simple_response(prompt, max_tokens=200)
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                # Validate required fields
                if self._validate_parsed_email(parsed_data):
                    logger.info("Successfully parsed email with LLM")
                    return parsed_data
            
            # If JSON parsing fails, fall back
            logger.warning("LLM response was not valid JSON, using fallback")
            return self._fallback_email_parsing(email_content)
            
        except Exception as e:
            logger.error(f"Error parsing email with LLM: {e}")
            return self._fallback_email_parsing(email_content)
    
    def _validate_parsed_email(self, data: Dict[str, Any]) -> bool:
        """Validate parsed email data structure."""
        required_fields = ['task_title', 'status', 'priority']
        valid_statuses = ['todo', 'in_progress', 'review', 'done', 'blocked']
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validate status and priority values
        if data['status'] not in valid_statuses:
            data['status'] = 'in_progress'  # Default fallback
        
        if data['priority'] not in valid_priorities:
            data['priority'] = 'medium'  # Default fallback
        
        return True
    
    def _fallback_email_parsing(self, email_content: str) -> Dict[str, Any]:
        """Fallback parsing when LLM is not available or fails."""
        content_lower = email_content.lower()
        
        # Extract basic information using keywords
        result = {
            'task_title': self._extract_task_title(email_content),
            'description': email_content[:200] + "..." if len(email_content) > 200 else email_content,
            'status': self._detect_status(content_lower),
            'priority': self._detect_priority(content_lower)
        }
        
        logger.info("Used fallback email parsing")
        return result
    
    def _extract_task_title(self, content: str) -> str:
        """Extract a reasonable task title from email content."""
        lines = content.strip().split('\n')
        
        # Look for lines that might be task titles
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100 and not line.startswith(('Hi', 'Hello', 'Dear', 'Thanks')):
                # Clean up the line
                title = re.sub(r'^(Re:|Fwd:|Subject:)', '', line, flags=re.IGNORECASE).strip()
                if title:
                    return title[:50]  # Limit length
        
        return "Email Update"
    
    def _detect_status(self, content_lower: str) -> str:
        """Detect task status from email content."""
        status_keywords = {
            'done': ['done', 'completed', 'finished', 'complete', 'delivered'],
            'blocked': ['blocked', 'stuck', 'issue', 'problem', 'blocker', 'waiting'],
            'review': ['review', 'feedback', 'check', 'testing', 'qa'],
            'todo': ['starting', 'begin', 'todo', 'plan', 'will start'],
            'in_progress': ['working', 'progress', 'developing', 'coding', 'implementing']
        }
        
        for status, keywords in status_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return status
        
        return 'in_progress'  # Default
    
    def _detect_priority(self, content_lower: str) -> str:
        """Detect priority from email content."""
        priority_keywords = {
            'urgent': ['urgent', 'asap', 'critical', 'emergency', 'immediately'],
            'high': ['high', 'important', 'priority', 'soon', 'quickly'],
            'low': ['low', 'minor', 'later', 'when possible', 'no rush']
        }
        
        for priority, keywords in priority_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return priority
        
        return 'medium'  # Default
    
    async def generate_simple_summary(self, data: Dict[str, Any], summary_type: str = "status") -> str:
        """Generate simple summaries optimized for local LLMs."""
        if not self.is_available:
            return self._fallback_summary(data, summary_type)
        
        if summary_type == "kanban":
            prompt = f"""Summarize this kanban board data in 2-3 sentences:

Data: {json.dumps(data, default=str)}

Summary:"""
        elif summary_type == "team":
            prompt = f"""Summarize this team status in 2-3 sentences:

Data: {json.dumps(data, default=str)}

Summary:"""
        else:
            prompt = f"""Summarize this information in 2-3 sentences:

Data: {json.dumps(data, default=str)}

Summary:"""
        
        try:
            response = await self.generate_simple_response(prompt, max_tokens=150)
            return response if response else self._fallback_summary(data, summary_type)
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._fallback_summary(data, summary_type)
    
    def _fallback_summary(self, data: Dict[str, Any], summary_type: str) -> str:
        """Generate fallback summaries without LLM."""
        if summary_type == "kanban":
            return f"Kanban board contains {len(data.get('tasks', []))} tasks across multiple columns."
        elif summary_type == "team":
            return f"Team status summary with {len(data.get('members', []))} members."
        else:
            return "Summary of current status and activities."
    
    async def health_check(self) -> Dict[str, Any]:
        """Check LLM service health."""
        try:
            if not self.session:
                return {"status": "unhealthy", "error": "No session"}
            
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    return {
                        "status": "healthy",
                        "model": self.model,
                        "available": self.is_available
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"Ollama returned status {response.status}"
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup LLM service resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_available = False
            logger.info("LLM service cleanup completed")
        except Exception as e:
            logger.error(f"Error during LLM service cleanup: {e}")