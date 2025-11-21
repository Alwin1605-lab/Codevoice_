"""
Project-related database models for the Voice Controlled IDE using MongoDB and Beanie.
Includes Project, ProjectFile, CodeSession, and VoiceCommand models.
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie.odm.operators.find.logical import Or

class ProjectFile(BaseModel):
    """Individual files within AI-generated projects."""
    file_path: str
    file_name: str
    content: Optional[str] = None
    file_type: Optional[str] = None  # js, py, html, css, etc.
    language: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Project(Document):
    """AI-generated projects created by users."""
    user_id: str  # Reference to User ID
    
    # Project information
    name: str
    description: Optional[str] = None
    natural_language_prompt: Optional[str] = ""  # Original user description
    project_type: Optional[str] = None  # web_app, api, cli, etc.
    framework: Optional[str] = None  # React, Vue, Node.js, Python, etc.
    features: Optional[List[str]] = None  # Selected features as list
    
    # GitHub integration
    github_repo_url: Optional[str] = None
    github_repo_name: Optional[str] = None
    
    # Generation metadata
    ai_generated: Optional[bool] = False
    ai_model_used: Optional[str] = None
    generation_status: str = "generating"  # generating, completed, failed
    gemini_metadata: Optional[Dict[str, Any]] = None  # Full Gemini response
    project_structure: Optional[Dict[str, Any]] = None  # Generated file structure
    recommended_dependencies: Optional[Dict[str, Any]] = None  # Dependencies from Gemini
    environment_variables: Optional[Dict[str, Any]] = None  # Required env vars
    scripts: Optional[Dict[str, Any]] = None  # Build/run scripts
    setup_instructions: Optional[List[str]] = None  # Setup steps
    
    # Status and visibility
    is_public: bool = False
    
    # Files (embedded)
    files: List[ProjectFile] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "projects"
        indexes = [
            "user_id",
            "created_at",
            "generation_status",
            [("user_id", 1), ("created_at", -1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<Project(name='{self.name}', framework='{self.framework}', status='{self.generation_status}')>"
    
    async def add_file(self, file_data: ProjectFile):
        """Add a file to the project."""
        self.files.append(file_data)
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def update_status(self, status: str):
        """Update generation status."""
        self.generation_status = status
        self.updated_at = datetime.utcnow()
        await self.save()
    
    def get_file_count(self) -> int:
        """Get total number of files in project."""
        return len(self.files)
    
    def get_total_size(self) -> int:
        """Get total size of all files in bytes."""
        return sum(f.size_bytes or 0 for f in self.files)

class CodeSession(Document):
    """Individual code generation sessions for tracking user interactions."""
    user_id: str  # Reference to User ID
    
    # Session information
    session_name: Optional[str] = None
    problem_description: Optional[str] = None
    programming_language: Optional[str] = None
    generated_code: Optional[str] = None
    
    # AI metadata
    ai_model_used: Optional[str] = None
    prompt_used: Optional[str] = None
    
    # Execution results
    execution_result: Optional[str] = None
    compilation_status: Optional[str] = None  # success, failed, not_attempted
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "code_sessions"
        indexes = [
            "user_id",
            "created_at",
            "programming_language",
            "compilation_status"
        ]
    
    def __repr__(self):
        return f"<CodeSession(language='{self.programming_language}', status='{self.compilation_status}')>"
    
    async def update_execution_result(self, result: str, status: str):
        """Update execution results."""
        self.execution_result = result
        self.compilation_status = status
        self.updated_at = datetime.utcnow()
        await self.save()

class VoiceCommand(Document):
    """History of voice commands issued by users."""
    user_id: str  # Reference to User ID
    session_id: Optional[str] = None  # Optional session grouping
    
    # Command information
    command_text: str
    command_type: Optional[str] = None  # 'generate_code', 'create_project', 'transcribe', etc.
    audio_file_path: Optional[str] = None
    
    # Processing metadata
    transcription_accuracy: Optional[str] = None  # String to handle percentage values
    processing_time_ms: Optional[int] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "voice_commands"
        indexes = [
            "user_id",
            "created_at",
            "command_type",
            "success",
            [("user_id", 1), ("created_at", -1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<VoiceCommand(command_type='{self.command_type}', success={self.success})>"
    
    async def mark_as_processed(self, success: bool, error_message: Optional[str] = None):
        """Mark command as processed with result."""
        self.success = success
        if error_message:
            self.error_message = error_message
        await self.save()
    
    @classmethod
    async def get_user_command_stats(cls, user_id: str) -> Dict[str, Any]:
        """Get command statistics for a user."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$command_type",
                "count": {"$sum": 1},
                "success_count": {
                    "$sum": {"$cond": [{"$eq": ["$success", True]}, 1, 0]}
                }
            }}
        ]
        
        result = await cls.aggregate(pipeline).to_list()
        
        stats = {}
        for item in result:
            command_type = item["_id"] or "unknown"
            stats[command_type] = {
                "total": item["count"],
                "successful": item["success_count"],
                "success_rate": item["success_count"] / item["count"] if item["count"] > 0 else 0
            }
        
        return stats