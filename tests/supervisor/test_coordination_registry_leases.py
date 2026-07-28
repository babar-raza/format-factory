"""TC-COORD-002/003: AgentRegistry + LeaseManager.

Mission AGENT-COORD-2026-07-15. No sleeps: staleness is exercised by
injecting a future clock (now_fn), never by waiting.
"""
from __future__ import annotations

import threading
from datetime import timedelta
from pathlib import Path

import pytest

from coordination import db as cdb
from coordination import root as croot
from coordination.errors import (LeaseConflict, LeaseStale, NotRegistered,
                                 TakeoverDenied)
from coordination.ids import iso, utcnow
from coordination.leases import LeaseManager, mode_covers, modes_conflict
from coordination.registry import AgentRegistry


@pytest.fixture()
def env(tmp_path, monkeypatch):
    """Isolated coordination root + fake worktree; returns (root, repo)."""
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "src" / "python" / "fods").mkdir(parents=True)
    (repo / "tools" / "readme_sync").mkdir(parents=True)
    (repo / "src" / "python" / "fods" / "model.py").write_text("m = 1\n",
                                                               encoding="utf-8")
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    cdb.ensure_db(root)
    return root, repo


def future_clock(seconds: int):
    return lambda: iso(utcnow() + timedelta(seconds=seconds))


class TestRegistry:
    def test_register_captures_identity_fields(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        ra = reg.register("claude-code", session_id="sess-1",
                          task_id="TC-X-001", plan_authority="plans/p.md",
                          declared_scope=["src/python/fods/**"])
        assert ra.agent_id.startswith("agent-claude-code-")
        assert ra.resumed is False
        conn = cdb.connect(root)
        try:
            row = conn.execute("SELECT * FROM agents").fetchone()
            for field in ("agent_token_hash", "hostname", "repo_identity",
                          "worktree_id", "worktree_path", "started_at",
                          "last_heartbeat"):
                assert row[field], field
            assert row["claude_session_id"] == "sess-1"
            assert row["task_id"] == "TC-X-001"
            assert row["status"] == "ACTIVE"
            # No secrets stored raw.
            assert ra.token not in (row["agent_token_hash"] or "")
        finally:
            conn.close()

    def test_session_resume_is_idempotent_and_rotates_token(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        first = reg.register("claude-code", session_id="sess-r")
        second = reg.register("claude-code", session_id="sess-r")
        assert second.agent_id == first.agent_id
        assert second.resumed is True
        assert second.token != first.token
        # Old token no longer authenticates; new one does.
        conn = cdb.connect(root)
        try:
            with pytest.raises(NotRegistered):
                reg.authenticate(conn, first.agent_id, first.token)
            reg.authenticate(conn, second.agent_id, second.token)
        finally:
            conn.close()

    def test_runtime_identity_files_round_trip(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        ra = reg.register("codex", session_id="sess-f")
        by_agent = reg.read_runtime_identity(agent_id=ra.agent_id)
        by_session = reg.read_runtime_identity(session_id="sess-f")
        assert by_agent["token"] == by_session["token"] == ra.token

    def test_bad_token_and_unknown_agent(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        ra = reg.register("kilo-code")
        conn = cdb.connect(root)
        try:
            with pytest.raises(NotRegistered):
                reg.authenticate(conn, ra.agent_id, "wrong")
            with pytest.raises(NotRegistered):
                reg.authenticate(conn, "agent-ghost", "x")
        finally:
            conn.close()

    def test_reap_marks_stale_suspect_and_heartbeat_resurrects(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        ra = reg.register("claude-code", heartbeat_ttl_s=60)
        # As-of one hour in the future the heartbeat is expired.
        stale_reg = AgentRegistry(root, start=repo, now_fn=future_clock(3600))
        assert stale_reg.reap() == 1
        conn = cdb.connect(root)
        try:
            row = conn.execute("SELECT status FROM agents").fetchone()
            assert row["status"] == "STALE_SUSPECT"
        finally:
            conn.close()
        assert reg.heartbeat(ra.agent_id, ra.token) == "ACTIVE"

    def test_complete_releases_all_leases(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        lm = LeaseManager(root, start=repo)
        ra = reg.register("claude-code")
        lm.claim(ra.agent_id, ra.token, ["src/python/fods/model.py"])
        released = reg.complete(ra.agent_id, ra.token)
        assert released == 1
        conn = cdb.connect(root)
        try:
            assert conn.execute(
                "SELECT status FROM leases").fetchone()["status"] == "RELEASED"
            assert conn.execute(
                "SELECT status FROM agents").fetchone()["status"] == "COMPLETED"
        finally:
            conn.close()

    def test_idle_releases_only_auto_leases(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        lm = LeaseManager(root, start=repo)
        ra = reg.register("claude-code")
        lm.claim(ra.agent_id, ra.token, ["src/python/fods"], origin="explicit")
        conn = cdb.connect(root)
        try:
            with cdb.immediate(conn):
                agent = reg.authenticate(conn, ra.agent_id, ra.token)
                lm.auto_claim(conn, agent, "tools/readme_sync/x.py")
        finally:
            conn.close()
        assert reg.idle(ra.agent_id, ra.token) == 1
        conn = cdb.connect(root)
        try:
            rows = {r["origin"]: r["status"] for r in
                    conn.execute("SELECT origin, status FROM leases")}
            assert rows["auto"] == "RELEASED"
            assert rows["explicit"] == "ACTIVE"
        finally:
            conn.close()


class TestModeMatrix:
    @pytest.mark.parametrize("a,b,expected", [
        ("OBSERVE", "EXCLUSIVE_WRITE", False),
        ("OBSERVE", "OBSERVE", False),
        ("APPEND", "APPEND", False),
        ("APPEND", "EXCLUSIVE_WRITE", True),
        ("APPEND", "SRSW", True),
        ("EXCLUSIVE_WRITE", "EXCLUSIVE_WRITE", True),
        ("SRSW", "EXCLUSIVE_WRITE", True),
        ("SRSW", "OBSERVE", False),
    ])
    def test_modes_conflict(self, a, b, expected):
        assert modes_conflict(a, b) is expected
        assert modes_conflict(b, a) is expected

    def test_mode_covers(self):
        assert mode_covers("EXCLUSIVE_WRITE", "APPEND")
        assert not mode_covers("OBSERVE", "EXCLUSIVE_WRITE")
        assert not mode_covers("APPEND", "SRSW")


class TestLeases:
    def _two_agents(self, root, repo):
        reg = AgentRegistry(root, start=repo)
        a = reg.register("claude-code", session_id="sess-a", task_id="TC-A")
        b = reg.register("codex", task_id="TC-B")
        return reg, a, b

    def test_disjoint_claims_coexist(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        la = lm.claim(a.agent_id, a.token, ["src/python/fods"])
        lb = lm.claim(b.agent_id, b.token, ["tools/readme_sync"])
        assert la[0]["status"] == "ACTIVE" and lb[0]["status"] == "ACTIVE"

    def test_exact_overlap_rejected_with_holder_info(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(a.agent_id, a.token, ["src/python/fods/model.py"])
        with pytest.raises(LeaseConflict) as exc:
            lm.claim(b.agent_id, b.token, ["src/python/fods/model.py"])
        assert exc.value.holder_agent_id == a.agent_id
        assert exc.value.holder_lease_id

    def test_parent_dir_blocks_child_file_and_vice_versa(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(a.agent_id, a.token, ["src/python/fods"])
        with pytest.raises(LeaseConflict):
            lm.claim(b.agent_id, b.token, ["src/python/fods/model.py"])
        # And the reverse: child file lease blocks a parent dir claim.
        lm2 = LeaseManager(root, start=repo)
        lm2.claim(b.agent_id, b.token, ["tools/readme_sync/run.py"])
        with pytest.raises(LeaseConflict):
            lm2.claim(a.agent_id, a.token, ["tools/readme_sync"])

    def test_sibling_prefix_name_is_not_overlap(self, env):
        root, repo = env
        (repo / "src" / "python" / "fods2").mkdir()
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(a.agent_id, a.token, ["src/python/fods"])
        # 'fods2' shares the string prefix but is NOT inside 'fods'.
        lm.claim(b.agent_id, b.token, ["src/python/fods2"])

    def test_case_insensitive_overlap(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(a.agent_id, a.token, ["src/python/fods/model.py"])
        with pytest.raises(LeaseConflict):
            lm.claim(b.agent_id, b.token, ["SRC/PYTHON/FODS/MODEL.PY"])

    def test_observe_and_append_compat(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(a.agent_id, a.token, ["reports/journal.log"], mode="APPEND")
        lm.claim(b.agent_id, b.token, ["reports/journal.log"], mode="APPEND")
        lm.claim(b.agent_id, b.token, ["src/python/fods"], mode="OBSERVE")
        lm.claim(a.agent_id, a.token, ["src/python/fods"])  # write over observe ok
        with pytest.raises(LeaseConflict):
            lm.claim(b.agent_id, b.token, ["reports/journal.log"])  # EW vs APPEND

    def test_multi_resource_claim_is_all_or_nothing(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(b.agent_id, b.token, ["tools/readme_sync"])
        with pytest.raises(LeaseConflict):
            lm.claim(a.agent_id, a.token,
                     ["src/python/fods", "tools/readme_sync"])
        conn = cdb.connect(root)
        try:
            mine = conn.execute(
                "SELECT COUNT(*) AS n FROM leases WHERE agent_id=?",
                (a.agent_id,)).fetchone()["n"]
            assert mine == 0  # nothing partially acquired
        finally:
            conn.close()

    def test_own_reclaim_reuses_lease(self, env):
        root, repo = env
        _, a, _ = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        first = lm.claim(a.agent_id, a.token, ["src/python/fods"])
        again = lm.claim(a.agent_id, a.token, ["src/python/fods/model.py"])
        assert again[0]["reused"] is True
        assert again[0]["lease_id"] == first[0]["lease_id"]

    def test_logical_resources_are_global_scope(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        lm.claim(a.agent_id, a.token, ["logical:mission:MAIN"])
        with pytest.raises(LeaseConflict):
            lm.claim(b.agent_id, b.token, ["logical:mission:main"])

    def test_claim_race_exactly_one_winner(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        agents = [reg.register(f"claude-code", task_id=f"TC-{i}")
                  for i in range(10)]
        wins: list[str] = []
        errors: list[Exception] = []

        def worker(ra):
            lm = LeaseManager(root, start=repo)
            try:
                lm.claim(ra.agent_id, ra.token, ["src/python/fods/model.py"])
                wins.append(ra.agent_id)
            except LeaseConflict as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(ra,)) for ra in agents]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(wins) == 1
        assert len(errors) == 9

    def test_release_foreign_lease_denied(self, env):
        root, repo = env
        _, a, b = self._two_agents(root, repo)
        lm = LeaseManager(root, start=repo)
        la = lm.claim(a.agent_id, a.token, ["src/python/fods"])
        with pytest.raises(LeaseStale):
            lm.release(b.agent_id, b.token, [la[0]["lease_id"]])
        conn = cdb.connect(root)
        try:
            assert conn.execute(
                "SELECT status FROM leases WHERE lease_id=?",
                (la[0]["lease_id"],)).fetchone()["status"] == "ACTIVE"
        finally:
            conn.close()


class TestStaleAndTakeover:
    def _stale_lease(self, root, repo):
        reg = AgentRegistry(root, start=repo)
        a = reg.register("claude-code", heartbeat_ttl_s=60)
        lm = LeaseManager(root, start=repo)
        la = lm.claim(a.agent_id, a.token, ["src/python/fods"],
                      ttl_seconds=60)
        # One hour later: agent heartbeat and lease TTL (2x) both long gone.
        future = LeaseManager(root, start=repo, now_fn=future_clock(3600))
        result = future.reap()
        return reg, a, la[0], future, result

    def test_reaper_transitions_are_recoverable_not_destructive(self, env):
        root, repo = env
        reg, a, lease, future, result = self._stale_lease(root, repo)
        assert result["agents_marked"] == 1
        assert result["leases_marked"] == 1
        conn = cdb.connect(root)
        try:
            assert conn.execute("SELECT status FROM leases").fetchone()[
                "status"] == "STALE"
        finally:
            conn.close()
        # Owner comes back: heartbeat + renew fully recovers.
        reg.heartbeat(a.agent_id, a.token)
        lm = LeaseManager(root, start=repo)
        assert lm.renew(a.agent_id, a.token) == 1
        conn = cdb.connect(root)
        try:
            assert conn.execute("SELECT status FROM leases").fetchone()[
                "status"] == "ACTIVE"
        finally:
            conn.close()

    def test_takeover_requires_stale_and_reason(self, env):
        root, repo = env
        reg, a, lease, future, _ = self._stale_lease(root, repo)
        b = reg.register("codex", task_id="TC-B")
        # The takeover also happens "one hour later" -- same injected clock.
        with pytest.raises(TakeoverDenied):
            future.takeover(b.agent_id, b.token, lease["lease_id"], "  ")
        new = future.takeover(b.agent_id, b.token, lease["lease_id"],
                              "owner crashed; resuming TC-A work")
        assert new["agent_id"] == b.agent_id
        assert new["takeover_of"] == lease["lease_id"]
        conn = cdb.connect(root)
        try:
            old = conn.execute("SELECT * FROM leases WHERE lease_id=?",
                               (lease["lease_id"],)).fetchone()
            assert old["status"] == "TAKEN_OVER"
            assert old["superseded_by"] == new["lease_id"]
            ev = conn.execute(
                "SELECT * FROM coordination_events WHERE verb='TAKEOVER'"
            ).fetchone()
            assert "owner crashed" in ev["detail"]
        finally:
            conn.close()

    def test_takeover_of_active_lease_denied(self, env):
        root, repo = env
        reg = AgentRegistry(root, start=repo)
        a = reg.register("claude-code")
        b = reg.register("codex")
        lm = LeaseManager(root, start=repo)
        la = lm.claim(a.agent_id, a.token, ["src/python/fods"])
        with pytest.raises(TakeoverDenied):
            lm.takeover(b.agent_id, b.token, la[0]["lease_id"], "want it")
