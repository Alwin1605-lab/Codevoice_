"""
Collaboration-related database models for the Voice Controlled IDE using MongoDB and Beanie.
Includes CollaborationSession, SessionParticipant, CollaborationInvite, and CollaborationEvent models.
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ParticipantRole(str, Enum):
    """Roles for collaboration participants."""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"

class InviteStatus(str, Enum):
    """Status of collaboration invites."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class EventType(str, Enum):
    """Types of collaboration events."""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CODE_CHANGED = "code_changed"
    VOICE_COMMAND = "voice_command"
    CHAT_MESSAGE = "chat_message"
    FILE_CREATED = "file_created"
    FILE_DELETED = "file_deleted"

class SessionParticipant(BaseModel):
    """Participant in a collaboration session."""
    user_id: str
    username: str
    role: ParticipantRole = ParticipantRole.EDITOR
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    cursor_position: Optional[Dict[str, Any]] = None  # Current cursor position in editor

class CollaborationSession(Document):
    """Real-time collaboration sessions where multiple users can work together."""
    host_user_id: str  # Reference to User ID
    project_id: Optional[str] = None  # Reference to Project ID
    
    # Session information
    name: str
    description: Optional[str] = None
    session_code: str  # Unique join code for others
    
    # Session settings
    is_active: bool = True
    max_participants: int = 10
    
    # Participants (embedded)
    participants: List[SessionParticipant] = []
    
    # Session state
    current_file: Optional[str] = None
    shared_code: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "collaboration_sessions"
        indexes = [
            "host_user_id",
            "session_code",
            "is_active",
            "created_at",
            [("host_user_id", 1), ("is_active", 1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<CollaborationSession(name='{self.name}', active={self.is_active})>"
    
    async def add_participant(self, user_id: str, username: str, role: ParticipantRole = ParticipantRole.EDITOR):
        """Add a participant to the session."""
        if len(self.participants) >= self.max_participants:
            raise ValueError("Session is at maximum capacity")
        
        # Check if user is already a participant
        for participant in self.participants:
            if participant.user_id == user_id:
                participant.is_active = True
                participant.last_activity = datetime.utcnow()
                await self.save()
                return
        
        # Add new participant
        new_participant = SessionParticipant(
            user_id=user_id,
            username=username,
            role=role
        )
        self.participants.append(new_participant)
        self.last_activity = datetime.utcnow()
        await self.save()
    
    async def remove_participant(self, user_id: str):
        """Remove a participant from the session."""
        self.participants = [p for p in self.participants if p.user_id != user_id]
        self.last_activity = datetime.utcnow()
        await self.save()
    
    async def end_session(self):
        """End the collaboration session."""
        self.is_active = False
        self.ended_at = datetime.utcnow()
        await self.save()
    
    def get_active_participants(self) -> List[SessionParticipant]:
        """Get list of active participants."""
        return [p for p in self.participants if p.is_active]
    
    def get_participant_count(self) -> int:
        """Get count of active participants."""
        return len(self.get_active_participants())

class CollaborationInvite(Document):
    """Invitations to join collaboration sessions."""
    session_id: str  # Reference to CollaborationSession
    inviter_user_id: str  # User who sent the invite
    invitee_email: str  # Email of invited user
    invitee_user_id: Optional[str] = None  # User ID if they have an account
    
    # Invite information
    message: Optional[str] = None
    role: ParticipantRole = ParticipantRole.EDITOR
    status: InviteStatus = InviteStatus.PENDING
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # When the invite expires
    responded_at: Optional[datetime] = None
    
    class Settings:
        name = "collaboration_invites"
        indexes = [
            "session_id",
            "invitee_email",
            "status",
            "expires_at",
            [("session_id", 1), ("status", 1)]  # Compound index
        ]
    
    def __repr__(self):
        return f"<CollaborationInvite(email='{self.invitee_email}', status='{self.status}')>"
    
    async def accept_invite(self, user_id: str):
        """Accept the collaboration invite."""
        self.status = InviteStatus.ACCEPTED
        self.invitee_user_id = user_id
        self.responded_at = datetime.utcnow()
        await self.save()
    
    async def decline_invite(self):
        """Decline the collaboration invite."""
        self.status = InviteStatus.DECLINED
        self.responded_at = datetime.utcnow()
        await self.save()
    
    def is_expired(self) -> bool:
        """Check if the invite has expired."""
        return datetime.utcnow() > self.expires_at

class CollaborationEvent(Document):
    """Events that occur during collaboration sessions."""
    session_id: str  # Reference to CollaborationSession
    user_id: str  # User who triggered the event
    
    # Event information
    event_type: EventType
    description: str
    data: Optional[Dict[str, Any]] = None  # Additional event data
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "collaboration_events"
        indexes = [
            "session_id",
            "user_id",
            "event_type",
            "created_at",
            [("session_id", 1), ("created_at", -1)]  # Compound index for session timeline
        ]
    
    def __repr__(self):
        return f"<CollaborationEvent(type='{self.event_type}', session='{self.session_id}')>"
    
    @classmethod
    async def log_event(cls, session_id: str, user_id: str, event_type: EventType, 
                       description: str, data: Optional[Dict[str, Any]] = None):
        """Log a collaboration event."""
        event = cls(
            session_id=session_id,
            user_id=user_id,
            event_type=event_type,
            description=description,
            data=data
        )
        await event.insert()
        return event
    
    @classmethod
    async def get_session_timeline(cls, session_id: str, limit: int = 100):
        """Get timeline of events for a session."""
        return await cls.find(
            cls.session_id == session_id
        ).sort(-cls.created_at).limit(limit).to_list()