import os
import sys
import asyncio
import queue
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock

# Mock modules that might not be available or are system-dependent
# This MUST be done before importing modules that load them
sys.modules['sounddevice'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['win32gui'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['win32api'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['win32com'] = MagicMock()
sys.modules['win32com.client'] = MagicMock()
sys.modules['uiautomation'] = MagicMock()

from src.services.voice_layer import VoiceLayer
from src.services.ambient import AmbientService
from src.tools.desktop_control import DesktopControlTool
from main import APEXEngine, handle_slash


class MockEngine:
    def __init__(self):
        self.hooks = MagicMock()
        self.hooks.fire = AsyncMock()
        self.retina = MagicMock()
        self.retina.capture_screen = MagicMock(return_value="mock_screen.png")
        self.workspace = MagicMock()
        self.workspace.get_active = MagicMock(return_value=None)
        self.session_id = "test-session"
        self.groq_client = MagicMock()
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
        self.input_queue = asyncio.Queue()
        self.voice_enabled = False
        self.ambient_enabled = False
        self.voice = MagicMock()
        self.ambient = MagicMock()


# 1. Voice Layer Tests
def test_voice_layer_init_and_speak():
    with patch('src.services.voice_layer.win32com') as mock_win32com, \
         patch('src.services.voice_layer.kokoro_onnx', None):
        mock_sapi = MagicMock()
        mock_win32com.client = MagicMock()
        mock_win32com.Dispatch.return_value = mock_sapi
        mock_sapi.GetVoices.return_value.Count = 1
        mock_sapi.GetVoices.return_value.Item.return_value.GetDescription.return_value = "Microsoft David Desktop"
        
        voice = VoiceLayer(MockEngine())
        assert voice.sapi_speaker == mock_sapi
        
        # Test markdown cleaning & queuing
        voice.speak("Hello **Architect**, check `this` [link](http://test.com)!")
        assert not voice.speak_queue.empty()
        item = voice.speak_queue.get()
        assert item == "Hello Architect, check this link!"
        
        # Test stop
        voice.start(lambda x: None)
        assert voice.is_active is True
        voice.stop()
        assert voice.is_active is False


def test_voice_layer_transcribe_fallback():
    engine = MockEngine()
    voice = VoiceLayer(engine)
    voice.whisper_model = None
    voice._mock_transcription = "test response"
    
    # Force mock transcription path
    with patch('sys.argv', ['test']), patch('os.getenv', return_value=None):
        transcript = voice._transcribe(np.zeros(16000))
        assert transcript == "test response"


# 2. Ambient Layer Tests
@pytest.mark.asyncio
async def test_ambient_service_watcher_loops():
    engine = MockEngine()
    ambient = AmbientService(engine)
    
    # Mock pyperclip
    import pyperclip
    pyperclip.paste = MagicMock(return_value="mock_clipboard_data")
    
    # Mock win32gui
    import win32gui
    win32gui.GetForegroundWindow = MagicMock(return_value=12345)
    win32gui.GetWindowText = MagicMock(return_value="VS Code")
    
    # Mock psutil
    import psutil
    mock_process = MagicMock()
    mock_process.name.return_value = "code.exe"
    psutil.Process.return_value = mock_process
    
    # Start and verify setup
    ambient.start()
    assert ambient.is_active is True
    assert ambient.last_clipboard == "mock_clipboard_data"
    
    # Stop background watchers so they do not run indefinitely
    ambient.stop()
    assert ambient.is_active is False
    
    # Test clipboard change detection manually (exactly one iteration)
    ambient.is_active = True
    def side_effect():
        ambient.is_active = False
        return "new_clipboard_data"
    pyperclip.paste = MagicMock(side_effect=side_effect)
    
    await ambient._clipboard_watcher_loop()
    # Should trigger hook fire
    engine.hooks.fire.assert_any_call("AmbientClipboardChange", {
        "content": "new_clipboard_data",
        "length": 18
    })


# 3. Desktop Control Tool Tests
@pytest.mark.asyncio
async def test_desktop_control_click_and_type():
    tool = DesktopControlTool()
    
    with patch('src.tools.desktop_control.pyautogui') as mock_pyautogui:
        # Test coord click
        res = await tool.execute("click", '{"x": 100, "y": 200}')
        assert res["success"] is True
        mock_pyautogui.click.assert_called_with(100, 200)
        
        # Test type
        res_type = await tool.execute("type", '{"text": "Hello World", "enter": true}')
        assert res_type["success"] is True
        mock_pyautogui.write.assert_called_with("Hello World", interval=0.02)
        mock_pyautogui.press.assert_called_with("enter")


@pytest.mark.asyncio
async def test_desktop_control_powershell():
    tool = DesktopControlTool()
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("powershell_output", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        res = await tool.execute("powershell", '{"command": "Get-Process"}')
        assert res["success"] is True
        assert res["output"] == "powershell_output"


# 4. Integration Tests
@pytest.mark.asyncio
async def test_main_slash_commands():
    engine = MockEngine()
    engine.console = MagicMock()
    
    # Configure mock voice/ambient start and stop behaviors
    engine.voice.is_active = False
    engine.ambient.is_active = False
    engine.voice.start.side_effect = lambda *a, **k: setattr(engine.voice, 'is_active', True)
    engine.voice.stop.side_effect = lambda *a, **k: setattr(engine.voice, 'is_active', False)
    engine.ambient.start.side_effect = lambda *a, **k: setattr(engine.ambient, 'is_active', True)
    engine.ambient.stop.side_effect = lambda *a, **k: setattr(engine.ambient, 'is_active', False)
    
    # Test /voice on/off
    await handle_slash(engine, "/voice on", "skills")
    assert engine.voice_enabled is True
    assert engine.voice.is_active is True
    
    await handle_slash(engine, "/voice off", "skills")
    assert engine.voice_enabled is False
    assert engine.voice.is_active is False
    
    # Test /ambient on/off
    await handle_slash(engine, "/ambient on", "skills")
    assert engine.ambient_enabled is True
    assert engine.ambient.is_active is True
    
    await handle_slash(engine, "/ambient off", "skills")
    assert engine.ambient_enabled is False
    assert engine.ambient.is_active is False
