import os
import requests
import json
import base64
from typing import Dict, Optional, List
from fastapi import HTTPException

class GitHubService:
    def __init__(self):
        self.token = os.getenv('GIT_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> Dict:
        """Create a new GitHub repository"""
        data = {
            'name': repo_name,
            'description': description,
            'private': private,
            'auto_init': True,
            'gitignore_template': 'Node'
        }
        
        response = requests.post(
            f'{self.base_url}/user/repos',
            headers=self.headers,
            json=data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create repository: {response.text}"
            )
    
    def create_file(self, username: str, repo_name: str, file_path: str, content: str, commit_message: str) -> Dict:
        """Create or update a file in the repository"""
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            'message': commit_message,
            'content': encoded_content
        }
        
        response = requests.put(
            f'{self.base_url}/repos/{username}/{repo_name}/contents/{file_path}',
            headers=self.headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create file: {response.text}"
            )
    
    def create_multiple_files(self, username: str, repo_name: str, files: List[Dict], commit_message: str = "Initial project setup") -> List[Dict]:
        """Create multiple files in the repository"""
        results = []
        
        for file_info in files:
            try:
                result = self.create_file(
                    username, 
                    repo_name, 
                    file_info['path'], 
                    file_info['content'], 
                    commit_message
                )
                results.append({
                    'path': file_info['path'],
                    'status': 'success',
                    'data': result
                })
            except Exception as e:
                results.append({
                    'path': file_info['path'],
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        response = requests.get(
            f'{self.base_url}/user',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get user info: {response.text}"
            )
    
    def list_repositories(self, username: str) -> List[Dict]:
        """List user repositories"""
        response = requests.get(
            f'{self.base_url}/users/{username}/repos',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to list repositories: {response.text}"
            )

# Global instance
github_service = GitHubService()