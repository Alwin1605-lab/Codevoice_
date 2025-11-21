import os
from fastapi import APIRouter, Form
from run_code_utils import wrap_runnable_code, run_locally
from remote_execution import run_remote, RemoteExecError, list_remote_languages
from groq_compiler import compile_with_groq_analysis
from judge0_executor import execute_with_judge0, is_language_supported, get_language_info
from codex_compiler import CodexCompilationRequest, CodexLanguage, CodexExecutionMode

router = APIRouter()

@router.get("/compile/providers")
async def get_compile_providers():
    import os
    provider = os.getenv("EXEC_PROVIDER") or os.getenv("USE_REMOTE_EXECUTION") or "judge0"
    langs = list_remote_languages()
    judge0_info = get_language_info()
    
    return {
        "provider": provider, 
        "remote_languages": langs,
        "judge0_info": judge0_info,
        "supported_services": ["codex", "judge0", "remote", "local", "groq"]
    }

@router.post("/compile/")
async def compile_code(
    code: str = Form(...),
    language: str = Form(...),
    inputs: str = Form("")
):
    # Inputs can be a string (from textarea) or empty
    inputs_list = [i for i in inputs.splitlines() if i.strip()] if inputs else []
    runnable_code = wrap_runnable_code(language, code)
    stdin = "\n".join(inputs_list) if inputs_list else ""
    
    # Determine execution provider
    provider = os.getenv("EXEC_PROVIDER", "codex").lower()
    use_remote = os.getenv("USE_REMOTE_EXECUTION", "").strip().lower() not in ("", "false", "0", "no", "local")
    
    # Try Codex first (premium AI-powered compilation)
    if provider == "codex" and os.getenv("CODEX_API_KEY"):
        try:
            print(f"Executing {language} code with Codex...")
            # Map language names to Codex enum
            codex_lang_map = {
                "python": CodexLanguage.PYTHON,
                "javascript": CodexLanguage.JAVASCRIPT,
                "typescript": CodexLanguage.TYPESCRIPT,
                "java": CodexLanguage.JAVA,
                "cpp": CodexLanguage.CPP,
                "c": CodexLanguage.C,
                "csharp": CodexLanguage.CSHARP,
                "go": CodexLanguage.GO,
                "rust": CodexLanguage.RUST,
                "php": CodexLanguage.PHP,
                "ruby": CodexLanguage.RUBY
            }
            
            if language.lower() in codex_lang_map:
                from codex_compiler import compile_code as codex_compile
                
                codex_request = CodexCompilationRequest(
                    code=runnable_code,
                    language=codex_lang_map[language.lower()],
                    mode=CodexExecutionMode.COMPILE_AND_RUN,
                    input_data=stdin,
                    explain_output=True
                )
                
                # Call Codex compilation endpoint directly
                codex_result = await codex_compile(codex_request)
                exec_result = codex_result.body.decode() if hasattr(codex_result, 'body') else {}
                
                if isinstance(exec_result, str):
                    import json
                    exec_result = json.loads(exec_result)
                
                if exec_result.get("success"):
                    execution_data = exec_result.get("execution_result", {})
                    return {
                        "stdout": execution_data.get("runtime_output", ""),
                        "stderr": execution_data.get("error_output", ""),
                        "compile_output": execution_data.get("compilation_output", ""),
                        "execution_method": "codex",
                        "codex_analysis": exec_result.get("codex_analysis")
                    }
        except Exception as e:
            print(f"Codex execution failed: {e}, trying Judge0...")
    
    # Try Judge0 second (best for localhost development)
    if provider in ["judge0", "codex"] or (provider not in ["local", "remote"] and is_language_supported(language)):
        try:
            print(f"Executing {language} code with Judge0...")
            stdout, stderr, compile_output = await execute_with_judge0(language, runnable_code, stdin)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "compile_output": compile_output,
                "execution_method": "judge0"
            }
        except Exception as e:
            print(f"Judge0 execution failed: {e}, trying other methods...")
    
    # Try remote execution
    if use_remote or provider == "remote":
        try:
            stdout, stderr, compile_output = run_remote(language, runnable_code, stdin)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "compile_output": compile_output,
                "execution_method": "remote"
            }
        except RemoteExecError as e:
            print(f"Remote execution failed: {e}, falling back to local")
    
    # Try local execution as fallback
    try:
        stdout, stderr, compile_output = run_locally(language, runnable_code, stdin)
        return {
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "execution_method": "local"
        }
    except Exception as e:
        print(f"Local execution failed: {e}, falling back to Groq simulation")
    
    # Fallback to Groq simulation
    try:
        stdout, stderr, compile_output = compile_with_groq_analysis(language, runnable_code, stdin)
        return {
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "execution_method": "groq_simulation"
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"All compilation methods failed (Codex, Judge0, Remote, Local, Groq). Last error: {str(e)}",
            "compile_output": "",
            "execution_method": "failed"
        }

@router.post("/compile/judge0")
async def compile_with_judge0(
    code: str = Form(...),
    language: str = Form(...),
    inputs: str = Form("")
):
    """Explicitly use Judge0 API for code execution."""
    try:
        if not is_language_supported(language):
            return {
                "stdout": "",
                "stderr": f"Language '{language}' not supported by Judge0",
                "compile_output": f"Supported languages: {', '.join(get_language_info()['supported_languages'])}",
                "execution_method": "error"
            }
        
        runnable_code = wrap_runnable_code(language, code)
        stdout, stderr, compile_output = await execute_with_judge0(language, runnable_code, inputs)
        
        return {
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "execution_method": "judge0",
            "language_supported": True
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "compile_output": "",
            "execution_method": "judge0_error",
            "language_supported": is_language_supported(language)
        }

@router.get("/compile/judge0/info")
async def get_judge0_info():
    """Get information about Judge0 service."""
    return get_language_info()
