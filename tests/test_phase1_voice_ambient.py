import os
import sys
import asyncio
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock

# Mock modules that might not be available or are system-dependent
sys.modules['sounddevice'] = MagicMock()
sys.modules['soundfile'] = MagicMock()
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
        self.console = MagicMock()
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
        self.voice_task = None
        self.ambient_enabled = False
        self.voice = MagicMock()
        self.ambient = MagicMock()


# 1. Voice Layer Tests
@pytest.mark.asyncio
async def test_voice_layer_init_and_speak():
    mock_kokoro_inst = MagicMock()
    mock_kokoro_inst.create.return_value = (np.zeros(16000), 16000)
    
    with patch('src.services.voice_layer.Kokoro', return_value=mock_kokoro_inst) as mock_kokoro, \
         patch('src.services.voice_layer.sd') as mock_sd, \
         patch('os.path.exists', return_value=True):
         
        voice = VoiceLayer(console=MagicMock())
        await voice.speak("Hello **Architect**, check `this`!")
        
        mock_kokoro_inst.create.assert_called_once()
        args, kwargs = mock_kokoro_inst.create.call_args
        assert "Hello Architect, check this!" in args[0]


@pytest.mark.asyncio
async def test_voice_mute():
    mock_kokoro_inst = MagicMock()
    with patch('src.services.voice_layer.Kokoro', return_value=mock_kokoro_inst) as mock_kokoro, \
         patch('os.path.exists', return_value=True):
        voice = VoiceLayer(console=MagicMock())
        voice.mute(True)
        assert voice._muted is True
        await voice.speak("Hello")
        mock_kokoro_inst.create.assert_not_called()


@pytest.mark.asyncio
async def test_voice_transcribe():
    voice = VoiceLayer(console=MagicMock())
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"text": "hello apex"}
    mock_response.raise_for_status = MagicMock()
    
    with patch('httpx.AsyncClient.post', return_value=mock_response) as mock_post:
        res = await voice._transcribe(np.zeros(16000))
        assert res == "hello apex"


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
    engine.voice = MagicMock()
    engine.voice.run = AsyncMock()
    engine.voice_enabled = False
    
    # Test /voice on
    await handle_slash(engine, "/voice on", "skills")
    assert engine.voice_enabled is True
    assert engine.voice_task is not None
    
    # Test /voice mute
    await handle_slash(engine, "/voice mute", "skills")
    engine.voice.mute.assert_called_with(True)
    
    # Test /voice unmute
    await handle_slash(engine, "/voice unmute", "skills")
    engine.voice.mute.assert_called_with(False)
    
    # Test /voice off
    await handle_slash(engine, "/voice off", "skills")
    assert engine.voice_enabled is False
    engine.voice.stop.assert_called_once()
    assert engine.voice_task.cancelled() or engine.voice_task.cancelling()
