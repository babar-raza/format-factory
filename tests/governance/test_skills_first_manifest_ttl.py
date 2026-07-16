"""test_skills_first_manifest_ttl.py — SFC-GAP-C prerequisite (2026-07-17).

Manifest expiry (TTL): a manifest created and never explicitly closed must not
stay "live" forever -- that would make a tool-layer check for "a live manifest
covers this path" a hollow security property. All comparisons are UTC-based
(matching manifest.is_expired's own datetime.now(timezone.utc) default) to
avoid local-timezone day-boundary flakiness.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance.skills_first import manifest as M  # noqa: E402
from tools.governance.skills_first.registries import load_skills  # noqa: E402


def _an_active_skill() -> str:
    for s in load_skills():
        if s.is_active and s.command_file and (REPO_ROOT / s.command_file).exists():
            return s.skill_id
    pytest.skip("no active skill with on-disk command file")


def test_create_manifest_sets_expires_at_in_future():
    sid = _an_active_skill()
    m = M.create_manifest(
        task_id="TC-TTL-001", agent_type="CLAUDE_CODE",
        requested_operation="ttl test", selected_skill_ids=[sid],
        allowed_paths=["tools/governance/**"], write=False)
    exp = datetime.fromisoformat(m["expires_at"])
    assert exp > datetime.now(timezone.utc)


def test_create_manifest_rejects_non_positive_ttl():
    sid = _an_active_skill()
    with pytest.raises(M.ManifestError):
        M.create_manifest(
            task_id="TC-TTL-002", agent_type="CLAUDE_CODE",
            requested_operation="ttl test", selected_skill_ids=[sid],
            allowed_paths=["tools/governance/**"], ttl_hours=0, write=False)


def test_custom_ttl_hours_respected():
    sid = _an_active_skill()
    m = M.create_manifest(
        task_id="TC-TTL-003", agent_type="CLAUDE_CODE",
        requested_operation="ttl test", selected_skill_ids=[sid],
        allowed_paths=["tools/governance/**"], ttl_hours=0.001, write=False)
    # ~3.6 seconds -- should already be expired by the time we check.
    import time
    time.sleep(0.05)
    assert M.is_expired(m, now=datetime.now(timezone.utc) + timedelta(hours=1))


def test_is_expired_true_for_manifest_missing_field():
    """Fail-closed: a manifest written before this field existed (no
    expires_at at all) is treated as already expired, never perpetually live."""
    assert M.is_expired({"execution_id": "sfx-legacy"}) is True


def test_is_expired_true_for_malformed_timestamp():
    assert M.is_expired({"expires_at": "not-a-date"}) is True


def test_is_expired_false_before_ttl_elapses():
    sid = _an_active_skill()
    m = M.create_manifest(
        task_id="TC-TTL-004", agent_type="CLAUDE_CODE",
        requested_operation="ttl test", selected_skill_ids=[sid],
        allowed_paths=["tools/governance/**"], ttl_hours=4, write=False)
    assert M.is_expired(m, now=datetime.now(timezone.utc)) is False


def test_is_expired_true_after_ttl_elapses():
    sid = _an_active_skill()
    m = M.create_manifest(
        task_id="TC-TTL-005", agent_type="CLAUDE_CODE",
        requested_operation="ttl test", selected_skill_ids=[sid],
        allowed_paths=["tools/governance/**"], ttl_hours=4, write=False)
    future = datetime.now(timezone.utc) + timedelta(hours=5)
    assert M.is_expired(m, now=future) is True


def test_validate_manifest_requires_expires_at():
    """Old manifests missing expires_at fail validate_manifest (fail closed)."""
    sid = _an_active_skill()
    m = M.create_manifest(
        task_id="TC-TTL-006", agent_type="CLAUDE_CODE",
        requested_operation="ttl test", selected_skill_ids=[sid],
        allowed_paths=["tools/governance/**"], write=False)
    del m["expires_at"]
    errs = M.validate_manifest(m)
    assert any("expires_at" in e for e in errs)
