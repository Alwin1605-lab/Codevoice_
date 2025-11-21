"""
MongoDB connection and database management for Voice Controlled IDE.
Handles Motor async MongoDB setup, connection management, and database initialization.
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from typing import Optional
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoDB client and database instances
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_database: Optional[AsyncIOMotorDatabase] = None

class MongoDB:
    """MongoDB connection manager using Motor async driver."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Establish connection to MongoDB."""
        try:
            # Create MongoDB client with connection settings
            self.client = AsyncIOMotorClient(
                config.MONGODB_URL,
                minPoolSize=config.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=config.MONGODB_MAX_POOL_SIZE,
                maxIdleTimeMS=config.MONGODB_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=config.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                # Additional settings for production
                retryWrites=True,
                w="majority"
            )
            
            # Get database
            self.database = self.client[config.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB at {config.MONGODB_URL}")
            
            # Initialize Beanie with all document models
            await self.init_beanie()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def init_beanie(self):
        """Initialize Beanie ODM with all document models."""
        try:
            # Import all Document models (not BaseModel classes)
            from models.user_models import User
            from models.project_models import Project, CodeSession, VoiceCommand
            from models.collaboration_models import CollaborationSession, CollaborationInvite, CollaborationEvent
            from models.analytics_models import LearningProgress, TranscriptionAnalytics, Notification, UsageAnalytics, APIRateLimit, AudioFile, ProjectBackup
            from models.generation_models import GenerationTask
            
            # Initialize Beanie with all Document models only
            await init_beanie(
                database=self.database,
                document_models=[
                    # User models
                    User,
                    # Project models
                    Project, CodeSession, VoiceCommand,
                    # Collaboration models
                    CollaborationSession, CollaborationInvite, CollaborationEvent,
                    # Analytics models
                    LearningProgress, TranscriptionAnalytics, Notification, UsageAnalytics, 
                    APIRateLimit, AudioFile, ProjectBackup,
                    # Background tasks
                    GenerationTask
                ]
            )
            
            logger.info("Beanie ODM initialized successfully with all models")
            
        except Exception as e:
            logger.error(f"Failed to initialize Beanie: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def ping(self):
        """Test MongoDB connection."""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the current database instance."""
        return self.database
    
    def get_client(self) -> AsyncIOMotorClient:
        """Get the current client instance."""
        return self.client

# Global MongoDB instance
mongodb = MongoDB()

async def connect_to_mongodb():
    """Connect to MongoDB and initialize Beanie."""
    global mongodb_client, mongodb_database
    
    success = await mongodb.connect()
    if success:
        mongodb_client = mongodb.get_client()
        mongodb_database = mongodb.get_database()
    
    return success

async def disconnect_from_mongodb():
    """Disconnect from MongoDB."""
    await mongodb.disconnect()

async def get_database() -> AsyncIOMotorDatabase:
    """Get the current MongoDB database instance."""
    if mongodb_database is None:
        await connect_to_mongodb()
    return mongodb_database

async def test_mongodb_connection():
    """Test the MongoDB connection and return status information."""
    try:
        if mongodb_client is None:
            await connect_to_mongodb()
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        # Get server info
        server_info = await mongodb_client.server_info()
        
        # Get database stats
        db_stats = await mongodb_database.command('dbStats')
        
        logger.info("MongoDB connection test successful")
        return {
            "status": "connected",
            "mongodb_url": config.MONGODB_URL,
            "database_name": config.MONGODB_DATABASE,
            "server_version": server_info.get("version", "Unknown"),
            "collections_count": db_stats.get("collections", 0),
            "data_size": db_stats.get("dataSize", 0),
            "storage_size": db_stats.get("storageSize", 0),
            "message": "Connection successful"
        }
        
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

async def get_mongodb_info():
    """Get information about the current MongoDB setup."""
    try:
        if mongodb_client is None:
            await connect_to_mongodb()
        
        # Get server info
        server_info = await mongodb_client.server_info()
        
        # Get database stats
        db_stats = await mongodb_database.command('dbStats')
        
        # Get collection names
        collection_names = await mongodb_database.list_collection_names()
        
        return {
            "database_type": "MongoDB",
            "server_version": server_info.get("version", "Unknown"),
            "url": config.MONGODB_URL,
            "database_name": config.MONGODB_DATABASE,
            "collections": collection_names,
            "collections_count": len(collection_names),
            "data_size_bytes": db_stats.get("dataSize", 0),
            "storage_size_bytes": db_stats.get("storageSize", 0),
            "indexes_count": db_stats.get("indexes", 0),
            "pool_settings": {
                "min_pool_size": config.MONGODB_MIN_POOL_SIZE,
                "max_pool_size": config.MONGODB_MAX_POOL_SIZE,
                "max_idle_time_ms": config.MONGODB_MAX_IDLE_TIME_MS,
                "server_selection_timeout_ms": config.MONGODB_SERVER_SELECTION_TIMEOUT_MS
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get MongoDB info: {e}")
        return {"error": str(e)}

async def create_indexes():
    """Create database indexes for better performance."""
    try:
        if mongodb_database is None:
            await connect_to_mongodb()
        
        # Create indexes for better query performance
        indexes_created = []
        
        # Users collection indexes
        users_collection = mongodb_database["users"]
        await users_collection.create_index("username", unique=True)
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("created_at")
        indexes_created.extend(["users.username", "users.email", "users.created_at"])
        
        # Projects collection indexes
        projects_collection = mongodb_database["projects"]
        await projects_collection.create_index("user_id")
        await projects_collection.create_index("created_at")
        await projects_collection.create_index("generation_status")
        await projects_collection.create_index([("user_id", 1), ("created_at", -1)])
        indexes_created.extend(["projects.user_id", "projects.created_at", "projects.generation_status"])
        
        # Voice commands collection indexes
        voice_commands_collection = mongodb_database["voice_commands"]
        await voice_commands_collection.create_index("user_id")
        await voice_commands_collection.create_index("created_at")
        await voice_commands_collection.create_index("command_type")
        indexes_created.extend(["voice_commands.user_id", "voice_commands.created_at", "voice_commands.command_type"])
        
        # Collaboration sessions collection indexes
        collab_sessions_collection = mongodb_database["collaboration_sessions"]
        await collab_sessions_collection.create_index("host_user_id")
        await collab_sessions_collection.create_index("session_code", unique=True)
        await collab_sessions_collection.create_index("is_active")
        indexes_created.extend(["collaboration_sessions.host_user_id", "collaboration_sessions.session_code"])
        
        # Notifications collection indexes
        notifications_collection = mongodb_database["notifications"]
        await notifications_collection.create_index("user_id")
        await notifications_collection.create_index("read")
        await notifications_collection.create_index("created_at")
        indexes_created.extend(["notifications.user_id", "notifications.read", "notifications.created_at"])
        
        logger.info(f"Created {len(indexes_created)} indexes: {', '.join(indexes_created)}")
        return indexes_created
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        return []

# Dependency for FastAPI
async def get_mongodb_client():
    """FastAPI dependency for getting MongoDB client."""
    if mongodb_client is None:
        await connect_to_mongodb()
    return mongodb_client