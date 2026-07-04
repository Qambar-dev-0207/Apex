import sys
import os
import asyncio
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.voice_layer import VoiceLayer

class DummyEngine:
    def __init__(self):
        self.session_id = "test-session"
        self.loop = asyncio.get_event_loop()

def main():
    print("Testing APEX Voice Layer Initialization...")
    
    # Enable APEX mock voice env variable just in case, but let's test actual init first
    engine = DummyEngine()
    
    try:
        voice = VoiceLayer(engine)
        print("\nInitialization Results:")
        print(f"SAPI TTS Speaker Available: {voice.sapi_speaker is not None}")
        if voice.sapi_speaker:
            try:
                desc = voice.sapi_speaker.Voice.GetDescription()
                print(f"Selected TTS Voice: {desc}")
            except Exception as e:
                print(f"Failed to get SAPI voice description: {e}")
        
        print(f"Whisper Model Loaded (Local STT): {voice.whisper_model is not None}")
        
        # Test cleaning markdown
        test_md = "Hello **Architect**, check `this` code!"
        cleaned = voice._clean_markdown(test_md)
        print(f"Markdown Cleaning Test:\n  Raw: {test_md}\n  Clean: {cleaned}")
        
        # Run SAPI speak test if available (very briefly speak a test line)
        if voice.sapi_speaker:
            print("\nTriggering a quick test spoken phrase...")
            voice.sapi_speaker.Speak("Voice system initialization test complete.")
            print("Speak complete.")
        else:
            print("\nSAPI Speaker is None, skipping audio playback test.")
            
    except Exception as e:
        print(f"Voice Layer initialization crashed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
