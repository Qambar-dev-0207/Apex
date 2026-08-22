"""
Unit tests for APEX Filesystem CRUD capabilities (Create, Read, Write, Update, Delete),
ParallelExecutor filesystem actions, and AutoToolSelector regex routing.
"""

import os
import json
import tempfile
import shutil
import pytest
from unittest.mock import MagicMock

from src.tools.filesystem import FilesystemAgent
from src.tools.safety import SafetyGuard
from src.tools.auto_selector import regex_match
from src.routers.router import ParallelExecutor


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def fs_agent(temp_dir):
    safety = SafetyGuard(mode="auto-approve")
    return FilesystemAgent(safety=safety)


@pytest.mark.asyncio
async def test_fs_create_file(fs_agent, temp_dir):
    """Test creating empty files and files with initial content in subdirectories."""
    p1 = os.path.join(temp_dir, "sub", "test1.txt")
    res1 = await fs_agent.create_file(p1, content="hello world")
    assert res1["success"] is True
    assert os.path.exists(p1)
    with open(p1, "r", encoding="utf-8") as f:
        assert f.read() == "hello world"

    # Empty file
    p2 = os.path.join(temp_dir, "sub", "empty.py")
    res2 = await fs_agent.create_file(p2)
    assert res2["success"] is True
    assert os.path.exists(p2)


@pytest.mark.asyncio
async def test_fs_create_dir(fs_agent, temp_dir):
    """Test creating nested directories."""
    nested = os.path.join(temp_dir, "nested", "level2", "level3")
    res = await fs_agent.create_dir(nested)
    assert res["success"] is True
    assert os.path.isdir(nested)


@pytest.mark.asyncio
async def test_fs_read_file(fs_agent, temp_dir):
    """Test reading full files and reading line slices."""
    p = os.path.join(temp_dir, "multiline.txt")
    content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
    await fs_agent.write_file(p, content)

    # Full read
    r_full = await fs_agent.read_file(p)
    assert r_full["success"] is True
    assert r_full["output"] == content

    # Line slice [2, 4]
    r_slice = await fs_agent.read_file(p, start_line=2, end_line=4)
    assert r_slice["success"] is True
    assert "Line 2" in r_slice["output"]
    assert "Line 3" in r_slice["output"]
    assert "Line 4" in r_slice["output"]
    assert "Line 1" not in r_slice["raw_content"]

    # Missing file
    r_missing = await fs_agent.read_file(os.path.join(temp_dir, "nonexistent.txt"))
    assert r_missing["success"] is False
    assert "File not found" in r_missing["error"]


@pytest.mark.asyncio
async def test_fs_write_file(fs_agent, temp_dir):
    """Test writing and overwriting files."""
    p = os.path.join(temp_dir, "sample.json")
    res = await fs_agent.write_file(p, '{"apex": "ready"}')
    assert res["success"] is True
    assert res["lines"] == 1
    assert os.path.exists(p)


@pytest.mark.asyncio
async def test_fs_update_file_modes(fs_agent, temp_dir):
    """Test surgical replace, multi-edit batch, append mode, and full replace mode."""
    p = os.path.join(temp_dir, "code.py")
    await fs_agent.write_file(p, "def func_a():\n    return 1\n\ndef func_b():\n    return 2\n")

    # Surgical search & replace
    r_patch = await fs_agent.update_file(p, old_string="return 1", new_string="return 42")
    assert r_patch["success"] is True
    r_read = await fs_agent.read_file(p)
    assert "return 42" in r_read["output"]

    # Append mode
    r_append = await fs_agent.update_file(p, content="def func_c():\n    return 3\n", mode="append")
    assert r_append["success"] is True
    r_read = await fs_agent.read_file(p)
    assert "func_c" in r_read["output"]

    # Multi-edit batch
    r_multi = await fs_agent.update_file(p, edits=[
        {"old_string": "return 42", "new_string": "return 100"},
        {"old_string": "return 2", "new_string": "return 200"},
    ])
    assert r_multi["success"] is True
    r_read = await fs_agent.read_file(p)
    assert "return 100" in r_read["output"]
    assert "return 200" in r_read["output"]


@pytest.mark.asyncio
async def test_fs_edit_file_surgical(fs_agent, temp_dir):
    """Test surgical edit method directly."""
    p = os.path.join(temp_dir, "notes.txt")
    await fs_agent.write_file(p, "title: Draft\nstatus: Incomplete\n")

    r = await fs_agent.edit_file(p, "status: Incomplete", "status: Completed")
    assert r["success"] is True
    r_read = await fs_agent.read_file(p)
    assert "status: Completed" in r_read["output"]

    # Missing old_string error
    r_fail = await fs_agent.edit_file(p, "nonexistent line", "replacement")
    assert r_fail["success"] is False
    assert "not found" in r_fail["error"]


@pytest.mark.asyncio
async def test_fs_delete_file_and_dir(fs_agent, temp_dir):
    """Test deleting single files, empty dirs, and recursive directories."""
    # Delete file
    f = os.path.join(temp_dir, "to_delete.txt")
    await fs_agent.write_file(f, "temp")
    r_del = await fs_agent.delete_file(f)
    assert r_del["success"] is True
    assert not os.path.exists(f)

    # Delete directory recursively
    d = os.path.join(temp_dir, "dir_to_delete")
    sub_f = os.path.join(d, "inner.txt")
    await fs_agent.create_file(sub_f, "inside")
    r_dir_del = await fs_agent.delete_dir(d, recursive=True)
    assert r_dir_del["success"] is True
    assert not os.path.exists(d)


@pytest.mark.asyncio
async def test_parallel_executor_filesystem_crud(temp_dir):
    """Test that ParallelExecutor handles create, read, write, update, delete steps."""
    safety = SafetyGuard(mode="auto-approve")
    executor = ParallelExecutor()
    executor.safety_guard = safety
    executor.fs = FilesystemAgent(safety=safety)

    mock_workspace = MagicMock()
    mock_active = MagicMock()
    mock_active.root_dir = temp_dir
    mock_workspace.get_active.return_value = mock_active
    executor.workspace = mock_workspace

    # 1. Step: create
    step_create = {
        "id": 1,
        "action": "create new file",
        "tool": "filesystem",
        "input_data": json.dumps({"path": "apex_doc.md", "content": "# APEX Architecture"})
    }
    r1 = await executor.execute_step(step_create)
    assert r1["success"] is True
    assert os.path.exists(os.path.join(temp_dir, "apex_doc.md"))

    # 2. Step: read
    step_read = {
        "id": 2,
        "action": "read file",
        "tool": "filesystem",
        "input_data": "apex_doc.md"
    }
    r2 = await executor.execute_step(step_read)
    assert r2["success"] is True
    assert "# APEX Architecture" in r2["output"]

    # 3. Step: update
    step_update = {
        "id": 3,
        "action": "update file",
        "tool": "filesystem",
        "input_data": json.dumps({
            "path": "apex_doc.md",
            "old_string": "# APEX Architecture",
            "new_string": "# APEX Sovereign OS"
        })
    }
    r3 = await executor.execute_step(step_update)
    assert r3["success"] is True

    # 4. Step: verify read
    r_check = await executor.execute_step(step_read)
    assert "# APEX Sovereign OS" in r_check["output"]

    # 5. Step: delete
    step_delete = {
        "id": 4,
        "action": "delete file",
        "tool": "filesystem",
        "input_data": "apex_doc.md"
    }
    r4 = await executor.execute_step(step_delete)
    assert r4["success"] is True
    assert not os.path.exists(os.path.join(temp_dir, "apex_doc.md"))


def test_auto_selector_file_crud_patterns():
    """Test regex matching for create, read, write, and delete single-tool prompts."""
    # Create file
    r_create = regex_match("create file app.py")
    assert r_create is not None
    assert r_create["tool"] == "filesystem"
    assert r_create["action"] == "create"
    assert r_create["input_data"] == "app.py"

    # Touch file
    r_touch = regex_match("touch schema.prisma")
    assert r_touch is not None
    assert r_touch["action"] == "create"

    # Read / View file
    r_read = regex_match("view config.yaml")
    assert r_read is not None
    assert r_read["action"] == "read"

    # Write file
    r_write = regex_match("write file status.txt: all systems online")
    assert r_write is not None
    assert r_write["tool"] == "filesystem"
    assert r_write["action"] == "write"
    parsed_write = json.loads(r_write["input_data"])
    assert parsed_write["path"] == "status.txt"
    assert parsed_write["content"] == "all systems online"

    # Delete file
    r_del = regex_match("delete file old_log.log")
    assert r_del is not None
    assert r_del["tool"] == "filesystem"
    assert r_del["action"] == "delete"
    assert r_del["input_data"] == "old_log.log"

    # Rm file
    r_rm = regex_match("rm temp.py")
    assert r_rm is not None
    assert r_rm["action"] == "delete"
