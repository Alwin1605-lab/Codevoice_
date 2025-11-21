import whisper
import speech_recognition as sr
import os
import wave
from pydub import AudioSegment
import tempfile

def speech_to_txt(path):
    """
    Convert speech to text using Whisper with SpeechRecognition fallback
    """
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Check if file exists
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Audio file not found: {abs_path}")
        
        # Check if file is not empty
        file_size = os.path.getsize(abs_path)
        if file_size == 0:
            raise ValueError("Audio file is empty")
        
        if file_size < 100:  # Very small file, likely corrupted
            raise ValueError(f"Audio file too small ({file_size} bytes), likely corrupted")
        
        print(f"🎤 Starting transcription process...")
        print(f"   File: {abs_path}")
        print(f"   Size: {file_size} bytes")
        
        # Method 1: Convert to proper format first using pydub, then use Whisper
        try:
            print("🔄 Method 1: Convert to WAV and use Whisper...")
            
            # Load audio with pydub (handles many formats)
            audio = AudioSegment.from_file(abs_path)
            
            # Convert to proper WAV format
            temp_wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            audio.export(temp_wav_file.name, format="wav", parameters=["-ar", "16000", "-ac", "1"])
            
            print(f"🔄 Converted to proper WAV format: {temp_wav_file.name}")
            
            # Load Whisper model - use tiny.en for faster processing
            model = whisper.load_model("tiny.en")
            
            print(f"🎵 Transcribing with Whisper...")
            result = model.transcribe(
                temp_wav_file.name, 
                language="en",
                verbose=False,
                fp16=False,  # CPU compatibility
                temperature=0.0,
                condition_on_previous_text=False
            )
            
            transcript = result['text'].strip()
            
            # Clean up temp file
            try:
                os.unlink(temp_wav_file.name)
            except:
                pass
            
            if not transcript:
                raise ValueError("Whisper returned empty transcript")
            
            print(f"✅ Whisper success - Full transcript:")
            print("="*80)
            print("🎯 TRANSCRIBED CONTENT:")
            print(f"📝 '{transcript}'")
            print("="*80)
            return transcript
            
        except Exception as whisper_error:
            print(f"❌ Whisper with conversion failed: {whisper_error}")
            print("🔄 Trying SpeechRecognition fallback...")
            
            # Method 2: Use SpeechRecognition with format conversion
            try:
                recognizer = sr.Recognizer()
                
                # Convert using pydub to proper format for SpeechRecognition
                audio = AudioSegment.from_file(abs_path)
                temp_wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                audio.export(temp_wav_file.name, format="wav")
                
                # Perform speech recognition
                with sr.AudioFile(temp_wav_file.name) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)
                
                # Try Google Speech Recognition
                transcript = recognizer.recognize_google(audio_data, language='en-US')
                
                # Clean up temp file
                try:
                    os.unlink(temp_wav_file.name)
                except:
                    pass
                
                if not transcript.strip():
                    raise ValueError("Google API returned empty transcript")
                
                print(f"✅ Google Speech Recognition success - Full transcript:")
                print("="*80)
                print("🎯 TRANSCRIBED CONTENT (via Google API):")
                print(f"📝 '{transcript.strip()}'")
                print("="*80)
                return transcript.strip()
                
            except Exception as sr_error:
                print(f"❌ SpeechRecognition failed: {sr_error}")
                
                # Method 3: Basic audio validation with informative message
                try:
                    print("🔄 Method 3: Audio validation...")
                    
                    # Try to get duration using pydub
                    audio = AudioSegment.from_file(abs_path)
                    duration = len(audio) / 1000.0  # Convert to seconds
                    
                    print(f"📊 Audio info: {duration:.2f}s duration")
                    
                    if duration < 0.5:
                        return "[Audio too short - please record for at least 1 second]"
                    elif duration > 60:
                        return "[Audio too long - please keep answers under 60 seconds]"
                    else:
                        return f"[Audio file processed ({duration:.1f}s) but transcription services unavailable. Please provide a text answer as backup.]"
                
                except Exception as basic_error:
                    print(f"❌ Audio validation failed: {basic_error}")
                    return f"[Audio file error: {str(basic_error)}]"
        
    except Exception as e:
        print(f"❌ Fatal speech-to-text error: {e}")
        return f"[Transcription completely failed: {str(e)}]"