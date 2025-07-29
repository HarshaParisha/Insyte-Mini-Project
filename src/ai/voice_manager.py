"""
Insyte AI - Voice Manager
Handles offline voice transcription using OpenAI Whisper for productivity features.
"""

import whisper
import numpy as np
import soundfile as sf
import logging
from typing import Optional, Dict, Any
import os

class VoiceManager:
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Voice Manager with Whisper model.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = None
        self.logger = logging.getLogger(__name__)
        
    def load_model(self) -> bool:
        """
        Load the Whisper model for transcription.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.logger.info("Whisper model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {str(e)}")
            return False
    
    def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code for transcription (e.g., 'en' for English)
            
        Returns:
            dict: Transcription result with text, segments, and metadata
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded. Call load_model() first.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            self.logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True
            )
            
            # Extract relevant information
            transcription = {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "duration": result.get("duration", 0),
                "confidence": self._calculate_confidence(result["segments"])
            }
            
            self.logger.info("Transcription completed successfully")
            return transcription
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            return {
                "text": "",
                "language": language,
                "segments": [],
                "duration": 0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def transcribe_numpy_array(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcribe audio from numpy array.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio data
            
        Returns:
            dict: Transcription result
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded. Call load_model() first.")
        
        try:
            # Whisper expects 16kHz mono audio
            if sample_rate != 16000:
                # Simple resampling (for production, use librosa.resample)
                self.logger.warning(f"Audio sample rate is {sample_rate}Hz, expected 16kHz")
            
            # Normalize audio data to [-1, 1] range
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            result = self.model.transcribe(audio_data)
            
            return {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "confidence": self._calculate_confidence(result["segments"])
            }
            
        except Exception as e:
            self.logger.error(f"Error transcribing numpy array: {str(e)}")
            return {
                "text": "",
                "language": "en",
                "segments": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _calculate_confidence(self, segments: list) -> float:
        """Calculate average confidence score from segments."""
        if not segments:
            return 0.0
        
        total_confidence = sum(
            segment.get("avg_logprob", 0) for segment in segments
        )
        
        # Convert log probability to confidence score (0-1)
        avg_logprob = total_confidence / len(segments)
        confidence = np.exp(avg_logprob)
        
        return min(max(confidence, 0.0), 1.0)
    
    def get_supported_formats(self) -> list:
        """Return list of supported audio formats."""
        return [
            ".wav", ".mp3", ".m4a", ".flac", ".ogg", 
            ".mp4", ".webm", ".3gp", ".aac"
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return information about the loaded Whisper model."""
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_size": self.model_size,
            "supported_formats": self.get_supported_formats(),
            "languages": list(whisper.tokenizer.LANGUAGES.keys())
        }
