from fastapi import APIRouter, Form
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)

@router.post("/explain-code/")
async def explain_code(
    code: str = Form(...),
    language: str = Form(...),
    difficulty_level: str = Form("beginner")  # beginner, intermediate, advanced
):
    """
    Learning Mode: Voice-based explanations of what a code snippet does
    """
    try:
        client = get_groq_client()
        
        difficulty_prompts = {
            "beginner": "Explain this code in very simple terms, as if teaching a complete beginner. Use everyday analogies and avoid technical jargon.",
            "intermediate": "Explain this code assuming basic programming knowledge. Include some technical details but keep it accessible.",
            "advanced": "Provide a detailed technical explanation including algorithms, time complexity, and design patterns used."
        }
        
        prompt = f"""
{difficulty_prompts.get(difficulty_level, difficulty_prompts["beginner"])}

Language: {language}
Code:
```{language}
{code}
```

Structure your explanation as:
1. What this code does (main purpose)
2. How it works (step by step)
3. Key concepts used
4. Potential improvements or common issues

Keep the explanation clear and educational.
"""

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        explanation = response.choices[0].message.content
        return {"explanation": explanation, "language": language, "level": difficulty_level}
        
    except Exception as e:
        return {"error": f"Code explanation failed: {str(e)}"}

@router.post("/analyze-error/")
async def analyze_error(
    code: str = Form(...),
    error_message: str = Form(...),
    language: str = Form(...)
):
    """
    Analyze and explain errors in a beginner-friendly way
    """
    try:
        client = get_groq_client()
        
        prompt = f"""
You are a helpful programming tutor. A student has encountered an error and needs help understanding it.

Language: {language}
Code:
```{language}
{code}
```

Error Message:
{error_message}

Please provide:
1. What the error means in simple terms
2. Why this error occurred (root cause)
3. How to fix it (step-by-step solution)
4. Tips to avoid similar errors in the future

Be encouraging and educational in your response.
"""

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content
        return {"analysis": analysis, "language": language}
        
    except Exception as e:
        return {"error": f"Error analysis failed: {str(e)}"}