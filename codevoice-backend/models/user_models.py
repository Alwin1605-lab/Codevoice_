"""
User-related database models for the Voice Controlled IDE using MongoDB and Beanie.
Includes User, UserVoiceSettings, and UserAPISettings models.
"""

from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AssistiveTechnologies(BaseModel):
    """Assistive technologies used by the user."""
    screen_reader: bool = False
    voice_control: bool = False
    switch_control: bool = False
    other: str = ""

class UserVoiceSettings(BaseModel):
    """Voice control settings and preferences for users."""
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)  # Speech rate (0.5-2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)  # Voice pitch
    voice_volume: float = Field(default=0.8, ge=0.0, le=1.0)  # Volume level
    preferred_voice: Optional[str] = None  # Voice engine preference
    voice_commands_enabled: bool = True
    auto_save_enabled: bool = True
    voice_feedback_enabled: bool = True
    wake_word: str = "hey code"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserAPISettings(BaseModel):
    """API keys and AI model preferences for users."""
    groq_api_key_encrypted: Optional[str] = None
    gemini_api_key_encrypted: Optional[str] = None
    openai_api_key_encrypted: Optional[str] = None
    
    preferred_ai_model: str = "llama-3.3-70b-versatile"
    max_tokens: str = "4000"  # String to handle 'unlimited'
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(Document):
    """
    Main user model for authentication and profile information.
    """
    username: str  # Will be indexed via Settings
    email: EmailStr  # Will be indexed via Settings
    password_hash: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    github_username: Optional[str] = None
    github_token_encrypted: Optional[str] = None  # Encrypted GitHub personal access token
    
    # Accessibility and disability support fields
    disability: Optional[str] = None
    can_type: bool = True
    preferred_input_method: Optional[str] = None
    typing_speed: Optional[str] = None
    additional_needs: Optional[str] = None
    programming_experience: Optional[str] = None
    preferred_languages: List[str] = []
    assistive_technologies: Optional[AssistiveTechnologies] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Status flags
    is_active: bool = True
    email_verified: bool = False
    preferred_language: str = "en"
    
    # Embedded settings
    voice_settings: Optional[UserVoiceSettings] = None
    api_settings: Optional[UserAPISettings] = None
    
    # Friends and social features
    friends: List[str] = []  # List of user IDs who are friends
    friend_requests_sent: List[str] = []  # Pending outgoing requests
    friend_requests_received: List[str] = []  # Pending incoming requests
    
    class Settings:
        name = "users"
        indexes = [
            [("username", 1)],  # Unique index for username
            [("email", 1)],     # Unique index for email  
            "created_at",
            "is_active",
            [("is_active", 1), ("created_at", -1)]  # Compound index for active users
        ]
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    
    async def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        await self.save()
    
    async def update_voice_settings(self, voice_settings: UserVoiceSettings):
        """Update voice settings."""
        voice_settings.updated_at = datetime.utcnow()
        self.voice_settings = voice_settings
        await self.save()
    
    async def update_api_settings(self, api_settings: UserAPISettings):
        """Update API settings."""
        api_settings.updated_at = datetime.utcnow()
        self.api_settings = api_settings
        await self.save()
    
    def has_voice_settings(self) -> bool:
        """Check if user has voice settings configured."""
        return self.voice_settings is not None
    
    def has_api_settings(self) -> bool:
        """Check if user has API settings configured."""
        return self.api_settings is not None
    
    def get_voice_speed(self) -> float:
        """Get voice speed setting or default."""
        if self.voice_settings:
            return self.voice_settings.voice_speed
        return 1.0
    
    def get_preferred_ai_model(self) -> str:
        """Get preferred AI model or default."""
        if self.api_settings:
            return self.api_settings.preferred_ai_model
        return "llama-3.3-70b-versatile"