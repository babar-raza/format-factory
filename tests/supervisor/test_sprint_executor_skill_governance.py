"""test_sprint_executor_skill_governance.py — SFC-GAP-E (2026-07-17).

Covers sprint_executor.py's pre-spawn manifest binding and scoped hash-diff
change detection (the replacement for the rejected git-diff-based provenance
idea, which the plan's red-team review showed is provably unsound in a
shared, non-isolated working tree under 44+ concurrent agents).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

import sprint_executor  # noqa: E402


# ── _hash_snapshot / _diff_snapshots: the core soundness property ─────────

def test_snapshot_scoped_to_declared_patterns_only(tmp_path):
    """A file OUTSIDE the given patterns must never appear in the snapshot --
    this is what makes the diff sound under concurrency: only the narrow,
    authorized scope is ever compared, never the whole repo."""
    (tmp_path / "in_scope").mkdir()
    (tmp_path / "out_of_scope").mkdir()
    (tmp_path / "in_scope" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "out_of_scope" / "b.py").write_text("y = 2\n", encoding="utf-8")

    snap = sprint_executor._hash_snapshot(tmp_path, ["in_scope/"])
    assert "in_scope/a.py" in snap
    assert "out_of_scope/b.py" not in snap


def test_diff_detects_added_removed_changed_files(tmp_path):
    (tmp_path / "scope").mkdir()
    unchanged = tmp_path / "scope" / "unchanged.py"
    unchanged.write_text("same\n", encoding="utf-8")
    to_remove = tmp_path / "scope" / "to_remove.py"
    to_remove.write_text("gone\n", encoding="utf-8")
    to_change = tmp_path / "scope" / "to_change.py"
    to_change.write_text("before\n", encoding="utf-8")

    before = sprint_executor._hash_snapshot(tmp_path, ["scope/"])

    to_remove.unlink()
    to_change.write_text("after\n", encoding="utf-8")
    (tmp_path / "scope" / "added.py").write_text("new\n", encoding="utf-8")

    after = sprint_executor._hash_snapshot(tmp_path, ["scope/"])
    changed = sprint_executor._diff_snapshots(before, after)

    assert "scope/added.py" in changed
    assert "scope/to_remove.py" in changed
    assert "scope/to_change.py" in changed
    assert "scope/unchanged.py" not in changed


def test_concurrent_other_agent_write_outside_scope_not_attributed(tmp_path):
    """The specific regression this design fixes: a DIFFERENT, concurrent
    agent's write to a file outside this sprint's declared allowed_paths must
    never show up as one of THIS sprint's changed files -- unlike a
    time-window git-diff, which would have caught it."""
    (tmp_path / "my_scope").mkdir()
    (tmp_path / "other_agents_area").mkdir()
    before = sprint_executor._hash_snapshot(tmp_path, ["my_scope/"])

    # Simulate: my sprint writes within its own scope...
    (tmp_path / "my_scope" / "mine.py").write_text("my work\n", encoding="utf-8")
    # ...while a DIFFERENT concurrent agent writes somewhere else entirely,
    # in the same shared tree, during the same window.
    (tmp_path / "other_agents_area" / "theirs.py").write_text(
        "someone else's work\n", encoding="utf-8")

    after = sprint_executor._hash_snapshot(tmp_path, ["my_scope/"])
    changed = sprint_executor._diff_snapshots(before, after)

    assert changed == ["my_scope/mine.py"]
    assert not any("other_agents_area" in c for c in changed)


def test_snapshot_sees_uncommitted_changes_directly(tmp_path):
    """Unlike a git-commit-range diff, a content-hash snapshot sees
    uncommitted working-tree edits immediately -- no commit required."""
    (tmp_path / "scope").mkdir()
    f = tmp_path / "scope" / "f.py"
    f.write_text("v1\n", encoding="utf-8")
    before = sprint_executor._hash_snapshot(tmp_path, ["scope/"])
    f.write_text("v2\n", encoding="utf-8")  # never committed
    after = sprint_executor._hash_snapshot(tmp_path, ["scope/"])
    assert sprint_executor._diff_snapshots(before, after) == ["scope/f.py"]


# ── _resolve_sprint_scope: real skill vs. fallback ─────────────────────────

def test_resolve_sprint_scope_falls_back_when_nothing_resolves():
    skill_ids, allowed_paths, decision, rationale = sprint_executor._resolve_sprint_scope(
        "zzz nonsense text matching nothing registered qqq\n", _REPO)
    assert skill_ids == ["autonomous-loop"]
    assert allowed_paths == sprint_executor._FALLBACK_LANE_PATHS
    assert "FALLBACK" in rationale


def test_fallback_scope_is_bounded_not_unbounded():
    """The fallback must be a named, finite list of lanes -- never '**' or
    an unbounded grant, even as a fallback."""
    for p in sprint_executor._FALLBACK_LANE_PATHS:
        assert p not in ("**", "*", "")
        assert not p.startswith("/")


# ── cmd_run_sprint: manifest created BEFORE the subprocess spawns ─────────

def test_manifest_created_before_subprocess_spawn(tmp_path, monkeypatch):
    """Call-order proof: the SFC manifest must exist on disk before the
    (mocked) claude subprocess is ever invoked."""
    repo_root = tmp_path
    (repo_root / "reports" / "supervisor").mkdir(parents=True)
    (repo_root / "reports" / "supervisor" / "next-sprint.md").write_text(
        "Run the governance validators for this sprint.\n", encoding="utf-8")

    call_order = []

    def fake_inject_declaration(sprint_id, repo_root):
        decl_dir = repo_root / ".local" / "evidences" / sprint_id
        decl_dir.mkdir(parents=True, exist_ok=True)
        decl_path = decl_dir / "evidence-declaration.yaml"
        decl_path.write_text("sprint_id: " + sprint_id + "\n", encoding="utf-8")
        return decl_path

    manifest_created_at = []

    def fake_create_manifest(**kwargs):
        manifest_created_at.append("manifest_created")
        return {
            "execution_id": "sfx-test-run-order",
            "schema": "skills-first-control/execution-manifest@1",
        }

    def fake_subprocess_run(*args, **kwargs):
        call_order.append("subprocess_run")
        assert "manifest_created" in manifest_created_at, (
            "subprocess must not spawn before the manifest is created"
        )
        class R:
            returncode = 0
            stdout = "ok"
            stderr = ""
        return R()

    monkeypatch.setattr(sprint_executor, "cmd_inject_declaration",
                        fake_inject_declaration)
    with patch("tools.governance.skills_first.manifest.create_manifest",
              side_effect=fake_create_manifest), \
         patch("subprocess.run", side_effect=fake_subprocess_run):
        result = sprint_executor.cmd_run_sprint("TC-TEST-001", repo_root)

    assert manifest_created_at == ["manifest_created"]
    assert call_order == ["subprocess_run"]
    assert result["sfc_manifest_execution_id"] == "sfx-test-run-order"


def test_manifest_failure_is_non_blocking_sprint_still_runs(tmp_path, monkeypatch):
    """If SFC manifest creation fails for any reason, the sprint must still
    run -- never worse than today's zero-governance baseline."""
    repo_root = tmp_path
    (repo_root / "reports" / "supervisor").mkdir(parents=True)
    (repo_root / "reports" / "supervisor" / "next-sprint.md").write_text(
        "text\n", encoding="utf-8")

    def fake_inject_declaration(sprint_id, repo_root):
        decl_dir = repo_root / ".local" / "evidences" / sprint_id
        decl_dir.mkdir(parents=True, exist_ok=True)
        decl_path = decl_dir / "evidence-declaration.yaml"
        decl_path.write_text("x\n", encoding="utf-8")
        return decl_path

    def fake_subprocess_run(*args, **kwargs):
        class R:
            returncode = 0
            stdout = "ok"
            stderr = ""
        return R()

    monkeypatch.setattr(sprint_executor, "cmd_inject_declaration",
                        fake_inject_declaration)
    with patch("tools.governance.skills_first.manifest.create_manifest",
              side_effect=RuntimeError("boom")), \
         patch("subprocess.run", side_effect=fake_subprocess_run):
        result = sprint_executor.cmd_run_sprint("TC-TEST-002", repo_root)

    assert result["exit_code"] == 0
    assert result["sfc_manifest_execution_id"] is None
