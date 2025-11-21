import sounddevice as sd
import numpy as np
import keyboard
from scipy.io.wavfile import write
import os


def record_audio(question_id, user_name):
    fs = 44100  # Sample rate
    channels = 1  # Mono
    output_dir = os.path.join(os.path.dirname(__file__), "audio")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"answer_{user_name}_{question_id}.wav")
    print("Recording... Press Enter to stop.")
    frames = []

    def callback(indata, frames_count, time, status):
        frames.append(indata.copy())

    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
            keyboard.wait("enter")
        print("Recording finished.")
        audio_data = np.concatenate(frames, axis=0)
        write(output_file, fs, audio_data)
        print(f"Saved as {output_file}")
        return output_file
    except Exception as e:
        print(f"Error during recording: {e}")
        return None
