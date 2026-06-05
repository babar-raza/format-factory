"""
R100 — MCP Status Classifier Unit Tests
Tests check_mcp_status() for all 6 classification states.
"""
import sys
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from check_mcp_status import check_mcp_status, read_current_mode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_repo(tmp_path, mode=0, mcp_json=None, policies=None):
    """Create a minimal repo structure for testing."""
    # .supervisor/config.yaml
    config_dir = tmp_path / ".supervisor"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_text = f"# Config\nStatus: MODE {mode}\n"
    (config_dir / "config.yaml").write_text(config_text, encoding="utf-8")

    # .vscode/mcp.json (optional)
    if mcp_json is not None:
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        (vscode_dir / "mcp.json").write_text(json.dumps(mcp_json), encoding="utf-8")

    # .supervisor/policies.yaml (optional)
    if policies is not None:
        (config_dir / "policies.yaml").write_text(
            yaml.dump(policies), encoding="utf-8"
        )

    return tmp_path


# ---------------------------------------------------------------------------
# read_current_mode
# ---------------------------------------------------------------------------

def test_read_mode_from_config(tmp_path):
    _setup_repo(tmp_path, mode=3)
    assert read_current_mode(tmp_path) == 3


def test_read_mode_missing_config(tmp_path):
    assert read_current_mode(tmp_path) == 0


# ---------------------------------------------------------------------------
# check_mcp_status — all 6 states
# ---------------------------------------------------------------------------

def test_mcp_disabled():
    """MODE < 4, no mcp.json → MCP_DISABLED."""
    repo = _setup_repo(Path(__import__("tempfile").mkdtemp()), mode=2)
    status = check_mcp_status(repo)
    assert status["classification"] == "MCP_DISABLED"
    assert status["mode"] == 2
    assert status["file_present"] is False


def test_mcp_config_missing():
    """MODE >= 4 but no mcp.json → MCP_CONFIG_MISSING."""
    repo = _setup_repo(Path(__import__("tempfile").mkdtemp()), mode=4)
    status = check_mcp_status(repo)
    assert status["classification"] == "MCP_CONFIG_MISSING"
    assert status["mode"] == 4


def test_mcp_config_present_not_active():
    """mcp.json present but MODE < 4 → MCP_CONFIG_PRESENT_NOT_ACTIVE."""
    repo = _setup_repo(
        Path(__import__("tempfile").mkdtemp()),
        mode=2,
        mcp_json={"servers": {"test": {"type": "stdio", "command": "node"}}},
    )
    status = check_mcp_status(repo)
    assert status["classification"] == "MCP_CONFIG_PRESENT_NOT_ACTIVE"
    assert status["file_present"] is True
    assert status["server_count"] == 1


def test_mcp_config_present_mode4_active():
    """mcp.json present and MODE 4+ → MCP_CONFIG_PRESENT_MODE4_ACTIVE."""
    repo = _setup_repo(
        Path(__import__("tempfile").mkdtemp()),
        mode=4,
        mcp_json={"servers": {
            "srv1": {"type": "stdio", "command": "node"},
            "srv2": {"type": "sse", "command": "python"},
        }},
    )
    status = check_mcp_status(repo)
    assert status["classification"] == "MCP_CONFIG_PRESENT_MODE4_ACTIVE"
    assert status["server_count"] == 2
    server_names = [s["name"] for s in status["servers"]]
    assert "srv1" in server_names
    assert "srv2" in server_names


def test_mcp_misconfigured():
    """mcp.json present but invalid JSON → MCP_MISCONFIGURED."""
    import tempfile
    repo = Path(tempfile.mkdtemp())
    _setup_repo(repo, mode=4)
    vscode_dir = repo / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    (vscode_dir / "mcp.json").write_text("{invalid json!!!", encoding="utf-8")

    status = check_mcp_status(repo)
    assert status["classification"] == "MCP_MISCONFIGURED"
    assert status["file_present"] is True


def test_mcp_blocked_policy():
    """Policy blocks MCP and MODE < 4 → MCP_BLOCKED_POLICY."""
    repo = _setup_repo(
        Path(__import__("tempfile").mkdtemp()),
        mode=3,
        policies={
            "autonomous_continuation": {
                "hard_prohibitions": ["mcp_activation_beyond_mode_3"],
            }
        },
    )
    status = check_mcp_status(repo)
    assert status["classification"] == "MCP_BLOCKED_POLICY"
    assert status["mode"] == 3


def test_mcp_blocked_policy_not_triggered_at_mode4():
    """Policy has mcp block but MODE >= 4 means it doesn't apply → normal classification."""
    repo = _setup_repo(
        Path(__import__("tempfile").mkdtemp()),
        mode=4,
        policies={
            "autonomous_continuation": {
                "hard_prohibitions": ["mcp_activation_beyond_mode_3"],
            }
        },
    )
    status = check_mcp_status(repo)
    # MODE 4 + no mcp.json → MCP_CONFIG_MISSING (not blocked)
    assert status["classification"] == "MCP_CONFIG_MISSING"


def test_mcp_status_has_timestamp():
    """All statuses include a timestamp."""
    repo = _setup_repo(Path(__import__("tempfile").mkdtemp()), mode=0)
    status = check_mcp_status(repo)
    assert "timestamp" in status
    assert len(status["timestamp"]) > 10
