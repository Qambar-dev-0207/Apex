import pyautogui
from PIL import Image
import os
import time
from datetime import datetime
from typing import Optional, List

class RetinaTool:
    """
    Provides APEX with visual input capabilities.
    """
    def __init__(self, storage_dir: str = "data/vision"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def capture_screen(self, filename: Optional[str] = None) -> str:
        """
        Captures a screenshot and saves it to the storage directory.
        """
        if not filename:
            filename = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        path = os.path.join(self.storage_dir, filename)
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Optimize for LLM (Resize if too large, convert to JPEG to save space)
        # Gemini supports up to 3072x3072, but smaller is faster.
        max_size = (1536, 1536)
        screenshot.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save as JPEG for better compression
        jpeg_path = path.replace(".png", ".jpg")
        screenshot.convert("RGB").save(jpeg_path, "JPEG", quality=85)
        
        return os.path.abspath(jpeg_path)

    def cleanup_old_snaps(self, max_age_hours: int = 24):
        """
        Removes old screenshots.
        """
        now = time.time()
        for f in os.listdir(self.storage_dir):
            path = os.path.join(self.storage_dir, f)
            if os.stat(path).st_mtime < now - (max_age_hours * 3600):
                os.remove(path)
