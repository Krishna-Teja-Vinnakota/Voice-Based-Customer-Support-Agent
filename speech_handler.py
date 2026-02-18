"""
Speech Handler - Speech-to-Text and Text-to-Speech
Uses OpenAI Whisper for STT and Google Cloud TTS for TTS
"""

import os
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SpeechHandler:
    def __init__(self, text_mode=False):
        """
        Initialize speech handler
        Args:
            text_mode: If True, skip audio initialization
        """
        self.text_mode = text_mode
        self.whisper_model = None
        self.tts_client = None
        
        if not text_mode:
            # Initialize Whisper for Speech-to-Text
            self._init_whisper()
            
            # Initialize Google TTS for Text-to-Speech
            self._init_google_tts()
    
    def _init_whisper(self):
        """Initialize Whisper STT"""
        try:
            import whisper
            print("[Speech] Loading Whisper model (this may take a moment)...")

            # Model Options: tiny, base, small, medium, large
            self.whisper_model = whisper.load_model("small")
            print("[Speech] Whisper model loaded successfully")
        except Exception as e:
            print(f"[Speech] Warning: Could not load Whisper: {e}")
            print("[Speech] Speech-to-text will not be available")
    
    def _init_google_tts(self):
        """Initialize Google Cloud TTS"""
        try:
            from google.cloud import texttospeech
            
            # Check for credentials
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                self.tts_client = texttospeech.TextToSpeechClient()
                print("[Speech] Google Cloud TTS initialized successfully")
            else:
                print("[Speech] Warning: Google Cloud credentials not found")
                print("[Speech] Set GOOGLE_APPLICATION_CREDENTIALS in .env")
                print("[Speech] Text-to-speech will fall back to text output")
        except Exception as e:
            print(f"[Speech] Warning: Could not initialize Google TTS: {e}")
            print("[Speech] Text-to-speech will fall back to text output")
    
    def speech_to_text(self, audio_file_path):
        """
        Convert speech to text using Whisper
        Args:
            audio_file_path: Path to audio file
        Returns:
            Transcribed text
        """
        if self.text_mode or not self.whisper_model:
            # In text mode, get input from user
            return input("\nYou: ").strip()
        
        try:
            print(f"[Speech] Transcribing audio from {audio_file_path}...")
            result = self.whisper_model.transcribe(audio_file_path)
            text = result["text"].strip()
            print(f"[Speech] Transcribed: {text}")
            return text
        except Exception as e:
            print(f"[Speech] Error in speech-to-text: {e}")
            return ""
    
    def text_to_speech(self, text, output_path="output.mp3"):
        """
        Convert text to speech using Google Cloud TTS
        Args:
            text: Text to convert
            output_path: Where to save the audio file
        Returns:
            Path to generated audio file or None
        """
        if self.text_mode or not self.tts_client:
            # Fall back to text output
            print(f"\nAgent: {text}")
            return None
        
        try:
            from google.cloud import texttospeech
            
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-F",  # Female neural voice
                # Other good options:
                # "en-US-Neural2-J" - Male
                # "en-US-Neural2-C" - Female
                # "en-US-Wavenet-F" - Female Wavenet
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.3,  # Normal speed
                pitch=0.0,  # Normal pitch
            )
            
            # Perform the text-to-speech request
            print(f"[Speech] Generating speech with Google TTS...")
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Write the response to the output file
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            
            print(f"[Speech] Audio saved to {output_path}")
            print(f"[Agent Says]: {text}")
            return output_path
            
        except Exception as e:
            print(f"[Speech] Error in text-to-speech: {e}")
            print(f"[Agent Says]: {text}")
            return None
    
    def record_audio(self, duration=5, sample_rate=16000, output_file="input.wav"):
        """
        Record audio from microphone
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            output_file: Where to save the recording
        Returns:
            Path to recorded audio file
        """
        if self.text_mode:
            return None
        
        try:
            import sounddevice as sd
            import soundfile as sf
            
            print(f"\n[Speech] 🎤 Recording for {duration} seconds... Speak now!")
            print("[Speech] " + "="*50)
            
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            
            # Save to file
            sf.write(output_file, audio, sample_rate)
            print(f"[Speech] ✓ Recording saved to {output_file}")
            return output_file
            
        except Exception as e:
            print(f"[Speech] Error recording audio: {e}")
            return None
    
    def play_audio(self, audio_file_path):
        """
        Play audio file
        Args:
            audio_file_path: Path to audio file to play
        """
        if self.text_mode:
            return
        
        try:
            import sounddevice as sd
            import soundfile as sf
            
            data, sample_rate = sf.read(audio_file_path)
            print(f"[Speech] 🔊 Playing audio...")
            sd.play(data, sample_rate)
            sd.wait()
            print(f"[Speech] ✓ Playback complete")
            
        except Exception as e:
            print(f"[Speech] Error playing audio: {e}")


# For testing
if __name__ == "__main__":
    print("Testing Speech Handler with Google TTS and Whisper...")
    print("\nNote: This requires:")
    print("1. GOOGLE_APPLICATION_CREDENTIALS set in .env")
    print("2. Whisper installed (pip install openai-whisper)")
    print("3. Audio device available\n")
    
    # Test in text mode (safe for testing)
    speech = SpeechHandler(text_mode=True)
    
    # Test TTS
    speech.text_to_speech("Hello! This is a test of Google Cloud Text to Speech.")
    
    print("\n✓ Test complete!")
