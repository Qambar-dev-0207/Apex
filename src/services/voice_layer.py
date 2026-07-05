import os
import queue
import sys
import time
import asyncio
import threading
import numpy as np
from typing import Optional, Callable

# Lazy import helpers to avoid crash if some dependencies are missing
sounddevice = None
whisper = None
openwakeword = None
win32com = None
kokoro_onnx = None

try:
    import sounddevice as sd
    sounddevice = sd
except ImportError:
    pass

try:
    import whisper
except ImportError:
    pass

try:
    import openwakeword
except ImportError:
    pass

try:
    import win32com.client
    win32com = win32com.client
except ImportError:
    pass

try:
    import kokoro_onnx
except ImportError:
    pass


class VoiceLayer:
    """
    Voice Layer Service for APEX.
    Handles hands-free speech interactions:
    - Audio capturing using sounddevice.
    - Wake-word detection using openwakeword, with a Whisper-based energy-VAD fallback.
    - Voice Activity Detection (VAD) using local energy threshold.
    - Speech-To-Text (STT) using local openai-whisper or Groq API fallback.
    - Text-To-Speech (TTS) using native Windows SAPI5 (Microsoft David Desktop male voice).
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.is_active = False
        self.audio_queue = queue.Queue()
        self.speak_queue = queue.Queue()
        self.loop_thread = None
        self.speak_thread = None
        self.whisper_model = None
        self.sapi_speaker = None
        self.kokoro = None
        self.use_kokoro = False
        self.wake_word = "hey apex"
        
        # Audio stream settings
        self.sample_rate = 16000
        self.block_size = 1024
        self.energy_threshold = 0.015  # RMS energy threshold for VAD
        self.silence_blocks_limit = 25  # ~1.6 seconds of silence to stop recording
        
        # Wake word state
        self.listening_for_command = False
        self.command_callback: Optional[Callable[[str], None]] = None

        self._initialize_tts()
        self._initialize_stt()

    def _initialize_tts(self):
        """Initialize Kokoro ONNX local TTS or fallback to Windows SAPI5."""
        apex_dir = os.path.join(os.path.expanduser("~"), ".apex")
        model_path = os.path.join(apex_dir, "kokoro-v0_19.onnx")
        voices_path = os.path.join(apex_dir, "voices.bin")

        if kokoro_onnx and os.path.exists(model_path) and os.path.exists(voices_path) and sounddevice:
            try:
                from kokoro_onnx import Kokoro
                self.kokoro = Kokoro(model_path, voices_path)
                self.use_kokoro = True
                print(f"[Voice] TTS initialized using Kokoro ONNX local model.")
                return
            except Exception as e:
                print(f"[Voice] Kokoro ONNX TTS initialization failed: {e}. Falling back to SAPI5.")

        if win32com:
            try:
                self.sapi_speaker = win32com.Dispatch("SAPI.SpVoice")
                voices = self.sapi_speaker.GetVoices()
                # Find Microsoft David Desktop or any male voice
                male_voice_index = 0
                for i in range(voices.Count):
                    desc = voices.Item(i).GetDescription().lower()
                    if "david" in desc or "male" in desc:
                        male_voice_index = i
                        break
                self.sapi_speaker.Voice = voices.Item(male_voice_index)
                print(f"[Voice] TTS initialized using SAPI5 voice: {voices.Item(male_voice_index).GetDescription()}")
            except Exception as e:
                print(f"[Voice] SAPI5 TTS initialization failed: {e}")
        else:
            print("[Voice] win32com/Kokoro not available, speech output will be printed only.")

    def _initialize_stt(self):
        """Initialize local Whisper model or setup fallback."""
        if whisper:
            try:
                # Try to load lightweight 'tiny' model offline
                # If weights are missing, it will raise an exception when offline.
                print("[Voice] Loading local Whisper 'tiny' model...")
                self.whisper_model = whisper.load_model("tiny", device="cpu")
                print("[Voice] Local Whisper model loaded successfully.")
            except Exception as e:
                print(f"[Voice] Local Whisper load failed (likely offline and weights not cached): {e}")
                print("[Voice] STT will fall back to Groq API or console simulation.")
        else:
            print("[Voice] whisper package not imported, using STT API/simulation fallbacks.")

    def speak(self, text: str):
        """Enqueue text to be spoken asynchronously."""
        if not text:
            return
        # Clean text from markdown styling for smoother reading
        clean_text = self._clean_markdown(text)
        self.speak_queue.put(clean_text)

    def _clean_markdown(self, text: str) -> str:
        """Strip markdown markers for clean speech."""
        text = text.replace("**", "").replace("*", "").replace("`", "")
        text = text.replace("[bold]", "").replace("[/bold]", "")
        text = text.replace("[cyan]", "").replace("[/cyan]", "")
        text = text.replace("[yellow]", "").replace("[/yellow]", "")
        text = text.replace("[green]", "").replace("[/green]", "")
        text = text.replace("[red]", "").replace("[/red]", "")
        # Remove markdown link syntax [text](url) -> text
        import re
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        return text

    def start(self, callback: Callable[[str], None]):
        """Start background threads for voice processing."""
        if self.is_active:
            return
        self.is_active = True
        self.command_callback = callback
        
        # Start TTS speak thread
        self.speak_thread = threading.Thread(target=self._speak_loop, daemon=True)
        self.speak_thread.start()
        
        # Start Voice listening thread
        self.loop_thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.loop_thread.start()
        
        self.speak("Voice systems online, Architect.")

    def stop(self):
        """Stop voice operations."""
        self.is_active = False
        self.speak_queue.put(None)  # stop sentinel
        self.audio_queue.put(None)  # stop sentinel

    def _speak_loop(self):
        """Background thread handling TTS synthesis."""
        while self.is_active:
            try:
                text = self.speak_queue.get(timeout=1.0)
                if text is None:  # Exit sentinel
                    break
                if self.use_kokoro and sounddevice:
                    try:
                        # Use a pleasant female voice 'af_bella' as the default APEX voice
                        samples, sample_rate = self.kokoro.create(text, voice="af_bella", speed=1.0, lang="en-us")
                        sounddevice.play(samples, sample_rate)
                        sounddevice.wait()
                    except Exception as e:
                        print(f"[Voice] Kokoro TTS playback failed: {e}")
                        # Fallback to SAPI5 if available
                        if self.sapi_speaker:
                            self.sapi_speaker.Speak(text)
                        else:
                            print(f"\n[Voice Output] {text}\n")
                elif self.sapi_speaker:
                    # Speak blockingly in this background thread
                    self.sapi_speaker.Speak(text)
                else:
                    print(f"\n[Voice Output] {text}\n")
                self.speak_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Voice] Speak loop error: {e}")

    def _listening_loop(self):
        """Background thread listening for wake word or voice commands."""
        if not sounddevice:
            print("[Voice] sounddevice is missing. Voice activation offline.")
            return

        def _audio_callback(indata, frames, time_info, status):
            if status:
                pass
            self.audio_queue.put(indata.copy())

        # Start input stream
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1,
                                blocksize=self.block_size, callback=_audio_callback):
                print(f"[Voice] Microphone stream active. Listening for '{self.wake_word}'...")
                recording_buffer = []
                is_recording = False
                silence_blocks = 0
                
                while self.is_active:
                    try:
                        data = self.audio_queue.get(timeout=1.0)
                        if data is None:
                            break
                        
                        # Compute root-mean-square (RMS) energy
                        rms = np.sqrt(np.mean(data**2))
                        
                        if is_recording:
                            recording_buffer.append(data)
                            if rms < self.energy_threshold:
                                silence_blocks += 1
                            else:
                                silence_blocks = 0
                                
                            # Stop recording if user has been silent or max length (10s) is reached
                            if silence_blocks > self.silence_blocks_limit or len(recording_buffer) > (self.sample_rate * 10 // self.block_size):
                                is_recording = False
                                audio_bytes = np.concatenate(recording_buffer, axis=0).flatten()
                                recording_buffer = []
                                self._process_audio(audio_bytes)
                        else:
                            # Start recording if sound level is above threshold
                            if rms >= self.energy_threshold:
                                is_recording = True
                                silence_blocks = 0
                                recording_buffer.append(data)
                                
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"[Voice] Listening loop inner error: {e}")
                        
        except Exception as e:
            print(f"[Voice] Microphone initialization failed: {e}")

    def _process_audio(self, audio_data: np.ndarray):
        """Process recorded audio buffer and convert it to text."""
        # Convert floating point array to 16-bit PCM for potential Whisper compatibility
        # sounddevice records in float32 by default
        transcript = self._transcribe(audio_data)
        if not transcript:
            return

        clean_transcript = transcript.strip().lower().rstrip(".,?!")
        print(f"[Voice Hearing] Detected: '{clean_transcript}'")

        if not self.listening_for_command:
            # Wake word state
            if self.wake_word in clean_transcript or "apex" in clean_transcript:
                self.listening_for_command = True
                self.speak("Listening.")
                print("[Voice] Wake word detected. Waiting for command...")
        else:
            # Command state
            self.listening_for_command = False
            if clean_transcript:
                if self.command_callback:
                    # Invoke REPL input callback in the main thread or event loop
                    self.command_callback(clean_transcript)

    def _transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio array using local Whisper or fallback API."""
        if self.whisper_model:
            try:
                # whisper expects float32 np.ndarray at 16000Hz
                result = self.whisper_model.transcribe(audio_data, fp16=False)
                return result.get("text", "")
            except Exception as e:
                print(f"[Voice] Local Whisper transcription error: {e}")
        
        # Fallback to Groq API if api key is available
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and self.engine and hasattr(self.engine, "groq_client"):
            try:
                # Write audio_data to temporary WAV file to send to API
                import tempfile
                import scipy.io.wavfile as wav
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    temp_path = f.name
                
                # Rescale float to 16-bit int WAV
                scaled = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
                wav.write(temp_path, self.sample_rate, scaled)
                
                # Call Groq transcribe API (assuming engine's groq_client has a translation or audio transcription capability)
                # If groq_client doesn't have it directly, we use requests or groq library
                from groq import Groq
                client = Groq(api_key=api_key)
                with open(temp_path, "rb") as audio_file:
                    translation = client.audio.transcriptions.create(
                        file=(temp_path, audio_file.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                return str(translation)
            except Exception as e:
                print(f"[Voice] Groq STT API fallback failed: {e}")

        # Final fallback - Mock simulation for testing
        if "test" in sys.argv or os.getenv("APEX_MOCK_VOICE") == "1":
            # For testing, if we input mock data, we return it
            if hasattr(self, "_mock_transcription"):
                return self._mock_transcription
            return ""
        
        return ""
