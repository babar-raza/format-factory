"""Unit tests — Skills-First Control: execution manifest + resolution.

Covers the fail-closed manifest creation/validation contract and deterministic
skill resolution (docs/governance/skill-only-policy.yaml sections 4 + 6).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance.skills_first import manifest as M  # noqa: E402
from tools.governance.skills_first import resolve as R  # noqa: E402
from tools.governance.skills_first.registries import load_skills  # noqa: E402


def _an_active_skill() -> str:
    for s in load_skills():
        if s.is_active and s.command_file and (REPO_ROOT / s.command_file).exists():
            return s.skill_id
    pytest.skip("no active skill with on-disk command file")


# ── manifest creation: happy path ──────────────────────────────────────────

def test_create_manifest_binds_skill_and_hash():
    sid = _an_active_skill()
    m = M.create_manifest(
        task_id="TC-UT-001", agent_type="CLAUDE_CODE",
        requested_operation="unit test", selected_skill_ids=[sid],
        allowed_paths=["tools/governance/**"], write=False)
    assert m["status"] == "CREATED"
    assert sid in m["skill_hashes"] and len(m["skill_hashes"][sid]) == 64
    assert m["schema"] == M.SCHEMA_CONST
    assert M.validate_manifest(m) == []


# ── manifest creation: fail-closed rejections ──────────────────────────────

def test_create_manifest_rejects_empty_skill_list():
    with pytest.raises(M.ManifestError):
        M.create_manifest(task_id="T", agent_type="CLAUDE_CODE",
                          requested_operation="x", selected_skill_ids=[],
                          allowed_paths=["a/**"])


def test_create_manifest_rejects_unregistered_skill():
    with pytest.raises(M.ManifestError):
        M.create_manifest(task_id="T", agent_type="CLAUDE_CODE",
                          requested_operation="x",
                          selected_skill_ids=["not-a-real-skill-xyz"],
                          allowed_paths=["a/**"])


def test_create_manifest_rejects_empty_allowed_paths():
    sid = _an_active_skill()
    with pytest.raises(M.ManifestError):
        M.create_manifest(task_id="T", agent_type="CLAUDE_CODE",
                          requested_operation="x", selected_skill_ids=[sid],
                          allowed_paths=[""])  # empty string filtered -> empty


def test_create_manifest_rejects_bad_agent_type():
    sid = _an_active_skill()
    with pytest.raises(M.ManifestError):
        M.create_manifest(task_id="T", agent_type="ROGUE",
                          requested_operation="x", selected_skill_ids=[sid],
                          allowed_paths=["a/**"])


# ── manifest validation: schema violations ─────────────────────────────────

def test_validate_manifest_flags_missing_hash():
    sid = _an_active_skill()
    m = M.create_manifest(task_id="T", agent_type="CLAUDE_CODE",
                          requested_operation="x", selected_skill_ids=[sid],
                          allowed_paths=["a/**"])
    m["skill_hashes"] = {}  # strip the hash
    errs = M.validate_manifest(m)
    assert any("no captured skill hash" in e for e in errs)


def test_validate_manifest_flags_bad_status_and_schema():
    m = {"schema": "wrong", "execution_id": "sfx-1", "task_id": "T",
         "agent_type": "CLAUDE_CODE", "requested_operation": "x",
         "selected_skill_ids": ["s"], "skill_hashes": {"s": "h"},
         "allowed_paths": ["a/**"], "status": "BOGUS", "created_at": "now"}
    errs = M.validate_manifest(m)
    assert any("schema must be" in e for e in errs)
    assert any("invalid status" in e for e in errs)


# ── resolution: deterministic route -> skill ───────────────────────────────

def test_resolve_returns_active_skill_for_known_operation():
    res = R.resolve("run the governance validators for this sprint",
                    ["tools/governance/x.py"])
    assert res["verdict"] == "RESOLVED"
    assert res["selected_skill_id"]
    # resolved skill must be active + registered
    active = {s.skill_id for s in load_skills() if s.is_active}
    assert res["selected_skill_id"] in active


def test_resolve_missing_capability_for_nonsense_operation():
    res = R.resolve("frobnicate the quux widget zzzyx", [])
    assert res["verdict"] == "MISSING_SKILL_CAPABILITY"
    assert res["selected_skill_id"] is None
    # policy: must NOT fabricate or pick a loosely related skill
    assert res["resolution_decision"] == "CREATE_MISSING_MICRO_SKILL"
