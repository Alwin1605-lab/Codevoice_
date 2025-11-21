"""
MongoDB-based User API with comprehensive logging for the Voice Controlled IDE.
Handles user authentication, registration, and profile management using Beanie ODM.
"""

import logging
import hashlib
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, ValidationError

from models.user_models import User, UserVoiceSettings, UserAPISettings, AssistiveTechnologies

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/user_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed

def sanitize_user_data(user: User) -> Dict[str, Any]:
    """Remove sensitive fields from user data before returning."""
    user_dict = user.dict()
    user_dict.pop('password_hash', None)
    
    # Convert ObjectId to string for JSON serialization
    if 'id' in user_dict:
        user_dict['id'] = str(user_dict['id'])
    if '_id' in user_dict:
        user_dict['id'] = str(user_dict.pop('_id'))
    
    # Convert datetime objects to ISO format strings
    for key, value in user_dict.items():
        if isinstance(value, datetime):
            user_dict[key] = value.isoformat()
    
    return user_dict

class UserRegistration(BaseModel):
    """User registration model."""
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    """Profile update model."""
    full_name: Optional[str] = None
    disability: Optional[str] = None
    can_type: Optional[bool] = None
    preferred_input_method: Optional[str] = None
    typing_speed: Optional[str] = None
    additional_needs: Optional[str] = None
    programming_experience: Optional[str] = None
    preferred_languages: Optional[List[str]] = None
    assistive_technologies: Optional[Dict[str, Any]] = None
    github_username: Optional[str] = None
    preferred_language: Optional[str] = None

@router.post('/register')
async def register_user(registration: UserRegistration = Body(...)):
    """Register a new user."""
    try:
        logger.info(f"Registration attempt for email: {registration.email}")
        
        # Check if user already exists
        existing_user = await User.find_one(User.email == registration.email)
        if existing_user:
            logger.warning(f"Registration failed - user already exists: {registration.email}")
            raise HTTPException(status_code=400, detail="User already exists with this email")
        
        # Create new user
        user = User(
            username=registration.name.lower().replace(' ', '_'),
            email=registration.email,
            password_hash=hash_password(registration.password),
            full_name=registration.name,
            is_active=True,
            email_verified=False,
            preferred_language="en",
            can_type=True,
            preferred_languages=[],
            assistive_technologies=AssistiveTechnologies()
        )
        
        # Save user to MongoDB
        await user.insert()
        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
        
        # Return sanitized user data
        user_data = sanitize_user_data(user)
        return JSONResponse(
            content={"message": "User registered successfully", "user": user_data},
            status_code=201
        )
        
    except ValidationError as e:
        logger.error(f"Validation error during registration: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post('/login')
async def login_user(login: UserLogin = Body(...)):
    """Authenticate user login."""
    try:
        logger.info(f"Login attempt for email: {login.email}")
        
        # Find user by email
        user = await User.find_one(User.email == login.email)
        if not user:
            logger.warning(f"Login failed - user not found: {login.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login.password, user.password_hash):
            logger.warning(f"Login failed - invalid password for: {login.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed - user account inactive: {login.email}")
            raise HTTPException(status_code=403, detail="Account is inactive")
        
        # Update last login
        await user.update_last_login()
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
        
        # Return sanitized user data
        user_data = sanitize_user_data(user)
        return JSONResponse(
            content={"message": "Login successful", "user": user_data}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get('/list')
async def list_all_users():
    """List all users in the system (for friend discovery)."""
    try:
        logger.info("Listing all users")
        
        # Fetch all active users
        users = await User.find(User.is_active == True).to_list()
        
        # Sanitize and return user data
        users_data = [sanitize_user_data(user) for user in users]
        
        logger.info(f"Retrieved {len(users_data)} users")
        return JSONResponse(content={"users": users_data})
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get('/{user_id}')
async def get_user_profile(user_id: str):
    """Get user profile by ID."""
    try:
        logger.info(f"Profile request for user ID: {user_id}")
        
        # Find user by ID
        user = await User.get(user_id)
        if not user:
            logger.warning(f"Profile request failed - user not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Profile retrieved successfully for user: {user.email}")
        
        # Return sanitized user data
        user_data = sanitize_user_data(user)
        return JSONResponse(content={"user": user_data})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put('/{user_id}')
async def update_user_profile(user_id: str, profile: ProfileUpdate = Body(...)):
    """Update user profile."""
    try:
        logger.info(f"Profile update request for user ID: {user_id}")
        
        # Find user by ID
        user = await User.get(user_id)
        if not user:
            logger.warning(f"Profile update failed - user not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user fields
        update_data = profile.dict(exclude_none=True)
        updated_fields = []
        
        for field, value in update_data.items():
            if field == "assistive_technologies" and value:
                user.assistive_technologies = AssistiveTechnologies(**value)
                updated_fields.append(field)
            elif hasattr(user, field):
                setattr(user, field, value)
                updated_fields.append(field)
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        # Save changes
        await user.save()
        logger.info(f"Profile updated successfully for user {user.email}. Updated fields: {updated_fields}")
        
        # Return sanitized user data
        user_data = sanitize_user_data(user)
        return JSONResponse(
            content={"message": "Profile updated successfully", "user": user_data}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get('/{user_id}/voice-settings')
async def get_voice_settings(user_id: str):
    """Get user voice settings."""
    try:
        logger.info(f"Voice settings request for user ID: {user_id}")
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        voice_settings = user.voice_settings.dict() if user.voice_settings else None
        return JSONResponse(content={"voice_settings": voice_settings})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving voice settings for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put('/{user_id}/voice-settings')
async def update_voice_settings(user_id: str, settings: dict = Body(...)):
    """Update user voice settings."""
    try:
        logger.info(f"Voice settings update for user ID: {user_id}")
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        voice_settings = UserVoiceSettings(**settings)
        await user.update_voice_settings(voice_settings)
        
        logger.info(f"Voice settings updated for user: {user.email}")
        
        return JSONResponse(
            content={"message": "Voice settings updated successfully"}
        )
        
    except ValidationError as e:
        logger.error(f"Validation error updating voice settings: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating voice settings for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post('/{user_id}/friends/request')
async def send_friend_request(user_id: str, friend_request: dict = Body(...)):
    """Send a friend request to another user."""
    try:
        friend_id = friend_request.get('friend_id')
        if not friend_id:
            raise HTTPException(status_code=400, detail="friend_id is required")
        
        logger.info(f"Friend request: {user_id} -> {friend_id}")
        
        # Find both users
        user = await User.get(user_id)
        friend = await User.get(friend_id)
        
        if not user or not friend:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Initialize friend lists if not exists
        if not hasattr(user, 'friend_requests_sent'):
            user.friend_requests_sent = []
        if not hasattr(friend, 'friend_requests_received'):
            friend.friend_requests_received = []
        
        # Check if already friends or request exists
        if hasattr(user, 'friends') and friend_id in user.friends:
            raise HTTPException(status_code=400, detail="Already friends")
        if friend_id in user.friend_requests_sent:
            raise HTTPException(status_code=400, detail="Friend request already sent")
        
        # Add friend request
        user.friend_requests_sent.append(friend_id)
        friend.friend_requests_received.append(user_id)
        
        await user.save()
        await friend.save()
        
        logger.info(f"Friend request sent from {user.email} to {friend.email}")
        
        return JSONResponse(
            content={"message": "Friend request sent successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending friend request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post('/{user_id}/friends/accept')
async def accept_friend_request(user_id: str, friend_request: dict = Body(...)):
    """Accept a friend request."""
    try:
        friend_id = friend_request.get('friend_id')
        if not friend_id:
            raise HTTPException(status_code=400, detail="friend_id is required")
        
        logger.info(f"Accept friend request: {user_id} accepting {friend_id}")
        
        # Find both users
        user = await User.get(user_id)
        friend = await User.get(friend_id)
        
        if not user or not friend:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Initialize lists if not exists
        if not hasattr(user, 'friend_requests_received'):
            user.friend_requests_received = []
        if not hasattr(user, 'friends'):
            user.friends = []
        if not hasattr(friend, 'friend_requests_sent'):
            friend.friend_requests_sent = []
        if not hasattr(friend, 'friends'):
            friend.friends = []
        
        # Verify friend request exists
        if friend_id not in user.friend_requests_received:
            raise HTTPException(status_code=400, detail="No friend request from this user")
        
        # Add to friends lists
        if friend_id not in user.friends:
            user.friends.append(friend_id)
        if user_id not in friend.friends:
            friend.friends.append(user_id)
        
        # Remove from pending requests
        user.friend_requests_received.remove(friend_id)
        if user_id in friend.friend_requests_sent:
            friend.friend_requests_sent.remove(user_id)
        
        await user.save()
        await friend.save()
        
        logger.info(f"Friend request accepted: {user.email} and {friend.email} are now friends")
        
        return JSONResponse(
            content={"message": "Friend request accepted"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting friend request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get('/{user_id}/friends')
async def get_friends(user_id: str):
    """Get user's friends list."""
    try:
        logger.info(f"Getting friends for user: {user_id}")
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Initialize friends list if not exists
        if not hasattr(user, 'friends'):
            user.friends = []
        
        # Fetch friend user objects
        friends_data = []
        for friend_id in user.friends:
            friend = await User.get(friend_id)
            if friend:
                friends_data.append(sanitize_user_data(friend))
        
        logger.info(f"Retrieved {len(friends_data)} friends for user {user.email}")
        
        return JSONResponse(content={"friends": friends_data})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting friends for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")