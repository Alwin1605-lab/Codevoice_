"""
Judge0 API integration for code execution.
Works with localhost and provides reliable code execution for multiple languages.
"""

import asyncio
import aiohttp
import base64
import json
import time
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class Judge0Executor:
    """Judge0 API executor for running code in multiple languages."""
    
    # Judge0 CE API endpoint (free community edition - direct access)
    BASE_URL = "https://judge0-ce.p.rapidapi.com"
    FREE_BASE_URL = "https://ce.judge0.com"  # Free community edition without API key
    
    # Language ID mappings for Judge0
    LANGUAGE_IDS = {
        'python': 71,      # Python 3.8.1
        'python3': 71,
        'javascript': 63,  # JavaScript (Node.js 12.14.0)
        'java': 62,        # Java (OpenJDK 13.0.1)
        'cpp': 54,         # C++ (GCC 9.2.0)
        'c': 50,           # C (GCC 9.2.0)
        'csharp': 51,      # C# (Mono 6.6.0.161)
        'go': 60,          # Go (1.13.5)
        'rust': 73,        # Rust (1.40.0)
        'php': 68,         # PHP (7.4.1)
        'ruby': 72,        # Ruby (2.7.0)
        'kotlin': 78,      # Kotlin (1.3.70)
        'swift': 83,       # Swift (5.2.3)
        'typescript': 74,  # TypeScript (3.7.4)
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Judge0 executor with optional API key for higher rate limits."""
        self.api_key = api_key
        self.use_free_tier = not api_key  # Use free tier if no API key
        
        if self.use_free_tier:
            self.base_url = self.FREE_BASE_URL
            self.headers = {'Content-Type': 'application/json'}
        else:
            self.base_url = self.BASE_URL
            self.headers = {
                'Content-Type': 'application/json',
                'X-RapidAPI-Key': api_key,
                'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
            }
    
    async def execute_code(
        self, 
        language: str, 
        code: str, 
        inputs: str = "",
        timeout: int = 10
    ) -> Tuple[str, str, str]:
        """
        Execute code using Judge0 API.
        
        Args:
            language: Programming language
            code: Source code to execute
            inputs: Input data for the program
            timeout: Maximum execution time in seconds
            
        Returns:
            Tuple of (stdout, stderr, compile_output)
        """
        try:
            language_id = self.LANGUAGE_IDS.get(language.lower())
            if not language_id:
                raise ValueError(f"Unsupported language: {language}")
            
            # Prepare submission data
            submission_data = {
                "language_id": language_id,
                "source_code": base64.b64encode(code.encode()).decode(),
                "stdin": base64.b64encode(inputs.encode()).decode() if inputs else "",
                "expected_output": "",
                "cpu_time_limit": timeout,
                "memory_limit": 128000,  # 128 MB
                "wall_time_limit": timeout + 5,
            }
            
            async with aiohttp.ClientSession() as session:
                # Submit code for execution
                submission_url = f"{self.base_url}/submissions"
                
                logger.info(f"Submitting {language} code to Judge0 at {submission_url}...")
                async with session.post(
                    submission_url, 
                    headers=self.headers,
                    json=submission_data
                ) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        raise Exception(f"Failed to submit code: {response.status} - {error_text}")
                    
                    result = await response.json()
                    token = result.get('token')
                    if not token:
                        raise Exception("No token received from Judge0")
                
                # Poll for results
                logger.info(f"Polling for results with token: {token}")
                return await self._poll_for_results(session, token, timeout * 2)
                
        except Exception as e:
            logger.error(f"Judge0 execution failed: {e}")
            return "", str(e), f"Execution failed: {e}"
    
    async def _poll_for_results(
        self, 
        session: aiohttp.ClientSession, 
        token: str, 
        max_wait: int = 30
    ) -> Tuple[str, str, str]:
        """Poll Judge0 API for execution results."""
        result_url = f"{self.BASE_URL}/submissions/{token}"
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            async with session.get(result_url, headers=self.headers) as response:
                if response.status != 200:
                    continue
                
                result = await response.json()
                status_id = result.get('status', {}).get('id')
                
                # Status: 1=In Queue, 2=Processing, 3=Accepted, 4=Wrong Answer, 5=Time Limit Exceeded, etc.
                if status_id in [1, 2]:  # Still processing
                    await asyncio.sleep(1)
                    continue
                
                # Execution completed
                stdout = ""
                stderr = ""
                compile_output = ""
                
                if result.get('stdout'):
                    stdout = base64.b64decode(result['stdout']).decode()
                if result.get('stderr'):
                    stderr = base64.b64decode(result['stderr']).decode()
                if result.get('compile_output'):
                    compile_output = base64.b64decode(result['compile_output']).decode()
                
                # Handle different status codes
                status_description = result.get('status', {}).get('description', 'Unknown')
                if status_id == 3:  # Accepted
                    return stdout, stderr, compile_output
                elif status_id == 6:  # Compilation Error
                    return "", stderr or compile_output, f"Compilation Error: {compile_output}"
                elif status_id == 5:  # Time Limit Exceeded
                    return stdout, "Time Limit Exceeded", compile_output
                elif status_id == 4:  # Wrong Answer (runtime error)
                    return stdout, stderr or "Runtime Error", compile_output
                else:
                    return stdout, stderr or f"Execution failed: {status_description}", compile_output
        
        return "", "Execution timeout - no response from Judge0", ""
    
    def get_supported_languages(self) -> Dict[str, int]:
        """Get mapping of supported languages to their Judge0 IDs."""
        return self.LANGUAGE_IDS.copy()

# Global executor instance
judge0_executor = Judge0Executor()

async def execute_with_judge0(language: str, code: str, inputs: str = "") -> Tuple[str, str, str]:
    """
    Execute code using Judge0 API.
    
    Args:
        language: Programming language
        code: Source code
        inputs: Input data
        
    Returns:
        Tuple of (stdout, stderr, compile_output)
    """
    return await judge0_executor.execute_code(language, code, inputs)

def is_language_supported(language: str) -> bool:
    """Check if a language is supported by Judge0."""
    return language.lower() in judge0_executor.LANGUAGE_IDS

def get_language_info() -> Dict[str, any]:
    """Get information about supported languages."""
    return {
        "supported_languages": list(judge0_executor.LANGUAGE_IDS.keys()),
        "total_languages": len(judge0_executor.LANGUAGE_IDS),
        "service": "Judge0 Community Edition",
        "free_tier": "50 requests/day",
        "works_with_localhost": True
    }