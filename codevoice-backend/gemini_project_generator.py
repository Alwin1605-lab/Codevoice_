"""
Gemini-powered Project Generation API
Intelligent project scaffolding and template generation using Google's Gemini AI.
"""

import os
import json
import zipfile
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
import uuid
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import logging
import asyncio
from collections import deque
from models.generation_models import GenerationTask, TaskStatus
import json as _json

# Redis pub/sub support (optional) - import dynamically to avoid static import issues
try:
    import importlib
    _redis_mod = importlib.import_module('redis')
    aioredis = getattr(_redis_mod, 'asyncio', None)
except Exception:
    aioredis = None

_redis_client = None
_redis_pubsub_prefix = os.getenv('PROJECT_TASKS_REDIS_PREFIX', 'project_tasks')
_redis_url = os.getenv('REDIS_URL') or os.getenv('REDIS_URI')
if aioredis and _redis_url:
    try:
        _redis_client = aioredis.from_url(_redis_url)
    except Exception:
        _redis_client = None
from fastapi import WebSocket, WebSocketDisconnect

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/project-generation", tags=["project-generation"])
_job_queue: deque = deque()
_worker_started = False

async def _ensure_worker():
    global _worker_started
    if _worker_started:
        return
    _worker_started = True
    asyncio.create_task(_worker_loop())

async def _worker_loop():
    while True:
        try:
            if _job_queue:
                task_id = _job_queue.popleft()
                task = await GenerationTask.find_one(GenerationTask.task_id == task_id)
                if not task:
                    continue
                await task.mark_running()
                try:
                    # Rehydrate request to model for generation
                    req = ProjectGenerationRequest(**task.request)
                    # Run sync generation and capture result json
                    result = await generate_project(req)
                    # Normalize result into a serializable payload
                    payload = None
                    # If the endpoint returned a FastAPI response object
                    if hasattr(result, 'media_type') and hasattr(result, 'body'):
                        try:
                            # body may be bytes
                            raw = result.body
                            if isinstance(raw, (bytes, bytearray)):
                                payload = raw.decode('utf-8', errors='ignore')
                            else:
                                payload = str(raw)
                        except Exception:
                            payload = None
                    # If the endpoint returned a dict-like object
                    elif isinstance(result, dict):
                        payload = result
                    # If the endpoint returned a JSONResponse
                    elif isinstance(result, JSONResponse):
                        try:
                            payload = json.loads(result.body.decode('utf-8'))
                        except Exception:
                            payload = result.body.decode('utf-8', errors='ignore')
                    # If the endpoint returned a FileResponse, record the path
                    elif isinstance(result, FileResponse):
                        payload = {"file_path": getattr(result, 'path', None)}

                    # Fallback: stringify
                    if payload is None:
                        try:
                            payload = str(result)
                        except Exception:
                            payload = {"result_repr": repr(result)}

                    await task.mark_completed(result={"response": payload})
                    # metrics: increment generation task counter
                    try:
                        from .metrics import generation_tasks_total
                        generation_tasks_total.labels(status='completed').inc()
                    except Exception:
                        pass
                    # Publish update to Redis channel (if enabled)
                    try:
                        if _redis_client is not None:
                            channel = f"{_redis_pubsub_prefix}:{task_id}"
                            await _redis_client.publish(channel, _json.dumps({"task_id": task_id, "status": task.status, "result": task.result, "error": task.error}))
                    except Exception:
                        logger.debug("Redis publish failed; continuing without pub/sub")
                except Exception as gen_err:
                    await task.mark_failed(str(gen_err))
                    try:
                        from .metrics import generation_tasks_total
                        generation_tasks_total.labels(status='failed').inc()
                    except Exception:
                        pass
                    try:
                        if _redis_client is not None:
                            channel = f"{_redis_pubsub_prefix}:{task_id}"
                            await _redis_client.publish(channel, _json.dumps({"task_id": task_id, "status": task.status, "error": task.error}))
                    except Exception:
                        logger.debug("Redis publish failed for failure notification")
            else:
                await asyncio.sleep(0.2)
        except Exception:
            await asyncio.sleep(0.5)

class ProjectType(str, Enum):
    """Supported project types for generation."""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    API_SERVER = "api_server"
    CLI_TOOL = "cli_tool"
    MACHINE_LEARNING = "machine_learning"
    DATA_ANALYSIS = "data_analysis"
    GAME_DEV = "game_dev"
    MICROSERVICE = "microservice"
    LIBRARY = "library"

class Framework(str, Enum):
    """Supported frameworks for project generation."""
    # Web Frameworks
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"
    SVELTE = "svelte"
    
    # Backend Frameworks
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    EXPRESS = "express"
    SPRING_BOOT = "spring_boot"
    
    # Mobile Frameworks
    REACT_NATIVE = "react_native"
    FLUTTER = "flutter"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    
    # Desktop Frameworks
    ELECTRON = "electron"
    TKINTER = "tkinter"
    QT = "qt"
    
    # Data Science
    JUPYTER = "jupyter"
    STREAMLIT = "streamlit"
    DASH = "dash"

class ComplexityLevel(str, Enum):
    """Project complexity levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class ProjectGenerationRequest(BaseModel):
    """Request model for project generation."""
    project_name: str
    project_type: ProjectType
    framework: Framework
    complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    description: str
    features: List[str] = []
    technologies: List[str] = []
    include_tests: bool = True
    include_docker: bool = False
    include_ci_cd: bool = False
    database_type: Optional[str] = None
    authentication: bool = False
    api_documentation: bool = True
    include_tests: bool = False

@router.post("/generate/async")
async def generate_project_async(request: ProjectGenerationRequest = Body(...)):
    """Enqueue an async project generation and return a task id."""
    try:
        await _ensure_worker()
        task_id = str(uuid.uuid4())
        task = GenerationTask(task_id=task_id, status=TaskStatus.queued, request=request.dict())
        await task.insert()
        _job_queue.append(task_id)
        return JSONResponse(content={"task_id": task_id, "status": TaskStatus.queued})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue generation: {e}")

@router.get("/tasks/{task_id}")
async def get_generation_status(task_id: str):
    """Get generation task status and result if available."""
    task = await GenerationTask.find_one(GenerationTask.task_id == task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={
        "task_id": task.task_id,
        "status": task.status,
        "result": task.result,
        "artifact_path": task.artifact_path,
        "error": task.error
    })

def get_gemini_client():
    """Initialize and return Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    genai.configure(api_key=api_key)
    # Using latest stable flash model
    return genai.GenerativeModel('models/gemini-2.0-flash')

def get_project_prompt(request: ProjectGenerationRequest) -> str:
    """Generate comprehensive prompt for project generation."""
    
    features_str = ", ".join(request.features) if request.features else "standard features"
    tech_str = ", ".join(request.technologies) if request.technologies else "recommended technologies"
    
    prompt = f"""
You are an expert software architect and full-stack developer. Generate a complete project structure for:

**Project Details:**
- Name: {request.project_name}
- Type: {request.project_type.value}
- Framework: {request.framework.value}
- Complexity: {request.complexity.value}
- Description: {request.description}
- Features: {features_str}
- Technologies: {tech_str}

**Requirements:**
- Include tests: {request.include_tests}
- Include Docker: {request.include_docker}
- Include CI/CD: {request.include_ci_cd}
- Database: {request.database_type or "None specified"}
- Authentication: {request.authentication}
- API Documentation: {request.api_documentation}

**Generate a JSON response with the following structure:**
```json
{{
    "project_structure": {{
        "folders": ["folder1", "folder2/subfolder"],
        "files": {{
            "file_path": {{
                "content": "file content here",
                "description": "what this file does"
            }}
        }}
    }},
    "setup_instructions": [
        "Step 1: Install dependencies",
        "Step 2: Configure environment"
    ],
    "recommended_dependencies": {{
        "production": ["dep1", "dep2"],
        "development": ["dev-dep1", "dev-dep2"]
    }},
    "environment_variables": {{
        "VAR_NAME": "description of what this variable is for"
    }},
    "scripts": {{
        "script_name": "script command or code"
    }},
    "architecture_notes": "Brief explanation of the project architecture and design decisions"
}}
```

**Guidelines:**
1. Create a production-ready project structure appropriate for {request.complexity.value} complexity
2. Include proper configuration files (package.json, requirements.txt, etc.)
3. Add appropriate folder structure and organization
4. Include basic implementation files with proper imports and structure
5. Add configuration for requested features (Docker, CI/CD, tests)
6. Ensure the structure follows best practices for {request.framework.value}
7. Include README.md with comprehensive setup and usage instructions

Generate ONLY the JSON response, no additional text.
"""
    return prompt

@router.post("/generate")
async def generate_project(request: ProjectGenerationRequest = Body(...)):
    """
    Generate a complete project structure using Gemini AI.
    """
    try:
        logger.info(f"Generating project: {request.project_name} ({request.project_type.value})")
        
        # Get Gemini client
        model = get_gemini_client()
        
        # Generate project prompt
        prompt = get_project_prompt(request)
        
        # Generate project structure
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate project content")
        
        # Parse the JSON response
        try:
            # Clean the response text (remove code blocks if present)
            cleaned_response = response.text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            project_data = json.loads(cleaned_response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response.text[:500]}...")
            raise HTTPException(status_code=500, detail="Failed to parse generated project structure")
        
        # Add metadata
        project_data["metadata"] = {
            "project_name": request.project_name,
            "project_type": request.project_type.value,
            "framework": request.framework.value,
            "complexity": request.complexity.value,
            "generated_at": "2025-09-21T00:00:00Z",
            "generator": "Gemini AI"
        }
        
        logger.info(f"Successfully generated project structure for {request.project_name}")
        
        return JSONResponse(content={
            "success": True,
            "project": project_data,
            "message": f"Project '{request.project_name}' generated successfully"
        })
        
    except Exception as e:
        logger.error(f"Project generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Project generation failed: {str(e)}")

@router.post("/generate-files")
async def generate_project_files(request: ProjectGenerationRequest = Body(...)):
    """
    Generate project files and return as downloadable zip.
    """
    try:
        # First generate the project structure
        logger.info(f"Generating files for project: {request.project_name}")
        
        model = get_gemini_client()
        prompt = get_project_prompt(request)
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate project content")
        
        # Parse response
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        project_data = json.loads(cleaned_response)
        
        # Create temporary directory for project files
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / request.project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Create folder structure
            if "folders" in project_data.get("project_structure", {}):
                for folder in project_data["project_structure"]["folders"]:
                    folder_path = project_dir / folder
                    folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create files
            if "files" in project_data.get("project_structure", {}):
                for file_path, file_data in project_data["project_structure"]["files"].items():
                    full_file_path = project_dir / file_path
                    full_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    content = file_data.get("content", "") if isinstance(file_data, dict) else str(file_data)
                    full_file_path.write_text(content, encoding="utf-8")
                    # Publish per-file progress to Redis (if enabled)
                    try:
                        if _redis_client is not None:
                            channel = f"{_redis_pubsub_prefix}:{request.project_name}"
                            await _redis_client.publish(channel, json.dumps({"event": "file_generated", "file": file_path, "project": request.project_name}))
                    except Exception:
                        logger.debug("Failed to publish file_generated event to Redis")
            
            # Create zip file
            zip_path = Path(temp_dir) / f"{request.project_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_dir.parent)
                        zipf.write(file_path, arcname)
            
            # Copy zip to a permanent location (for this session)
            output_dir = Path("generated_projects")
            output_dir.mkdir(exist_ok=True)
            final_zip_path = output_dir / f"{request.project_name}.zip"
            shutil.copy2(zip_path, final_zip_path)
            
            logger.info(f"Project files generated: {final_zip_path}")
            
            return FileResponse(
                path=str(final_zip_path),
                filename=f"{request.project_name}.zip",
                media_type="application/zip"
            )
            
    except Exception as e:
        logger.error(f"Project file generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Project file generation failed: {str(e)}")

@router.get("/templates")
async def get_project_templates():
    """Get available project templates and frameworks."""
    return JSONResponse(content={
        "project_types": [ptype.value for ptype in ProjectType],
        "frameworks": [framework.value for framework in Framework],
        "complexity_levels": [level.value for level in ComplexityLevel],
        "template_combinations": {
            "web_app": ["react", "vue", "angular", "nextjs", "svelte"],
            "api_server": ["fastapi", "flask", "django", "express", "spring_boot"],
            "mobile_app": ["react_native", "flutter", "swift", "kotlin"],
            "desktop_app": ["electron", "tkinter", "qt"],
            "machine_learning": ["jupyter", "streamlit", "dash"],
            "data_analysis": ["jupyter", "streamlit", "dash"]
        },
        "features": [
            "user_authentication",
            "database_integration",
            "api_endpoints",
            "real_time_updates",
            "file_upload",
            "email_notifications",
            "payment_integration",
            "admin_dashboard",
            "user_profiles",
            "search_functionality",
            "caching",
            "logging",
            "monitoring",
            "rate_limiting",
            "internationalization"
        ]
    })

@router.post("/customize-template")
async def customize_project_template(
    project_type: ProjectType = Body(...),
    framework: Framework = Body(...),
    features: List[str] = Body([])
):
    """
    Get customized project template based on selections.
    """
    try:
        model = get_gemini_client()
        
        features_str = ", ".join(features) if features else "basic features"
        
        prompt = f"""
Generate a detailed project template specification for:
- Project Type: {project_type.value}
- Framework: {framework.value}
- Features: {features_str}

Provide a JSON response with:
1. Recommended folder structure
2. Essential files and their purposes
3. Recommended dependencies
4. Configuration suggestions
5. Best practices for this combination

Format as JSON only.
"""
        
        response = model.generate_content(prompt)
        
        # Parse response
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        
        template_data = json.loads(cleaned_response.strip())
        
        return JSONResponse(content={
            "success": True,
            "template": template_data,
            "project_type": project_type.value,
            "framework": framework.value,
            "features": features
        })
        
    except Exception as e:
        logger.error(f"Template customization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Template customization failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for Gemini project generation service."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(content={
                "status": "unhealthy",
                "service": "Gemini Project Generation",
                "api_configured": False,
                "error": "GEMINI_API_KEY not found"
            }, status_code=503)
        
        # Test basic Gemini connection
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "Gemini Project Generation",
            "api_configured": True,
            "model": "models/gemini-2.0-flash"
        })
        
    except Exception as e:
        return JSONResponse(content={
            "status": "unhealthy",
            "service": "Gemini Project Generation",
            "api_configured": False,
            "error": str(e)
        }, status_code=503)


@router.websocket('/ws/tasks/{task_id}')
async def task_progress_ws(websocket: WebSocket, task_id: str):
    """Simple websocket that streams task status updates for a given `task_id`.

    This implementation polls the database for task status changes and pushes
    JSON messages to the connected client. It's intentionally simple to avoid
    coupling with task update hooks; for production use a pub/sub or events system.
    """
    await websocket.accept()
    try:
        # Prefer Redis pub/sub subscription if available (more real-time, no polling)
        if _redis_client is not None:
            try:
                channel = f"{_redis_pubsub_prefix}:{task_id}"
                pubsub = _redis_client.pubsub()
                await pubsub.subscribe(channel)
                async for msg in pubsub.listen():
                    # msg example: {'type': 'message', 'pattern': None, 'channel': b'...', 'data': b'...'}
                    if msg is None:
                        continue
                    if msg.get('type') != 'message':
                        continue
                    try:
                        data = msg.get('data')
                        if isinstance(data, (bytes, bytearray)):
                            payload = _json.loads(data.decode('utf-8', errors='ignore'))
                        elif isinstance(data, str):
                            payload = _json.loads(data)
                        else:
                            payload = {"message": str(data)}
                    except Exception:
                        payload = {"message": str(msg.get('data'))}

                    await websocket.send_json(payload)
                    # Close on terminal status
                    if payload.get('status') in (TaskStatus.completed, TaskStatus.failed) or payload.get('error'):
                        await websocket.close()
                        try:
                            await pubsub.unsubscribe(channel)
                        except Exception:
                            pass
                        return
            except Exception:
                # Fall through to DB polling fallback
                logger.debug('Redis pubsub failed; falling back to DB polling')

        # Fallback: poll DB for status changes
        last_status = None
        while True:
            task = await GenerationTask.find_one(GenerationTask.task_id == task_id)
            if not task:
                await websocket.send_json({"error": "task_not_found", "task_id": task_id})
                await asyncio.sleep(1.0)
                continue

            payload = {
                "task_id": task.task_id,
                "status": task.status,
                "result": task.result,
                "artifact_path": task.artifact_path,
                "error": task.error
            }

            # Only send updates when status changes to reduce chatty messages
            if task.status != last_status:
                await websocket.send_json(payload)
                last_status = task.status

            # If task is in a terminal state, send final payload and close
            if task.status in (TaskStatus.completed, TaskStatus.failed):
                await websocket.send_json(payload)
                await websocket.close()
                return

            await asyncio.sleep(0.8)
    except WebSocketDisconnect:
        return
    except Exception as e:
        try:
            await websocket.send_json({"error": "internal_error", "detail": str(e)})
            await websocket.close()
        except Exception:
            pass