"""
Database test and status endpoints for MongoDB.
"""

from fastapi import APIRouter
from database import test_mongodb_connection, get_mongodb_info, create_indexes
from config import config

router = APIRouter()

@router.get("/database/status")
async def get_database_status():
    """Get MongoDB connection status and information."""
    return await test_mongodb_connection()

@router.get("/database/info")
async def get_database_info_endpoint():
    """Get detailed MongoDB information."""
    return await get_mongodb_info()

@router.post("/database/create-indexes")
async def create_database_indexes():
    """Create database indexes for better performance."""
    indexes = await create_indexes()
    return {
        "message": "Indexes created successfully",
        "indexes_created": indexes,
        "count": len(indexes)
    }

@router.get("/database/config")
async def get_database_config():
    """Get current database configuration."""
    return {
        "mongodb_url": config.MONGODB_URL,
        "database_name": config.MONGODB_DATABASE,
        "min_pool_size": config.MONGODB_MIN_POOL_SIZE,
        "max_pool_size": config.MONGODB_MAX_POOL_SIZE,
        "max_idle_time_ms": config.MONGODB_MAX_IDLE_TIME_MS,
        "server_selection_timeout_ms": config.MONGODB_SERVER_SELECTION_TIMEOUT_MS
    }