"""TC-AMD-MCP-001: Tests for mcp_bridge.py.

Verifies:
  - TOOLS list contains exactly 3 tools
  - get_sprint_verdict reads maturity-signal.json content
  - get_work_item_grade returns error dict (not exception) when file missing
  - unknown tool name returns error dict (not exception)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from mcp_bridge import TOOLS, handle_call


def test_tools_list_returns_three_tools():
    """TOOLS constant has exactly 3 read-only tools defined."""
    assert len(TOOLS) == 3
    names = {t["name"] for t in TOOLS}
    assert "format_factory__get_sprint_verdict" in names
    assert "format_factory__get_next_work_items" in names
    assert "format_factory__get_work_item_grade" in names


def test_get_sprint_verdict_reads_signal_file(tmp_path, monkeypatch):
    """Returns maturity-signal.json content when file exists."""
    import mcp_bridge as mb
    signal_data = {
        "schema": "format-factory-maturity-signal/v1",
        "sprint_verdict": "ACCEPTED_VERIFIED",
        "autonomous_continue": True,
    }
    sig_dir = tmp_path / "reports" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "maturity-signal.json").write_text(json.dumps(signal_data), encoding="utf-8")

    monkeypatch.setattr(mb, "_REPO", tmp_path)
    result = mb.handle_call("format_factory__get_sprint_verdict", {})
    assert result["sprint_verdict"] == "ACCEPTED_VERIFIED"


def test_get_work_item_grade_not_found(tmp_path, monkeypatch):
    """Returns error dict (not exception) when work-item-grades.md is missing."""
    import mcp_bridge as mb
    monkeypatch.setattr(mb, "_REPO", tmp_path)

    result = handle_call("format_factory__get_work_item_grade", {"item_id": "TC-MISSING-001"})
    assert "error" in result
    assert isinstance(result["error"], str)


def test_handle_call_unknown_tool():
    """Unknown tool name returns error dict, never raises."""
    result = handle_call("format_factory__nonexistent_tool", {})
    assert "error" in result
    assert "unknown_tool" in result["error"]
