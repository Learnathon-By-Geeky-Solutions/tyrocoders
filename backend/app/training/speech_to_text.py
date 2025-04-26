import sounddevice as sd
import numpy as np
import wave
import threading
import requests
import time
import os
import logging
from pynput import keyboard
from core.config import settings
from core.logger import logger
from typing import Optional, List, Union

class AudioRecorder:
    def __init__(self, 
                 sample_rate: int = 16000, 
                 audio_filename: str = "recorded.wav"):
        self.ASSEMBLYAI_API_KEY = settings.ASSEMBLYAI_API_KEY
        self.SAMPLE_RATE = sample_rate
        self.AUDIO_FILENAME = audio_filename
        
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_data: List[np.ndarray] = []
        self.key_pressed = False

    def record_audio(self) -> None:
        """Record audio from microphone"""
        self.audio_data = []
        logger.info("Recording started. Press 'm' again to stop.")
        
        with sd.InputStream(samplerate=self.SAMPLE_RATE, channels=1, dtype='int16') as stream:
            while self.is_recording:
                frame, _ = stream.read(1024)
                self.audio_data.append(frame.copy())

    def toggle_recording(self) -> None:
        """Toggle audio recording on and off"""
        if self.key_pressed:
            return
        
        self.key_pressed = True
        self.is_recording = not self.is_recording
        
        if self.is_recording:
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()
        else:
            self._stop_recording()

    def _stop_recording(self) -> None:
        """Stop recording and process audio"""
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
            
            if self.save_audio_to_wav_file():
                transcript = self.transcribe_with_assemblyai(self.AUDIO_FILENAME)
                logger.info(f"Transcript:\n{transcript}")
            else:
                logger.error("Failed to save audio file")

    def save_audio_to_wav_file(self) -> bool:
        """Save audio data to WAV file"""
        if not self.audio_data:
            logger.error("No audio data to save")
            return False
        
        try:
            audio_np = np.concatenate(self.audio_data)
            max_amplitude = np.max(np.abs(audio_np))
            
            if max_amplitude < 100:
                logger.warning(f"Audio is very quiet (max amplitude: {max_amplitude})")
            
            with wave.open(self.AUDIO_FILENAME, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(audio_np.tobytes())
            
            file_size = os.path.getsize(self.AUDIO_FILENAME)
            logger.info(f"Recording saved to {self.AUDIO_FILENAME} "
                        f"({len(audio_np)} samples, {file_size} bytes)")
            return True
        
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False

    def transcribe_with_assemblyai(self, file_path: str) -> Union[str, None]:
        """Transcribe audio using AssemblyAI"""
        try:
            # Validate file
            self._validate_audio_file(file_path)
            
            # Upload audio
            audio_url = self._upload_audio_file(file_path)
            
            # Start transcription
            transcript_id = self._start_transcription(audio_url)
            
            # Poll for transcription
            transcript = self._poll_transcription(transcript_id)
            
            # Delete original file after successful transcription
            self.delete_audio_file(file_path)
            
            return transcript
        
        except ValueError as e:
            logger.error(str(e))
            return str(e)

    def _validate_audio_file(self, file_path: str) -> None:
        """Validate audio file properties"""
        if not os.path.exists(file_path):
            raise ValueError("Audio file not found")
        
        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            raise ValueError("Audio file too small, likely no audio recorded")
        
        try:
            with wave.open(file_path, 'rb') as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                    raise ValueError("Invalid WAV format - must be mono with 16-bit samples")
                
                if wf.getnframes() < 100:
                    raise ValueError("WAV file contains too few frames to process")
        except Exception as e:
            raise ValueError(f"Error validating WAV file: {e}")

    def _upload_audio_file(self, file_path: str) -> str:
        """Upload audio file to AssemblyAI"""
        base_url = "https://api.assemblyai.com/v2"
        headers = {"authorization": self.ASSEMBLYAI_API_KEY}
        
        logger.info("Uploading audio file")
        upload_url = f"{base_url}/upload"
        
        with open(file_path, "rb") as audio_file:
            upload_response = requests.post(
                upload_url,
                headers=headers,
                data=audio_file
            )
        
        if upload_response.status_code != 200:
            raise ValueError(f"Upload failed: {upload_response.text}")
        
        logger.info("Upload successful")
        return upload_response.json()["upload_url"]

    def _start_transcription(self, audio_url: str) -> str:
        """Start transcription process"""
        base_url = "https://api.assemblyai.com/v2"
        headers = {
            "authorization": self.ASSEMBLYAI_API_KEY,
            "content-type": "application/json"
        }
        
        logger.info("Starting transcription")
        transcript_endpoint = f"{base_url}/transcript"
        
        json_body = {
            "audio_url": audio_url,
            "language_code": "en"
        }
        
        response = requests.post(
            transcript_endpoint,
            json=json_body,
            headers=headers
        )
        
        if response.status_code != 200:
            raise ValueError(f"Transcription request failed: {response.text}")
        
        transcript_id = response.json()["id"]
        logger.info(f"Transcription started with ID: {transcript_id}")
        return transcript_id

    def _poll_transcription(self, transcript_id: str, max_attempts: int = 30) -> str:
        """Poll for transcription completion"""
        base_url = "https://api.assemblyai.com/v2"
        headers = {"authorization": self.ASSEMBLYAI_API_KEY}
        polling_endpoint = f"{base_url}/transcript/{transcript_id}"
        
        for attempt in range(max_attempts):
            try:
                polling_response = requests.get(polling_endpoint, headers=headers)
                
                if polling_response.status_code != 200:
                    raise ValueError(f"Polling failed: {polling_response.text}")
                
                transcription_result = polling_response.json()
                status = transcription_result["status"]
                
                if status == "completed":
                    if not transcription_result.get("text"):
                        raise ValueError("No speech detected in the audio")
                    return transcription_result["text"]
                
                elif status == "error":
                    raise ValueError(f"Transcription error: {transcription_result.get('error', 'Unknown')}")
                
                logger.info(f"Transcription status: {status}")
                time.sleep(2)
            
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ValueError(f"Transcription failed after {max_attempts} attempts: {e}")
        
        raise ValueError("Transcription timed out")

    def delete_audio_file(self, file_path: str) -> None:
        """Delete audio file"""
        try:
            os.remove(file_path)
            logger.info("Audio file deleted")
        except Exception as e:
            logger.error(f"Error deleting audio file: {e}")

def main():
    recorder = AudioRecorder()
    
    def on_press(key):
        try:
            if key.char == 'm':  # Start/stop recording when 'm' is pressed
                recorder.toggle_recording()
            elif key == keyboard.Key.esc:  # Stop the listener when 'esc' is pressed
                return False
        except AttributeError:
            pass

    def on_release(key):
        try:
            if key.char == 'm':
                recorder.key_pressed = False
        except AttributeError:
            pass

    # Set up keyboard listener
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )

    # Start the listener
    listener.start()
    logger.info("Press 'm' to start/stop recording. Press 'esc' to quit.")
    listener.join()

if __name__ == "__main__":
    main()