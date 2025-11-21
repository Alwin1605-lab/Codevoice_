"""
Configuration management for the Voice Controlled IDE backend.
Handles API keys, tokens, environment variables, and MongoDB settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing environment variables."""
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = os.getenv("GIT_TOKEN")
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL", 
        "mongodb://localhost:27017"
    )
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "voice_controlled_ide")
    MONGODB_TEST_DATABASE: str = os.getenv("MONGODB_TEST_DATABASE", "voice_controlled_ide_test")
    
    # MongoDB Connection Settings
    MONGODB_MIN_POOL_SIZE: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_MAX_POOL_SIZE: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    MONGODB_MAX_IDLE_TIME_MS: int = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "30000"))
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # CORS Settings
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))
    WEBSOCKET_CONNECTION_TIMEOUT: int = int(os.getenv("WEBSOCKET_CONNECTION_TIMEOUT", "300"))
    
    # Rate Limiting
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))  # requests per minute
    
    # File Storage
    AUDIO_UPLOAD_DIR: str = os.getenv("AUDIO_UPLOAD_DIR", "audio")
    MAX_AUDIO_FILE_SIZE: int = int(os.getenv("MAX_AUDIO_FILE_SIZE", "50000000"))  # 50MB
    AUDIO_FILE_RETENTION_DAYS: int = int(os.getenv("AUDIO_FILE_RETENTION_DAYS", "7"))
    
    @classmethod
    def validate_required_keys(cls) -> dict:
        """
        Validate that required API keys and configuration are present.
        Returns a dictionary with validation results.
        """
        validation_results = {
            "missing_keys": [],
            "available_keys": [],
            "warnings": []
        }
        
        # Check for required keys
        if not cls.GROQ_API_KEY:
            validation_results["missing_keys"].append("GROQ_API_KEY")
        else:
            validation_results["available_keys"].append("GROQ_API_KEY")
        
        if not cls.GEMINI_API_KEY:
            validation_results["missing_keys"].append("GEMINI_API_KEY")
        else:
            validation_results["available_keys"].append("GEMINI_API_KEY")
        
        if not cls.GITHUB_TOKEN:
            validation_results["missing_keys"].append("GIT_TOKEN")
        else:
            validation_results["available_keys"].append("GIT_TOKEN")
        
        # Check MongoDB URL
        if cls.MONGODB_URL == "mongodb://localhost:27017":
            validation_results["warnings"].append("Using default MONGODB_URL (please configure for production)")
        
        # Check secret key
        if cls.SECRET_KEY == "your-secret-key-change-in-production":
            validation_results["warnings"].append("Using default SECRET_KEY (SECURITY RISK: change for production)")
        
        # Add warnings for optional keys
        if not cls.OPENAI_API_KEY:
            validation_results["warnings"].append("OPENAI_API_KEY not set (optional)")
        
        return validation_results
    
    @classmethod
    def get_status_report(cls) -> str:
        """
        Generate a human-readable status report of configuration.
        """
        validation = cls.validate_required_keys()
        
        report = "Configuration Status:\n"
        report += "=" * 30 + "\n"
        
        if validation["available_keys"]:
            report += "✅ Available API Keys:\n"
            for key in validation["available_keys"]:
                report += f"   - {key}\n"
        
        if validation["missing_keys"]:
            report += "\n❌ Missing Required Keys:\n"
            for key in validation["missing_keys"]:
                report += f"   - {key}\n"
        
        if validation["warnings"]:
            report += "\n⚠️  Warnings:\n"
            for warning in validation["warnings"]:
                report += f"   - {warning}\n"
        
        report += f"\nServer Configuration:\n"
        report += f"   - Host: {cls.HOST}\n"
        report += f"   - Port: {cls.PORT}\n"
        report += f"   - Debug: {cls.DEBUG}\n"
        
        report += f"\nMongoDB Configuration:\n"
        report += f"   - URL: {cls.MONGODB_URL}\n"
        report += f"   - Database: {cls.MONGODB_DATABASE}\n"
        report += f"   - Pool Size: {cls.MONGODB_MIN_POOL_SIZE}-{cls.MONGODB_MAX_POOL_SIZE}\n"
        
        return report

# Create a global config instance
config = Config()