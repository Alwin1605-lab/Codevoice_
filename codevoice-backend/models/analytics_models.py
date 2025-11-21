"""
Analytics and system-related database models for the Voice Controlled IDE using MongoDB and Beanie.
Includes learning progress, notifications, usage analytics, and file storage models.
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """Types of notifications."""
    COLLABORATION_INVITE = "collaboration_invite"
    SYSTEM_UPDATE = "system_update"
    PROJECT_GENERATED = "project_generated"
    ERROR_ALERT = "error_alert"
    FEATURE_ANNOUNCEMENT = "feature_announcement"

class ActionType(str, Enum):
    """Types of user actions for analytics."""
    LOGIN = "login"
    LOGOUT = "logout"
    GENERATE_PROJECT = "generate_project"
    VOICE_COMMAND = "voice_command"
    TRANSCRIBE_AUDIO = "transcribe_audio"
    COLLABORATION_JOIN = "collaboration_join"
    API_CALL = "api_call"

class LearningProgress(Document):
    """User progress tracking for learning mode features."""
    user_id: str  # Reference to User ID
    
    # Learning information
    topic: str  # 'Python Basics', 'React Components', etc.
    level: str = "beginner"  # beginner, intermediate, advanced
    completion_percentage: float = 0.0
    current_lesson: Optional[str] = None
    exercises_completed: int = 0
    total_exercises: Optional[int] = None
    
    # Learning metrics
    time_spent_minutes: int = 0
    mistakes_count: int = 0
    hints_used: int = 0
    
    # Timestamps
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "learning_progress"
        indexes = [
            "user_id",
            "topic",
            "level",
            "last_accessed",
            [("user_id", 1), ("topic", 1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<LearningProgress(topic='{self.topic}', completion={self.completion_percentage}%)>"
    
    async def update_progress(self, completion_percentage: float, lesson: Optional[str] = None):
        """Update learning progress."""
        self.completion_percentage = completion_percentage
        if lesson:
            self.current_lesson = lesson
        self.last_accessed = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

class TranscriptionAnalytics(Document):
    """Analytics for voice transcription accuracy and performance."""
    user_id: str  # Reference to User ID
    
    # Audio information
    audio_duration_seconds: float
    word_count: int
    audio_format: Optional[str] = None
    
    # Quality metrics
    accuracy_score: Optional[float] = None  # 0.0 to 1.0
    confidence_score: Optional[float] = None
    transcription_model: str = "whisper-1"
    language_detected: Optional[str] = None
    processing_time_ms: int
    
    # Error tracking
    error_occurred: bool = False
    error_message: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "transcription_analytics"
        indexes = [
            "user_id",
            "created_at",
            "transcription_model",
            "accuracy_score",
            [("user_id", 1), ("created_at", -1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<TranscriptionAnalytics(accuracy={self.accuracy_score}, model='{self.transcription_model}')>"

class Notification(Document):
    """User notifications for collaboration invites, system updates, etc."""
    user_id: str  # Reference to User ID
    
    # Notification content
    notification_type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None  # Additional notification data
    action_url: Optional[str] = None
    
    # Status
    read: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "notification_type",
            "read",
            "created_at",
            "expires_at",
            [("user_id", 1), ("read", 1), ("created_at", -1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<Notification(type='{self.notification_type}', read={self.read})>"
    
    async def mark_as_read(self):
        """Mark notification as read."""
        self.read = True
        self.read_at = datetime.utcnow()
        await self.save()
    
    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

class UsageAnalytics(Document):
    """System usage analytics for tracking user behavior and feature usage."""
    user_id: str  # Reference to User ID
    session_id: Optional[str] = None
    
    # Action information
    action: ActionType
    page: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Request information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    
    # Performance metrics
    response_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "usage_analytics"
        indexes = [
            "user_id",
            "action",
            "session_id",
            "created_at",
            "success",
            [("user_id", 1), ("created_at", -1)],  # User timeline
            [("action", 1), ("created_at", -1)]     # Action analytics
        ]
    
    def __repr__(self):
        return f"<UsageAnalytics(action='{self.action}', page='{self.page}')>"
    
    @classmethod
    async def log_action(cls, user_id: str, action: ActionType, page: Optional[str] = None, 
                        metadata: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None):
        """Log a user action."""
        analytics = cls(
            user_id=user_id,
            action=action,
            page=page,
            metadata=metadata,
            session_id=session_id
        )
        await analytics.insert()
        return analytics

class APIRateLimit(Document):
    """API rate limiting tracking for preventing abuse."""
    user_id: str  # Reference to User ID
    
    # Rate limit information
    endpoint: str
    requests_count: int = 0
    window_start: datetime = Field(default_factory=datetime.utcnow)
    window_duration_minutes: int = 60
    limit_exceeded_count: int = 0
    
    # Rate limit settings
    max_requests_per_window: int = 100
    
    class Settings:
        name = "api_rate_limits"
        indexes = [
            "user_id",
            "endpoint",
            "window_start",
            [("user_id", 1), ("endpoint", 1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<APIRateLimit(endpoint='{self.endpoint}', count={self.requests_count})>"
    
    def is_limit_exceeded(self) -> bool:
        """Check if rate limit is exceeded."""
        # Check if current window is still valid
        window_end = self.window_start.replace(minute=self.window_start.minute + self.window_duration_minutes)
        if datetime.utcnow() > window_end:
            # Reset window
            self.window_start = datetime.utcnow()
            self.requests_count = 0
        
        return self.requests_count >= self.max_requests_per_window
    
    async def increment_request(self):
        """Increment request count."""
        if not self.is_limit_exceeded():
            self.requests_count += 1
            await self.save()
        else:
            self.limit_exceeded_count += 1
            await self.save()
            raise ValueError("Rate limit exceeded")

class AudioFile(Document):
    """Storage tracking for uploaded audio files."""
    user_id: str  # Reference to User ID
    
    # File information
    file_name: str
    file_path: str
    file_size_bytes: int
    duration_seconds: float
    format: str  # wav, mp3, etc.
    transcription_id: Optional[str] = None
    
    # Processing status
    processed: bool = False
    processing_error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Auto-cleanup old files
    
    class Settings:
        name = "audio_files"
        indexes = [
            "user_id",
            "file_name",
            "created_at",
            "expires_at",
            "processed",
            [("user_id", 1), ("created_at", -1)]  # User file timeline
        ]
    
    def __repr__(self):
        return f"<AudioFile(file_name='{self.file_name}', format='{self.format}')>"
    
    def is_expired(self) -> bool:
        """Check if file has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

class ProjectBackup(Document):
    """Backup snapshots of projects for recovery and versioning."""
    project_id: str  # Reference to Project ID
    user_id: str  # Reference to User ID (for ownership)
    
    # Backup information
    backup_data: Dict[str, Any]  # Complete project snapshot
    backup_size_bytes: int
    backup_type: str = "auto"  # auto, manual, pre_generation
    version: int = 1
    
    # Backup metadata
    description: Optional[str] = None
    tags: List[str] = []
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "project_backups"
        indexes = [
            "project_id",
            "user_id",
            "backup_type",
            "created_at",
            "version",
            [("project_id", 1), ("version", -1)]  # Project version history
        ]
    
    def __repr__(self):
        return f"<ProjectBackup(type='{self.backup_type}', size={self.backup_size_bytes} bytes)>"
    
    @classmethod
    async def create_backup(cls, project_id: str, user_id: str, backup_data: Dict[str, Any], 
                           backup_type: str = "auto", description: Optional[str] = None):
        """Create a new project backup."""
        # Get the next version number
        last_backup = await cls.find(
            cls.project_id == project_id
        ).sort(-cls.version).limit(1).first_or_none()
        
        version = (last_backup.version + 1) if last_backup else 1
        
        backup = cls(
            project_id=project_id,
            user_id=user_id,
            backup_data=backup_data,
            backup_size_bytes=len(str(backup_data)),
            backup_type=backup_type,
            version=version,
            description=description
        )
        await backup.insert()
        return backup