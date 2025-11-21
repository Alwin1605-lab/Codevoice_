from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Lazily initialize Groq client to avoid requiring API key at import time.
_groq_client = None
def _get_groq_client() -> Groq:
  global _groq_client
  if _groq_client is None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
      # Defer clear message until actual use
      raise RuntimeError("GROQ_API_KEY is not set; cannot use transcription endpoint.")
    _groq_client = Groq(api_key=api_key)
  return _groq_client
TRANSCRIBE_MODEL = os.getenv("GROQ_TRANSCRIBE_MODEL", "whisper-large-v3")

# Normalization control
# Set GROQ_TRANSCRIBE_NORMALIZE=true (default) to post-process transcripts and map
# spoken symbol names to actual symbols. Alternatively, ENABLE_SYMBOL_NORMALIZATION=true
# is also recognized for backward compatibility. Set to false/0/no/off to disable.
_normalize_env = os.getenv("GROQ_TRANSCRIBE_NORMALIZE")
if _normalize_env is None:
  _normalize_env = os.getenv("ENABLE_SYMBOL_NORMALIZATION", "true")
ENABLE_SYMBOL_NORMALIZATION = str(_normalize_env).lower() in {"1", "true", "yes", "on"}


def normalize_spoken_symbols(text: str) -> str:
  """
  Convert common spoken descriptions of programming symbols into actual symbols.
  This targets phrases like "open parenthesis", "close bracket", "colon", "arrow",
  and whitespace tokens like "space", "tab", and "newline".

  The replacement is conservative and case-insensitive, only affecting standalone words/phrases.
  """
  if not text:
    return text

  # Ordered patterns: put longer/more specific phrases first to avoid partial matches.
  patterns = [
    # Arrows and comparisons (specific to general)
    (r"\bhyphen\s+angular\s+bracket\b", "->"),
    (r"\bminus\s+greater\s+than\b", "->"),
    (r"\bright\s+arrow\b", "->"),
    (r"\bdouble\s+equals\b", "=="),
    (r"\btriple\s+equals\b", "==="),
    (r"\bnot\s+equal(?:s|\s+to)?\b", "!="),
    (r"\bless\s+than\s+or\s+equal\s+to\b", "<="),
    (r"\bgreater\s+than\s+or\s+equal\s+to\b", ">="),
    (r"\bopen\s+(?:angle|angular)\s+bracket\b|\bleft\s+(?:angle|angular)\s+bracket\b", "<"),
    (r"\bclose\s+(?:angle|angular)\s+bracket\b|\bright\s+(?:angle|angular)\s+bracket\b", ">"),
    (r"\bless\s+than\b", "<"),
    (r"\bgreater\s+than\b", ">"),

    # Parentheses / Brackets / Braces
    (r"\bopen\s+parenthesis\b|\bleft\s+parenthesis\b|\bopen\s+paren\b|\bleft\s+paren\b", "("),
    (r"\bclose\s+parenthesis\b|\bright\s+parenthesis\b|\bclose\s+paren\b|\bright\s+paren\b", ")"),
    (r"\bopen\s+square\s+bracket\b|\bleft\s+square\s+bracket\b|\bopen\s+bracket\b|\bleft\s+bracket\b", "["),
    (r"\bclose\s+square\s+bracket\b|\bright\s+square\s+bracket\b|\bclose\s+bracket\b|\bright\s+bracket\b", "]"),
  # Fallback when speaker omits 'open' before 'square bracket' (e.g., 'list square bracket int close square bracket')
  # Kept after the specific open/close rules to avoid partial replacements.
  (r"\bsquare\s+bracket\b", "["),
    (r"\bopen\s+(?:curly\s+)?(?:brace|bracket)\b|\bleft\s+(?:curly\s+)?(?:brace|bracket)\b", "{"),
    (r"\bclose\s+(?:curly\s+)?(?:brace|bracket)\b|\bright\s+(?:curly\s+)?(?:brace|bracket)\b", "}"),

    # Punctuation and operators
    (r"\bsemicolon\b", ";"),
    (r"\bcolon\b", ":"),
    (r"\bcomma\b", ","),
    (r"\bellipsis\b", "..."),
    (r"\bperiod\b|\bdot\b", "."),
    (r"\bexclamation\s+(?:mark|point)\b", "!"),
    (r"\bquestion\s+mark\b", "?"),
    
    # Mathematical and assignment operators
    (r"\bplus\s+equals\b|\bplus\s+assign\b", "+="),
    (r"\bminus\s+equals\b|\bminus\s+assign\b", "-="),
    (r"\btimes\s+equals\b|\bmultiply\s+equals\b", "*="),
    (r"\bdivide\s+equals\b|\bdivision\s+equals\b", "/="),
    (r"\bmodulo\s+equals\b|\bmod\s+equals\b", "%="),
    (r"\bpower\s+equals\b|\bexponent\s+equals\b", "**="),
    (r"\bfloor\s+divide\s+equals\b", "//="),
    (r"\bplus\s+plus\b|\bincrement\b", "++"),
    (r"\bminus\s+minus\b|\bdecrement\b", "--"),
    (r"\bpower\b|\bexponent\b|\bto\s+the\s+power\s+of\b", "**"),
    (r"\bfloor\s+divide\b|\binteger\s+divide\b", "//"),
    (r"\bmodulo\b|\bmod\b|\bremainder\b", "%"),
    
    # Logical operators
    (r"\band\s+and\b|\blogical\s+and\b", "&&"),
    (r"\bor\s+or\b|\blogical\s+or\b", "||"),
    (r"\bnot\s+not\b|\blogical\s+not\b", "!!"),
    (r"\band\b", " and "),
    (r"\bor\b", " or "),
    (r"\bnot\b", " not "),
    
    # Bitwise operators
    (r"\bbitwise\s+and\b", "&"),
    (r"\bbitwise\s+or\b", "|"),
    (r"\bbitwise\s+xor\b|\bexclusive\s+or\b", "^"),
    (r"\bbitwise\s+not\b|\bcomplement\b", "~"),
    (r"\bleft\s+shift\b", "<<"),
    (r"\bright\s+shift\b", ">>"),
    
    # Basic operators
    (r"\bplus\b", "+"),
    (r"\bminus\b|\bhyphen\b|\bdash\b", "-"),
    (r"\btimes\b|\bmultiply\b|\bmultiplied\s+by\b", "*"),
    (r"\bdivide\b|\bdivided\s+by\b|\bdivision\b", "/"),
    (r"\bunderscore\b", "_"),
    (r"\bequals\b|\bequal\s+to\b|\bassign\b", "="),
    (r"\bbold\b", "bool"),
    (r"\basterisk\b|\bstar\b", "*"),
    (r"\bforward\s+slash\b|\bslash\b", "/"),
    (r"\bback\s*slash\b", r"\\"),
    (r"\bpipe\b|\bvertical\s+bar\b", "|"),
    (r"\bampersand\b", "&"),
    (r"\bpercent\b", "%"),
    (r"\bhash\b|\bpound\b|\bnumber\s+sign\b", "#"),
    (r"\bat\s+(?:symbol\b)?|\bat\b", "@"),
    (r"\btilde\b", "~"),
    (r"\bcaret\b|\bcircumflex\b", "^"),

    # Quotes
    (r"\bdouble\s+quote?s?\b|\bquotation\s+mark?s?\b", '"'),
    (r"\bsingle\s+quote?s?\b|\bapostrophe\b", "'"),
    (r"\bbacktick?s?\b", "`"),

    # Whitespace tokens
    (r"\bnew\s*line\b|\bnewline\b", "\n"),
    (r"\btab\b", "\t"),
    (r"\bspace\b", " "),
  ]

  out = text
  for pattern, repl in patterns:
    out = re.sub(pattern, repl, out, flags=re.IGNORECASE)

  # Normalize arrow spacing to a single space on both sides
  out = re.sub(r"\s*->\s*", " -> ", out)

  # Remove extra spaces around brackets and before common punctuation
  out = re.sub(r"([\(\[\{])\s+", r"\1", out)     # no space after opening
  out = re.sub(r"\s+([\)\]\}])", r"\1", out)     # no space before closing
  out = re.sub(r"\s+([,:;\.\?\!])", r"\1", out)  # no space before punctuation

  # Additional cleanup for stray commas and identifier + [ spacing
  out = re.sub(r"(?:\s*,\s*){2,}", ", ", out)  # collapse duplicate commas
  out = re.sub(r"([\(\[\{])\s*,\s*", r"\1", out)  # no comma after opening bracket
  out = re.sub(r"\s*,\s*([\)\]\}])", r"\1", out)  # no comma before closing bracket
  out = re.sub(r",\s*:\s*", ": ", out)               # no comma before colon
  out = re.sub(r",\s*->", " ->", out)                 # no comma before arrow
  out = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+\[", r"\1[", out)  # tighten X [ to X[

  # Collapse multiple spaces/tabs into one space, but keep newlines
  # Replace runs of spaces/tabs not including newlines
  out = re.sub(r"[ \t]{2,}", " ", out)

  return out.strip()

ASSISTANT_PROMPT = (
  "You are a code and math transcription assistant. "
  "Transcribe the audio as literally as possible, focusing on technical, programming, and mathematical terms. "
  "Do not hallucinate or change keywords. If you hear words like 'factorial', 'for loop', 'if statement', 'print', 'input', or numbers, transcribe them exactly as spoken. "
  "If the audio is unclear, do your best to guess the intended code or math term, but do not replace with unrelated words. "
  "Correct only obvious grammar or spelling mistakes, but never change code or math terms."
)


@router.post("/transcribe/")
async def transcribe_audio(
  file: UploadFile = File(...),
  language: str = Form("en")
):
  # Persist uploaded file and keep bytes in-memory for Groq API reuse
  audio_dir = os.path.join(os.path.dirname(__file__), "audio")
  os.makedirs(audio_dir, exist_ok=True)

  audio_bytes = await file.read()
  audio_path = os.path.join(audio_dir, file.filename)
  with open(audio_path, "wb") as f:
    f.write(audio_bytes)

  language = (language or "en").lower()
  client = _get_groq_client()

  native_text = None
  english_text = None

  try:
    # For non-English requests, first capture the native transcript (if supported)
    if language != "en":
      try:
        transcription = client.audio.transcriptions.create(
          file=(file.filename or "audio.wav", audio_bytes),
          model=TRANSCRIBE_MODEL,
          prompt=ASSISTANT_PROMPT,
          response_format="json",
          temperature=0.0,
          language=language
        )
        native_text = transcription.text
      except Exception as inner_err:
        native_text = None
        print(f"[transcription] native transcription failed: {inner_err}")

    # Always attempt English translation for downstream AI usage
    try:
      translation = client.audio.translations.create(
        file=(file.filename or "audio.wav", audio_bytes),
        model=TRANSCRIBE_MODEL,
        prompt=ASSISTANT_PROMPT,
        response_format="json",
        temperature=0.0
      )
      english_text = translation.text
    except Exception as translation_err:
      english_text = native_text
      print(f"[transcription] english translation failed: {translation_err}")

    if ENABLE_SYMBOL_NORMALIZATION and english_text:
      english_text = normalize_spoken_symbols(english_text)

    if native_text is None and english_text is not None:
      native_text = english_text

    if english_text is None:
      raise RuntimeError("Transcription failed: no transcript produced")

    return JSONResponse({
      "language": language,
      "transcript": english_text,
      "transcript_native": native_text,
      "translated_to": "en"
    })
  except Exception as e:
    return JSONResponse({"error": str(e)}, status_code=500)