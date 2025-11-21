import pyttsx3
import threading
import queue
from typing import Dict, List, Optional
from fastapi import APIRouter, Form, HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

class VoiceNarrator:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._initialize_engine()
        self._start_worker()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to set a pleasant voice (prefer female voices for better clarity)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    self.engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 180)  # Speed of speech
            self.engine.setProperty('volume', 0.8)  # Volume level
            
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.engine = None
    
    def _start_worker(self):
        """Start the worker thread for TTS"""
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()
    
    def _speech_worker(self):
        """Worker thread to handle TTS queue"""
        while True:
            try:
                text, priority = self.speech_queue.get(timeout=1)
                if text is None:  # Shutdown signal
                    break
                
                if self.engine:
                    self.is_speaking = True
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as e:
                        print(f"TTS error: {e}")
                        # Reinitialize engine if it failed
                        try:
                            self._initialize_engine()
                        except:
                            pass
                    finally:
                        self.is_speaking = False
                
                self.speech_queue.task_done()
            except queue.Empty:
                # Timeout, continue loop
                continue
            except Exception as e:
                print(f"Error in speech worker: {e}")
                self.is_speaking = False
    
    def speak(self, text: str, priority: int = 1):
        """Add text to speech queue"""
        if self.engine:
            self.speech_queue.put((text, priority))
    
    def speak_immediately(self, text: str):
        """Speak text immediately, clearing queue"""
        if self.engine:
            # Clear existing queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.speak(text, priority=0)
    
    def stop_speaking(self):
        """Stop current speech and clear queue"""
        if self.engine:
            self.engine.stop()
            
            # Clear queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.is_speaking = False
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices"""
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for voice in voices:
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'gender': 'female' if 'female' in voice.name.lower() else 'male',
                'language': getattr(voice, 'languages', ['en-US'])[0] if hasattr(voice, 'languages') else 'en-US'
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def set_voice(self, voice_id: str):
        """Set the voice by ID"""
        if self.engine:
            self.engine.setProperty('voice', voice_id)
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.engine:
            self.engine.setProperty('rate', max(50, min(400, rate)))
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))

# Global narrator instance
narrator = VoiceNarrator()

# Voice narration templates for different scenarios
NARRATION_TEMPLATES = {
    "code_compilation": {
        "start": "Compiling your code now...",
        "success": "Compilation successful! Your code is ready to run.",
        "error": "Compilation failed. Please check the error messages.",
        "timeout": "Compilation is taking longer than expected."
    },
    "code_execution": {
        "start": "Running your program...",
        "success": "Program executed successfully!",
        "error": "Runtime error occurred during execution.",
        "finished": "Program finished execution."
    },
    "transcription": {
        "start": "Listening for voice input...",
        "processing": "Processing your voice command...",
        "success": "Voice command transcribed successfully.",
        "error": "Could not understand voice input. Please try again."
    },
    "file_operations": {
        "save_start": "Saving your file...",
        "save_success": "File saved successfully!",
        "save_error": "Error saving file. Please try again.",
        "load_start": "Loading file...",
        "load_success": "File loaded successfully!",
        "load_error": "Error loading file."
    },
    "general": {
        "welcome": "Welcome to Voice Controlled IDE! You can start coding with voice commands.",
        "help": "Say 'help' for available commands, or 'compile' to run your code.",
        "goodbye": "Thank you for using Voice Controlled IDE. Goodbye!"
    }
}

@router.post("/speak/")
async def speak_text(
    text: str = Form(...),
    priority: int = Form(1),
    immediate: bool = Form(False)
):
    """Convert text to speech"""
    try:
        # Log the request
        print(f"TTS Request: '{text[:50]}...' (immediate={immediate}, queue_size={narrator.speech_queue.qsize()})")
        
        if immediate:
            narrator.speak_immediately(text)
        else:
            narrator.speak(text, priority)
        
        return {
            "success": True,
            "message": "Text added to speech queue",
            "text": text,
            "immediate": immediate,
            "queue_size": narrator.speech_queue.qsize(),
            "is_speaking": narrator.is_speaking
        }
    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech error: {str(e)}")

@router.post("/speak-template/")
async def speak_template(
    category: str = Form(...),
    event: str = Form(...),
    custom_text: Optional[str] = Form(None)
):
    """Speak using predefined templates"""
    try:
        if category not in NARRATION_TEMPLATES:
            raise HTTPException(status_code=400, detail=f"Unknown category: {category}")
        
        template = NARRATION_TEMPLATES[category]
        
        if event not in template:
            raise HTTPException(status_code=400, detail=f"Unknown event: {event}")
        
        text = custom_text if custom_text else template[event]
        narrator.speak(text)
        
        return {
            "success": True,
            "category": category,
            "event": event,
            "text": text
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech error: {str(e)}")

@router.post("/stop-speech/")
async def stop_speech():
    """Stop current speech and clear queue"""
    try:
        narrator.stop_speaking()
        return {"success": True, "message": "Speech stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping speech: {str(e)}")

@router.get("/voice-status/")
async def get_voice_status():
    """Get current voice status"""
    return {
        "is_speaking": narrator.is_speaking,
        "queue_size": narrator.speech_queue.qsize(),
        "engine_available": narrator.engine is not None
    }

@router.get("/available-voices/")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices = narrator.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting voices: {str(e)}")

@router.post("/configure-voice/")
async def configure_voice(
    voice_id: Optional[str] = Form(None),
    rate: Optional[int] = Form(None),
    volume: Optional[float] = Form(None)
):
    """Configure voice settings"""
    try:
        if voice_id:
            narrator.set_voice(voice_id)
        
        if rate is not None:
            narrator.set_rate(rate)
        
        if volume is not None:
            narrator.set_volume(volume)
        
        return {
            "success": True,
            "message": "Voice configured successfully",
            "settings": {
                "voice_id": voice_id,
                "rate": rate,
                "volume": volume
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring voice: {str(e)}")

@router.get("/narration-templates/")
async def get_narration_templates():
    """Get all available narration templates"""
    return {"templates": NARRATION_TEMPLATES}

@router.post("/narrate-compilation/")
async def narrate_compilation(
    status: str = Form(...),  # start, success, error, timeout
    error_message: Optional[str] = Form(None)
):
    """Narrate compilation events"""
    try:
        if status == "error" and error_message:
            text = f"Compilation failed. {error_message[:100]}..."  # Limit length
        else:
            text = NARRATION_TEMPLATES["code_compilation"].get(status, "Compilation update")
        
        narrator.speak(text)
        
        return {
            "success": True,
            "status": status,
            "text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narration error: {str(e)}")

@router.post("/narrate-execution/")
async def narrate_execution(
    status: str = Form(...),  # start, success, error, finished
    output: Optional[str] = Form(None)
):
    """Narrate code execution events"""
    try:
        if status == "success" and output:
            text = f"Program executed successfully! Output: {output[:50]}..."
        elif status == "error" and output:
            text = f"Runtime error: {output[:50]}..."
        else:
            text = NARRATION_TEMPLATES["code_execution"].get(status, "Execution update")
        
        narrator.speak(text)
        
        return {
            "success": True,
            "status": status,
            "text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narration error: {str(e)}")

@router.post("/narrate-transcription/")
async def narrate_transcription(
    status: str = Form(...),  # start, processing, success, error
    transcribed_text: Optional[str] = Form(None)
):
    """Narrate transcription events"""
    try:
        if status == "success" and transcribed_text:
            text = f"Voice command received: {transcribed_text[:50]}..."
        else:
            text = NARRATION_TEMPLATES["transcription"].get(status, "Transcription update")
        
        narrator.speak(text)
        
        return {
            "success": True,
            "status": status,
            "text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narration error: {str(e)}")

# Helper function for easy integration
def narrate_event(category: str, event: str, custom_text: str = None):
    """Helper function to narrate events from other modules"""
    try:
        if category in NARRATION_TEMPLATES and event in NARRATION_TEMPLATES[category]:
            text = custom_text if custom_text else NARRATION_TEMPLATES[category][event]
            narrator.speak(text)
    except Exception as e:
        print(f"Narration error: {e}")

# Export for use in other modules
__all__ = ['router', 'narrator', 'narrate_event', 'NARRATION_TEMPLATES']