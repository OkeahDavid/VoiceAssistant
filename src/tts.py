"""
TTS Module - Text-to-Speech
Converts text to spoken English locally using pyttsx3
"""
import pyttsx3
from typing import Optional


class TTSModule:
    """
    TTS module using pyttsx3 (no deep learning, faster initialization)
    """
    def __init__(self):
        self.engine = pyttsx3.init()
        
        # Set properties
        self.engine.setProperty('rate', 150)  # Speed
        self.engine.setProperty('volume', 0.9)  # Volume
        
    def text_to_speech(self, text: str, output_file: Optional[str] = None, play: bool = True) -> None:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            output_file: Optional file path to save audio
            play: Whether to play the audio
        """
        if not text:
            return
            
        if output_file:
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
        
        if play:
            self.engine.say(text)
            self.engine.runAndWait()


if __name__ == "__main__":
    # Test TTS module
    print("Testing TTS...")
    tts = TTSModule()
    tts.text_to_speech("Hello! I am your voice assistant. How can I help you today?")
