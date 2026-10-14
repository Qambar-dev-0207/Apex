"""
Comprehensive test suite for APEX AppLauncher Service, Tool Integration, and Security Guardrails.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

from src.services.app_launcher import (
    AppLauncherService,
    AppRecord,
    DENIED_BINARIES,
    BUILTIN_APPS,
)
from src.tools.desktop_control import DesktopControlTool
from src.tools.auto_selector import regex_match
from src.tools.registry import REGISTRY, resolve_tool_name


@pytest.fixture
def test_launcher(tmp_path):
    """Fixture providing an isolated AppLauncherService with a temporary cache file."""
    cache_file = str(tmp_path / "test_apps_cache.json")
    launcher = AppLauncherService(cache_file=cache_file)
    return launcher


# ── 1. Core Service & Normalization Tests ────────────────────────────────────

def test_key_normalization():
    assert AppLauncherService.normalize_key("  Visual Studio Code (64-bit)!  ") == "visual studio code 64 bit"
    assert AppLauncherService.compact_key("Visual Studio Code (64-bit)!") == "visualstudiocode64bit"
    assert AppLauncherService.normalize_key("") == ""
    assert AppLauncherService.compact_key("") == ""


def test_alias_generation(test_launcher):
    aliases = test_launcher._generate_aliases("Visual Studio Code", executable="Code.exe")
    assert "visual studio code" in aliases
    assert "visualstudiocode" in aliases
    assert "vscode" in aliases
    assert "code" in aliases

    chrome_aliases = test_launcher._generate_aliases("Google Chrome", executable="chrome.exe")
    assert "google chrome" in aliases or "google chrome" in chrome_aliases
    assert "chrome" in chrome_aliases
    assert "browser" in chrome_aliases


def test_builtins_indexed(test_launcher):
    """Verify built-in system tools are present."""
    calc_res = test_launcher.find_app("calc")
    assert calc_res is not None
    app, conf, mtype = calc_res
    assert app.name == "Calculator"
    assert conf == 1.0

    notepad_res = test_launcher.find_app("notepad")
    assert notepad_res is not None
    assert notepad_res[0].name == "Notepad"

    terminal_res = test_launcher.find_app("terminal")
    assert terminal_res is not None


# ── 2. Retrieval & Matching Tests ───────────────────────────────────────────

def test_exact_hash_resolution(test_launcher):
    """Verify O(1) exact hash match occurs with confidence 1.0."""
    res = test_launcher.find_app("notepad")
    assert res is not None
    app, conf, mtype = res
    assert app.name == "Notepad"
    assert conf == 1.0
    assert mtype in ("exact_hash", "compact_hash")


def test_semantic_alias_resolution(test_launcher):
    """Verify semantic task keywords map to canonical defaults."""
    res = test_launcher.find_app("notes")
    assert res is not None
    app, conf, mtype = res
    assert app.name == "Notepad"

    res_tasks = test_launcher.find_app("tasks")
    assert res_tasks is not None
    assert res_tasks[0].name == "Task Manager"


def test_fuzzy_matching_typos(test_launcher):
    """Verify SequenceMatcher / Levenshtein catches typos with >= 0.65 confidence."""
    # Typo: notepadd -> Notepad
    res = test_launcher.find_app("notepadd")
    assert res is not None
    app, conf, mtype = res
    assert app.name == "Notepad"
    assert conf >= 0.70
    assert "fuzzy" in mtype

    # Typo: calculater -> Calculator
    res_calc = test_launcher.find_app("calculater")
    assert res_calc is not None
    assert res_calc[0].name == "Calculator"
    assert res_calc[1] >= 0.75


def test_unknown_app_returns_none(test_launcher):
    res = test_launcher.find_app("completely_nonexistent_xyz_app_123456")
    assert res is None


# ── 3. Security & Safety Guardrail Tests ────────────────────────────────────

def test_command_injection_rejected(test_launcher):
    """Verify shell metacharacters in query are immediately blocked."""
    injection_queries = [
        "calc & format C:",
        "notepad; rm -rf /",
        "chrome | powershell",
        "calc `calc`",
        "app $EVIL",
        "notepad > out.txt",
    ]
    for q in injection_queries:
        res = test_launcher.launch_app(q)
        assert res["success"] is False
        assert "disallowed command injection" in res["error"].lower()


def test_argument_injection_rejected(test_launcher):
    """Verify dangerous shell metacharacters in arguments are blocked."""
    res = test_launcher.launch_app("notepad", args="test.txt; rm -rf /")
    assert res["success"] is False
    assert "disallowed shell injection" in res["error"].lower()


def test_denied_binaries_blocked(test_launcher):
    """Verify prohibited destructive binaries cannot be indexed or launched."""
    for binary in DENIED_BINARIES:
        assert test_launcher._is_excluded("Test Tool", f"C:\\Windows\\System32\\{binary}") is True

    # Attempt to manually create a fake record pointing to a denied binary
    fake_app = AppRecord(
        id="evil_format",
        name="Format Utility",
        target="C:\\Windows\\System32\\format.com",
        source="system",
        launch_type="direct",
        aliases=["format"],
    )
    test_launcher.apps["evil_format"] = fake_app
    test_launcher._hash_map["format"] = fake_app

    launch_res = test_launcher.launch_app("format")
    assert launch_res["success"] is False
    assert "security policy blocked" in launch_res["error"].lower()


def test_uninstaller_filtering(test_launcher):
    """Verify uninstallers and setup assistants are filtered during discovery."""
    assert test_launcher._is_excluded("Uninstall Chrome", "C:\\Google\\unins000.exe") is True
    assert test_launcher._is_excluded("App Setup Assistant", "C:\\Setup\\installer.exe") is True
    assert test_launcher._is_excluded("Crash Reporter", "C:\\App\\crashpad_handler.exe") is True


def test_uwp_malicious_appid_rejected(test_launcher):
    """Verify UWP AppID syntax is strictly checked against malicious characters."""
    bad_uwp = AppRecord(
        id="bad_uwp",
        name="Bad App",
        target="malicious&cmd.exe/c calc",
        source="uwp",
        launch_type="uwp",
        aliases=["badapp"],
    )
    test_launcher.apps["bad_uwp"] = bad_uwp
    test_launcher._hash_map["badapp"] = bad_uwp

    res = test_launcher.launch_app("badapp")
    assert res["success"] is False
    assert "invalid uwp appid syntax" in res["error"].lower()


# ── 4. Cache & Persistence Tests ────────────────────────────────────────────

def test_cache_save_and_load(tmp_path):
    cache_path = str(tmp_path / "apps_cache.json")
    launcher1 = AppLauncherService(cache_file=cache_path)
    assert os.path.exists(cache_path)

    # Verify cache file size is microscopic (< 500 KB)
    cache_size_kb = os.path.getsize(cache_path) / 1024
    assert cache_size_kb < 500.0

    # Load in new instance
    launcher2 = AppLauncherService(cache_file=cache_path)
    assert len(launcher2.apps) == len(launcher1.apps)
    assert len(launcher2._hash_map) == len(launcher1._hash_map)

    # Test resolution from loaded cache
    res = launcher2.find_app("calc")
    assert res is not None
    assert res[0].name == "Calculator"


# ── 5. Integration Tests: Tool Registry, Router, & AutoSelector ─────────────

def test_tool_registry_registration():
    assert "app_launcher" in REGISTRY
    spec = REGISTRY["app_launcher"]
    assert "launch" in spec.actions
    assert "search" in spec.actions
    assert "list" in spec.actions
    assert "open_app" in spec.aliases
    assert "apps" in spec.aliases


def test_desktop_control_integration(test_launcher):
    desktop = DesktopControlTool(app_launcher=test_launcher)
    # List apps action
    import asyncio
    list_res = asyncio.run(desktop.execute("list_apps", ""))
    assert list_res["success"] is True
    assert list_res["total_count"] > 0

    # Search app action
    search_res = asyncio.run(desktop.execute("search_app", "calc"))
    assert search_res["success"] is True
    assert search_res["app"]["name"] == "Calculator"


def test_auto_selector_tier1_matching():
    """Verify tier-1 regex matching in AutoToolSelector dispatches to app_launcher."""
    # App launch queries
    m_spotify = regex_match("open spotify")
    assert m_spotify is not None
    assert m_spotify["tool"] == "app_launcher"
    assert m_spotify["action"] == "launch"
    assert m_spotify["input_data"] == "spotify"

    m_chrome = regex_match("launch chrome")
    assert m_chrome is not None
    assert m_chrome["tool"] == "app_launcher"
    assert m_chrome["action"] == "launch"
    assert m_chrome["input_data"] == "chrome"

    m_calc = regex_match("start the calculator app")
    assert m_calc is not None
    assert m_calc["tool"] == "app_launcher"
    assert m_calc["action"] == "launch"
    assert m_calc["input_data"] == "calculator"

    # Search & list queries
    m_search = regex_match("search app editor")
    assert m_search is not None
    assert m_search["tool"] == "app_launcher"
    assert m_search["action"] == "search"
    assert m_search["input_data"] == "editor"

    m_list = regex_match("list installed apps")
    assert m_list is not None
    assert m_list["tool"] == "app_launcher"
    assert m_list["action"] == "list"

    # CRITICAL: Verify file operations still route to filesystem:read and do not collide
    m_file = regex_match("open src/main.py")
    assert m_file is not None
    assert m_file["tool"] == "filesystem"
    assert m_file["action"] == "read"
    assert m_file["input_data"] == "src/main.py"
