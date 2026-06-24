"""TC-AMD-MACH-001: Tests for pytest/temp path guard in write_plan_lock.py.

Verifies that:
  - _is_temp_path() correctly detects pytest/temp paths
  - Temp paths skip the shared active-plan-lock.json write
  - Real plan paths still write to the shared lock
  - Session-keyed lock is always written (even for temp paths)
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path

import pytest

# Ensure tools/supervisor is on sys.path
_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from write_plan_lock import _is_temp_path, write_lock


# ---------------------------------------------------------------------------
# _is_temp_path detection tests
# ---------------------------------------------------------------------------


def test_is_temp_path_detects_pytest_appdata():
    """Windows pytest temp path is detected as temp."""
    assert _is_temp_path(
        "C:/Users/prora/AppData/Local/Temp/pytest-10380/test_foo_0/plan.md"
    )


def test_is_temp_path_detects_pytest_linux():
    """Linux pytest temp path is detected as temp."""
    assert _is_temp_path("/tmp/pytest-of-user/test_abc_0/plan.md")


def test_is_temp_path_allows_real_plan():
    """Real plan paths are NOT detected as temp."""
    assert not _is_temp_path("plans/recursive-hugging-bird.md")
    assert not _is_temp_path("C:/Users/prora/.claude/plans/recursive-hugging-bird.md")


# ---------------------------------------------------------------------------
# write_lock() shared lock guard tests
# ---------------------------------------------------------------------------


def test_temp_path_skips_shared_lock(tmp_path, monkeypatch):
    """Temp plan paths skip shared lock write; session-keyed lock is still written."""
    import write_plan_lock as wpl

    # Redirect the shared lock and plan-locks dir to tmp_path
    fake_shared = tmp_path / "active-plan-lock.json"
    fake_locks_dir = tmp_path / "plan-locks"

    monkeypatch.setattr(wpl, "_shared_lock_path", fake_shared)
    monkeypatch.setattr(wpl, "_plan_locks_dir", fake_locks_dir)
    monkeypatch.setattr(wpl, "_get_session_id", lambda: "test-session-001")

    # Use a pytest-looking temp path
    temp_plan = str(tmp_path / "pytest-9999" / "test_something_0" / "plan.md")
    write_lock(plan_path=temp_plan)

    # Shared lock must NOT be written
    assert not fake_shared.exists(), "Shared lock should be skipped for temp path"

    # Session-keyed lock MUST be written
    keyed_files = list(fake_locks_dir.glob("*.json"))
    assert len(keyed_files) == 1, "Session-keyed lock should still be written"
    data = json.loads(keyed_files[0].read_text())
    # write_lock() normalizes backslashes to forward slashes (line 150)
    assert data["plan_path"] == temp_plan.replace("\\", "/")
    assert data["status"] == "IN_PROGRESS"


def test_real_path_writes_shared_lock(tmp_path, monkeypatch):
    """Real plan paths write to the shared active-plan-lock.json."""
    import write_plan_lock as wpl

    fake_shared = tmp_path / "active-plan-lock.json"
    fake_locks_dir = tmp_path / "plan-locks"

    monkeypatch.setattr(wpl, "_shared_lock_path", fake_shared)
    monkeypatch.setattr(wpl, "_plan_locks_dir", fake_locks_dir)
    monkeypatch.setattr(wpl, "_get_session_id", lambda: "test-session-002")

    real_plan = "plans/recursive-hugging-bird.md"
    write_lock(plan_path=real_plan)

    # Shared lock MUST be written for real plan
    assert fake_shared.exists(), "Shared lock should be written for real plan path"
    data = json.loads(fake_shared.read_text())
    assert data["plan_path"] == real_plan
    assert data["status"] == "IN_PROGRESS"
