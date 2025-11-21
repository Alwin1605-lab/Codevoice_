from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from ai_code_generator import ai_generator
from github_service import github_service
from websocket_manager import manager
from fastapi import Header, HTTPException, Depends
from auth_dependencies import get_current_user_id
import uuid

router = APIRouter()

class ProjectGenerationRequest(BaseModel):
    name: str
    description: str
    type: str = "web-app"
    framework: str = "react"
    features: List[str] = []
    pushToGithub: bool = False
    githubSettings: Optional[Dict] = None

class GitHubRepoRequest(BaseModel):
    repo_name: str
    description: str = ""
    private: bool = False

class CollaborationInviteRequest(BaseModel):
    to_user_ids: List[str]
    project_name: str
    message: str = ""

# AI Project Generation Endpoints
@router.post("/generate-ai-project/")
async def generate_ai_project(request: ProjectGenerationRequest):
    """Generate a complete project using AI"""
    try:
        # Generate project structure using AI
        project_result = ai_generator.generate_project_structure(request.dict())
        
        if not project_result.get('success'):
            return {
                "success": False,
                "error": project_result.get('error', 'Unknown error'),
                "fallback_used": True,
                "files": project_result.get('fallback_files', [])
            }
        
        response_data = {
            "success": True,
            "project_name": request.name,
            "description": request.description,
            "framework": request.framework,
            "features": request.features,
            "files": project_result['files'],
            "github_url": None
        }
        
        # If GitHub push is requested, create repository
        if request.pushToGithub and request.githubSettings:
            try:
                github_result = await create_github_repository_with_files(
                    request.name,
                    request.description,
                    project_result['files'],
                    request.githubSettings
                )
                response_data["github_url"] = github_result.get("html_url")
                response_data["github_created"] = True
            except Exception as e:
                response_data["github_error"] = str(e)
                response_data["github_created"] = False
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_github_repository_with_files(repo_name: str, description: str, files: List[Dict], github_settings: Dict):
    """Create GitHub repository and upload all files"""
    
    # Create repository
    repo_data = github_service.create_repository(
        repo_name=repo_name,
        description=description,
        private=github_settings.get('isPublic', True) == False
    )
    
    # Get username from GitHub API
    user_info = github_service.get_user_info()
    username = user_info['login']
    
    # Upload all files
    file_results = github_service.create_multiple_files(
        username=username,
        repo_name=repo_name,
        files=files,
        commit_message="Initial AI-generated project setup"
    )
    
    return {
        "html_url": repo_data["html_url"],
        "clone_url": repo_data["clone_url"],
        "files_uploaded": len([r for r in file_results if r['status'] == 'success']),
        "files_failed": len([r for r in file_results if r['status'] == 'error']),
        "file_results": file_results
    }

# GitHub Integration Endpoints
@router.post("/github/create-repo/")
async def create_github_repo(request: GitHubRepoRequest):
    """Create a new GitHub repository"""
    try:
        result = github_service.create_repository(
            repo_name=request.repo_name,
            description=request.description,
            private=request.private
        )
        return {
            "success": True,
            "repository": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/github/user-info/")
async def get_github_user():
    """Get authenticated GitHub user information"""
    try:
        user_info = github_service.get_user_info()
        return user_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/github/repos/{username}")
async def list_user_repos(username: str):
    """List repositories for a user"""
    try:
        repos = github_service.list_repositories(username)
        return {"repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Collaboration Endpoints
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_name: str = "Anonymous", x_user_id: str = Header(default=None, alias="X-User-Id")):
    """WebSocket endpoint for real-time collaboration"""
    # Require a user id header for stable identity
    user_id = x_user_id or str(uuid.uuid4())
    user_info = {
        'id': user_id,
        'name': user_name,
        'avatar': '',
        'connected_at': None
    }
    
    await manager.connect(websocket, session_id, user_info)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process and broadcast message
            await manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.get("/collaboration/sessions/")
async def list_collaboration_sessions():
    """List all active collaboration sessions"""
    sessions = manager.list_active_sessions()
    return {"sessions": sessions}

@router.post("/collaboration/invite/")
async def send_collaboration_invite(request: CollaborationInviteRequest, x_user_id: str = Header(default=None, alias="X-User-Id")):
    """Send collaboration invites to users"""
    try:
        # For demo purposes, create a session ID
        session_id = str(uuid.uuid4())
        
        # Mock sender info (in real app, get from authentication)
        from_user = {
            'id': x_user_id or 'current_user_id',
            'name': 'Current User',
            'avatar': ''
        }
        
        invites_sent = []
        for user_id in request.to_user_ids:
            invite = await manager.send_collaboration_invite(
                from_user=from_user,
                to_user_id=user_id,
                session_id=session_id,
                project_name=request.project_name
            )
            invites_sent.append(invite)
        
        return {
            "success": True,
            "session_id": session_id,
            "invites_sent": len(invites_sent),
            "invites": invites_sent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collaboration/accept-invite/")
async def accept_collaboration_invite(invite_data: Dict):
    """Accept a collaboration invite"""
    try:
        # In a real implementation, this would:
        # 1. Validate the invite
        # 2. Add user to the collaboration session
        # 3. Update invite status in database
        
        return {
            "success": True,
            "message": "Invite accepted successfully",
            "session_id": invite_data.get("invite_id"),
            "project_id": invite_data.get("project_id")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Project Management
@router.get("/projects/")
async def list_ai_projects():
    """List AI-generated projects"""
    # In a real implementation, this would fetch from database
    # For now, return mock data
    return {
        "projects": [
            {
                "name": "ai-chat-app",
                "description": "Real-time chat application with AI features",
                "framework": "react",
                "features": ["authentication", "real-time-chat", "ai-integration"],
                "created_at": "2025-09-18T10:00:00Z",
                "github_url": "https://github.com/user/ai-chat-app"
            },
            {
                "name": "task-manager",
                "description": "Voice-controlled task management system",
                "framework": "nextjs",
                "features": ["authentication", "database", "voice-control"],
                "created_at": "2025-09-18T09:00:00Z",
                "github_url": "https://github.com/user/task-manager"
            }
        ]
    }

@router.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ai_generator": "active",
            "github_service": "active" if github_service.token else "inactive",
            "websocket_manager": "active"
        }
    }