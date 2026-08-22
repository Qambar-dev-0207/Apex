"""
RetinaTool — APEX's vision + multimedia understanding subsystem.

Capabilities:
  • capture_screen()                 — screenshot the current display
  • describe_image(path, prompt?)    — Gemini 2.5 multimodal description / Q&A
  • ocr_image(path)                  — Gemini-backed OCR
  • describe_video(path, ...)        — sample frames, send to Gemini for a temporal description
  • transcribe_audio(path)           — Groq Whisper if available
  • understand_media(path)           — auto-detect file type and route

Heavy deps are optional and imported lazily so APEX boots even if cv2 / pyautogui
are unavailable in the runtime.
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None


# Supported file extensions
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


class RetinaTool:
    """
    Gemini-backed vision + multimedia understanding. Pyautogui drives screen
    capture; cv2 (lazy import) drives video frame extraction.
    """

    def __init__(self, storage_dir: str = "data/vision",
                 gemini_model: str = "gemini-3.5-flash"):
        load_dotenv()
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.gemini_model = gemini_model
        self._gemini = None  # lazy

    # ── lazy Gemini client ──────────────────────────────────────────────
    def _ensure_gemini(self):
        if self._gemini is not None:
            return self._gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            from google import genai  # type: ignore
            self._gemini = genai.Client(api_key=api_key)
        except Exception:
            return None
        return self._gemini

    # ── screen capture ──────────────────────────────────────────────────
    def capture_screen(self, filename: Optional[str] = None) -> str:
        if not pyautogui or not Image:
            raise RuntimeError("pyautogui/Pillow not available — install requirements.txt")
        if not filename:
            filename = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(self.storage_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
        jpeg_path = path.replace(".png", ".jpg")
        screenshot.convert("RGB").save(jpeg_path, "JPEG", quality=85)
        return os.path.abspath(jpeg_path)

    def cleanup_old_snaps(self, max_age_hours: int = 24) -> None:
        now = time.time()
        for f in os.listdir(self.storage_dir):
            p = os.path.join(self.storage_dir, f)
            try:
                if os.stat(p).st_mtime < now - (max_age_hours * 3600):
                    os.remove(p)
            except OSError:
                pass

    # ── image understanding ─────────────────────────────────────────────
    async def describe(self, path: str, prompt: Optional[str] = None) -> str:
        """
        Auto-routes by file extension: image / video / audio.
        Backwards-compat alias used by harness and router.
        """
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_EXTS:
            return await self.describe_image(path, prompt)
        if ext in VIDEO_EXTS:
            return await self.describe_video(path, prompt=prompt)
        if ext in AUDIO_EXTS:
            return await self.transcribe_audio(path)
        return f"[unknown media type: {ext}]"

    def _is_ocr_request(self, path: str, prompt: Optional[str]) -> bool:
        if not prompt:
            # If no prompt, it's a generic description. If it's a screenshot, treat as OCR-shaped.
            abs_path = os.path.abspath(path)
            abs_storage = os.path.abspath(self.storage_dir)
            return "snap_" in os.path.basename(path) or abs_path.startswith(abs_storage)
            
        p = prompt.lower()
        ocr_keywords = {
            "read", "text", "ocr", "extract", "verbatim", "transcribe", 
            "written", "code", "error", "message", "what does it say", 
            "what is on my screen", "read the text", "terminal", "log", 
            "console", "screenshot", "screen"
        }
        if any(kw in p for kw in ocr_keywords):
            return True
            
        # Also check file source
        abs_path = os.path.abspath(path)
        abs_storage = os.path.abspath(self.storage_dir)
        if "snap_" in os.path.basename(path) or abs_path.startswith(abs_storage):
            return True
            
        return False

    def _is_pure_extraction_prompt(self, prompt: str) -> bool:
        p = prompt.lower()
        if "extract all visible text from this image verbatim" in p:
            return True
        if p.strip() in ("extract text", "ocr", "read text", "get text"):
            return True
        return False

    async def _run_local_ocr(self, path: str) -> Optional[str]:
        if not pytesseract or not Image:
            return None
        try:
            loop = asyncio.get_event_loop()
            
            def _ocr():
                try:
                    return pytesseract.image_to_string(Image.open(path))
                except Exception:
                    # Try common Windows paths for tesseract binary
                    common_paths = [
                        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                        r"C:\Users\qamba\AppData\Local\Tesseract-OCR\tesseract.exe",
                    ]
                    for cp in common_paths:
                        if os.path.exists(cp):
                            pytesseract.pytesseract.tesseract_cmd = cp
                            return pytesseract.image_to_string(Image.open(path))
                    raise
            
            text = await loop.run_in_executor(None, _ocr)
            return text.strip() if text else None
        except Exception:
            return None

    async def describe_image(self, path: str, prompt: Optional[str] = None) -> str:
        if not os.path.exists(path):
            return f"[image not found: {path}]"

        # 1. Tier 1: Local OCR check for OCR-shaped requests
        if self._is_ocr_request(path, prompt):
            ocr_text = await self._run_local_ocr(path)
            if ocr_text:
                # If it's a pure extraction request, return the text directly
                if not prompt or self._is_pure_extraction_prompt(prompt):
                    return ocr_text
                
                # If specific question, query Gemini using text-only call
                client = self._ensure_gemini()
                if client:
                    try:
                        instruction = (
                            f"Below is the OCR text extracted from a screenshot/image.\n"
                            f"Answer this prompt using that text:\n{prompt}\n\n"
                            f"OCR Text:\n{ocr_text}"
                        )
                        loop = asyncio.get_event_loop()
                        res = await loop.run_in_executor(
                            None,
                            lambda: client.models.generate_content(
                                model=self.gemini_model,
                                contents=instruction,
                            ),
                        )
                        return (res.text or "").strip()
                    except Exception:
                        pass # Fall through to multimodal on API failure

        # 2. Fall through to Gemini Multimodal
        client = self._ensure_gemini()
        if not client:
            return "[vision unavailable: GEMINI_API_KEY missing]"
        try:
            from google.genai import types  # type: ignore
            mime = self._guess_image_mime(path)
            with open(path, "rb") as f:
                data = f.read()
            instruction = prompt or (
                "Describe this image in detail. Focus on what's actionable: "
                "text content, UI elements, code, diagrams, errors. "
                "Be precise and concise."
            )
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=self.gemini_model,
                    contents=[
                        types.Part.from_bytes(data=data, mime_type=mime),
                        instruction,
                    ],
                ),
            )
            return (res.text or "").strip()
        except Exception as e:
            return f"[image describe error: {e}]"

    async def ocr_image(self, path: str) -> str:
        return await self.describe_image(
            path,
            prompt="Extract ALL visible text from this image verbatim. "
                   "Preserve line breaks. Output text only, no commentary.",
        )

    # ── video understanding ─────────────────────────────────────────────
    def _extract_frames(
        self, video_path: str, max_frames: int = 8
    ) -> List[str]:
        """
        Uniformly sample up to `max_frames` frames from a video; save as JPEGs
        under storage_dir/frames_<ts>/ and return their paths.
        """
        try:
            import cv2  # type: ignore
        except Exception:
            raise RuntimeError("opencv-python not installed — `pip install opencv-python`")
        if not os.path.exists(video_path):
            raise FileNotFoundError(video_path)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"could not open video: {video_path}")
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        if total <= 0:
            cap.release()
            raise RuntimeError("video has 0 frames or unknown length")
        frame_count = min(max_frames, max(1, total))
        indices = [int(i * (total - 1) / max(1, frame_count - 1)) for i in range(frame_count)]
        out_dir = os.path.join(
            self.storage_dir,
            f"frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        )
        os.makedirs(out_dir, exist_ok=True)
        paths: List[str] = []
        for i, idx in enumerate(indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                continue
            out = os.path.join(out_dir, f"f{i:02d}_t{idx}.jpg")
            cv2.imwrite(out, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            paths.append(out)
        cap.release()
        return paths

    async def describe_video(
        self,
        path: str,
        max_frames: int = 8,
        prompt: Optional[str] = None,
    ) -> str:
        if not os.path.exists(path):
            return f"[video not found: {path}]"
        client = self._ensure_gemini()
        if not client:
            return "[vision unavailable: GEMINI_API_KEY missing]"
        try:
            frames = self._extract_frames(path, max_frames=max_frames)
        except Exception as e:
            return f"[frame extraction failed: {e}]"
        if not frames:
            return "[no frames extracted]"
        try:
            from google.genai import types  # type: ignore
            parts: List[Any] = []
            for fp in frames:
                with open(fp, "rb") as f:
                    parts.append(
                        types.Part.from_bytes(data=f.read(), mime_type="image/jpeg")
                    )
            instruction = prompt or (
                "These frames are uniformly sampled from a single video in time order. "
                "Summarize what happens across the clip — actions, scene changes, "
                "any visible text or UI. Output a single concise paragraph followed by "
                "a bulleted timeline of key moments."
            )
            parts.append(instruction)
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=self.gemini_model,
                    contents=parts,
                ),
            )
            return (res.text or "").strip()
        except Exception as e:
            return f"[video describe error: {e}]"

    # ── audio transcription (Groq Whisper) ──────────────────────────────
    async def transcribe_audio(self, path: str) -> str:
        if not os.path.exists(path):
            return f"[audio not found: {path}]"
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "[audio: GROQ_API_KEY missing — set it for Whisper transcription]"
        try:
            from groq import Groq  # type: ignore
        except Exception:
            return "[audio: groq package missing]"
        try:
            client = Groq(api_key=api_key)
            loop = asyncio.get_event_loop()

            def _do():
                with open(path, "rb") as f:
                    res = client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=(os.path.basename(path), f.read()),
                        response_format="text",
                    )
                # Some Groq SDK versions return the text directly; others an object.
                return getattr(res, "text", str(res))

            return (await loop.run_in_executor(None, _do)).strip()
        except Exception as e:
            return f"[audio transcribe error: {e}]"

    # ── unified router ──────────────────────────────────────────────────
    async def understand_media(
        self, path: str, prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_EXTS:
            return {"kind": "image", "output": await self.describe_image(path, prompt)}
        if ext in VIDEO_EXTS:
            return {"kind": "video", "output": await self.describe_video(path, prompt=prompt)}
        if ext in AUDIO_EXTS:
            return {"kind": "audio", "output": await self.transcribe_audio(path)}
        return {"kind": "unknown", "output": f"unsupported extension: {ext}"}

    # ── helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _guess_image_mime(path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        return {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".gif": "image/gif",
        }.get(ext, "image/jpeg")
