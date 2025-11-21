from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import pyttsx3

router = APIRouter()

@router.post("/speak/")
async def speak_text(text: str = Form(...)):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        return JSONResponse({"success": True, "message": "Spoken successfully."})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})