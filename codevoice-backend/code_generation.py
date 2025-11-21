from fastapi import APIRouter, Form, Request
from groq import Groq
import os
from dotenv import load_dotenv
import re
import logging

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    logging.warning("GROQ_API_KEY not set in .env file. Groq endpoints will return an error until configured.")
    client = None
else:
    client = Groq(api_key=API_KEY)

router = APIRouter()
logger = logging.getLogger(__name__)

def clean_code(text: str) -> str:
    # Prefer the largest fenced code block if multiple are present
    blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)
    if blocks:
        return max((b.strip() for b in blocks), key=len)
    # Fallback: strip surrounding backticks and whitespace
    return re.sub(r"^`+|`+$", "", text).strip()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FALLBACK_MODELS = [
    m.strip() for m in os.getenv(
        "GROQ_MODEL_FALLBACKS",
        "llama-3.1-8b-instant, deepseek-r1-distill-llama-70b, gemma2-9b-it"
    ).split(",") if m.strip()
]


def build_prompt(problem: str, language: str) -> str:
    return f"""
Write a complete, error-free {language} program for the following problem:
{problem}

Output rules:
1. Return ONLY the code.
2. Do not add explanations, headings, or Markdown backticks.
3. Ensure the code is ready to run without modification.
If the language is C, return a C function and not the main function unless required.
"""


def try_models_sequentially(prompt: str, preferred_model: str | None = None):
    if client is None:
        raise RuntimeError("GROQ_API_KEY not configured")

    models = []
    if preferred_model:
        models.append(preferred_model)
    # ensure default and fallbacks are included
    models += [DEFAULT_MODEL] + [m for m in FALLBACK_MODELS if m != DEFAULT_MODEL and m != preferred_model]

    last_error = None
    for m in models:
        try:
            logger.info(f"Trying Groq model: {m}")
            response = client.chat.completions.create(
                model=m,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.choices[0].message.content
            # update metrics if available
            try:
                from .metrics import ai_requests_total
                ai_requests_total.labels(provider='groq', model=m).inc()
            except Exception:
                pass
            return content, m
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Model {m} failed: {last_error}")
            try:
                from .metrics import ai_errors_total
                ai_errors_total.labels(provider='groq', model=m).inc()
            except Exception:
                pass
            # Continue to next model on known recoverable errors
            if "model_decommissioned" in last_error or "invalid_request_error" in last_error:
                continue
            # For other errors, continue trying next model as a best-effort
            continue
    raise RuntimeError(last_error or "Unknown error calling Groq API")


@router.post("/generate-code/")
async def generate_code(
    request: Request,
    prompt: str = Form(...),
    type: str = Form(...),
    model: str | None = Form(None)
):
    build_prompt_text = build_prompt(prompt, type)
    try:
        # Check user quota (best-effort)
        try:
            from .quota import check_and_debit_user_quota
            user_id = request.headers.get('X-User-Id')
            allowed = await check_and_debit_user_quota(user_id, cost=1)
            if not allowed:
                return {"error": "Quota exceeded", "success": False}, 429
        except Exception:
            pass

        code_text, used_model = try_models_sequentially(build_prompt_text, preferred_model=model)
        cleaned_code = clean_code(code_text)
        # metrics: record model usage
        try:
            from .metrics import ai_requests_total
            ai_requests_total.labels(provider='groq', model=used_model).inc()
        except Exception:
            pass
        return {"code": cleaned_code, "model": used_model, "success": True}
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        return {"error": f"Code generation failed: {str(e)}", "success": False}
