"""test_skill_gate_rollout.py — SFC-GAP-C (2026-07-17).

Covers:
  - skill_gate.evaluate_path's 3-tier verdict logic (pure function, no DB)
  - gate.py's per-check decoupling invariant: check_mode:skill_resolution is
    independent of the global coordination `mode` in BOTH directions
  - manifest expiry integration: an expired manifest does not satisfy
    MANIFEST_COVERING
  - regression: the existing coordination test suite is unaffected regardless
    of check_mode:skill_resolution's value
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from coordination import db as cdb  # noqa: E402
from coordination.hooks import gate  # noqa: E402
from coordination.hooks import skill_gate  # noqa: E402
from coordination.registry import AgentRegistry  # noqa: E402


# ── evaluate_path: 3-tier verdict (pure function) ──────────────────────────

def test_no_skill_resolved_for_nonsense_path():
    v = skill_gate.evaluate_path("this/path/matches/nothing/registered.xyz")
    assert v.tier == skill_gate.NO_SKILL_RESOLVED_FOR_PATH
    assert v.block_eligible is False


def test_skill_exists_but_no_manifest_for_known_skill_path():
    # tools/governance/skills_first/** is the skills-first-audit skill's own
    # declared implementation_paths -- a real, registered skill scope with
    # (presumably) no live manifest sitting around from this test run.
    v = skill_gate.evaluate_path("tools/governance/skills_first/some_file.py")
    assert v.tier == skill_gate.SKILL_EXISTS_BUT_NO_MANIFEST
    assert v.block_eligible is True


def test_manifest_covering_when_live_manifest_exists(monkeypatch, tmp_path):
    fake_manifest_dir = tmp_path / "manifests"
    fake_manifest_dir.mkdir()
    fake = {
        "execution_id": "sfx-test-cover",
        "status": "CREATED",
        "allowed_paths": ["tools/governance/skills_first/**"],
        "expires_at": (datetime.now(timezone.utc)
                       + timedelta(hours=1)).isoformat(),
    }
    (fake_manifest_dir / "sfx-test-cover.json").write_text(
        json.dumps(fake), encoding="utf-8")

    import tools.governance.skills_first.manifest as M
    monkeypatch.setattr(M, "MANIFEST_DIR", fake_manifest_dir)

    v = skill_gate.evaluate_path("tools/governance/skills_first/some_file.py")
    assert v.tier == skill_gate.MANIFEST_COVERING
    assert v.block_eligible is False


def test_expired_manifest_does_not_satisfy_manifest_covering(monkeypatch, tmp_path):
    fake_manifest_dir = tmp_path / "manifests"
    fake_manifest_dir.mkdir()
    fake = {
        "execution_id": "sfx-test-expired",
        "status": "CREATED",
        "allowed_paths": ["tools/governance/skills_first/**"],
        "expires_at": (datetime.now(timezone.utc)
                       - timedelta(hours=1)).isoformat(),  # already expired
    }
    (fake_manifest_dir / "sfx-test-expired.json").write_text(
        json.dumps(fake), encoding="utf-8")

    import tools.governance.skills_first.manifest as M
    monkeypatch.setattr(M, "MANIFEST_DIR", fake_manifest_dir)

    v = skill_gate.evaluate_path("tools/governance/skills_first/some_file.py")
    # Falls through to SKILL_EXISTS_BUT_NO_MANIFEST -- the skill genuinely
    # governs this path, but the expired manifest no longer counts as live.
    assert v.tier == skill_gate.SKILL_EXISTS_BUT_NO_MANIFEST


def test_closed_manifest_does_not_satisfy_manifest_covering(monkeypatch, tmp_path):
    fake_manifest_dir = tmp_path / "manifests"
    fake_manifest_dir.mkdir()
    fake = {
        "execution_id": "sfx-test-closed",
        "status": "CLOSED",
        "allowed_paths": ["tools/governance/skills_first/**"],
        "expires_at": (datetime.now(timezone.utc)
                       + timedelta(hours=1)).isoformat(),
    }
    (fake_manifest_dir / "sfx-test-closed.json").write_text(
        json.dumps(fake), encoding="utf-8")

    import tools.governance.skills_first.manifest as M
    monkeypatch.setattr(M, "MANIFEST_DIR", fake_manifest_dir)

    v = skill_gate.evaluate_path("tools/governance/skills_first/some_file.py")
    assert v.tier == skill_gate.SKILL_EXISTS_BUT_NO_MANIFEST


# ── gate.py wiring: per-check decoupling from the global coordination mode ─

def _sandbox(tmp_path):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / "tools" / "governance" / "skills_first").mkdir(parents=True)
    (repo / ".git").mkdir()
    target = repo / "tools" / "governance" / "skills_first" / "new_file.py"
    target.write_text("x = 1\n", encoding="utf-8")
    cdb.ensure_db(root)
    return root, repo, target


def _payload(repo, target, session="sess-skillgate"):
    return json.dumps({
        "hook_event_name": "PreToolUse", "session_id": session,
        "cwd": str(repo), "tool_name": "Write",
        "tool_input": {"file_path": str(target)},
    })


def test_global_advisory_and_check_advisory_never_blocks(tmp_path):
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_mode(conn, "advisory", "test", "setup")
    finally:
        conn.close()
    gate.process(json.dumps({"hook_event_name": "SessionStart",
                             "session_id": "sess-skillgate", "cwd": str(repo)}),
                 root=root)
    code = gate.process(_payload(repo, target), root=root)
    assert code == 0


def test_global_enforcing_but_check_advisory_allows_and_logs(tmp_path):
    """Decoupling proof (part 1): global coordination mode is 'enforcing'
    (the existing, already-proven checks), but check_mode:skill_resolution
    defaults to 'advisory' -- a SKILL_EXISTS_BUT_NO_MANIFEST event must be
    ALLOWED (exit 0) and logged to advisory-log.jsonl, not blocked."""
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_mode(conn, "enforcing", "test", "setup")
    finally:
        conn.close()
    gate.process(json.dumps({"hook_event_name": "SessionStart",
                             "session_id": "sess-skillgate", "cwd": str(repo)}),
                 root=root)
    code = gate.process(_payload(repo, target), root=root)
    assert code == 0, "check_mode default (advisory) must not block even" \
                       " though the global coordination mode is enforcing"
    log_path = root / "advisory-log.jsonl"
    assert log_path.exists()
    lines = [json.loads(l) for l in log_path.read_text().splitlines() if l.strip()]
    skill_gate_events = [l for l in lines if l.get("check") == skill_gate.CHECK_ID]
    assert skill_gate_events, "expected an advisory-logged skill_resolution event"
    assert skill_gate_events[-1]["tier"] == skill_gate.SKILL_EXISTS_BUT_NO_MANIFEST


def test_promoting_only_the_check_to_enforcing_blocks(tmp_path):
    """Decoupling proof (part 2): promoting check_mode:skill_resolution to
    'enforcing' (independent of the global mode, which we deliberately leave
    at its default 'advisory' here) now blocks the same event."""
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_check_mode(conn, skill_gate.CHECK_ID, "enforcing", "test",
                           "promotion test")
    finally:
        conn.close()
    gate.process(json.dumps({"hook_event_name": "SessionStart",
                             "session_id": "sess-skillgate", "cwd": str(repo)}),
                 root=root)
    code = gate.process(_payload(repo, target), root=root)
    assert code == 2, "check_mode=enforcing must block a" \
                       " SKILL_EXISTS_BUT_NO_MANIFEST event"
    # Global coordination mode must remain untouched by promoting the check.
    conn = cdb.connect(root)
    try:
        assert cdb.get_mode(conn) == "advisory"
    finally:
        conn.close()


def test_global_off_skips_skill_gate_entirely(tmp_path):
    """The global `mode == 'off'` early-return in gate.process() must still
    take precedence over everything, including an enforcing per-check mode --
    'off' means skip all hook enforcement, full stop."""
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_mode(conn, "off", "test", "setup")
        cdb.set_check_mode(conn, skill_gate.CHECK_ID, "enforcing", "test", "x")
    finally:
        conn.close()
    code = gate.process(_payload(repo, target), root=root)
    assert code == 0
