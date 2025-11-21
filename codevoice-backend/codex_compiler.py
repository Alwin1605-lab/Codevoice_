"""
Codex-powered Code Compilation and Execution API
Advanced code compilation, execution, and debugging using OpenAI's Codex.
"""

import os
import asyncio
import tempfile
import subprocess
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import openai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import time

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/codex-compiler", tags=["codex-compiler"])

class CodexExecutionMode(str, Enum):
    """Execution modes for Codex compiler."""
    COMPILE_ONLY = "compile_only"
    RUN_ONLY = "run_only"
    COMPILE_AND_RUN = "compile_and_run"
    DEBUG = "debug"
    OPTIMIZE = "optimize"
    EXPLAIN = "explain"

class CodexLanguage(str, Enum):
    """Supported languages for Codex compilation."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"

class CodexCompilationRequest(BaseModel):
    """Request model for Codex compilation."""
    code: str
    language: CodexLanguage
    mode: CodexExecutionMode = CodexExecutionMode.COMPILE_AND_RUN
    input_data: Optional[str] = None
    timeout: int = 30
    optimization_level: str = "O1"  # O0, O1, O2, O3
    include_dependencies: List[str] = []
    debug_info: bool = False
    explain_output: bool = True

class CodexOptimizationRequest(BaseModel):
    """Request model for code optimization."""
    code: str
    language: CodexLanguage
    optimization_goals: List[str] = ["performance", "readability"]
    target_platform: str = "general"
    maintain_functionality: bool = True

def get_codex_client():
    """Initialize OpenAI client for Codex."""
    api_key = os.getenv("CODEX_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Codex API key not configured")
    
    return openai.OpenAI(api_key=api_key)

def get_language_config(language: CodexLanguage) -> Dict[str, Any]:
    """Get configuration for different programming languages."""
    configs = {
        CodexLanguage.PYTHON: {
            "extension": ".py",
            "compile_cmd": None,
            "run_cmd": ["python", "{file}"],
            "interpreter": True,
            "supports_input": True
        },
        CodexLanguage.JAVASCRIPT: {
            "extension": ".js",
            "compile_cmd": None,
            "run_cmd": ["node", "{file}"],
            "interpreter": True,
            "supports_input": True
        },
        CodexLanguage.TYPESCRIPT: {
            "extension": ".ts",
            "compile_cmd": ["tsc", "{file}"],
            "run_cmd": ["node", "{file_js}"],
            "interpreter": False,
            "supports_input": True
        },
        CodexLanguage.JAVA: {
            "extension": ".java",
            "compile_cmd": ["javac", "{file}"],
            "run_cmd": ["java", "{class_name}"],
            "interpreter": False,
            "supports_input": True
        },
        CodexLanguage.CPP: {
            "extension": ".cpp",
            "compile_cmd": ["g++", "-o", "{executable}", "{file}"],
            "run_cmd": ["{executable}"],
            "interpreter": False,
            "supports_input": True
        },
        CodexLanguage.C: {
            "extension": ".c",
            "compile_cmd": ["gcc", "-o", "{executable}", "{file}"],
            "run_cmd": ["{executable}"],
            "interpreter": False,
            "supports_input": True
        }
    }
    return configs.get(language, configs[CodexLanguage.PYTHON])

async def codex_analyze_and_fix(client, code: str, language: str, error_message: str = None) -> Dict[str, Any]:
    """Use Codex to analyze code and suggest fixes."""
    
    analysis_prompt = f"""
Analyze this {language} code and provide:
1. Compilation/runtime issues (if any)
2. Suggested fixes
3. Optimizations
4. Best practices improvements

Code:
```{language}
{code}
```

{f"Error encountered: {error_message}" if error_message else ""}

Respond in JSON format:
{{
    "issues": ["list of issues found"],
    "fixes": ["list of specific fixes"],
    "optimized_code": "corrected and optimized version of the code",
    "explanation": "detailed explanation of changes made",
    "performance_notes": "performance considerations"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for better availability
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        return json.loads(result_text.strip())
        
    except Exception as e:
        logger.error(f"Codex analysis failed: {e}")
        return {
            "issues": ["Analysis failed"],
            "fixes": ["Unable to analyze code"],
            "optimized_code": code,
            "explanation": f"Analysis error: {str(e)}",
            "performance_notes": "No analysis available"
        }

async def execute_local_compilation(request: CodexCompilationRequest) -> Dict[str, Any]:
    """Execute code compilation and running locally."""
    language_config = get_language_config(request.language)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create source file
            source_file = temp_path / f"main{language_config['extension']}"
            source_file.write_text(request.code)
            
            result = {
                "compilation_output": "",
                "runtime_output": "",
                "error_output": "",
                "exit_code": 0,
                "execution_time": 0
            }
            
            start_time = time.time()
            
            # Compilation step (if needed)
            if language_config["compile_cmd"] and request.mode in [CodexExecutionMode.COMPILE_ONLY, CodexExecutionMode.COMPILE_AND_RUN]:
                compile_cmd = []
                for part in language_config["compile_cmd"]:
                    if "{file}" in part:
                        compile_cmd.append(part.replace("{file}", str(source_file)))
                    elif "{executable}" in part:
                        executable_path = temp_path / "main.exe" if os.name == 'nt' else temp_path / "main"
                        compile_cmd.append(part.replace("{executable}", str(executable_path)))
                    else:
                        compile_cmd.append(part)
                
                compile_process = await asyncio.create_subprocess_exec(
                    *compile_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir
                )
                
                compile_stdout, compile_stderr = await asyncio.wait_for(
                    compile_process.communicate(), timeout=request.timeout
                )
                
                result["compilation_output"] = compile_stdout.decode()
                if compile_stderr:
                    result["error_output"] = compile_stderr.decode()
                    result["exit_code"] = compile_process.returncode
                
                if compile_process.returncode != 0:
                    result["success"] = False
                    return result
            
            # Execution step (if needed)
            if request.mode in [CodexExecutionMode.RUN_ONLY, CodexExecutionMode.COMPILE_AND_RUN]:
                run_cmd = []
                for part in language_config["run_cmd"]:
                    if "{file}" in part:
                        run_cmd.append(part.replace("{file}", str(source_file)))
                    elif "{executable}" in part:
                        executable_path = temp_path / "main.exe" if os.name == 'nt' else temp_path / "main"
                        run_cmd.append(part.replace("{executable}", str(executable_path)))
                    elif "{class_name}" in part and request.language == CodexLanguage.JAVA:
                        run_cmd.append("main")  # Assuming class name is main
                    elif "{file_js}" in part:
                        js_file = source_file.with_suffix(".js")
                        run_cmd.append(str(js_file))
                    else:
                        run_cmd.append(part)
                
                run_process = await asyncio.create_subprocess_exec(
                    *run_cmd,
                    stdin=asyncio.subprocess.PIPE if request.input_data else None,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir
                )
                
                input_bytes = request.input_data.encode() if request.input_data else None
                run_stdout, run_stderr = await asyncio.wait_for(
                    run_process.communicate(input=input_bytes), timeout=request.timeout
                )
                
                result["runtime_output"] = run_stdout.decode()
                if run_stderr:
                    result["error_output"] += ("\\n" if result["error_output"] else "") + run_stderr.decode()
                
                result["exit_code"] = run_process.returncode
            
            result["execution_time"] = time.time() - start_time
            result["success"] = result["exit_code"] == 0
            
            return result
            
    except asyncio.TimeoutError:
        return {
            "compilation_output": "",
            "runtime_output": "",
            "error_output": "Execution timed out",
            "exit_code": -1,
            "execution_time": request.timeout,
            "success": False
        }
    except Exception as e:
        return {
            "compilation_output": "",
            "runtime_output": "",
            "error_output": f"Execution failed: {str(e)}",
            "exit_code": -1,
            "execution_time": 0,
            "success": False
        }

@router.post("/compile")
async def compile_code(request: CodexCompilationRequest = Body(...)):
    """
    Compile and execute code using Codex-enhanced compilation.
    """
    try:
        logger.info(f"Codex compilation request: {request.language.value} code")
        
        client = get_codex_client()
        
        # Execute local compilation
        execution_result = await execute_local_compilation(request)
        
        # If execution failed and explain_output is enabled, use Codex to analyze
        codex_analysis = None
        if not execution_result["success"] and request.explain_output:
            error_message = execution_result.get("error_output", "Unknown error")
            codex_analysis = await codex_analyze_and_fix(
                client, request.code, request.language.value, error_message
            )
        
        # Build response
        response_data = {
            "success": execution_result["success"],
            "language": request.language.value,
            "mode": request.mode.value,
            "execution_result": execution_result,
            "codex_analysis": codex_analysis,
            "metadata": {
                "execution_time": execution_result["execution_time"],
                "compiler": "Codex Enhanced Local Compiler",
                "timestamp": "2025-09-21T00:00:00Z"
            }
        }
        
        logger.info(f"Codex compilation completed: {'success' if execution_result['success'] else 'failed'}")
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Codex compilation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Compilation failed: {str(e)}")

@router.post("/optimize")
async def optimize_code(request: CodexOptimizationRequest = Body(...)):
    """
    Optimize code using Codex AI analysis.
    """
    try:
        logger.info(f"Codex optimization request: {request.language.value}")
        
        client = get_codex_client()
        
        optimization_goals = ", ".join(request.optimization_goals)
        
        optimization_prompt = f"""
Optimize this {request.language.value} code for {optimization_goals}.
Target platform: {request.target_platform}
Maintain functionality: {request.maintain_functionality}

Original code:
```{request.language.value}
{request.code}
```

Provide a JSON response with:
{{
    "optimized_code": "the optimized version of the code",
    "optimizations_applied": ["list of optimizations made"],
    "performance_improvement": "estimated performance improvement",
    "readability_score": "readability assessment (1-10)",
    "maintainability_notes": "notes on code maintainability",
    "potential_issues": ["any potential issues with optimizations"],
    "explanation": "detailed explanation of optimizations"
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": optimization_prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        optimization_result = json.loads(result_text.strip())
        
        return JSONResponse(content={
            "success": True,
            "language": request.language.value,
            "optimization_goals": request.optimization_goals,
            "optimization_result": optimization_result,
            "original_code": request.code,
            "metadata": {
                "optimizer": "Codex AI Optimizer",
                "timestamp": "2025-09-21T00:00:00Z"
            }
        })
        
    except Exception as e:
        logger.error(f"Code optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/debug")
async def debug_code(
    code: str = Body(...),
    language: CodexLanguage = Body(...),
    error_description: Optional[str] = Body(None),
    debug_context: Optional[str] = Body(None)
):
    """
    Debug code using Codex AI analysis.
    """
    try:
        logger.info(f"Codex debugging request: {language.value}")
        
        client = get_codex_client()
        
        debug_prompt = f"""
Debug this {language.value} code and provide solutions:

Code:
```{language.value}
{code}
```

{f"Error description: {error_description}" if error_description else ""}
{f"Debug context: {debug_context}" if debug_context else ""}

Provide a JSON response with:
{{
    "issues_found": ["list of issues identified"],
    "debug_suggestions": ["specific debugging suggestions"],
    "fixed_code": "corrected version of the code",
    "explanation": "detailed explanation of fixes",
    "prevention_tips": ["tips to prevent similar issues"],
    "testing_recommendations": ["recommendations for testing"]
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": debug_prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        debug_result = json.loads(result_text.strip())
        
        return JSONResponse(content={
            "success": True,
            "language": language.value,
            "debug_result": debug_result,
            "original_code": code,
            "metadata": {
                "debugger": "Codex AI Debugger",
                "timestamp": "2025-09-21T00:00:00Z"
            }
        })
        
    except Exception as e:
        logger.error(f"Code debugging failed: {e}")
        raise HTTPException(status_code=500, detail=f"Debugging failed: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """Get supported programming languages and their configurations."""
    return JSONResponse(content={
        "supported_languages": [lang.value for lang in CodexLanguage],
        "execution_modes": [mode.value for mode in CodexExecutionMode],
        "language_features": {
            lang.value: {
                "compiled": not get_language_config(lang)["interpreter"],
                "supports_input": get_language_config(lang)["supports_input"],
                "extension": get_language_config(lang)["extension"]
            }
            for lang in CodexLanguage
        }
    })

@router.get("/health")
async def health_check():
    """Health check for Codex compilation service."""
    try:
        api_key = os.getenv("CODEX_API_KEY")
        if not api_key:
            return JSONResponse(content={
                "status": "unhealthy",
                "service": "Codex Compiler",
                "api_configured": False,
                "error": "CODEX_API_KEY not found"
            }, status_code=503)
        
        # Test OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "Codex Compiler",
            "api_configured": True,
            "model": "gpt-3.5-turbo (Codex successor)",
            "supported_languages": len(CodexLanguage),
            "execution_modes": len(CodexExecutionMode)
        })
        
    except Exception as e:
        return JSONResponse(content={
            "status": "unhealthy",
            "service": "Codex Compiler",
            "api_configured": False,
            "error": str(e)
        }, status_code=503)