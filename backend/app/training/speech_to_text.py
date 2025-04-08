import sounddevice as sd
import numpy as np
import wave
import threading
import requests
import time
import os
from pynput import keyboard
from core.config import settings

ASSEMBLYAI_API_KEY = settings.ASSEMBLYAI_API_KEY 
AUDIO_FILENAME = "recorded.wav"

is_recording = False
recording_thread = None
audio_data = []
key_pressed = False

def record_audio():
    global audio_data
    audio_data = []
    sample_rate = 16000  
    print("🎤 Recording started... Press 'm' again to stop.")
    
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
        while is_recording:
            frame, _ = stream.read(1024)
            # Make a copy to ensure we don't get reference issues
            audio_data.append(frame.copy())

def toggle_recording():
    global is_recording, recording_thread, key_pressed
    
    if key_pressed:
        return
    
    key_pressed = True
    is_recording = not is_recording
    
    if is_recording:
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
    else:
        if recording_thread and recording_thread.is_alive():
            recording_thread.join()
            if save_audio_to_wav_file():
                transcript = transcribe_with_assemblyai(AUDIO_FILENAME)
                print(f"\n📝 Transcript:\n{transcript}\n")
            else:
                print("❌ Failed to save audio file")

def on_release(key):
    global key_pressed
    try:
        if key.char == 'm':
            key_pressed = False
    except AttributeError:
        pass

def save_audio_to_wav_file():
    """Save audio data using the wave module instead of soundfile"""
    global audio_data
    
    if not audio_data or len(audio_data) == 0:
        print("❌ No audio data to save")
        return False
    
    try:
        # Convert list of arrays into a single array
        audio_np = np.concatenate(audio_data)
        
        # Check if audio is silent
        max_amplitude = np.max(np.abs(audio_np))
        if max_amplitude < 100:  # Very low volume threshold for int16
            print(f"⚠️ Warning: Audio is very quiet (max amplitude: {max_amplitude})")
        
        # Write using wave module which is more reliable for compatibility
        with wave.open(AUDIO_FILENAME, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(16000)  # 16kHz
            wf.writeframes(audio_np.tobytes())
        
        file_size = os.path.getsize(AUDIO_FILENAME)
        print(f"✅ Recording saved to {AUDIO_FILENAME} ({len(audio_np)} samples, {file_size} bytes)")
        return True
    
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return False

def transcribe_with_assemblyai(file_path):
    """Transcribe audio using AssemblyAI"""
    if not os.path.exists(file_path):
        return "❌ Audio file not found"
    
    file_size = os.path.getsize(file_path)
    if file_size < 1024:  # Less than 1KB
        return "❌ Audio file too small, likely no audio recorded"
    
    # Validate the WAV file before uploading
    try:
        with wave.open(file_path, 'rb') as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                return "❌ Invalid WAV format - must be mono with 16-bit samples"
            
            # Ensure it has some frames
            if wf.getnframes() < 100:
                return "❌ WAV file contains too few frames to process"
    except Exception as e:
        return f"❌ Error validating WAV file: {e}"
    
    base_url = "https://api.assemblyai.com/v2"
    headers = {
        "authorization": ASSEMBLYAI_API_KEY
    }
    
    # Upload audio file to AssemblyAI
    try:
        print("📤 Uploading audio file...")
        upload_url = f"{base_url}/upload"
        
        with open(file_path, "rb") as audio_file:
            upload_response = requests.post(
                upload_url,
                headers=headers,
                data=audio_file
            )
        
        if upload_response.status_code != 200:
            return f"❌ Upload failed with status code {upload_response.status_code}: {upload_response.text}"
        
        audio_url = upload_response.json()["upload_url"]
        print("✅ Upload successful")
    except Exception as e:
        return f"❌ Error uploading file: {e}"
    
    # Start transcription
    try:
        print("🔄 Starting transcription...")
        transcript_endpoint = f"{base_url}/transcript"
        
        # Set up the transcription configuration
        json_body = {
            "audio_url": audio_url,
            "language_code": "en"  # Specify English language
        }
        
        headers["content-type"] = "application/json"
        
        response = requests.post(
            transcript_endpoint,
            json=json_body,
            headers=headers
        )
        
        if response.status_code != 200:
            return f"❌ Transcription request failed: {response.status_code} - {response.text}"
        
        transcript_id = response.json()["id"]
        print(f"✅ Transcription started with ID: {transcript_id}")
    except Exception as e:
        return f"❌ Error starting transcription: {e}"
    
    # Poll for transcription completion
    print("⏳ Waiting for transcription to complete...")
    polling_endpoint = f"{base_url}/transcript/{transcript_id}"
    
    while True:
        try:
            polling_response = requests.get(polling_endpoint, headers=headers)
            
            if polling_response.status_code != 200:
                return f"❌ Polling failed with status {polling_response.status_code}: {polling_response.text}"
            
            transcription_result = polling_response.json()
            
            if transcription_result["status"] == "completed":
                # Successfully transcribed
                if not transcription_result.get("text"):
                    return "❌ No speech detected in the audio"
                
                delete_audio_file(file_path)  # Delete the audio file after successful transcription
                return transcription_result["text"]
            elif transcription_result["status"] == "error":
                return f"❌ Error: {transcription_result['error']}"
            else:
                print(f"🔄 Status: {transcription_result['status']}")
        except Exception as e:
            return f"❌ Error checking transcription status: {e}"
        
        time.sleep(2)  # Check every 2 seconds

def delete_audio_file(file_path):
    try:
        os.remove(file_path)
        print("✅ Audio file deleted.")
    except Exception as e:
        print(f"❌ Error deleting audio file: {e}")

def on_press(key):
    try:
        if key.char == 'm':  # Start/stop recording when 'm' is pressed
            toggle_recording()
        elif key == keyboard.Key.esc:  # Stop the listener when 'esc' is pressed
            return False
    except AttributeError:
        pass

# Set up keyboard listener with both press and release callbacks
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

# Start the listener
listener.start()
print("Press 'm' to start/stop recording. Press 'esc' to quit.")
listener.join()