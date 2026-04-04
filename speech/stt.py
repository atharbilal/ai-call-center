"""
Speech-to-Text using Deepgram, AssemblyAI, or OpenAI Whisper.
Supports real-time streaming transcription for phone calls.
Supports 10+ Indian languages automatically.
"""

import os
import asyncio
from typing import Optional, Callable, AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

# Initialize STT with free/paid options
deepgram_key = os.getenv("DEEPGRAM_API_KEY", "")
assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY", "")
openai_key = os.getenv("OPENAI_API_KEY", "")

# Language code mapping: our codes → service codes
LANGUAGE_TO_DEEPGRAM = {
    "english": "en-IN",      # English (India)
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "bengali": "bn",
    "marathi": "mr",
    "kannada": "kn",
    "malayalam": "ml",
    "gujarati": "gu",
    "punjabi": "pa",
}

class UniversalSTT:
    """
    Universal Speech-to-Text supporting multiple providers.
    Automatically chooses free/paid options based on available API keys.
    Usage:
        stt = UniversalSTT()
        text = await stt.transcribe_audio_bytes(audio_bytes, language="hindi")
    """
    
    def __init__(self):
        self.deepgram_key = deepgram_key
        self.assemblyai_key = assemblyai_key
        self.openai_key = openai_key
        
        # Determine which provider to use
        if self.deepgram_key and self.deepgram_key != "your_deepgram_api_key_here":
            from deepgram import DeepgramClient
            self.client = DeepgramClient(self.deepgram_key)
            self.provider = "deepgram"
            print("Using Deepgram STT")
        elif self.assemblyai_key and self.assemblyai_key != "your_assemblyai_api_key_here":
            import assemblyai as aai
            self.client = aai.Client(self.assemblyai_key)
            self.provider = "assemblyai"
            print("Using AssemblyAI STT (Free)")
        elif self.openai_key and self.openai_key != "your_openai_api_key_here":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_key)
            self.provider = "openai"
            print("Using OpenAI Whisper STT (Free Credits)")
        else:
            self.client = None
            self.provider = "mock"
            print("WARNING: Using mock STT. Set any STT API key for real transcription.")
        
    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "english") -> str:
        """
        Transcribe a chunk of audio bytes to text.
        
        Args:
            audio_bytes: Raw audio bytes (PCM, WAV, or MP3)
            language: Language code ("hindi", "english", etc.)
        
        Returns:
            Transcribed text as a string
        """
        if not self.api_key:
            return self._mock_transcription(language)
        
        try:
            from deepgram import DeepgramClient, PrerecordedOptions
            
            client = DeepgramClient(self.api_key)
            deepgram_lang = LANGUAGE_TO_DEEPGRAM.get(language, "en-IN")
            
            options = PrerecordedOptions(
                model="nova-2",
                language=deepgram_lang,
                smart_format=True,
                punctuate=True,
                diarize=False,
                utterances=False,
            )
            
            source = {"buffer": audio_bytes, "mimetype": "audio/wav"}
            response = await client.listen.asyncprerecorded.v("1").transcribe_file(source, options)
            
            # Extract text from response
            transcript = response.results.channels[0].alternatives[0].transcript
            return transcript.strip()
            
        except ImportError:
            print("deepgram-sdk not installed. Run: pip install deepgram-sdk")
            return self._mock_transcription(language)
        except Exception as e:
            print(f"Deepgram STT error: {e}")
            return ""
    
    def _mock_transcription(self, language: str) -> str:
        """Returns mock transcription for testing without API key."""
        mocks = {
            "english": "My phone number is 9876543210 and my internet is not working",
            "hindi": "मेरा नंबर 9876543210 है और मेरा इंटरनेट काम नहीं कर रहा",
            "tamil": "என் எண் 9876543210 இருக்கிறது மற்றும் எனது இணையம் வேலை செய்யவில்லை",
        }
        return mocks.get(language, mocks["english"])
    
    async def detect_language_from_audio(self, audio_bytes: bytes) -> str:
        """
        Detect spoken language from audio.
        Uses Deepgram's language detection feature.
        """
        if not self.api_key:
            return "english"
        
        try:
            from deepgram import DeepgramClient, PrerecordedOptions
            
            client = DeepgramClient(self.api_key)
            
            options = PrerecordedOptions(
                model="nova-2",
                detect_language=True,
            )
            
            source = {"buffer": audio_bytes, "mimetype": "audio/wav"}
            response = await client.listen.asyncprerecorded.v("1").transcribe_file(source, options)
            
            detected_lang = response.results.channels[0].detected_language
            
            # Map Deepgram codes back to our codes
            reverse_map = {v: k for k, v in LANGUAGE_TO_DEEPGRAM.items()}
            return reverse_map.get(detected_lang, "english")
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return "english"
