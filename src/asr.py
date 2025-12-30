"""
ASR Module - Automatic Speech Recognition using Whisper
Converts spoken English to text locally
"""
import whisper
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
from typing import Optional


class ASRModule:
    def __init__(self, model_name: str = "base"):
        """
        Initialize ASR module with Whisper model
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        self.sample_rate = 16000
        
    def record_audio(self, duration: int = 5, sample_rate: Optional[int] = None) -> np.ndarray:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate (defaults to 16000 Hz)
            
        Returns:
            Audio data as numpy array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        print(f"Recording for {duration} seconds...")
        audio = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='float32')
        sd.wait()
        print("Recording complete.")
        return audio.flatten()
    
    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio as numpy array
            
        Returns:
            Transcribed text
        """
        # Whisper expects audio in float32 format
        result = self.model.transcribe(audio_data, language="en")
        return result["text"].strip()
    
    def transcribe_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        result = self.model.transcribe(audio_file_path, language="en")
        return result["text"].strip()
    
    def record_and_transcribe(self, duration: int = 5) -> str:
        """
        Record audio and transcribe it
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        audio = self.record_audio(duration)
        return self.transcribe_audio(audio)


if __name__ == "__main__":
    # Test ASR module
    asr = ASRModule(model_name="base")
    
    print("\nTesting ASR...")
    print("Speak now!")
    text = asr.record_and_transcribe(duration=5)
    print(f"Transcribed: {text}")
