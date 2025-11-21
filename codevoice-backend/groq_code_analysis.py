"""
Groq-powered Code Analysis and Explanation API
Provides intelligent code explanations and error analysis based on user skill level.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from groq import Groq
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/code-analysis", tags=["code-analysis"])

class SkillLevel(str, Enum):
    """User programming skill levels for tailored explanations."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    EXPERT = "expert"

class ExplanationType(str, Enum):
    """Types of code explanations."""
    OVERVIEW = "overview"
    LINE_BY_LINE = "line_by_line"
    ALGORITHM = "algorithm"
    BEST_PRACTICES = "best_practices"
    OPTIMIZATION = "optimization"

class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis."""
    code: str
    language: str
    user_level: SkillLevel = SkillLevel.INTERMEDIATE
    explanation_type: ExplanationType = ExplanationType.OVERVIEW
    focus_areas: Optional[List[str]] = None  # e.g., ["performance", "readability", "security"]

class ErrorAnalysisRequest(BaseModel):
    """Request model for error analysis."""
    code: str
    language: str
    error_message: str
    user_level: SkillLevel = SkillLevel.INTERMEDIATE
    include_fix: bool = True

def get_groq_client():
    """Get Groq client for code analysis."""
    api_key = os.getenv("GROQ_COMPILER_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured")
    return Groq(api_key=api_key)

def get_level_specific_prompt(skill_level: SkillLevel, language: str) -> str:
    """Generate skill-level appropriate prompt instructions."""
    level_prompts = {
        SkillLevel.BEGINNER: f"""
You are explaining {language} code to a programming beginner. Use:
- Simple, non-technical language
- Define any programming terms you use
- Explain WHY things work, not just what they do
- Use analogies to real-world concepts
- Focus on fundamental concepts
- Avoid jargon and complex terminology
""",
        SkillLevel.INTERMEDIATE: f"""
You are explaining {language} code to someone with basic programming knowledge. Use:
- Clear, concise explanations
- Some technical terms with brief explanations
- Focus on how and why the code works
- Mention best practices when relevant
- Explain patterns and common techniques
""",
        SkillLevel.ADVANCED: f"""
You are explaining {language} code to an experienced programmer. Use:
- Technical precision and accuracy
- Discuss design patterns, algorithms, and architecture
- Focus on efficiency, maintainability, and scalability
- Mention alternative approaches and trade-offs
- Assume familiarity with programming concepts
""",
        SkillLevel.EXPERT: f"""
You are explaining {language} code to an expert programmer. Use:
- Highly technical analysis
- Deep dive into implementation details
- Discuss optimization opportunities and edge cases
- Compare with industry standards and best practices
- Focus on advanced concepts, performance, and architecture
"""
    }
    return level_prompts.get(skill_level, level_prompts[SkillLevel.INTERMEDIATE])

@router.post("/explain")
async def explain_code(request: CodeAnalysisRequest = Body(...)):
    """
    Generate intelligent code explanations based on user skill level.
    """
    try:
        client = get_groq_client()
        
        # Build the analysis prompt
        level_instruction = get_level_specific_prompt(request.user_level, request.language)
        
        explanation_prompts = {
            ExplanationType.OVERVIEW: "Provide a comprehensive overview of what this code does and how it works.",
            ExplanationType.LINE_BY_LINE: "Explain this code line by line, detailing what each line does.",
            ExplanationType.ALGORITHM: "Focus on the algorithm and logic flow. Explain the computational approach.",
            ExplanationType.BEST_PRACTICES: "Analyze this code for best practices, potential improvements, and code quality.",
            ExplanationType.OPTIMIZATION: "Analyze this code for performance optimization opportunities and efficiency improvements."
        }
        
        explanation_instruction = explanation_prompts.get(request.explanation_type, explanation_prompts[ExplanationType.OVERVIEW])
        
        focus_instruction = ""
        if request.focus_areas:
            focus_instruction = f"\\nPay special attention to: {', '.join(request.focus_areas)}"
        
        prompt = f"""{level_instruction}

{explanation_instruction}{focus_instruction}

Language: {request.language}
Code:
```{request.language}
{request.code}
```

Provide a clear, well-structured explanation appropriate for a {request.user_level.value} level programmer.
"""

        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt + "\n\nBe concise. Prefer bullet points. Limit to ~12 sentences."}],
            temperature=0.2,
            max_tokens=600
        )
        
        explanation = response.choices[0].message.content.strip()
        
        return JSONResponse(content={
            "explanation": explanation,
            "language": request.language,
            "user_level": request.user_level.value,
            "explanation_type": request.explanation_type.value,
            "focus_areas": request.focus_areas or [],
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code explanation failed: {str(e)}")

@router.post("/analyze-error")
async def analyze_error(request: ErrorAnalysisRequest = Body(...)):
    """
    Analyze code errors and provide explanations with optional fixes.
    """
    try:
        client = get_groq_client()
        
        level_instruction = get_level_specific_prompt(request.user_level, request.language)
        
        fix_instruction = "Also provide a corrected version of the code with clear explanations of what was fixed." if request.include_fix else ""
        
        prompt = f"""{level_instruction}

Analyze the following {request.language} code error and explain:
1. What the error means
2. Why it occurred
3. How to prevent it in the future
{fix_instruction}

Code:
```{request.language}
{request.code}
```

Error Message:
```
{request.error_message}
```

Provide a clear explanation appropriate for a {request.user_level.value} level programmer.
"""

        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt + "\n\nBe concise. Provide a short analysis and, if include_fix=true, a minimal corrected snippet."}],
            temperature=0.2,
            max_tokens=600
        )
        
        analysis = response.choices[0].message.content.strip()
        
        return JSONResponse(content={
            "analysis": analysis,
            "error_message": request.error_message,
            "language": request.language,
            "user_level": request.user_level.value,
            "include_fix": request.include_fix,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error analysis failed: {str(e)}")

@router.post("/suggest-improvements")
async def suggest_improvements(request: CodeAnalysisRequest = Body(...)):
    """
    Suggest code improvements based on user skill level.
    """
    try:
        client = get_groq_client()
        
        level_instruction = get_level_specific_prompt(request.user_level, request.language)
        
        improvement_focuses = {
            SkillLevel.BEGINNER: "readability, basic best practices, and code organization",
            SkillLevel.INTERMEDIATE: "efficiency, error handling, and maintainability", 
            SkillLevel.ADVANCED: "performance optimization, design patterns, and scalability",
            SkillLevel.EXPERT: "advanced optimizations, memory efficiency, and architectural improvements"
        }
        
        focus = improvement_focuses.get(request.user_level, improvement_focuses[SkillLevel.INTERMEDIATE])
        
        prompt = f"""{level_instruction}

Analyze this {request.language} code and suggest improvements focusing on {focus}.

Code:
```{request.language}
{request.code}
```

Provide:
1. Specific improvement suggestions
2. Explanation of why each improvement helps
3. Revised code examples where appropriate

Tailor your suggestions for a {request.user_level.value} level programmer.
"""

        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt + "\n\nBe concise. Give 5-10 targeted suggestions max."}],
            temperature=0.3,
            max_tokens=600
        )
        
        suggestions = response.choices[0].message.content.strip()
        
        return JSONResponse(content={
            "suggestions": suggestions,
            "language": request.language,
            "user_level": request.user_level.value,
            "focus_area": focus,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Code improvement analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code improvement analysis failed: {str(e)}")

@router.get("/skill-levels")
async def get_skill_levels():
    """Get available skill levels for code analysis."""
    return JSONResponse(content={
        "skill_levels": [level.value for level in SkillLevel],
        "explanation_types": [exp_type.value for exp_type in ExplanationType],
        "descriptions": {
            "beginner": "Simple explanations with analogies and basic concepts",
            "intermediate": "Clear technical explanations with some advanced concepts",
            "advanced": "Technical precision with design patterns and best practices",
            "expert": "Deep technical analysis with optimization and architecture focus"
        }
    })

@router.get("/health")
async def health_check():
    """Health check for the code analysis service."""
    try:
        client = get_groq_client()
        return JSONResponse(content={
            "status": "healthy",
            "service": "Groq Code Analysis API",
            "api_configured": True
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "unhealthy", 
            "service": "Groq Code Analysis API",
            "api_configured": False,
            "error": str(e)
        }, status_code=503)