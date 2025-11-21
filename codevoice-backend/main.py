from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
import logging
import os
from code_generation import router as code_router 
from compile_api import router as compile_router
from transcription import router as transcribe_router 
from txt_speech import router as txt_speech
from user_api_mongodb_clean import router as user_router  # Updated to use MongoDB
from learning_mode import router as learning_router
from multilang_support import router as multilang_router
from collaboration import router as collaboration_router
from project_manager import router as project_router
from voice_narration import router as narration_router
from voice_commands import router as commands_router
from enhanced_api import router as enhanced_router
from database_api import router as database_router
from project_api_db import router as project_db_router
from collaboration_api_db import router as collaboration_db_router
from voice_commands_api_db import router as voice_commands_db_router
from groq_code_analysis import router as groq_analysis_router
from gemini_project_generator import router as gemini_project_router
from metrics import metrics_response
from fastapi import Response
from codex_compiler import router as codex_compiler_router
from database import connect_to_mongodb, disconnect_from_mongodb
from contextlib import asynccontextmanager

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure main application logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Voice Controlled IDE application...")
    await connect_to_mongodb()
    logger.info("MongoDB connection established")
    yield
    # Shutdown
    logger.info("Shutting down Voice Controlled IDE application...")
    await disconnect_from_mongodb()
    logger.info("MongoDB connection closed")

app = FastAPI(
    title="Voice Controlled IDE API",
    description="AI-powered IDE with voice control and MongoDB backend",
    version="1.0.0",
    lifespan=lifespan
) 

app.add_middleware( 
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
) 

# Include all routers with logging
logger.info("Registering API routes...")

app.include_router(code_router)
logger.info("Registered code generation routes")

app.include_router(compile_router)          
logger.info("Registered compile API routes")

app.include_router(transcribe_router)
logger.info("Registered transcription routes")

app.include_router(txt_speech)
logger.info("Registered text-to-speech routes")

app.include_router(user_router)
logger.info("Registered MongoDB user API routes")

app.include_router(learning_router, prefix="/learning")
logger.info("Registered learning mode routes")

app.include_router(multilang_router, prefix="/multilang")
logger.info("Registered multilingual support routes")

app.include_router(collaboration_router, prefix="/collaboration")
logger.info("Registered collaboration routes")

app.include_router(project_router, prefix="/projects")
logger.info("Registered project management routes")

app.include_router(narration_router, prefix="/narration")
logger.info("Registered voice narration routes")

app.include_router(commands_router, prefix="/commands")
logger.info("Registered voice commands routes")

app.include_router(enhanced_router, prefix="/api")
logger.info("Registered enhanced API routes")

app.include_router(database_router, prefix="/api")
logger.info("Registered database API routes")

# NEW: Database-backed APIs that actually save to MongoDB
app.include_router(project_db_router)
logger.info("Registered database-backed project API routes")

app.include_router(collaboration_db_router)
logger.info("Registered database-backed collaboration API routes")

app.include_router(voice_commands_db_router)
logger.info("Registered database-backed voice commands API routes")

app.include_router(groq_analysis_router)
logger.info("Registered Groq code analysis routes")

app.include_router(gemini_project_router)
logger.info("Registered Gemini project generation routes")

app.include_router(codex_compiler_router)
logger.info("Registered Codex compiler routes")

@app.get("/health")
async def health_check():
    """Health check endpoint with MongoDB status."""
    logger.info("Health check requested")
    return {
        "status": "healthy", 
        "database": "mongodb",
        "timestamp": "2025-09-20T00:00:00Z",
        "version": "1.0.0"
    }


@app.get('/metrics')
async def metrics_endpoint():
    payload, content_type = metrics_response()
    return Response(content=payload, media_type=content_type)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)