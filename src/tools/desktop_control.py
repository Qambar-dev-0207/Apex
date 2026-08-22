import os
import json
import subprocess
from typing import Dict, Any

# Lazy imports for pyautogui, uiautomation, win32gui, and playwright
pyautogui = None
uiautomation = None
win32gui = None
win32con = None
win32process = None
win32api = None

try:
    import pyautogui
except ImportError:
    pass

try:
    import uiautomation
except ImportError:
    pass

try:
    import win32gui
    import win32con
    import win32process
    import win32api
except ImportError:
    pass


class DesktopControlTool:
    """
    Desktop & Browser Control Tool for APEX.
    Supports system level actions: click, type, read, list_elements, navigate, powershell.
    Integrates Playwright for web automation.
    """

    def __init__(self):
        # Configure pyautogui safety settings
        if pyautogui:
            pyautogui.FAILSAFE = True

    async def execute(self, action: str, input_data: str) -> Dict[str, Any]:
        """
        Main entry point for tool execution.
        """
        action = action.lower()
        
        # Parse JSON input if applicable
        data = {}
        if input_data:
            try:
                # Some LLM plans might emit raw JSON strings
                data = json.loads(input_data)
            except json.JSONDecodeError:
                # If not JSON, treat it as a string
                data = {"text": input_data, "command": input_data, "url": input_data}

        if action == "click":
            return await self.click(data)
        elif action == "type":
            return await self.type(data)
        elif action == "read":
            return await self.read(data)
        elif action == "list_elements":
            return await self.list_elements()
        elif action == "navigate":
            return await self.navigate(data)
        elif action == "powershell":
            return await self.powershell(data)
        else:
            return {"success": False, "error": f"Unknown desktop_control action: '{action}'"}

    async def click(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clicks an element by text, selector, or screen coordinates."""
        x = data.get("x")
        y = data.get("y")
        text = data.get("text")
        
        # Scenario 1: Coordinate Click (Using pyautogui)
        if x is not None and y is not None:
            if pyautogui:
                try:
                    pyautogui.click(int(x), int(y))
                    return {"success": True, "output": f"Clicked at coordinates ({x}, {y})"}
                except Exception as e:
                    return {"success": False, "error": f"Failed coordinate click: {e}"}
            else:
                return {"success": False, "error": "pyautogui is not available for coordinate clicks"}

        # Scenario 2: UI Automation Text Click (Windows UI Automation Tree)
        if uiautomation and text:
            try:
                # Find element in accessibility tree by text
                control = uiautomation.Control(Name=text)
                if control.Exists(maxSearchDepth=8):
                    control.Click()
                    return {"success": True, "output": f"Clicked element '{text}' using UIAutomation"}
            except Exception as e:
                pass  # Fallback to coordinate lookups if available

        # Scenario 3: Fallback finding active window coordinates
        if win32gui and text:
            try:
                # Let's search for a window title matching the text
                hwnd = win32gui.FindWindow(None, text)
                if hwnd:
                    rect = win32gui.GetWindowRect(hwnd)
                    # Get center coordinates of the window
                    cx = (rect[0] + rect[2]) // 2
                    cy = (rect[1] + rect[3]) // 2
                    if pyautogui:
                        pyautogui.click(cx, cy)
                        return {"success": True, "output": f"Found window '{text}' (HWND {hwnd}), clicked center at ({cx}, {cy})"}
            except Exception as e:
                return {"success": False, "error": f"Fallback window search/click failed: {e}"}

        return {"success": False, "error": f"Could not resolve elements or coordinates for click action with input {data}"}

    async def type(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Types text into the focused window or element."""
        text = data.get("text", "")
        selector = data.get("selector")
        
        # If selector target is defined, click it first
        if selector:
            click_res = await self.click({"text": selector})
            if not click_res["success"]:
                # Try clicking by coordinates/etc if defined in input
                pass
        
        if pyautogui and text:
            try:
                pyautogui.write(text, interval=0.02)
                # Press enter if requested
                if data.get("enter", True):
                    pyautogui.press("enter")
                return {"success": True, "output": f"Typed: '{text}'"}
            except Exception as e:
                return {"success": False, "error": f"Failed typing via pyautogui: {e}"}
                
        return {"success": False, "error": "No typing interface available"}

    async def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reads properties of elements matching the selector."""
        selector = data.get("selector", "")
        if uiautomation and selector:
            try:
                control = uiautomation.Control(Name=selector)
                if control.Exists():
                    return {
                        "success": True,
                        "output": f"Element: {selector} | Type: {control.ControlTypeName} | Enabled: {control.IsEnabled} | Rect: {control.BoundingRectangle}"
                    }
            except Exception as e:
                return {"success": False, "error": f"UIAutomation read failed: {e}"}
                
        # Fallback reading foreground window title
        if win32gui:
            try:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                return {"success": True, "output": f"Active Window: '{title}' (HWND {hwnd})"}
            except Exception as e:
                return {"success": False, "error": f"Active window read failed: {e}"}

        return {"success": False, "error": "No UI inspection utilities available"}

    async def list_elements(self) -> Dict[str, Any]:
        """Lists active top-level Windows visual tree controls/windows."""
        results = []
        
        # List windows using win32gui
        if win32gui:
            def enum_cb(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        results.append(f"HWND {hwnd}: '{title}'")
            try:
                win32gui.EnumWindows(enum_cb, None)
                return {"success": True, "output": "\n".join(results[:30])}
            except Exception as e:
                return {"success": False, "error": f"Failed listing windows: {e}"}
                
        return {"success": False, "error": "No active window listing utilities available"}

    async def navigate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Controls browser using Playwright."""
        url = data.get("url")
        if not url:
            return {"success": False, "error": "navigate action requires 'url'"}
            
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                # Run with 15s timeout to prevent hanging offline
                await page.goto(url, timeout=15000)
                title = await page.title()
                content = await page.content()
                
                # Take a snapshot to vision folder for ambient context if needed
                snap_path = "data/vision/playwright_snap.png"
                os.makedirs("data/vision", exist_ok=True)
                await page.screenshot(path=snap_path)
                
                await browser.close()
                return {
                    "success": True,
                    "output": f"Successfully loaded web page: '{title}'\nSnapshot saved to: {snap_path}\nPage content length: {len(content)} chars."
                }
        except Exception as e:
            return {"success": False, "error": f"Playwright browser automation failed: {e}"}

    async def powershell(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs a PowerShell command and returns stdout/stderr."""
        command = data.get("command")
        if not command:
            return {"success": False, "error": "powershell action requires 'command'"}
            
        try:
            process = subprocess.Popen(
                ["powershell", "-Command", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            # Enforce a 15-second timeout to prevent blocking the agent
            stdout, stderr = process.communicate(timeout=15)
            
            if process.returncode == 0:
                return {"success": True, "output": stdout}
            else:
                return {"success": False, "error": f"Exit code {process.returncode}\nError: {stderr}"}
        except subprocess.TimeoutExpired:
            process.kill()
            return {"success": False, "error": "PowerShell command timed out after 15 seconds"}
        except Exception as e:
            return {"success": False, "error": f"PowerShell execution failed: {e}"}
