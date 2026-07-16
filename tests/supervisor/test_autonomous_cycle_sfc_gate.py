"""test_autonomous_cycle_sfc_gate.py — SFC-GAP-E (2026-07-17).

Covers evaluate_sfc_closeout_gate() (autonomous_cycle.py) -- the acceptance
gate that decides whether an autonomous sprint's ledger update proceeds,
based on the SFC closeout gate evaluated against sprint_executor.py's
independently-computed changed-files list.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

import autonomous_cycle  # noqa: E402


def _an_active_skill():
    sys.path.insert(0, str(_REPO))
    from tools.governance.skills_first.registries import load_skills
    for s in load_skills():
        if s.is_active and s.command_file and (_REPO / s.command_file).exists():
            return s.skill_id
    pytest.skip("no active skill with on-disk command file")


def _make_declaration_dir(tmp_path):
    d = tmp_path / "evidences" / "TC-E2E-001"
    d.mkdir(parents=True)
    decl = d / "evidence-declaration.yaml"
    decl.write_text("sprint_id: TC-E2E-001\n", encoding="utf-8")
    return decl


def test_missing_sidecar_files_returns_inert_result(tmp_path):
    """No sfc-manifest-id.txt at all -> today's exact behavior: no gate, no
    block, nothing to see here."""
    decl = _make_declaration_dir(tmp_path)
    result = autonomous_cycle.evaluate_sfc_closeout_gate(decl, _REPO)
    assert result["gate_result"] is None
    assert result["governance_blocked"] is False
    assert result["error"] is None


def test_close_ok_scoped_and_evidenced(tmp_path):
    decl = _make_declaration_dir(tmp_path)
    sys.path.insert(0, str(_REPO))
    from tools.governance.skills_first.manifest import create_manifest

    m = create_manifest(
        task_id="TC-E2E-001", agent_type="LOCAL_AUTOMATION",
        requested_operation="test", selected_skill_ids=[_an_active_skill()],
        allowed_paths=["tools/governance/skills_first/**"], write=True)
    (decl.parent / "sfc-manifest-id.txt").write_text(
        m["execution_id"], encoding="utf-8")
    (decl.parent / "sfc-changed-files.json").write_text(
        json.dumps(["tools/governance/skills_first/audit.py"]),
        encoding="utf-8")

    with patch("builtins.print"):
        result = autonomous_cycle.evaluate_sfc_closeout_gate(decl, _REPO)

    assert result["gate_result"]["verdict"] == "CLOSE_OK"
    assert result["governance_blocked"] is False


def test_close_blocked_out_of_scope_change_advisory_does_not_block_by_default(tmp_path):
    """Default check_mode (advisory) must surface CLOSE_BLOCKED for
    visibility but NOT set governance_blocked=True -- promotion to enforcing
    is a separate decision."""
    decl = _make_declaration_dir(tmp_path)
    sys.path.insert(0, str(_REPO))
    from tools.governance.skills_first.manifest import create_manifest

    m = create_manifest(
        task_id="TC-E2E-001", agent_type="LOCAL_AUTOMATION",
        requested_operation="test", selected_skill_ids=[_an_active_skill()],
        allowed_paths=["tools/governance/skills_first/**"], write=True)
    (decl.parent / "sfc-manifest-id.txt").write_text(
        m["execution_id"], encoding="utf-8")
    (decl.parent / "sfc-changed-files.json").write_text(
        json.dumps(["src/python/fods/models.py"]),  # out of scope
        encoding="utf-8")

    with patch("builtins.print"):
        result = autonomous_cycle.evaluate_sfc_closeout_gate(decl, _REPO)

    assert result["gate_result"]["verdict"] == "CLOSE_BLOCKED"
    assert result["check_mode"] == "advisory"
    assert result["governance_blocked"] is False


def test_close_blocked_out_of_scope_blocks_when_check_mode_enforcing(tmp_path, monkeypatch):
    """Uses a REAL, isolated coordination root (via FF_AGENT_COORDINATION_ROOT)
    rather than patching by dotted string path -- the SFC gate function does a
    local `from tools.supervisor.coordination.db import ...`, and whether that
    resolves to the same module object mock.patch() targets depends on prior
    import order elsewhere in the test session; exercising the real function
    against real (but isolated) state sidesteps that ambiguity entirely."""
    sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
    from coordination import db as cdb
    from coordination.root import ENV_ROOT

    coord_root = tmp_path / "coord"
    monkeypatch.setenv(ENV_ROOT, str(coord_root))
    cdb.ensure_db(coord_root)
    conn = cdb.connect(coord_root)
    try:
        cdb.set_check_mode(conn, "sprint_closeout_governance", "enforcing",
                           "test", "promotion test")
    finally:
        conn.close()

    decl = _make_declaration_dir(tmp_path)
    sys.path.insert(0, str(_REPO))
    from tools.governance.skills_first.manifest import create_manifest

    m = create_manifest(
        task_id="TC-E2E-001", agent_type="LOCAL_AUTOMATION",
        requested_operation="test", selected_skill_ids=[_an_active_skill()],
        allowed_paths=["tools/governance/skills_first/**"], write=True)
    (decl.parent / "sfc-manifest-id.txt").write_text(
        m["execution_id"], encoding="utf-8")
    (decl.parent / "sfc-changed-files.json").write_text(
        json.dumps(["src/python/fods/models.py"]), encoding="utf-8")

    with patch("builtins.print"):
        result = autonomous_cycle.evaluate_sfc_closeout_gate(decl, _REPO)

    assert result["gate_result"]["verdict"] == "CLOSE_BLOCKED"
    assert result["check_mode"] == "enforcing"
    assert result["governance_blocked"] is True


def test_missing_evidence_creation_error_is_non_blocking(tmp_path):
    """A manifest-id sidecar pointing at a NONEXISTENT manifest must be
    reported as an error, not crash the caller."""
    decl = _make_declaration_dir(tmp_path)
    (decl.parent / "sfc-manifest-id.txt").write_text(
        "sfx-does-not-exist-anywhere", encoding="utf-8")

    with patch("builtins.print"):
        result = autonomous_cycle.evaluate_sfc_closeout_gate(decl, _REPO)

    assert result["gate_result"] is None
    assert result["error"] is not None
    assert result["governance_blocked"] is False
