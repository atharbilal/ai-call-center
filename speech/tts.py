"""
Text-to-Speech module.
Primary: ElevenLabs (most human-like voice)
Fallback: Google Cloud TTS (supports all Indian languages)
"""

import os
import asyncio
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID_EN = os.getenv("ELEVENLABS_VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
ELEVENLABS_VOICE_ID_HI = os.getenv("ELEVENLABS_VOICE_ID_HI", "21m00Tcm4TlvDq8ikWAM")

# Map language to voice IDs and Google TTS codes
LANGUAGE_CONFIG = {
    "english":   {"google_code": "en-IN", "google_name": "en-IN-Neural2-A", "gender": "FEMALE"},
    "hindi":     {"google_code": "hi-IN", "google_name": "hi-IN-Neural2-A", "gender": "FEMALE"},
    "tamil":     {"google_code": "ta-IN", "google_name": "ta-IN-Neural2-A", "gender": "FEMALE"},
    "telugu":    {"google_code": "te-IN", "google_name": "te-IN-Standard-A", "gender": "FEMALE"},
    "bengali":   {"google_code": "bn-IN", "google_name": "bn-IN-Neural2-A", "gender": "FEMALE"},
    "marathi":   {"google_code": "mr-IN", "google_name": "mr-IN-Neural2-A", "gender": "FEMALE"},
    "kannada":   {"google_code": "kn-IN", "google_name": "kn-IN-Neural2-A", "gender": "FEMALE"},
    "malayalam": {"google_code": "ml-IN", "google_name": "ml-IN-Neural2-A", "gender": "FEMALE"},
    "gujarati":  {"google_code": "gu-IN", "google_name": "gu-IN-Neural2-A", "gender": "FEMALE"},
    "punjabi":   {"google_code": "pa-IN", "google_name": "pa-IN-Standard-A", "gender": "FEMALE"},
}

class UniversalTTS:
    """
    Universal Text-to-Speech supporting multiple providers.
    Automatically chooses free/paid options based on available API keys.
    Usage:
        tts = UniversalTTS()
        audio_bytes = await tts.synthesize_speech("Hello, how are you?", language="english")
    """
    
    def __init__(self):
        # Initialize API keys from environment
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.google_key = os.getenv("GOOGLE_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.azure_key = os.getenv("AZURE_SPEECH_KEY", "")
        self.azure_region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        # Determine which provider to use
        if self.elevenlabs_key and self.elevenlabs_key != "your_elevenlabs_api_key_here":
            self.provider = "elevenlabs"
            print("Using ElevenLabs TTS (Paid)")
        elif self.google_key and self.google_key != "your_google_api_key_here":
            self.provider = "google"
            print("Using Google TTS (Free)")
        elif self.openai_key and self.openai_key != "your_openai_api_key_here":
            self.provider = "openai"
            print("Using OpenAI TTS (Free Credits)")
        elif self.azure_key and self.azure_key != "your_azure_speech_key_here":
            self.provider = "azure"
            print("Using Azure TTS (Free)")
        else:
            self.provider = "mock"
            print("WARNING: Using mock TTS. Set any TTS API key for real speech synthesis.")
    
    async def synthesize_speech(self, text: str, language: str = "english") -> bytes:
        """
        Convert text to speech audio bytes (MP3).
        
        Args:
            text: Text to speak
            language: Language code
        
        Returns:
            MP3 audio bytes
        """
        # For non-English/Hindi, use Google TTS (ElevenLabs doesn't support Indian languages well)
        if language not in ["english", "hindi"] or not self.api_key:
            return await self._google_tts(text, language)
        
        try:
            voice_id = ELEVENLABS_VOICE_ID_EN if language == "english" else ELEVENLABS_VOICE_ID_HI
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.3,
                            "use_speaker_boost": True
                        }
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"ElevenLabs error {response.status_code}: {response.text}")
                    return await self._google_tts(text, language)
                    
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}. Falling back to Google TTS.")
            return await self._google_tts(text, language)
    
    async def _google_tts(self, text: str, language: str = "english") -> bytes:
        """
        Google Cloud TTS fallback.
        Supports all Indian languages with Neural2 voices.
        """
        try:
            from google.cloud import texttospeech
            
            config = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["english"])
            
            client = texttospeech.TextToSpeechAsyncClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=config["google_code"],
                name=config["google_name"],
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.95,
                pitch=0.0,
            )
            
            response = await client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            return response.audio_content
            
        except ImportError:
            print("google-cloud-texttospeech not installed. Returning silent audio.")
            return self._silent_audio()
        except Exception as e:
            print(f"Google TTS error: {e}")
            return self._silent_audio()
    
    def _silent_audio(self) -> bytes:
        """Returns minimal silent MP3 for testing."""
        # Minimal valid MP3 header (silence)
        return bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
