"""
Database-backed Collaboration API that actually saves collaboration data to MongoDB.
This ensures collaboration sessions, events, and invites are persisted properly.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from models.collaboration_models import CollaborationSession, CollaborationEvent, CollaborationInvite, ParticipantRole
from models.user_models import User
from auth_dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])

class SessionCreate(BaseModel):
    """Model for creating a collaboration session."""
    name: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    max_participants: int = 10
    is_public: bool = False
    creator_id: str

class InviteCreate(BaseModel):
    """Model for creating a collaboration invite."""
    session_id: str
    invitee_email: EmailStr
    inviter_id: str
    role: ParticipantRole = ParticipantRole.EDITOR
    message: Optional[str] = None

class EventCreate(BaseModel):
    """Model for creating a collaboration event."""
    session_id: str
    user_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: Optional[datetime] = None

@router.post("/sessions")
async def create_session(session_data: SessionCreate = Body(...), current_user: User = Depends(get_current_user)):
    """Create a new collaboration session."""
    try:
        logger.info(f"Creating collaboration session: {session_data.name}")
        logger.info(f"Session data: {session_data.dict()}")
        logger.info(f"Current user: {current_user.id if current_user else 'None'}")
        
        # AuthN/AuthZ: ensure creator is current user
        if session_data.creator_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not allowed to create session for another user")

        # Generate unique session code
        import uuid
        session_code = str(uuid.uuid4())[:8].upper()

        # Create collaboration session
        session = CollaborationSession(
            name=session_data.name,
            description=session_data.description,
            project_id=session_data.project_id,
            host_user_id=session_data.creator_id,  # Use host_user_id instead of creator_id
            session_code=session_code,  # Add required session_code
            max_participants=session_data.max_participants
        )
        
        # Add creator as first participant
        await session.add_participant(
            user_id=session_data.creator_id,
            username=current_user.username or current_user.email.split('@')[0],
            role=ParticipantRole.ADMIN
        )
        
        await session.save()
        logger.info(f"Collaboration session created with ID: {session.id}, code: {session_code}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Collaboration session created successfully",
                "session": {
                    "id": str(session.id),
                    "name": session.name,
                    "description": session.description,
                    "project_id": session.project_id,
                    "host_user_id": session.host_user_id,
                    "session_code": session.session_code,
                    "max_participants": session.max_participants,
                    "current_participants": len(session.participants),
                    "is_active": session.is_active,
                    "created_at": session.created_at.isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating collaboration session: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions")
async def list_sessions(user_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """List collaboration sessions."""
    try:
        logger.info("Listing collaboration sessions")
        
        # Build query
        query = {}
        if user_id:
            query["participants.user_id"] = user_id
        
        sessions = await CollaborationSession.find(query).to_list()
        
        session_list = []
        for session in sessions:
            session_list.append({
                "id": str(session.id),
                "name": session.name,
                "description": session.description,
                "project_id": session.project_id,
                "host_user_id": session.host_user_id,
                "session_code": session.session_code,
                "max_participants": session.max_participants,
                "current_participants": len(session.participants),
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            })
        
        logger.info(f"Found {len(session_list)} collaboration sessions")
        return JSONResponse(content={"sessions": session_list})
        
    except Exception as e:
        logger.error(f"Error listing collaboration sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific collaboration session."""
    try:
        logger.info(f"Getting collaboration session: {session_id}")
        
        session = await CollaborationSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Only allow viewing if participant or host
        is_participant = any(p.user_id == str(current_user.id) for p in session.participants)
        if not is_participant and session.host_user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this session")
        
        session_data = {
            "id": str(session.id),
            "name": session.name,
            "description": session.description,
            "project_id": session.project_id,
            "host_user_id": session.host_user_id,
            "session_code": session.session_code,
            "max_participants": session.max_participants,
            "is_active": session.is_active,
            "participants": [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "role": p.role.value,
                    "joined_at": p.joined_at.isoformat()
                }
                for p in session.participants
            ],
            "created_at": session.created_at.isoformat(),
            "updated_at": session.last_activity.isoformat()
        }
        
        return JSONResponse(content={"session": session_data})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.post("/sessions/{session_id}/join")
async def join_session(session_id: str, user_data: dict = Body(...), current_user: User = Depends(get_current_user)):
    """Join a collaboration session."""
    try:
        user_id = user_data.get("user_id")
        username = user_data.get("username", f"user_{user_id}")
        if user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not allowed to join as another user")
        
        logger.info(f"User {user_id} joining session {session_id}")
        
        session = await CollaborationSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add participant
        await session.add_participant(user_id, username)
        await session.save()
        
        logger.info(f"User {user_id} joined session {session_id}")
        return JSONResponse(content={"message": "Successfully joined session"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")

@router.post("/sessions/{session_id}/leave")
async def leave_session(session_id: str, user_data: dict = Body(...), current_user: User = Depends(get_current_user)):
    """Leave a collaboration session."""
    try:
        user_id = user_data.get("user_id")
        if user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not allowed to leave as another user")
        
        logger.info(f"User {user_id} leaving session {session_id}")
        
        session = await CollaborationSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove participant
        await session.remove_participant(user_id)
        await session.save()
        
        logger.info(f"User {user_id} left session {session_id}")
        return JSONResponse(content={"message": "Successfully left session"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to leave session: {str(e)}")

@router.post("/invites")
async def create_invite(invite_data: InviteCreate = Body(...), current_user: User = Depends(get_current_user)):
    """Create a collaboration invite."""
    try:
        logger.info(f"Creating invite for session {invite_data.session_id}")
        
        # Check if session exists
        session = await CollaborationSession.get(invite_data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.creator_id != str(current_user.id) and invite_data.inviter_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to invite for this session")
        
        # Create invite
        invite = CollaborationInvite(
            session_id=invite_data.session_id,
            invitee_email=invite_data.invitee_email,
            inviter_id=invite_data.inviter_id,
            role=invite_data.role,
            message=invite_data.message
        )
        
        await invite.save()
        logger.info(f"Invite created with ID: {invite.id}")
        
        return JSONResponse(
            content={
                "message": "Invite created successfully",
                "invite": {
                    "id": str(invite.id),
                    "session_id": invite.session_id,
                    "invitee_email": invite.invitee_email,
                    "role": invite.role.value,
                    "status": invite.status.value,
                    "created_at": invite.created_at.isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating invite: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create invite: {str(e)}")

@router.get("/invites/{user_email}")
async def get_user_invites(user_email: str, current_user: User = Depends(get_current_user)):
    """Get all invites for a user email."""
    try:
        logger.info(f"Getting invites for user: {user_email}")
        
        if current_user.email != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to view invites for this user")
        invites = await CollaborationInvite.find(
            CollaborationInvite.invitee_email == user_email
        ).to_list()
        
        invite_list = []
        for invite in invites:
            invite_list.append({
                "id": str(invite.id),
                "session_id": invite.session_id,
                "inviter_id": invite.inviter_id,
                "role": invite.role.value,
                "status": invite.status.value,
                "message": invite.message,
                "created_at": invite.created_at.isoformat()
            })
        
        return JSONResponse(content={"invites": invite_list})
        
    except Exception as e:
        logger.error(f"Error getting invites for {user_email}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get invites: {str(e)}")

@router.post("/invites/{invite_id}/accept")
async def accept_invite(invite_id: str, current_user: User = Depends(get_current_user)):
    """Accept a collaboration invite."""
    try:
        logger.info(f"Accepting invite: {invite_id}")
        
        invite = await CollaborationInvite.get(invite_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")
        if invite.invitee_email != current_user.email:
            raise HTTPException(status_code=403, detail="Not authorized to accept this invite")
        
        # Accept the invite
        await invite.accept()
        await invite.save()
        
        logger.info(f"Invite {invite_id} accepted")
        return JSONResponse(content={"message": "Invite accepted successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invite {invite_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to accept invite: {str(e)}")

@router.post("/events")
async def create_event(event_data: EventCreate = Body(...)):
    """Create a collaboration event."""
    try:
        logger.info(f"Creating event for session {event_data.session_id}")
        
        # Create event
        event = CollaborationEvent(
            session_id=event_data.session_id,
            user_id=event_data.user_id,
            event_type=event_data.event_type,
            event_data=event_data.event_data,
            timestamp=event_data.timestamp or datetime.utcnow()
        )
        
        await event.save()
        logger.info(f"Event created with ID: {event.id}")
        
        return JSONResponse(
            content={
                "message": "Event created successfully",
                "event": {
                    "id": str(event.id),
                    "session_id": event.session_id,
                    "user_id": event.user_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/sessions/{session_id}/events")
async def get_session_events(session_id: str, limit: int = 50):
    """Get events for a collaboration session."""
    try:
        logger.info(f"Getting events for session {session_id}")
        
        events = await CollaborationEvent.find(
            CollaborationEvent.session_id == session_id
        ).sort(-CollaborationEvent.timestamp).limit(limit).to_list()
        
        event_list = []
        for event in events:
            event_list.append({
                "id": str(event.id),
                "session_id": event.session_id,
                "user_id": event.user_id,
                "event_type": event.event_type,
                "event_data": event.event_data,
                "timestamp": event.timestamp.isoformat()
            })
        
        return JSONResponse(content={"events": event_list})
        
    except Exception as e:
        logger.error(f"Error getting events for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")