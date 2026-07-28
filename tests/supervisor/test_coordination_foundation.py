"""TC-COORD-001: coordination foundation -- root resolver, canonicalizer, db.

Mission AGENT-COORD-2026-07-15 (plans/.claude/lazy-hugging-lovelace.md).
All DB state isolated to tmp_path via FF_AGENT_COORDINATION_ROOT.
"""
from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path

import pytest

from coordination import PROTOCOL_VERSION
from coordination import db as cdb
from coordination import root as croot
from coordination.errors import ResourceEscape


@pytest.fixture()
def coord_root(tmp_path, monkeypatch) -> Path:
    root = tmp_path / "coord"
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    cdb.ensure_db(root)
    return root


@pytest.fixture()
def fake_repo(tmp_path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    return repo


class TestRootResolution:
    def test_env_override_wins(self, tmp_path, monkeypatch):
        override = tmp_path / "custom-root"
        monkeypatch.setenv(croot.ENV_ROOT, str(override))
        assert croot.resolve_coordination_root() == override

    def test_default_is_outside_repo_and_keyed_on_common_dir(
            self, fake_repo, monkeypatch, tmp_path):
        monkeypatch.delenv(croot.ENV_ROOT, raising=False)
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "lad"))
        r = croot.resolve_coordination_root(fake_repo)
        assert str(tmp_path / "lad") in str(r)
        assert "ff-coordination" in str(r)
        # Key is stable and anchored.
        key, anchored = croot.repo_key(fake_repo)
        assert anchored is True
        assert key in str(r)
        # A subdirectory of the same repo resolves to the same root.
        assert croot.resolve_coordination_root(fake_repo / "src") == r

    def test_linked_worktree_shares_root_with_main(self, tmp_path, monkeypatch):
        monkeypatch.delenv(croot.ENV_ROOT, raising=False)
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "lad"))
        main = tmp_path / "main"
        (main / ".git" / "worktrees" / "wt1").mkdir(parents=True)
        linked = tmp_path / "wt1"
        linked.mkdir()
        gitdir = main / ".git" / "worktrees" / "wt1"
        (linked / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
        (gitdir / "commondir").write_text("../..\n", encoding="utf-8")
        assert croot.git_common_dir(linked) == croot.git_common_dir(main)
        assert (croot.resolve_coordination_root(linked)
                == croot.resolve_coordination_root(main))
        # Worktree identities remain distinct.
        assert (croot.worktree_identity(linked)[0]
                != croot.worktree_identity(main)[0])

    def test_unanchored_fallback_flagged(self, tmp_path, monkeypatch):
        monkeypatch.delenv(croot.ENV_ROOT, raising=False)
        bare = tmp_path / "nogit"
        bare.mkdir()
        # Guard: the tmp tree must genuinely contain no .git above it for this
        # assertion; skip if the tmp hierarchy is inside a repo.
        if croot.find_git_entry(bare) is not None:
            pytest.skip("tmp_path is inside a git repo; fallback untestable here")
        assert croot.is_anchored(bare) is False


class TestCanonicalResource:
    def test_relative_and_absolute_agree(self, fake_repo):
        k1, _ = croot.canonical_resource("src/a.py", fake_repo)
        k2, _ = croot.canonical_resource(str(fake_repo / "src" / "a.py"), fake_repo)
        assert k1 == k2 == "src/a.py"

    def test_case_insensitive_keys(self, fake_repo):
        k1, _ = croot.canonical_resource("SRC/A.PY", fake_repo)
        k2, _ = croot.canonical_resource("src/a.py", fake_repo)
        assert k1 == k2

    def test_dotdot_escape_rejected(self, fake_repo):
        with pytest.raises(ResourceEscape):
            croot.canonical_resource("../outside.txt", fake_repo)

    def test_absolute_outside_rejected(self, fake_repo, tmp_path):
        with pytest.raises(ResourceEscape):
            croot.canonical_resource(str(tmp_path / "elsewhere.txt"), fake_repo)

    def test_dotdot_inside_collapses(self, fake_repo):
        k, _ = croot.canonical_resource("src/../src/a.py", fake_repo)
        assert k == "src/a.py"

    def test_logical_passthrough(self, fake_repo):
        k, d = croot.canonical_resource("logical:Mission:MAIN", fake_repo)
        assert k == "logical:mission:main"
        assert d == "logical:Mission:MAIN"

    def test_nonexistent_file_still_keyed(self, fake_repo):
        k, _ = croot.canonical_resource("src/new_file.py", fake_repo)
        assert k == "src/new_file.py"

    def test_ancestor_keys(self):
        assert croot.ancestor_keys("a/b/c.py") == ["a/b", "a"]
        assert croot.ancestor_keys("top.py") == []


class TestDb:
    def test_ensure_db_creates_schema_and_defaults(self, coord_root):
        conn = cdb.connect(coord_root)
        try:
            tables = {r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            assert {"agents", "leases", "lease_baselines", "write_journal",
                    "conflicts", "coordination_events", "quarantined_rows",
                    "settings", "schema_meta"} <= tables
            assert cdb.get_mode(conn) == "advisory"
            row = conn.execute(
                "SELECT value FROM schema_meta WHERE key='protocol_version'"
            ).fetchone()
            assert int(row["value"]) == PROTOCOL_VERSION
        finally:
            conn.close()

    def test_ensure_db_idempotent(self, coord_root):
        cdb.ensure_db(coord_root)
        cdb.ensure_db(coord_root)

    def test_mode_change_is_audited(self, coord_root):
        conn = cdb.connect(coord_root)
        try:
            cdb.set_mode(conn, "enforcing", actor="tester", reason="pilot flip")
            assert cdb.get_mode(conn) == "enforcing"
            ev = conn.execute(
                "SELECT * FROM coordination_events WHERE verb='MODE_CHANGE'"
            ).fetchone()
            assert ev["from_status"] == "advisory"
            assert ev["to_status"] == "enforcing"
            assert "pilot flip" in ev["detail"]
        finally:
            conn.close()

    def test_invalid_mode_rejected(self, coord_root):
        conn = cdb.connect(coord_root)
        try:
            with pytest.raises(ValueError):
                cdb.set_mode(conn, "yolo", actor="t", reason="r")
        finally:
            conn.close()

    def test_immediate_rolls_back_on_error(self, coord_root):
        conn = cdb.connect(coord_root)
        try:
            with pytest.raises(RuntimeError):
                with cdb.immediate(conn):
                    conn.execute(
                        "INSERT INTO settings(key, value) VALUES('x', '1')")
                    raise RuntimeError("boom")
            assert cdb.get_setting(conn, "x", "missing") == "missing"
        finally:
            conn.close()

    def test_immediate_serializes_concurrent_writers(self, coord_root):
        """Two threads doing check-then-insert under immediate() -> exactly
        one wins on a unique key."""
        results: list[str] = []

        def worker(name: str):
            conn = cdb.connect(coord_root)
            try:
                with cdb.immediate(conn):
                    row = conn.execute(
                        "SELECT value FROM settings WHERE key='winner'"
                    ).fetchone()
                    if row is None:
                        conn.execute(
                            "INSERT INTO settings(key, value) VALUES('winner', ?)",
                            (name,))
                        results.append(name)
            except sqlite3.OperationalError:
                pass
            finally:
                conn.close()

        threads = [threading.Thread(target=worker, args=(f"t{i}",))
                   for i in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 1

    def test_quarantine_row(self, coord_root):
        conn = cdb.connect(coord_root)
        try:
            with cdb.immediate(conn):
                cdb.quarantine_row(conn, "leases", {"lease_id": "x", "bad": True},
                                   reason="malformed json column")
            q = conn.execute("SELECT * FROM quarantined_rows").fetchone()
            assert q["source_table"] == "leases"
            assert "malformed" in q["reason"]
        finally:
            conn.close()

    def test_event_ordering_by_rowid_not_clock(self, coord_root):
        conn = cdb.connect(coord_root)
        try:
            with cdb.immediate(conn):
                # Deliberately emit with a LATER timestamp first: rowid order
                # must still reflect insertion order.
                cdb.emit_event(conn, "system", "e1", "FIRST",
                               now_fn=lambda: "2099-01-01T00:00:00+00:00")
                cdb.emit_event(conn, "system", "e2", "SECOND",
                               now_fn=lambda: "2000-01-01T00:00:00+00:00")
            rows = conn.execute(
                "SELECT verb FROM coordination_events ORDER BY event_id"
            ).fetchall()
            assert [r["verb"] for r in rows] == ["FIRST", "SECOND"]
        finally:
            conn.close()
