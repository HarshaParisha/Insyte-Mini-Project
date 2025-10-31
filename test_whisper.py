"""
Test script to verify Whisper voice recognition is working properly.
This script will test with a simple audio file or create a test audio.
"""

import sys
import os
sys.path.append('src')

from ai.voice_manager import VoiceManager
import numpy as np
import soundfile as sf

def create_test_audio(filename="test_audio.wav", duration=3):
    """Create a simple test audio file with a tone."""
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Create a simple sine wave at 440 Hz (A note)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    sf.write(filename, audio, sample_rate)
    print(f"✅ Created test audio file: {filename}")
    return filename

def test_whisper():
    """Test Whisper transcription."""
    print("=" * 60)
    print("🎤 Testing Whisper Voice Recognition")
    print("=" * 60)
    
    # Initialize Voice Manager
    print("\n1️⃣  Initializing Voice Manager...")
    vm = VoiceManager(model_size="tiny")  # Use tiny model for fast testing
    
    # Load model
    print("2️⃣  Loading Whisper model (this may take a moment)...")
    success = vm.load_model()
    
    if not success:
        print("❌ Failed to load Whisper model!")
        return False
    
    print("✅ Whisper model loaded successfully!")
    
    # Get model info
    info = vm.get_model_info()
    print(f"\n📊 Model Info:")
    print(f"   - Status: {info['status']}")
    print(f"   - Model Size: {info['model_size']}")
    print(f"   - Supported Languages: {len(info['languages'])} languages")
    print(f"   - Supported Formats: {', '.join(info['supported_formats'])}")
    
    # Check if there are any audio files in the current directory
    print("\n3️⃣  Looking for audio files to test...")
    audio_files = []
    for ext in ['.wav', '.mp3', '.m4a']:
        audio_files.extend([f for f in os.listdir('.') if f.endswith(ext)])
    
    test_file = None
    
    if audio_files:
        print(f"   Found {len(audio_files)} audio file(s):")
        for i, f in enumerate(audio_files, 1):
            size_mb = os.path.getsize(f) / (1024 * 1024)
            print(f"   {i}. {f} ({size_mb:.2f} MB)")
        test_file = audio_files[0]
        print(f"\n   Using: {test_file}")
    else:
        print("   No audio files found. Creating a test tone...")
        test_file = create_test_audio()
    
    # Test transcription
    print(f"\n4️⃣  Transcribing: {test_file}")
    print("   (This will take a few seconds...)")
    
    try:
        result = vm.transcribe_audio(test_file)
        
        print("\n" + "=" * 60)
        print("📝 TRANSCRIPTION RESULT")
        print("=" * 60)
        
        if 'error' in result and result['error']:
            print(f"❌ Error: {result['error']}")
            return False
        
        if result['text']:
            print(f"\n✅ SUCCESS!")
            print(f"\n📄 Text: {result['text']}")
            print(f"🌍 Language: {result['language']}")
            print(f"⏱️  Duration: {result['duration']:.2f} seconds")
            print(f"📊 Confidence: {result['confidence']:.2%}")
            print(f"📌 Segments: {len(result['segments'])}")
            
            print("\n" + "=" * 60)
            print("🎉 Whisper is working perfectly!")
            print("=" * 60)
            return True
        else:
            print("⚠️  No text was transcribed (audio might be silent or contain no speech)")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR during transcription:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting Whisper Test...\n")
    success = test_whisper()
    
    if success:
        print("\n✅ All tests passed! Whisper is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        sys.exit(1)
