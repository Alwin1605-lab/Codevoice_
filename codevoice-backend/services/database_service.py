"""
Database service layer for Voice Controlled IDE using MongoDB.
Provides CRUD operations and business logic for all entities.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from models.user_models import User, UserVoiceSettings, UserAPISettings
from models.project_models import Project, ProjectFile, CodeSession, VoiceCommand
import bcrypt
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service layer for User operations."""
    
    @staticmethod
    async def create_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> Optional[User]:
        """Create a new user with hashed password."""
        try:
            # Check if user already exists
            existing_user = await User.find_one({"$or": [{"username": username}, {"email": email}]})
            if existing_user:
                return None
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name
            )
            
            await user.insert()
            logger.info(f"Created new user: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return None
    
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        try:
            # Find user by username or email
            user = await User.find_one({"$or": [{"username": username}, {"email": username}]})
            if not user or not user.is_active:
                return None
            
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                await user.update_last_login()
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            return None
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            return await User.get(ObjectId(user_id))
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        try:
            return await User.find_one({"username": username})
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            return None
    
    @staticmethod
    async def update_user_profile(user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile information."""
        try:
            user = await User.get(ObjectId(user_id))
            if not user:
                return False
            
            # Update allowed fields
            allowed_fields = ['full_name', 'profile_picture_url', 'github_username', 'preferred_language']
            for field in allowed_fields:
                if field in updates:
                    setattr(user, field, updates[field])
            
            user.updated_at = datetime.utcnow()
            await user.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user profile {user_id}: {e}")
            return False

class ProjectService:
    """Service layer for Project operations."""
    
    @staticmethod
    async def create_project(user_id: str, name: str, description: str, natural_language_prompt: str, 
                           framework: Optional[str] = None, features: Optional[List[str]] = None) -> Optional[Project]:
        """Create a new AI-generated project."""
        try:
            project = Project(
                user_id=ObjectId(user_id),
                name=name,
                description=description,
                natural_language_prompt=natural_language_prompt,
                framework=framework,
                features=features or []
            )
            
            await project.insert()
            logger.info(f"Created new project: {name} for user {user_id}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            return None
    
    @staticmethod
    async def get_user_projects(user_id: str, limit: int = 50, skip: int = 0) -> List[Project]:
        """Get all projects for a user."""
        try:
            return await Project.find({"user_id": ObjectId(user_id)}).sort([("created_at", -1)]).limit(limit).skip(skip).to_list()
        except Exception as e:
            logger.error(f"Failed to get projects for user {user_id}: {e}")
            return []
    
    @staticmethod
    async def get_project_by_id(project_id: str) -> Optional[Project]:
        """Get project by ID."""
        try:
            return await Project.get(ObjectId(project_id))
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None
    
    @staticmethod
    async def update_project_status(project_id: str, status: str, ai_model_used: Optional[str] = None) -> bool:
        """Update project generation status."""
        try:
            project = await Project.get(ObjectId(project_id))
            if not project:
                return False
            
            await project.update_status(status)
            if ai_model_used:
                project.ai_model_used = ai_model_used
                await project.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project status {project_id}: {e}")
            return False
    
    @staticmethod
    async def add_project_files(project_id: str, files_data: List[Dict[str, Any]]) -> bool:
        """Add files to a project."""
        try:
            project = await Project.get(ObjectId(project_id))
            if not project:
                return False
            
            for file_data in files_data:
                project_file = ProjectFile(**file_data)
                await project.add_file(project_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add files to project {project_id}: {e}")
            return False

class VoiceCommandService:
    """Service layer for VoiceCommand operations."""
    
    @staticmethod
    async def log_voice_command(user_id: str, command_text: str, command_type: Optional[str] = None,
                               audio_file_path: Optional[str] = None) -> Optional[VoiceCommand]:
        """Log a voice command."""
        try:
            voice_command = VoiceCommand(
                user_id=ObjectId(user_id),
                command_text=command_text,
                command_type=command_type,
                audio_file_path=audio_file_path
            )
            
            await voice_command.insert()
            return voice_command
            
        except Exception as e:
            logger.error(f"Failed to log voice command for user {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_user_voice_commands(user_id: str, limit: int = 100, skip: int = 0) -> List[VoiceCommand]:
        """Get voice commands for a user."""
        try:
            return await VoiceCommand.find({"user_id": ObjectId(user_id)}).sort([("created_at", -1)]).limit(limit).skip(skip).to_list()
        except Exception as e:
            logger.error(f"Failed to get voice commands for user {user_id}: {e}")
            return []
    
    @staticmethod
    async def get_command_stats(user_id: str) -> Dict[str, Any]:
        """Get voice command statistics for a user."""
        try:
            return await VoiceCommand.get_user_command_stats(ObjectId(user_id))
        except Exception as e:
            logger.error(f"Failed to get command stats for user {user_id}: {e}")
            return {}

class CodeSessionService:
    """Service layer for CodeSession operations."""
    
    @staticmethod
    async def create_code_session(user_id: str, problem_description: str, programming_language: str,
                                session_name: Optional[str] = None) -> Optional[CodeSession]:
        """Create a new code generation session."""
        try:
            session = CodeSession(
                user_id=ObjectId(user_id),
                session_name=session_name,
                problem_description=problem_description,
                programming_language=programming_language
            )
            
            await session.insert()
            return session
            
        except Exception as e:
            logger.error(f"Failed to create code session for user {user_id}: {e}")
            return None
    
    @staticmethod
    async def update_session_code(session_id: str, generated_code: str, ai_model_used: str,
                                prompt_used: str) -> bool:
        """Update session with generated code."""
        try:
            session = await CodeSession.get(ObjectId(session_id))
            if not session:
                return False
            
            session.generated_code = generated_code
            session.ai_model_used = ai_model_used
            session.prompt_used = prompt_used
            session.updated_at = datetime.utcnow()
            
            await session.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update code session {session_id}: {e}")
            return False
    
    @staticmethod
    async def get_user_sessions(user_id: str, limit: int = 50, skip: int = 0) -> List[CodeSession]:
        """Get code sessions for a user."""
        try:
            return await CodeSession.find({"user_id": ObjectId(user_id)}).sort([("created_at", -1)]).limit(limit).skip(skip).to_list()
        except Exception as e:
            logger.error(f"Failed to get code sessions for user {user_id}: {e}")
            return []

# Convenience functions for common operations
async def get_user_dashboard_data(user_id: str) -> Dict[str, Any]:
    """Get comprehensive dashboard data for a user."""
    try:
        user = await UserService.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Get recent projects
        recent_projects = await ProjectService.get_user_projects(user_id, limit=5)
        
        # Get recent voice commands
        recent_commands = await VoiceCommandService.get_user_voice_commands(user_id, limit=10)
        
        # Get recent code sessions
        recent_sessions = await CodeSessionService.get_user_sessions(user_id, limit=5)
        
        # Get command stats
        command_stats = await VoiceCommandService.get_command_stats(user_id)
        
        return {
            "user": user,
            "recent_projects": recent_projects,
            "recent_commands": recent_commands,
            "recent_sessions": recent_sessions,
            "command_stats": command_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data for user {user_id}: {e}")
        return {}