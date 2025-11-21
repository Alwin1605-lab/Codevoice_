"""
Database-backed Voice Commands API that actually saves voice command data to MongoDB.
This ensures voice commands, usage analytics, and user interactions are persisted.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.project_models import VoiceCommand
from models.analytics_models import UsageAnalytics, TranscriptionAnalytics, ActionType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice-commands", tags=["voice-commands"])

class VoiceCommandCreate(BaseModel):
    """Model for creating a voice command record."""
    user_id: str
    command_text: str
    command_type: str
    language: Optional[str] = "en"
    confidence_score: Optional[float] = None
    execution_successful: bool = True
    response_text: Optional[str] = None
    execution_time_ms: Optional[int] = None

class UsageAnalyticsCreate(BaseModel):
    """Model for creating usage analytics."""
    user_id: str
    feature_used: str
    session_duration_seconds: Optional[int] = None
    actions_performed: Optional[int] = None
    errors_encountered: Optional[int] = None
    success_rate: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

class TranscriptionAnalyticsCreate(BaseModel):
    """Model for creating transcription analytics."""
    user_id: str
    audio_duration_seconds: float
    transcription_text: str
    confidence_score: float
    language_detected: Optional[str] = "en"
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = "whisper"

@router.post("/commands")
async def save_voice_command(command_data: VoiceCommandCreate = Body(...)):
    """Save a voice command to the database."""
    try:
        logger.info(f"Saving voice command for user {command_data.user_id}: {command_data.command_text}")
        
        # Create voice command record
        command = VoiceCommand(
            user_id=command_data.user_id,
            command_text=command_data.command_text,
            command_type=command_data.command_type,
            success=command_data.execution_successful,
            processing_time_ms=command_data.execution_time_ms
        )
        
        await command.save()
        logger.info(f"Voice command saved with ID: {command.id}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Voice command saved successfully",
                "command": {
                    "id": str(command.id),
                    "user_id": command.user_id,
                    "command_text": command.command_text,
                    "command_type": command.command_type,
                    "success": command.success,
                    "created_at": command.created_at.isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error saving voice command: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save voice command: {str(e)}")

@router.get("/commands/{user_id}")
async def get_user_commands(user_id: str, limit: int = 50):
    """Get voice commands for a specific user."""
    try:
        logger.info(f"Getting voice commands for user: {user_id}")
        
        commands = await VoiceCommand.find(
            VoiceCommand.user_id == user_id
        ).sort(-VoiceCommand.timestamp).limit(limit).to_list()
        
        command_list = []
        for command in commands:
            command_list.append({
                "id": str(command.id),
                "command_text": command.command_text,
                "command_type": command.command_type,
                "language": command.language,
                "confidence_score": command.confidence_score,
                "execution_successful": command.execution_successful,
                "response_text": command.response_text,
                "execution_time_ms": command.execution_time_ms,
                "timestamp": command.timestamp.isoformat()
            })
        
        logger.info(f"Found {len(command_list)} voice commands for user {user_id}")
        return JSONResponse(content={"commands": command_list})
        
    except Exception as e:
        logger.error(f"Error getting voice commands for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice commands: {str(e)}")

@router.get("/commands")
async def get_all_commands(limit: int = 100):
    """Get all voice commands (for admin/analytics)."""
    try:
        logger.info("Getting all voice commands")
        
        commands = await VoiceCommand.find().sort(-VoiceCommand.timestamp).limit(limit).to_list()
        
        command_list = []
        for command in commands:
            command_list.append({
                "id": str(command.id),
                "user_id": command.user_id,
                "command_text": command.command_text,
                "command_type": command.command_type,
                "execution_successful": command.execution_successful,
                "timestamp": command.timestamp.isoformat()
            })
        
        return JSONResponse(content={"commands": command_list})
        
    except Exception as e:
        logger.error(f"Error getting all voice commands: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice commands: {str(e)}")

@router.post("/usage-analytics")
async def save_usage_analytics(analytics_data: UsageAnalyticsCreate = Body(...)):
    """Save usage analytics to the database."""
    try:
        logger.info(f"Saving usage analytics for user {analytics_data.user_id}: {analytics_data.feature_used}")
        
        # Map feature_used to action type
        action_mapping = {
            "project_creation": ActionType.GENERATE_PROJECT,
            "voice_command": ActionType.VOICE_COMMAND,
            "transcription": ActionType.TRANSCRIBE_AUDIO,
            "collaboration": ActionType.COLLABORATION_JOIN,
            "api_call": ActionType.API_CALL
        }
        
        action = action_mapping.get(analytics_data.feature_used, ActionType.API_CALL)
        
        # Create usage analytics record
        analytics = UsageAnalytics(
            user_id=analytics_data.user_id,
            action=action,
            metadata={
                "feature_used": analytics_data.feature_used,
                "session_duration_seconds": analytics_data.session_duration_seconds,
                "actions_performed": analytics_data.actions_performed,
                "errors_encountered": analytics_data.errors_encountered,
                "success_rate": analytics_data.success_rate,
                **(analytics_data.additional_data or {})
            }
        )
        
        await analytics.save()
        logger.info(f"Usage analytics saved with ID: {analytics.id}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Usage analytics saved successfully",
                "analytics": {
                    "id": str(analytics.id),
                    "user_id": analytics.user_id,
                    "action": analytics.action,
                    "metadata": analytics.metadata,
                    "created_at": analytics.created_at.isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error saving usage analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save usage analytics: {str(e)}")

@router.post("/transcription-analytics")
async def save_transcription_analytics(analytics_data: TranscriptionAnalyticsCreate = Body(...)):
    """Save transcription analytics to the database."""
    try:
        logger.info(f"Saving transcription analytics for user {analytics_data.user_id}")
        
        # Create transcription analytics record
        analytics = TranscriptionAnalytics(
            user_id=analytics_data.user_id,
            audio_duration_seconds=analytics_data.audio_duration_seconds,
            transcription_text=analytics_data.transcription_text,
            confidence_score=analytics_data.confidence_score,
            language_detected=analytics_data.language_detected,
            processing_time_ms=analytics_data.processing_time_ms,
            model_used=analytics_data.model_used
        )
        
        await analytics.save()
        logger.info(f"Transcription analytics saved with ID: {analytics.id}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Transcription analytics saved successfully",
                "analytics": {
                    "id": str(analytics.id),
                    "user_id": analytics.user_id,
                    "audio_duration_seconds": analytics.audio_duration_seconds,
                    "confidence_score": analytics.confidence_score,
                    "timestamp": analytics.timestamp.isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error saving transcription analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save transcription analytics: {str(e)}")

@router.get("/analytics/usage/{user_id}")
async def get_user_analytics(user_id: str, limit: int = 50):
    """Get usage analytics for a specific user."""
    try:
        logger.info(f"Getting usage analytics for user: {user_id}")
        
        analytics = await UsageAnalytics.find(
            UsageAnalytics.user_id == user_id
        ).sort(-UsageAnalytics.timestamp).limit(limit).to_list()
        
        analytics_list = []
        for item in analytics:
            analytics_list.append({
                "id": str(item.id),
                "feature_used": item.feature_used,
                "session_duration_seconds": item.session_duration_seconds,
                "actions_performed": item.actions_performed,
                "errors_encountered": item.errors_encountered,
                "success_rate": item.success_rate,
                "timestamp": item.timestamp.isoformat()
            })
        
        return JSONResponse(content={"analytics": analytics_list})
        
    except Exception as e:
        logger.error(f"Error getting usage analytics for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage analytics: {str(e)}")

@router.get("/analytics/transcription/{user_id}")
async def get_user_transcription_analytics(user_id: str, limit: int = 50):
    """Get transcription analytics for a specific user."""
    try:
        logger.info(f"Getting transcription analytics for user: {user_id}")
        
        analytics = await TranscriptionAnalytics.find(
            TranscriptionAnalytics.user_id == user_id
        ).sort(-TranscriptionAnalytics.timestamp).limit(limit).to_list()
        
        analytics_list = []
        for item in analytics:
            analytics_list.append({
                "id": str(item.id),
                "audio_duration_seconds": item.audio_duration_seconds,
                "transcription_text": item.transcription_text,
                "confidence_score": item.confidence_score,
                "language_detected": item.language_detected,
                "processing_time_ms": item.processing_time_ms,
                "model_used": item.model_used,
                "timestamp": item.timestamp.isoformat()
            })
        
        return JSONResponse(content={"analytics": analytics_list})
        
    except Exception as e:
        logger.error(f"Error getting transcription analytics for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transcription analytics: {str(e)}")

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get comprehensive stats for a user."""
    try:
        logger.info(f"Getting comprehensive stats for user: {user_id}")
        
        # Count voice commands
        total_commands = await VoiceCommand.find(VoiceCommand.user_id == user_id).count()
        successful_commands = await VoiceCommand.find(
            VoiceCommand.user_id == user_id,
            VoiceCommand.execution_successful == True
        ).count()
        
        # Count usage analytics
        total_sessions = await UsageAnalytics.find(UsageAnalytics.user_id == user_id).count()
        
        # Count transcription analytics
        total_transcriptions = await TranscriptionAnalytics.find(
            TranscriptionAnalytics.user_id == user_id
        ).count()
        
        stats = {
            "user_id": user_id,
            "voice_commands": {
                "total": total_commands,
                "successful": successful_commands,
                "success_rate": (successful_commands / total_commands * 100) if total_commands > 0 else 0
            },
            "usage_sessions": total_sessions,
            "transcriptions": total_transcriptions
        }
        
        return JSONResponse(content={"stats": stats})
        
    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")