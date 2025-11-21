from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Multi-language transcription support
SUPPORTED_LANGUAGES = {
    "en": "english",
    "es": "spanish", 
    "fr": "french",
    "de": "german",
    "it": "italian",
    "pt": "portuguese",
    "ru": "russian",
    "ja": "japanese",
    "ko": "korean",
    "zh": "chinese"
}

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)

def normalize_spoken_symbols_multilang(text: str, language: str = "en") -> str:
    """
    Multi-language symbol normalization
    """
    if not text:
        return text

    # English patterns (existing)
    en_patterns = [
        (r"\bopen\s+parenthesis\b", "("),
        (r"\bclose\s+parenthesis\b", ")"),
        (r"\bopen\s+bracket\b", "["),
        (r"\bclose\s+bracket\b", "]"),
        (r"\bopen\s+brace\b", "{"),
        (r"\bclose\s+brace\b", "}"),
        (r"\bplus\b", "+"),
        (r"\bminus\b", "-"),
        (r"\bequals\b", "="),
        (r"\bsemicolon\b", ";"),
        (r"\bcolon\b", ":"),
        (r"\bcomma\b", ","),
        (r"\bperiod\b|\bdot\b", "."),
        (r"\bnew\s*line\b", "\n"),
        (r"\btab\b", "\t"),
        (r"\bspace\b", " ")
    ]
    
    # Spanish patterns
    es_patterns = [
        (r"\babrir\s+paréntesis\b", "("),
        (r"\bcerrar\s+paréntesis\b", ")"),
        (r"\babrir\s+corchete\b", "["),
        (r"\bcerrar\s+corchete\b", "]"),
        (r"\babrir\s+llave\b", "{"),
        (r"\bcerrar\s+llave\b", "}"),
        (r"\bmás\b", "+"),
        (r"\bmenos\b", "-"),
        (r"\bigual\b", "="),
        (r"\bpunto\s+y\s+coma\b", ";"),
        (r"\bdos\s+puntos\b", ":"),
        (r"\bcoma\b", ","),
        (r"\bpunto\b", "."),
        (r"\bnueva\s+línea\b", "\n"),
        (r"\btabulación\b", "\t"),
        (r"\bespacio\b", " ")
    ]
    
    # French patterns
    fr_patterns = [
        (r"\bouvrir\s+parenthèse\b", "("),
        (r"\bfermer\s+parenthèse\b", ")"),
        (r"\bouvrir\s+crochet\b", "["),
        (r"\bfermer\s+crochet\b", "]"),
        (r"\bouvrir\s+accolade\b", "{"),
        (r"\bfermer\s+accolade\b", "}"),
        (r"\bplus\b", "+"),
        (r"\bmoins\b", "-"),
        (r"\bégal\b", "="),
        (r"\bpoint\s+virgule\b", ";"),
        (r"\bdeux\s+points\b", ":"),
        (r"\bvirgule\b", ","),
        (r"\bpoint\b", "."),
        (r"\bnouvelle\s+ligne\b", "\n"),
        (r"\btabulation\b", "\t"),
        (r"\bespace\b", " ")
    ]
    
    # German patterns
    de_patterns = [
        (r"\böffnende\s+klammer\b", "("),
        (r"\bschließende\s+klammer\b", ")"),
        (r"\böffnende\s+eckige\s+klammer\b", "["),
        (r"\bschließende\s+eckige\s+klammer\b", "]"),
        (r"\böffnende\s+geschweifte\s+klammer\b", "{"),
        (r"\bschließende\s+geschweifte\s+klammer\b", "}"),
        (r"\bplus\b", "+"),
        (r"\bminus\b", "-"),
        (r"\bgleich\b", "="),
        (r"\bsemikolon\b", ";"),
        (r"\bdoppelpunkt\b", ":"),
        (r"\bkomma\b", ","),
        (r"\bpunkt\b", "."),
        (r"\bneue\s+zeile\b", "\n"),
        (r"\btabulator\b", "\t"),
        (r"\bleerzeichen\b", " ")
    ]
    
    patterns_map = {
        "en": en_patterns,
        "es": es_patterns,
        "fr": fr_patterns,
        "de": de_patterns
    }
    
    patterns = patterns_map.get(language, en_patterns)
    
    out = text
    for pattern, repl in patterns:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    
    # Common cleanup regardless of language
    out = re.sub(r"\s*->\s*", " -> ", out)
    out = re.sub(r"([\(\[\{])\s+", r"\1", out)
    out = re.sub(r"\s+([\)\]\}])", r"\1", out)
    out = re.sub(r"\s+([,:;\.\?\!])", r"\1", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    
    return out.strip()

@router.post("/transcribe-multilang/")
async def transcribe_audio_multilang(
    file: UploadFile = File(...),
    target_language: str = Form("en"),
    source_language: str = Form("auto")
):
    """
    Multi-language transcription with automatic language detection
    """
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, file.filename)
    
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    
    try:
        client = get_groq_client()
        
        with open(audio_path, "rb") as f:
            # Use Groq's transcription with language specification
            translation = client.audio.translations.create(
                file=(audio_path, f.read()),
                model=os.getenv("GROQ_TRANSCRIBE_MODEL", "whisper-large-v3"),
                prompt=f"""
You are transcribing programming-related speech. 
The speaker is using {SUPPORTED_LANGUAGES.get(source_language, 'multiple languages')} to describe code.
Focus on technical terms, programming keywords, and code structure.
Transcribe exactly what is said, including programming symbols and commands.
""",
                response_format="json",
                temperature=0.0
            )
        
        transcript = translation.text
        
        # Apply multi-language symbol normalization
        if os.getenv("ENABLE_SYMBOL_NORMALIZATION", "true").lower() in ["true", "1", "yes"]:
            transcript = normalize_spoken_symbols_multilang(transcript, target_language)
        
        return JSONResponse({
            "transcript": transcript,
            "detected_language": source_language,
            "target_language": target_language
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)})

@router.post("/translate-commands/")
async def translate_voice_commands(
    command: str = Form(...),
    from_language: str = Form("en"),
    to_language: str = Form("en")
):
    """
    Translate voice commands between languages
    """
    try:
        client = get_groq_client()
        
        prompt = f"""
Translate this voice command from {SUPPORTED_LANGUAGES.get(from_language, from_language)} to {SUPPORTED_LANGUAGES.get(to_language, to_language)}.
Keep programming terminology and technical terms consistent.

Command: {command}

Provide only the translated command, nothing else.
"""

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        translated_command = response.choices[0].message.content.strip()
        return {
            "original": command,
            "translated": translated_command,
            "from_language": from_language,
            "to_language": to_language
        }
        
    except Exception as e:
        return {"error": f"Translation failed: {str(e)}"}