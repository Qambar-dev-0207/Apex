"""
VoiceLayer — hands-free input/output for APEX.

Pipeline:
  openWakeWord (wake word)
    → Silero VAD (start/stop recording on speech)
    → Voxtral Mini 3B (STT, served locally via vLLM, OpenAI-compatible)
    → feed transcript into APEX's normal input pipeline (same path as typed text)
    → Kokoro-82M (TTS, local ONNX, CPU-friendly)
    → sounddevice playback

Fully local — no cloud STT/TTS calls. Degrades gracefully: if any dependency
or model is missing, VoiceLayer reports itself offline instead of crashing
APEX's boot.
"""

import asyncio
import io
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

import numpy as np
from dotenv import load_dotenv

try:
    import sounddevice as sd
except Exception:
    sd = None

try:
    import openwakeword
    from openwakeword.model import Model as WakeWordModel
except Exception:
    openwakeword = None
    WakeWordModel = None

try:
    import torch
    _SILERO_AVAILABLE = True
except Exception:
    torch = None
    _SILERO_AVAILABLE = False

try:
    from kokoro_onnx import Kokoro
except Exception:
    Kokoro = None

import httpx


SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)


@dataclass
class VoiceConfig:
    wake_word_model_path: str = "apex_wake.onnx"   # trained custom wakeword
    vad_threshold: float = 0.5
    silence_timeout_sec: float = 1.2                # stop recording after this much silence
    max_utterance_sec: float = 20.0
    stt_endpoint: str = "http://localhost:8000/v1"   # vLLM-served Voxtral
    stt_model: str = "mistralai/Voxtral-Mini-3B-2507"
    kokoro_model_path: str = os.path.expanduser("~/.apex/kokoro-v0_19.onnx")
    kokoro_voices_path: str = os.path.expanduser("~/.apex/voices.bin")
    kokoro_voice: str = "af_heart"


class VoiceLayer:
    """
    Owns the full voice loop. `on_transcript` is the callback APEX wires to
    its normal input handling — treat a voice utterance exactly like a typed
    line so nothing downstream needs to know the difference.
    """

    def __init__(self, config: Optional[VoiceConfig] = None, console=None):
        load_dotenv()
        self.cfg = config or VoiceConfig()
        self.console = console
        self._wake_model = None
        self._kokoro = None
        self._running = False
        self._muted = False
        self.on_transcript: Optional[Callable[[str], Any]] = None

    # ── availability ─────────────────────────────────────────────────────
    @property
    def is_available(self) -> bool:
        return sd is not None and openwakeword is not None and _SILERO_AVAILABLE

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "bright_cyan", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[bold {color}][Voice] {msg}[/bold {color}]")

    # ── lazy model loading ───────────────────────────────────────────────
    def _ensure_wake_model(self):
        if self._wake_model is not None or WakeWordModel is None:
            return
        if not os.path.exists(self.cfg.wake_word_model_path):
            self._log(
                f"wake word model not found at {self.cfg.wake_word_model_path} — "
                "train one with openWakeWord's training notebook, or fall back to "
                "push-to-talk mode.",
                level="warn",
            )
            return
        self._wake_model = WakeWordModel(wakeword_models=[self.cfg.wake_word_model_path])

    def _ensure_kokoro(self):
        if self._kokoro is not None or Kokoro is None:
            return
        if not (os.path.exists(self.cfg.kokoro_model_path) and os.path.exists(self.cfg.kokoro_voices_path)):
            self._log("Kokoro model/voices not found — TTS disabled.", level="warn")
            return
        try:
            self._kokoro = Kokoro(self.cfg.kokoro_model_path, self.cfg.kokoro_voices_path)
        except Exception as e:
            self._log(f"Kokoro load error: {e} — TTS disabled.", level="warn")
            self._kokoro = None

    def _ensure_vad(self):
        if not _SILERO_AVAILABLE:
            return None, None
        try:
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True
            )
            return model, utils
        except Exception as e:
            self._log(f"VAD load error: {e}", level="warn")
            return None, None

    # ── STT ──────────────────────────────────────────────────────────────
    async def _transcribe(self, audio: np.ndarray) -> str:
        """Send recorded audio to the local Voxtral endpoint (OpenAI-compatible)."""
        buf = io.BytesIO()
        import soundfile as sf
        sf.write(buf, audio, SAMPLE_RATE, format="WAV")
        buf.seek(0)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                files = {"file": ("utterance.wav", buf, "audio/wav")}
                data = {"model": self.cfg.stt_model}
                r = await client.post(
                    f"{self.cfg.stt_endpoint}/audio/transcriptions",
                    files=files, data=data,
                )
                r.raise_for_status()
                return r.json().get("text", "").strip()
        except Exception as e:
            self._log(f"STT request failed: {e}", level="err")
            return ""

    # ── TTS ──────────────────────────────────────────────────────────────
    async def speak(self, text: str) -> None:
        if self._muted or not text.strip():
            return
        self._ensure_kokoro()
        if self._kokoro is None or sd is None:
            self._log(text)  # fallback: just print
            return
        try:
            # Clean markdown formatting before speaking
            import re
            clean_text = text.replace("**", "").replace("*", "").replace("`", "")
            clean_text = re.sub(r'\[cyan\]|\[/cyan\]|\[yellow\]|\[/yellow\]|\[green\]|\[/green\]|\[red\]|\[/red\]|\[bold\]|\[/bold\]', '', clean_text)
            clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)
            
            loop = asyncio.get_event_loop()
            samples, sr = await loop.run_in_executor(
                None, lambda: self._kokoro.create(clean_text, voice=self.cfg.kokoro_voice)
            )
            await loop.run_in_executor(None, lambda: (sd.play(samples, sr), sd.wait()))
        except Exception as e:
            self._log(f"TTS output failed: {e}", level="warn")
            self._log(text)

    def mute(self, muted: bool = True):
        self._muted = muted

    # ── recording (VAD-gated) ────────────────────────────────────────────
    async def _record_utterance(self) -> np.ndarray:
        """Records from mic until Silero VAD detects sustained silence."""
        vad_model, vad_utils = self._ensure_vad()
        frames: list[np.ndarray] = []
        silence_start: Optional[float] = None
        t0 = time.time()

        loop = asyncio.get_event_loop()
        q: asyncio.Queue = asyncio.Queue()

        def _callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q.put_nowait, indata.copy())

        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="float32",
            blocksize=FRAME_SAMPLES, callback=_callback,
        ):
            while True:
                chunk = await q.get()
                frames.append(chunk)
                is_speech = True
                if vad_model is not None:
                    tensor = torch.from_numpy(chunk.flatten())
                    prob = vad_model(tensor, SAMPLE_RATE).item()
                    is_speech = prob >= self.cfg.vad_threshold

                if is_speech:
                    silence_start = None
                else:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= self.cfg.silence_timeout_sec:
                        break

                if time.time() - t0 >= self.cfg.max_utterance_sec:
                    break

        return np.concatenate(frames).flatten()

    # ── main loop ────────────────────────────────────────────────────────
    async def run(self):
        """
        Long-running task. Listens for the wake word, records the follow-up
        utterance, transcribes it, and fires `on_transcript`. Runs forever
        until cancelled — wire alongside your other background_loop tasks.
        """
        if not self.is_available:
            self._log(
                "voice deps missing (sounddevice/openwakeword/torch) — "
                "voice layer disabled, text input still works normally.",
                level="warn",
            )
            return
        self._ensure_wake_model()
        if self._wake_model is None:
            return  # no trained wake model — stay silent rather than crash

        self._running = True
        self._log("listening for wake word...")

        loop = asyncio.get_event_loop()
        q: asyncio.Queue = asyncio.Queue()

        def _wake_callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q.put_nowait, indata.copy())

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                blocksize=FRAME_SAMPLES, callback=_wake_callback,
            ):
                while self._running:
                    chunk = await q.get()
                    scores = self._wake_model.predict(chunk.flatten())
                    if any(s >= 0.5 for s in scores.values()):
                        self._log("wake word detected — listening...")
                        await self.speak("Yes?")
                        audio = await self._record_utterance()
                        text = await self._transcribe(audio)
                        if text and self.on_transcript:
                            self._log(f"heard: {text}")
                            await self.on_transcript(text)
        except asyncio.CancelledError:
            return
        except Exception as e:
            self._log(f"voice loop crashed: {e}", level="err")

    def stop(self):
        self._running = False
