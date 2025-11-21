"""
Models package initialization.
Imports all model modules to ensure they are registered with Beanie ODM.
"""

from .user_models import *
from .project_models import *
from .collaboration_models import *
from .analytics_models import *

__all__ = [
    # User models
    "User", "UserVoiceSettings", "UserAPISettings",
    
    # Project models  
    "Project", "ProjectFile", "CodeSession", "VoiceCommand",
    
    # Collaboration models
    "CollaborationSession", "SessionParticipant", "CollaborationInvite", "CollaborationEvent",
    
    # Analytics models
    "LearningProgress", "TranscriptionAnalytics", "Notification", "UsageAnalytics", 
    "APIRateLimit", "AudioFile", "ProjectBackup"
]