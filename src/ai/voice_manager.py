"""
Insyte AI - Voice Manager
Handles offline voice transcription using OpenAI Whisper for productivity features.
"""

import whisper
import numpy as np
import logging
from typing import Optional, Dict, Any
import os

# Try to import audio libraries
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except:
    HAS_SOUNDFILE = False

try:
    import librosa
    HAS_LIBROSA = True
except:
    HAS_LIBROSA = False

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
    
    def transcribe_audio(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code for transcription (e.g., 'en' for English). 
                     If None, language will be auto-detected.
            
        Returns:
            dict: Transcription result with text, segments, and metadata
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded. Call load_model() first.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            self.logger.info(f"Transcribing audio: {audio_path}")
            
            # Check file size
            file_size = os.path.getsize(audio_path)
            self.logger.info(f"Audio file size: {file_size / (1024*1024):.2f} MB")
            
            if file_size == 0:
                raise ValueError("Audio file is empty (0 bytes)")
            
            # Load audio using available library (fallback chain)
            audio_data = None
            
            # Try librosa first (most reliable for various formats)
            if HAS_LIBROSA:
                try:
                    self.logger.info("Loading audio with librosa...")
                    audio_data, sr = librosa.load(audio_path, sr=16000, mono=True)
                    self.logger.info(f"Audio loaded: {len(audio_data)} samples at {sr}Hz")
                except Exception as e:
                    self.logger.warning(f"Librosa failed: {e}")
            
            # Try soundfile as fallback
            if audio_data is None and HAS_SOUNDFILE:
                try:
                    self.logger.info("Loading audio with soundfile...")
                    audio_data, sr = sf.read(audio_path)
                    # Convert to mono if stereo
                    if len(audio_data.shape) > 1:
                        audio_data = audio_data.mean(axis=1)
                    # Resample to 16kHz if needed
                    if sr != 16000:
                        # Simple resampling
                        audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=16000) if HAS_LIBROSA else audio_data
                    self.logger.info(f"Audio loaded: {len(audio_data)} samples")
                except Exception as e:
                    self.logger.warning(f"Soundfile failed: {e}")
            
            # If both failed, try Whisper's built-in loading (requires ffmpeg)
            if audio_data is None:
                self.logger.info("Trying Whisper's built-in audio loading (requires ffmpeg)...")
                # Whisper will attempt to use ffmpeg
                audio_data = audio_path  # Pass path directly to Whisper
            
            # Transcribe with Whisper
            transcribe_options = {
                "fp16": False,  # Use FP32 for CPU compatibility
                "verbose": False
            }
            
            # Only add language if specified
            if language:
                transcribe_options["language"] = language
            
            self.logger.info(f"Starting Whisper transcription with options: {transcribe_options}")
            
            # Pass audio data or path to Whisper
            result = self.model.transcribe(audio_data, **transcribe_options)
            
            # Extract relevant information
            transcription = {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": 0,
                "confidence": self._calculate_confidence(result.get("segments", []))
            }
            
            # Calculate duration from segments if available
            if transcription["segments"]:
                last_segment = transcription["segments"][-1]
                transcription["duration"] = last_segment.get("end", 0)
            
            self.logger.info(f"Transcription completed successfully. Text length: {len(transcription['text'])} chars")
            return transcription
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error during transcription: {error_msg}", exc_info=True)
            
            # Provide helpful error message
            if "ffmpeg" in error_msg.lower() or "WinError 2" in error_msg:
                error_msg = "FFmpeg not found. Please install FFmpeg or librosa: pip install librosa"
            
            return {
                "text": "",
                "language": language or "unknown",
                "segments": [],
                "duration": 0,
                "confidence": 0.0,
                "error": error_msg
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
