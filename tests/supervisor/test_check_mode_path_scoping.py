"""test_check_mode_path_scoping.py — path-scoped check_mode.

Covers:
  - get_check_mode_for_path falls back to the bare global check_id key when
    no path-prefix scope is configured
  - the longest configured prefix wins over a shorter, less specific one
  - promoting one path scope to enforcing does not affect a sibling scope,
    nor the bare global key
  - gate.py's skill-gate check actually consults the path-scoped mode (a
    scope-enforcing/rest-advisory split blocks only in-scope)
  - the global coordination `mode` off/enforcing distinction from
    test_skill_gate_rollout.py is unaffected by any of the above
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from coordination import db as cdb  # noqa: E402
from coordination.hooks import gate  # noqa: E402
from coordination.hooks import skill_gate  # noqa: E402

CHECK_ID = skill_gate.CHECK_ID


# ── get/set_check_mode_for_path: pure DB-layer behavior ────────────────────

def test_no_scope_configured_falls_back_to_global_check_key(tmp_path):
    root = tmp_path / "coord"
    cdb.ensure_db(root)
    conn = cdb.connect(root)
    try:
        assert cdb.get_check_mode_for_path(conn, CHECK_ID,
                                           "src/python/fods/x.py") == "advisory"
        cdb.set_check_mode(conn, CHECK_ID, "enforcing", "test", "setup")
        assert cdb.get_check_mode_for_path(conn, CHECK_ID,
                                           "src/python/fods/x.py") == "enforcing"
    finally:
        conn.close()


def test_longest_matching_prefix_wins(tmp_path):
    root = tmp_path / "coord"
    cdb.ensure_db(root)
    conn = cdb.connect(root)
    try:
        cdb.set_check_mode_for_path(conn, CHECK_ID, "src/python", "enforcing",
                                    "test", "broad promotion")
        cdb.set_check_mode_for_path(conn, CHECK_ID, "src/python/_shared",
                                    "advisory", "test",
                                    "carve out a not-yet-ready subtree")
        assert cdb.get_check_mode_for_path(
            conn, CHECK_ID, "src/python/fods/x.py") == "enforcing"
        assert cdb.get_check_mode_for_path(
            conn, CHECK_ID, "src/python/_shared/exceptions.py") == "advisory"
    finally:
        conn.close()


def test_promoting_one_scope_does_not_affect_sibling_or_global(tmp_path):
    root = tmp_path / "coord"
    cdb.ensure_db(root)
    conn = cdb.connect(root)
    try:
        cdb.set_check_mode_for_path(conn, CHECK_ID, "tools/governance",
                                    "enforcing", "test", "smallest blast radius")
        assert cdb.get_check_mode_for_path(
            conn, CHECK_ID, "tools/governance/skills_first/x.py") == "enforcing"
        assert cdb.get_check_mode_for_path(
            conn, CHECK_ID, "src/python/fods/x.py") == "advisory"
        assert cdb.get_check_mode(conn, CHECK_ID) == "advisory"
    finally:
        conn.close()


def test_set_check_mode_for_path_rejects_empty_prefix(tmp_path):
    root = tmp_path / "coord"
    cdb.ensure_db(root)
    conn = cdb.connect(root)
    try:
        try:
            cdb.set_check_mode_for_path(conn, CHECK_ID, "", "enforcing",
                                        "test", "x")
            assert False, "expected ValueError for empty path_prefix"
        except ValueError:
            pass
    finally:
        conn.close()


def test_scoped_promotion_is_audit_logged(tmp_path):
    root = tmp_path / "coord"
    cdb.ensure_db(root)
    conn = cdb.connect(root)
    try:
        cdb.set_check_mode_for_path(conn, CHECK_ID, "src/python/_shared",
                                    "enforcing", "test-actor", "promotion test")
        rows = conn.execute(
            "SELECT * FROM coordination_events WHERE verb='CHECK_MODE_CHANGE'"
            " ORDER BY rowid DESC LIMIT 1").fetchall()
        assert rows
        row = dict(rows[0])
        assert row["actor_agent_id"] == "test-actor"
        assert row["to_status"] == "enforcing"
        detail = json.loads(row["detail"])
        assert detail["path_prefix"] == "src/python/_shared"
    finally:
        conn.close()


# ── gate.py wiring: scope-enforcing/rest-advisory split blocks only in-scope ─

def _sandbox(tmp_path, rel_dir="tools/governance/skills_first",
            fname="new_file.py"):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / rel_dir.replace("/", "\\")).mkdir(parents=True)
    (repo / ".git").mkdir()
    target = repo / rel_dir.replace("/", "\\") / fname
    target.write_text("x = 1\n", encoding="utf-8")
    cdb.ensure_db(root)
    return root, repo, target


def _payload(repo, target, session="sess-scopetest"):
    return json.dumps({
        "hook_event_name": "PreToolUse", "session_id": session,
        "cwd": str(repo), "tool_name": "Write",
        "tool_input": {"file_path": str(target)},
    })


def test_scope_enforcing_blocks_only_that_scope(tmp_path):
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_check_mode_for_path(conn, CHECK_ID, "tools/governance",
                                    "enforcing", "test", "promotion")
    finally:
        conn.close()
    gate.process(json.dumps({"hook_event_name": "SessionStart",
                             "session_id": "sess-scopetest", "cwd": str(repo)}),
                 root=root)
    code = gate.process(_payload(repo, target), root=root)
    assert code == 2, "in-scope path must be blocked once its scope is enforcing"


def test_sibling_scope_remains_advisory_after_promotion(tmp_path):
    root, repo, target = _sandbox(tmp_path, rel_dir="src/python/_shared",
                                  fname="exceptions.py")
    conn = cdb.connect(root)
    try:
        # Promote an unrelated scope only -- src/python/_shared/ must stay
        # advisory (falls back to the still-default-advisory global key).
        cdb.set_check_mode_for_path(conn, CHECK_ID, "tools/governance",
                                    "enforcing", "test", "unrelated promotion")
    finally:
        conn.close()
    gate.process(json.dumps({"hook_event_name": "SessionStart",
                             "session_id": "sess-scopetest", "cwd": str(repo)}),
                 root=root)
    code = gate.process(_payload(repo, target), root=root)
    assert code == 0, "a sibling, non-promoted scope must not be blocked"


def test_block_message_includes_actionable_manifest_command(tmp_path, capsys):
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_check_mode_for_path(conn, CHECK_ID, "tools/governance",
                                    "enforcing", "test", "promotion")
    finally:
        conn.close()
    gate.process(json.dumps({"hook_event_name": "SessionStart",
                             "session_id": "sess-scopetest", "cwd": str(repo)}),
                 root=root)
    gate.process(_payload(repo, target), root=root)
    err = capsys.readouterr().err
    assert "manifest" in err and "--allowed-paths" in err and "--skill" in err


def test_global_off_still_wins_over_an_enforcing_scope(tmp_path):
    root, repo, target = _sandbox(tmp_path)
    conn = cdb.connect(root)
    try:
        cdb.set_mode(conn, "off", "test", "setup")
        cdb.set_check_mode_for_path(conn, CHECK_ID, "tools/governance",
                                    "enforcing", "test", "x")
    finally:
        conn.close()
    code = gate.process(_payload(repo, target), root=root)
    assert code == 0, "global mode=off must skip all hook enforcement," \
                       " including an enforcing path-scoped check"
