import os
import asyncio
import pyperclip
from PIL import Image, ImageChops

# Lazy import win32 modules for active window tracking
win32gui = None
win32process = None
win32api = None
win32con = None
psutil = None

try:
    import win32gui
    import win32process
    import win32api
    import win32con
except ImportError:
    pass

try:
    import psutil
except ImportError:
    pass


class AmbientService:
    """
    Ambient Layer Service for APEX.
    Runs continuous background watchers to observe the user's workspace, screen,
    clipboard, and active application context, feeding them into APEX's context.
    """

    def __init__(self, engine):
        self.engine = engine
        self.is_active = False
        self.watchers = []
        self.last_window_text = ""
        self.last_window_proc = ""
        self.last_clipboard = ""
        self.last_screenshot_path = None
        self.fs_state = {}  # filepath -> mtime
        self.workspace_root = os.getcwd()

    def start(self):
        """Start all ambient background tasks."""
        if self.is_active:
            return
        self.is_active = True
        self.workspace_root = os.getcwd()
        
        # Reset trackers
        self.last_window_text = ""
        self.last_window_proc = ""
        try:
            self.last_clipboard = pyperclip.paste()
        except Exception:
            self.last_clipboard = ""
        self.last_screenshot_path = None
        self._scan_fs_initial()

        # Run watchers in the asyncio event loop as tasks
        self.watchers = [
            asyncio.create_task(self._window_watcher_loop()),
            asyncio.create_task(self._clipboard_watcher_loop()),
            asyncio.create_task(self._fs_watcher_loop()),
            asyncio.create_task(self._screen_watcher_loop()),
        ]
        print("[Ambient] Ambient services initialized and monitoring.")

    def stop(self):
        """Stop all ambient background tasks."""
        self.is_active = False
        for task in self.watchers:
            task.cancel()
        self.watchers = []
        print("[Ambient] Ambient services stopped.")

    async def _window_watcher_loop(self):
        """Polls for changes to the active foreground window."""
        while self.is_active:
            try:
                if win32gui:
                    hwnd = win32gui.GetForegroundWindow()
                    if hwnd:
                        title = win32gui.GetWindowText(hwnd)
                        proc_name = "unknown"
                        if psutil:
                            try:
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                p = psutil.Process(pid)
                                proc_name = p.name()
                            except Exception:
                                pass
                        
                        if title != self.last_window_text or proc_name != self.last_window_proc:
                            self.last_window_text = title
                            self.last_window_proc = proc_name
                            # Update context in engine or console print
                            # print(f"[Ambient App] Switch to: {proc_name} ('{title}')")
                            
                            # Fire hook
                            if self.engine and hasattr(self.engine, "hooks"):
                                await self.engine.hooks.fire("UserPromptSubmit", {
                                    "ambient_context": f"User switched window to: {proc_name} - Title: {title}"
                                })
                await asyncio.sleep(2.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # print(f"[Ambient] Window watcher error: {e}")
                await asyncio.sleep(5.0)

    async def _clipboard_watcher_loop(self):
        """Polls for clipboard changes."""
        while self.is_active:
            try:
                current_clip = pyperclip.paste()
                if current_clip != self.last_clipboard:
                    self.last_clipboard = current_clip
                    # Trigger clipboard change notification and store in context
                    # print(f"[Ambient Clipboard] Clipboard changed: {len(current_clip)} chars")
                    
                    if self.engine and hasattr(self.engine, "hooks"):
                        await self.engine.hooks.fire("AmbientClipboardChange", {
                            "content": current_clip,
                            "length": len(current_clip)
                        })
                await asyncio.sleep(1.5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5.0)

    def _scan_fs_initial(self):
        """Scans workspace directory to establish initial file state."""
        self.fs_state = {}
        active = self.engine.workspace.get_active() if (self.engine and hasattr(self.engine, "workspace")) else None
        root = active.root_dir if active else self.workspace_root
        
        for dirpath, _, filenames in os.walk(root):
            # Skip hidden/large folders
            if any(part.startswith(".") or part in ("__pycache__", "node_modules", "data", "venv", "env") for part in dirpath.split(os.sep)):
                continue
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                try:
                    self.fs_state[full_path] = os.path.getmtime(full_path)
                except OSError:
                    pass

    async def _fs_watcher_loop(self):
        """Polls filesystem for changes (creation, modification, deletion) as watchdog fallback."""
        while self.is_active:
            try:
                active = self.engine.workspace.get_active() if (self.engine and hasattr(self.engine, "workspace")) else None
                root = active.root_dir if active else self.workspace_root
                
                current_state = {}
                for dirpath, _, filenames in os.walk(root):
                    if any(part.startswith(".") or part in ("__pycache__", "node_modules", "data", "venv", "env") for part in dirpath.split(os.sep)):
                        continue
                    for f in filenames:
                        full_path = os.path.join(dirpath, f)
                        try:
                            current_state[full_path] = os.path.getmtime(full_path)
                        except OSError:
                            pass
                
                # Check for changes
                added = []
                modified = []
                deleted = []
                
                for path, mtime in current_state.items():
                    if path not in self.fs_state:
                        added.append(path)
                    elif mtime > self.fs_state[path]:
                        modified.append(path)
                        
                for path in self.fs_state:
                    if path not in current_state:
                        deleted.append(path)
                        
                # Update state
                self.fs_state = current_state
                
                # Notify on changes
                for a in added:
                    # print(f"[Ambient File] Added: {os.path.basename(a)}")
                    if self.engine and hasattr(self.engine, "hooks"):
                        await self.engine.hooks.fire("AmbientFileChange", {"action": "added", "path": a})
                for m in modified:
                    # print(f"[Ambient File] Modified: {os.path.basename(m)}")
                    if self.engine and hasattr(self.engine, "hooks"):
                        await self.engine.hooks.fire("AmbientFileChange", {"action": "modified", "path": m})
                for d in deleted:
                    # print(f"[Ambient File] Deleted: {os.path.basename(d)}")
                    if self.engine and hasattr(self.engine, "hooks"):
                        await self.engine.hooks.fire("AmbientFileChange", {"action": "deleted", "path": d})
                        
                await asyncio.sleep(3.0)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5.0)

    async def _screen_watcher_loop(self):
        """Captures screen and triggers event on visual updates."""
        while self.is_active:
            try:
                if self.engine and hasattr(self.engine, "retina") and self.engine.retina:
                    # Capture screen using RetinaTool
                    # We run it in a thread since screenshot and file write are blocking
                    path = await asyncio.to_thread(self.engine.retina.capture_screen)
                    
                    if self.last_screenshot_path and os.path.exists(self.last_screenshot_path) and os.path.exists(path):
                        try:
                            # Compare visual difference using Pillow
                            with Image.open(self.last_screenshot_path) as img1, Image.open(path) as img2:
                                diff = ImageChops.difference(img1, img2)
                                bbox = diff.getbbox()
                                if bbox:
                                    # Screen has visual changes
                                    # print(f"[Ambient Screen] Visually updated: {bbox}")
                                    if self.engine and hasattr(self.engine, "hooks"):
                                        await self.engine.hooks.fire("AmbientScreenChange", {
                                            "path": path,
                                            "bbox": bbox
                                        })
                        except Exception:
                            pass
                        
                        # Cleanup old snap file
                        try:
                            os.remove(self.last_screenshot_path)
                        except OSError:
                            pass
                            
                    self.last_screenshot_path = path
                    
                await asyncio.sleep(5.0)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(10.0)
