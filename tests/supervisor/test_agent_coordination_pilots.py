"""TC-COORD-011: pytest harness for the 16-proof coordination pilot.

Mission AGENT-COORD-2026-07-15. The standalone script is the evidence
producer (reports/coordination/pilot-evidence/); this wrapper makes the
proofs part of the regression suite and additionally verifies the hook
script contract exactly as Claude Code invokes it (direct script execution,
JSON on stdin).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_PILOT = _REPO / "tests" / "supervisor" / "pilots" / "run_coordination_pilot.py"
_GATE = _REPO / "tools" / "supervisor" / "coordination" / "hooks" / "gate.py"


def test_pilot_suite_all_16_proofs_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("FF_AGENT_COORDINATION_ROOT",
                       str(tmp_path / "pilot-root-unused"))
    result = subprocess.run(
        [sys.executable, str(_PILOT)], capture_output=True, text=True,
        cwd=str(_REPO), timeout=600)
    assert result.returncode == 0, (
        f"pilot suite failed\nstdout:\n{result.stdout[-4000:]}\n"
        f"stderr:\n{result.stderr[-2000:]}")
    assert "16/16 proofs PASS" in result.stdout


def test_gate_script_direct_invocation_contract(tmp_path):
    """Run gate.py the way the settings.json hook does: as a script with the
    payload on stdin. Proves the sys.path bootstrap and exit codes."""
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "src").mkdir()

    def invoke(payload: dict | str) -> subprocess.CompletedProcess:
        raw = payload if isinstance(payload, str) else json.dumps(payload)
        env = {"FF_AGENT_COORDINATION_ROOT": str(root),
               "SYSTEMROOT": "C:\\Windows", "PATH": ""}
        import os
        env = {**os.environ, "FF_AGENT_COORDINATION_ROOT": str(root)}
        return subprocess.run([sys.executable, str(_GATE)], input=raw,
                              capture_output=True, text=True, env=env,
                              cwd=str(repo), timeout=60)

    # SessionStart bootstraps the db and registers the session agent.
    r = invoke({"hook_event_name": "SessionStart", "session_id": "s-sub",
                "cwd": str(repo)})
    assert r.returncode == 0, r.stderr
    assert (root / "coordination.db").exists()

    # Free-file write auto-claims (exit 0).
    r = invoke({"hook_event_name": "PreToolUse", "session_id": "s-sub",
                "cwd": str(repo), "tool_name": "Write",
                "tool_input": {"file_path": str(repo / "src" / "n.py")}})
    assert r.returncode == 0, r.stderr

    # Malformed stdin fails open (exit 0) with an incident record.
    r = invoke("this is not json")
    assert r.returncode == 0
    assert (root / "hook-incidents.jsonl").exists()
