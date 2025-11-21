"""
Database-backed Project API that actually saves projects to MongoDB.
This replaces the file-system only approach with proper database persistence.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from beanie import PydanticObjectId

from models.project_models import Project, ProjectFile, CodeSession, VoiceCommand
from models.user_models import User
from auth_dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    """Model for creating a new project."""
    name: str
    description: str
    natural_language_prompt: Optional[str] = ""
    project_type: Optional[str] = None
    framework: Optional[str] = None
    features: Optional[List[str]] = None
    github_repo_url: Optional[str] = None
    is_public: bool = False
    user_id: str  # Add user_id to the request model
    ai_generated: Optional[bool] = False
    gemini_metadata: Optional[dict] = None
    project_structure: Optional[dict] = None
    recommended_dependencies: Optional[dict] = None
    environment_variables: Optional[dict] = None
    scripts: Optional[dict] = None
    setup_instructions: Optional[List[str]] = None

class ProjectUpdate(BaseModel):
    """Model for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    features: Optional[List[str]] = None
    github_repo_url: Optional[str] = None
    is_public: Optional[bool] = None

class FileCreate(BaseModel):
    """Model for adding files to a project."""
    file_path: str
    file_name: str
    content: Optional[str] = None
    file_type: Optional[str] = None
    language: Optional[str] = None

class CodeSessionCreate(BaseModel):
    """Model for creating a code session."""
    project_id: Optional[str] = None
    user_id: str
    session_name: Optional[str] = None
    code_content: Optional[str] = None
    language: Optional[str] = None

@router.post("/create")
async def create_project(project_data: ProjectCreate = Body(...), current_user: User = Depends(get_current_user)):
    """Create a new project and save to database."""
    try:
        logger.info(f"Creating project: {project_data.name}")
        
        # Authorization: ensure the user_id matches the authenticated user
        if project_data.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not allowed to create project for another user")

        # Create the project document
        project = Project(
            user_id=project_data.user_id,
            name=project_data.name,
            description=project_data.description,
            natural_language_prompt=project_data.natural_language_prompt or "",
            project_type=project_data.project_type,
            framework=project_data.framework,
            features=project_data.features or [],
            github_repo_url=project_data.github_repo_url,
            is_public=project_data.is_public,
            ai_generated=project_data.ai_generated or False,
            gemini_metadata=project_data.gemini_metadata,
            project_structure=project_data.project_structure,
            recommended_dependencies=project_data.recommended_dependencies,
            environment_variables=project_data.environment_variables,
            scripts=project_data.scripts,
            setup_instructions=project_data.setup_instructions,
            generation_status="completed",
            files=[]
        )
        
        # Save to database
        await project.save()
        
        # Log project structure for debugging
        logger.info(f"Project created successfully with ID: {project.id}")
        if project.project_structure:
            files_count = len(project.project_structure.get('files', {}))
            folders_count = len(project.project_structure.get('folders', []))
            logger.info(f"Project structure: {files_count} files, {folders_count} folders")
            
            # Log first file as sample
            if files_count > 0:
                first_file = list(project.project_structure['files'].keys())[0]
                file_data = project.project_structure['files'][first_file]
                has_content = 'content' in file_data if isinstance(file_data, dict) else False
                content_len = len(file_data.get('content', '')) if isinstance(file_data, dict) else len(str(file_data))
                logger.info(f"Sample file '{first_file}': has_content={has_content}, length={content_len}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Project created successfully",
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "framework": project.framework,
                    "features": project.features,
                    "created_at": project.created_at.isoformat(),
                    "is_public": project.is_public
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.get("/list")
async def list_projects(user_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """List all projects (optionally filtered by user)."""
    try:
        logger.info("Listing projects")
        
        # Get projects (all for now, filter by user_id if provided)
        if user_id:
            projects = await Project.find(Project.user_id == user_id).to_list()
        else:
            # If listing without filter, only return user's own projects
            projects = await Project.find(Project.user_id == str(current_user.id)).to_list()
        
        project_list = []
        for project in projects:
            project_list.append({
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "framework": project.framework,
                "features": project.features,
                "file_count": len(project.files),
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "is_public": project.is_public,
                "generation_status": project.generation_status
            })
        
        logger.info(f"Found {len(project_list)} projects")
        return JSONResponse(content={"projects": project_list})
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")

@router.get("/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific project by ID."""
    try:
        logger.info(f"Getting project: {project_id}")
        
        # Find project by ID
        project = await Project.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.user_id != str(current_user.id) and not project.is_public:
            raise HTTPException(status_code=403, detail="Not authorized to view this project")
        
        project_data = {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "natural_language_prompt": project.natural_language_prompt,
            "framework": project.framework,
            "features": project.features,
            "github_repo_url": project.github_repo_url,
            "is_public": project.is_public,
            "generation_status": project.generation_status,
            "files": [
                {
                    "file_path": f.file_path,
                    "file_name": f.file_name,
                    "content": f.content,
                    "file_type": f.file_type,
                    "language": f.language,
                    "size_bytes": f.size_bytes,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in project.files
            ],
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
        
        return JSONResponse(content={"project": project_data})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@router.put("/{project_id}")
async def update_project(project_id: str, project_data: ProjectUpdate = Body(...), current_user: User = Depends(get_current_user)):
    """Update a project."""
    try:
        logger.info(f"Updating project: {project_id}")
        
        # Find project by ID
        project = await Project.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to update this project")
        
        # Update fields
        update_data = project_data.dict(exclude_none=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        await project.save()
        
        logger.info(f"Project {project_id} updated successfully")
        return JSONResponse(content={"message": "Project updated successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@router.post("/{project_id}/files")
async def add_file_to_project(project_id: str, file_data: FileCreate = Body(...), current_user: User = Depends(get_current_user)):
    """Add a file to a project."""
    try:
        logger.info(f"Adding file to project {project_id}: {file_data.file_name}")
        
        # Find project by ID
        project = await Project.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to modify this project")
        
        # Create new file
        new_file = ProjectFile(
            file_path=file_data.file_path,
            file_name=file_data.file_name,
            content=file_data.content,
            file_type=file_data.file_type,
            language=file_data.language,
            size_bytes=len(file_data.content.encode('utf-8')) if file_data.content else 0
        )
        
        # Add file to project
        project.files.append(new_file)
        project.updated_at = datetime.utcnow()
        await project.save()
        
        logger.info(f"File {file_data.file_name} added to project {project_id}")
        return JSONResponse(content={"message": "File added successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding file to project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add file: {str(e)}")

@router.get("/projects/{project_id}/debug")
async def debug_project_structure(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to inspect project structure."""
    try:
        project = await Project.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Return detailed structure info
        debug_info = {
            "project_name": project.name,
            "project_id": str(project.id),
            "has_project_structure": project.project_structure is not None,
            "structure_keys": list(project.project_structure.keys()) if project.project_structure else [],
        }
        
        if project.project_structure:
            if 'files' in project.project_structure:
                files_dict = project.project_structure['files']
                debug_info["files_count"] = len(files_dict)
                debug_info["file_paths"] = list(files_dict.keys())[:10]  # First 10 files
                debug_info["sample_file"] = {}
                
                # Show a sample file
                if files_dict:
                    first_file = list(files_dict.keys())[0]
                    file_data = files_dict[first_file]
                    debug_info["sample_file"] = {
                        "path": first_file,
                        "type": str(type(file_data)),
                        "is_dict": isinstance(file_data, dict),
                        "content_preview": str(file_data)[:200] if file_data else "empty"
                    }
                    if isinstance(file_data, dict):
                        debug_info["sample_file"]["keys"] = list(file_data.keys())
                        debug_info["sample_file"]["has_content"] = 'content' in file_data
                        debug_info["sample_file"]["content_length"] = len(file_data.get('content', ''))
            
            if 'folders' in project.project_structure:
                debug_info["folders_count"] = len(project.project_structure['folders'])
                debug_info["folders"] = project.project_structure['folders'][:10]
        
        return JSONResponse(content=debug_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Delete a project."""
    try:
        logger.info(f"Deleting project: {project_id}")
        
        # Find and delete project
        project = await Project.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this project")
        
        await project.delete()
        logger.info(f"Project {project_id} deleted successfully")
        
        return JSONResponse(content={"message": "Project deleted successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

@router.post("/code-session")
async def create_code_session(session_data: CodeSessionCreate = Body(...), current_user: User = Depends(get_current_user)):
    """Create a new code session."""
    try:
        # Enforce that session belongs to current user
        if session_data.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not allowed to create session for another user")
        logger.info(f"Creating code session for user: {session_data.user_id}")
        
        # Create code session
        session = CodeSession(
            project_id=session_data.project_id,
            user_id=session_data.user_id,
            session_name=session_data.session_name,
            code_content=session_data.code_content,
            language=session_data.language
        )
        
        await session.save()
        logger.info(f"Code session created with ID: {session.id}")
        
        return JSONResponse(
            content={
                "message": "Code session created successfully",
                "session": {
                    "id": str(session.id),
                    "project_id": session.project_id,
                    "user_id": session.user_id,
                    "session_name": session.session_name,
                    "language": session.language,
                    "created_at": session.created_at.isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating code session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create code session: {str(e)}")

@router.get("/code-sessions/{user_id}")
async def get_user_code_sessions(user_id: str, current_user: User = Depends(get_current_user)):
    """Get all code sessions for a user."""
    try:
        logger.info(f"Getting code sessions for user: {user_id}")
        
        if user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view these sessions")
        sessions = await CodeSession.find(CodeSession.user_id == user_id).to_list()
        
        session_list = []
        for session in sessions:
            session_list.append({
                "id": str(session.id),
                "project_id": session.project_id,
                "session_name": session.session_name,
                "language": session.language,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            })
        
        return JSONResponse(content={"sessions": session_list})
        
    except Exception as e:
        logger.error(f"Error getting code sessions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get code sessions: {str(e)}")