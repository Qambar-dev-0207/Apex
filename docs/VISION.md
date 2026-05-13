# APEX — Vision & Media Understanding

`src/tools/vision.py` — `RetinaTool`

---

## Overview

APEX can see, read, and hear. `RetinaTool` handles all media modalities:
- **Images** — describe content, extract text (OCR)
- **Video** — understand temporal content via frame sampling
- **Audio** — transcribe speech and sound
- **Auto-route** — `understand_media()` picks the right path by file extension

---

## Supported formats

| Kind | Extensions |
|---|---|
| Image | `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.gif` |
| Video | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` |
| Audio | `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a` |

---

## Methods

### `describe_image(path, prompt=None) → dict`

Sends the image to Gemini 2.5 Flash (multimodal) and returns a natural language description.

```python
result = await retina.describe_image("screenshot.png")
# result = {"kind": "image", "output": "A Python IDE showing..."}

result = await retina.describe_image("chart.png", prompt="What trend does this show?")
```

**Backend:** Gemini multimodal — image bytes encoded as base64 in the API call.

---

### `ocr_image(path) → dict`

Extracts verbatim text from an image. No paraphrasing — exact characters as they appear.

```python
result = await retina.ocr_image("invoice.png")
# result = {"kind": "image", "output": "Invoice #1234\nTotal: $500..."}
```

**Backend:** Gemini with prompt `"Extract all text verbatim. No analysis."`.

---

### `describe_video(path, max_frames=8, prompt=None) → dict`

Samples frames uniformly across the video duration, encodes them, and sends all to Gemini in a single multimodal call.

```python
result = await retina.describe_video("demo.mp4")
result = await retina.describe_video("lecture.mp4", max_frames=16, prompt="What concepts are taught?")
```

**How frame sampling works:**
```
1. cv2.VideoCapture opens the file
2. frame_count = total frames in video
3. frame_indices = linspace(0, frame_count-1, max_frames) [uniform spacing]
4. Each frame extracted → JPEG encode → base64
5. All frames sent to Gemini as a single message with temporal context
```

**Backend:** `opencv-python` (cv2) for extraction, Gemini 2.5 Flash for understanding.

**Offline:** Returns `{"kind": "video", "output": "Video description unavailable — Gemini offline."}` when key absent.

---

### `transcribe_audio(path) → dict`

Transcribes audio file using Groq's Whisper-large-v3 model.

```python
result = await retina.transcribe_audio("meeting.mp3")
# result = {"kind": "audio", "output": "Good morning everyone, today's agenda..."}
```

**Backend:** `groq.audio.transcriptions.create(model="whisper-large-v3", file=...)`

**Offline:** Returns `{"kind": "audio", "output": "Audio transcription unavailable — Groq offline."}`.

---

### `understand_media(path, prompt=None) → dict`

Auto-router. Detects media kind by extension and dispatches to the right method.

```python
result = await retina.understand_media("video.mp4")   # → describe_video
result = await retina.understand_media("photo.jpg")   # → describe_image
result = await retina.understand_media("talk.mp3")    # → transcribe_audio
result = await retina.understand_media("doc.pdf")     # → {"kind": "unknown", "output": "unsupported..."}
```

---

### `describe(path, prompt=None)` — legacy alias

Calls `understand_media()`. Kept for backwards compatibility with older harness tool calls.

---

### `capture_screen() → str`

Takes a screenshot using PIL and saves to a temp file. Returns the file path.

---

## Harness tool names

When using `/harness`, the corresponding tool schemas are:

| Harness tool | Maps to |
|---|---|
| `vision_capture` | `capture_screen()` |
| `vision_describe` | `describe_image(path, prompt)` |
| `vision_ocr` | `ocr_image(path)` |
| `video_describe` | `describe_video(path, max_frames, prompt)` |
| `audio_transcribe` | `transcribe_audio(path)` |
| `understand_media` | `understand_media(path, prompt)` |

---

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Video frame extraction (`cv2.VideoCapture`) |
| `Pillow` | Screenshot capture |
| `groq` | Whisper audio transcription |
| `google-generativeai` | Gemini multimodal vision |
