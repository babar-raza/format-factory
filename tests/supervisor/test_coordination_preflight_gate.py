"""TC-COORD-004/005/006: attribution, preflight, CLI, doctor, hook gate.

Mission AGENT-COORD-2026-07-15. Sandboxed: coordination root and repos live
in tmp_path; the hook gate is exercised in-process via gate.process() with
synthetic stdin payloads (golden-fixture contract).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from coordination import db as cdb
from coordination import root as croot
from coordination.baselines import (DELETED_EXTERNALLY, GENERATED,
                                    NO_BASELINE, OTHER_AGENT_CHANGE,
                                    OWN_CHANGE, PRE_EXISTING_USER_CHANGE,
                                    UNCHANGED, UNKNOWN, BaselineTracker,
                                    sha256_file)
from coordination.hooks import gate
from coordination.leases import LeaseManager
from coordination.preflight import preflight, record_write
from coordination.registry import AgentRegistry


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("original\n", encoding="utf-8")
    (repo / "src" / "b.py").write_text("bee\n", encoding="utf-8")
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    monkeypatch.delenv("FF_AGENT_ID", raising=False)
    monkeypatch.delenv("FF_AGENT_TOKEN", raising=False)
    monkeypatch.delenv("FF_COORD_BYPASS", raising=False)
    cdb.ensure_db(root)
    return root, repo


def _register(root, repo, provider="claude-code", **kw):
    return AgentRegistry(root, start=repo).register(provider, **kw)


def _claim_file(root, repo, ra, path, **kw):
    lm = LeaseManager(root, start=repo)
    return lm.claim(ra.agent_id, ra.token, [path], **kw)[0]


class TestClassifyChange:
    def _setup(self, root, repo):
        ra = _register(root, repo)
        lease = _claim_file(root, repo, ra, "src/a.py")
        conn = cdb.connect(root)
        tracker = BaselineTracker()
        with cdb.immediate(conn):
            tracker.capture(conn, lease["lease_id"], [("src/a.py", "src/a.py")],
                            repo)
        return ra, lease, conn, tracker

    def test_unchanged_and_own_change(self, env):
        root, repo = env
        ra, lease, conn, tracker = self._setup(root, repo)
        try:
            cls, _ = tracker.classify_change(conn, ra.agent_id,
                                             lease["lease_id"], "src/a.py", repo)
            assert cls == UNCHANGED
            (repo / "src" / "a.py").write_text("mine\n", encoding="utf-8")
            with cdb.immediate(conn):
                tracker.journal(conn, ra.agent_id, lease["lease_id"],
                                "src/a.py", "edit", None,
                                sha256_file(repo / "src" / "a.py"), "hook")
            cls, _ = tracker.classify_change(conn, ra.agent_id,
                                             lease["lease_id"], "src/a.py", repo)
            assert cls == OWN_CHANGE
        finally:
            conn.close()

    def test_other_agent_and_generated(self, env):
        root, repo = env
        ra, lease, conn, tracker = self._setup(root, repo)
        rb = _register(root, repo, "codex")
        try:
            (repo / "src" / "a.py").write_text("theirs\n", encoding="utf-8")
            with cdb.immediate(conn):
                tracker.journal(conn, rb.agent_id, None, "src/a.py", "edit",
                                None, sha256_file(repo / "src" / "a.py"),
                                "cli")
            cls, detail = tracker.classify_change(
                conn, ra.agent_id, lease["lease_id"], "src/a.py", repo)
            assert cls == OTHER_AGENT_CHANGE
            assert detail["apparent_owner"] == rb.agent_id

            (repo / "src" / "a.py").write_text("genout\n", encoding="utf-8")
            with cdb.immediate(conn):
                tracker.journal(conn, rb.agent_id, None, "src/a.py",
                                "regenerate", None,
                                sha256_file(repo / "src" / "a.py"), "guard")
            cls, _ = tracker.classify_change(
                conn, ra.agent_id, lease["lease_id"], "src/a.py", repo)
            assert cls == GENERATED
        finally:
            conn.close()

    def test_deleted_unknown_nobaseline(self, env):
        root, repo = env
        ra, lease, conn, tracker = self._setup(root, repo)
        try:
            (repo / "src" / "a.py").unlink()
            cls, _ = tracker.classify_change(conn, ra.agent_id,
                                             lease["lease_id"], "src/a.py", repo)
            assert cls == DELETED_EXTERNALLY
            (repo / "src" / "a.py").write_text("mystery\n", encoding="utf-8")
            cls, _ = tracker.classify_change(conn, ra.agent_id,
                                             lease["lease_id"], "src/a.py", repo)
            assert cls == UNKNOWN
            cls, _ = tracker.classify_change(conn, ra.agent_id,
                                             lease["lease_id"], "src/b.py", repo)
            assert cls == NO_BASELINE
        finally:
            conn.close()

    def test_pre_existing_user_change_via_real_git(self, env, tmp_path):
        root, _ = env
        repo = tmp_path / "gitrepo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo,
                       check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo,
                       check=True)
        f = repo / "x.txt"
        f.write_text("committed\n", encoding="utf-8")
        subprocess.run(["git", "add", "x.txt"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "c1"], cwd=repo, check=True)
        # Local modification exists at claim time (dirty tree is normal).
        f.write_text("locally modified\n", encoding="utf-8")
        ra = _register(root, repo)
        lease = _claim_file(root, repo, ra, "x.txt")
        conn = cdb.connect(root)
        tracker = BaselineTracker()
        try:
            with cdb.immediate(conn):
                tracker.capture(conn, lease["lease_id"], [("x.txt", "x.txt")],
                                repo)
            # Someone reverts the file to its committed content.
            f.write_text("committed\n", encoding="utf-8")
            cls, detail = tracker.classify_change(
                conn, ra.agent_id, lease["lease_id"], "x.txt", repo)
            assert cls == PRE_EXISTING_USER_CHANGE
            assert detail["head_match"] is True
        finally:
            conn.close()


class TestPreflight:
    def test_unregistered_denied_exit3(self, env):
        root, repo = env
        res = preflight("src/a.py", root=root, start=repo)
        assert res.decision == "deny" and res.exit_code == 3

    def test_free_file_auto_claims_and_captures_baseline(self, env):
        root, repo = env
        ra = _register(root, repo)
        res = preflight("src/a.py", root=root, start=repo,
                        agent_id=ra.agent_id, token=ra.token)
        assert res.allowed and res.auto_claimed
        conn = cdb.connect(root)
        try:
            lease = conn.execute("SELECT * FROM leases").fetchone()
            assert lease["origin"] == "auto"
            base = conn.execute("SELECT * FROM lease_baselines").fetchone()
            assert base["baseline_sha256"] == sha256_file(repo / "src" / "a.py")
        finally:
            conn.close()

    def test_foreign_holder_denied_exit2_with_conflict(self, env):
        root, repo = env
        ra = _register(root, repo)
        rb = _register(root, repo, "codex")
        _claim_file(root, repo, ra, "src/a.py")
        res = preflight("src/a.py", root=root, start=repo,
                        agent_id=rb.agent_id, token=rb.token)
        assert res.exit_code == 2
        assert ra.agent_id in res.reason
        assert res.conflict_id

    def test_own_write_flow_allows_then_external_denies(self, env):
        root, repo = env
        ra = _register(root, repo)
        assert preflight("src/a.py", root=root, start=repo,
                         agent_id=ra.agent_id, token=ra.token).allowed
        # Simulate the PostToolUse journal after our own write.
        (repo / "src" / "a.py").write_text("v2 by me\n", encoding="utf-8")
        record_write("src/a.py", root=root, start=repo,
                     agent_id=ra.agent_id, token=ra.token, source="hook")
        res = preflight("src/a.py", root=root, start=repo,
                        agent_id=ra.agent_id, token=ra.token)
        assert res.allowed and res.classification == OWN_CHANGE
        # External unattributable edit -> refuse + preserve.
        (repo / "src" / "a.py").write_text("sabotage\n", encoding="utf-8")
        res = preflight("src/a.py", root=root, start=repo,
                        agent_id=ra.agent_id, token=ra.token)
        assert res.exit_code == 5 and res.classification == UNKNOWN
        assert res.conflict_id
        assert (repo / "src" / "a.py").read_text(
            encoding="utf-8") == "sabotage\n"  # preserved, never reverted

    def test_rebaseline_recovers_after_review(self, env):
        root, repo = env
        ra = _register(root, repo)
        preflight("src/a.py", root=root, start=repo, agent_id=ra.agent_id,
                  token=ra.token)
        (repo / "src" / "a.py").write_text("external\n", encoding="utf-8")
        res = preflight("src/a.py", root=root, start=repo,
                        agent_id=ra.agent_id, token=ra.token)
        assert res.exit_code == 5
        # Deliberate recovery: recapture the baseline (renew --rebaseline).
        conn = cdb.connect(root)
        try:
            with cdb.immediate(conn):
                BaselineTracker().capture(conn, res.lease_id,
                                          [("src/a.py", "src/a.py")], repo)
        finally:
            conn.close()
        res2 = preflight("src/a.py", root=root, start=repo,
                         agent_id=ra.agent_id, token=ra.token)
        assert res2.allowed

    def test_escape_denied(self, env):
        root, repo = env
        ra = _register(root, repo)
        res = preflight("../outside.txt", root=root, start=repo,
                        agent_id=ra.agent_id, token=ra.token)
        assert res.exit_code == 2 and "escape" in res.reason


class TestGateContract:
    """Golden stdin fixtures against gate.process() -- the hook contract."""

    def _payload(self, repo, event, session="sess-hook", **kw):
        return json.dumps({"hook_event_name": event, "session_id": session,
                           "transcript_path": "t.jsonl", "cwd": str(repo),
                           **kw})

    def test_session_start_registers_ambient_agent(self, env):
        root, repo = env
        assert gate.process(self._payload(repo, "SessionStart"),
                            root=root) == 0
        reg = AgentRegistry(root, start=repo)
        assert reg.get_by_session("sess-hook") is not None
        assert reg.read_runtime_identity(session_id="sess-hook") is not None

    def test_pre_write_free_file_auto_claims(self, env):
        root, repo = env
        gate.process(self._payload(repo, "SessionStart"), root=root)
        code = gate.process(self._payload(
            repo, "PreToolUse", tool_name="Write",
            tool_input={"file_path": str(repo / "src" / "a.py")}), root=root)
        assert code == 0
        conn = cdb.connect(root)
        try:
            lease = conn.execute("SELECT * FROM leases").fetchone()
            assert lease["origin"] == "auto"
            assert lease["resource_key"] == "src/a.py"
        finally:
            conn.close()

    def test_pre_write_never_registered_session_still_ambient(self, env):
        """A session that never saw SessionStart gets registered on first
        write (ambient path, P14)."""
        root, repo = env
        code = gate.process(self._payload(
            repo, "PreToolUse", session="fresh-sess", tool_name="Edit",
            tool_input={"file_path": str(repo / "src" / "b.py")}), root=root)
        assert code == 0
        assert AgentRegistry(root, start=repo).get_by_session(
            "fresh-sess") is not None

    def test_foreign_lease_blocks_enforcing_logs_advisory(self, env, capsys):
        root, repo = env
        ra = _register(root, repo, "codex")  # the other agent
        _claim_file(root, repo, ra, "src/a.py")
        payload = self._payload(
            repo, "PreToolUse", tool_name="Write",
            tool_input={"file_path": str(repo / "src" / "a.py")})
        # advisory (default): allowed but logged
        assert gate.process(payload, root=root) == 0
        advisory = (root / "advisory-log.jsonl").read_text(encoding="utf-8")
        assert "would_block" in advisory and "src" in advisory
        # enforcing: blocked with remediation on stderr
        conn = cdb.connect(root)
        cdb.set_mode(conn, "enforcing", "test", "pilot")
        conn.close()
        assert gate.process(payload, root=root) == 2
        err = capsys.readouterr().err
        assert "BLOCKED" in err and ra.agent_id in err

    def test_post_write_journals_with_hook_source(self, env):
        root, repo = env
        gate.process(self._payload(repo, "SessionStart"), root=root)
        target = repo / "src" / "a.py"
        gate.process(self._payload(repo, "PreToolUse", tool_name="Write",
                                   tool_input={"file_path": str(target)}),
                     root=root)
        target.write_text("hook wrote this\n", encoding="utf-8")
        gate.process(self._payload(repo, "PostToolUse", tool_name="Write",
                                   tool_input={"file_path": str(target)},
                                   tool_response={"success": True}),
                     root=root)
        conn = cdb.connect(root)
        try:
            j = conn.execute("SELECT * FROM write_journal").fetchone()
            assert j["source"] == "hook"
            assert j["post_sha256"] == sha256_file(target)
        finally:
            conn.close()

    def test_malformed_and_unknown_fail_open_with_incident(self, env):
        root, repo = env
        assert gate.process("not json at all", root=root) == 0
        assert gate.process(self._payload(repo, "BrandNewEvent"),
                            root=root) == 0
        incidents = (root / "hook-incidents.jsonl").read_text(encoding="utf-8")
        assert incidents.count("FAIL_OPEN") >= 2

    def test_broad_staging_blocked_only_with_other_agents(self, env, capsys):
        root, repo = env
        conn = cdb.connect(root)
        cdb.set_mode(conn, "enforcing", "test", "pilot")
        conn.close()
        gate.process(self._payload(repo, "SessionStart"), root=root)
        payload = self._payload(repo, "PreToolUse", tool_name="Bash",
                                tool_input={"command": "git add -A"})
        #

        # Solo agent: allowed (single-agent workflows unaffected).
        assert gate.process(payload, root=root) == 0
        _register(root, repo, "codex")  # a second live agent appears
        assert gate.process(payload, root=root) == 2
        assert "explicit reviewed file list" in capsys.readouterr().err
        # Explicit-path staging stays allowed.
        ok = self._payload(repo, "PreToolUse", tool_name="Bash",
                           tool_input={"command": "git add src/a.py"})
        assert gate.process(ok, root=root) == 0

    def test_destructive_cleanup_blocked_with_other_agents(self, env, capsys):
        root, repo = env
        conn = cdb.connect(root)
        cdb.set_mode(conn, "enforcing", "test", "pilot")
        conn.close()
        gate.process(self._payload(repo, "SessionStart"), root=root)
        _register(root, repo, "codex")
        for cmd in ("git checkout -- .", "git clean -fd", "git stash",
                    "git reset --hard HEAD"):
            payload = self._payload(repo, "PreToolUse", tool_name="Bash",
                                    tool_input={"command": cmd})
            assert gate.process(payload, root=root) == 2, cmd
        capsys.readouterr()

    def test_generator_without_lease_blocked(self, env, capsys):
        root, repo = env
        conn = cdb.connect(root)
        cdb.set_mode(conn, "enforcing", "test", "pilot")
        conn.close()
        gate.process(self._payload(repo, "SessionStart"), root=root)
        _register(root, repo, "codex")
        payload = self._payload(
            repo, "PreToolUse", tool_name="Bash",
            tool_input={"command":
                        "python tools/capability_sync/run_sync.py --mode full"})
        assert gate.process(payload, root=root) == 2
        assert "guard-run" in capsys.readouterr().err

    def test_bypass_env_allows_but_audits(self, env, monkeypatch):
        root, repo = env
        conn = cdb.connect(root)
        cdb.set_mode(conn, "enforcing", "test", "pilot")
        conn.close()
        ra = _register(root, repo, "codex")
        _claim_file(root, repo, ra, "src/a.py")
        gate.process(self._payload(repo, "SessionStart"), root=root)
        monkeypatch.setenv("FF_COORD_BYPASS", "hotfix per operator")
        payload = self._payload(
            repo, "PreToolUse", tool_name="Write",
            tool_input={"file_path": str(repo / "src" / "a.py")})
        assert gate.process(payload, root=root) == 0
        conn = cdb.connect(root)
        try:
            ev = conn.execute("SELECT * FROM coordination_events WHERE"
                              " verb='BYPASS'").fetchone()
            assert ev is not None and "hotfix" in ev["detail"]
        finally:
            conn.close()

    def test_session_end_releases_auto_leases(self, env):
        root, repo = env
        gate.process(self._payload(repo, "SessionStart"), root=root)
        gate.process(self._payload(repo, "PreToolUse", tool_name="Write",
                                   tool_input={"file_path":
                                               str(repo / "src" / "a.py")}),
                     root=root)
        gate.process(self._payload(repo, "SessionEnd"), root=root)
        conn = cdb.connect(root)
        try:
            lease = conn.execute("SELECT status FROM leases").fetchone()
            assert lease["status"] == "RELEASED"
            agent = conn.execute("SELECT status FROM agents").fetchone()
            assert agent["status"] == "IDLE"
        finally:
            conn.close()

    def test_local_and_off_mode_fast_paths(self, env):
        root, repo = env
        gate.process(self._payload(repo, "SessionStart"), root=root)
        local = self._payload(repo, "PreToolUse", tool_name="Write",
                              tool_input={"file_path":
                                          str(repo / ".local" / "s.json")})
        assert gate.process(local, root=root) == 0
        conn = cdb.connect(root)
        cdb.set_mode(conn, "off", "test", "maintenance")
        conn.close()
        anything = self._payload(repo, "PreToolUse", tool_name="Write",
                                 tool_input={"file_path":
                                             str(repo / "src" / "a.py")})
        assert gate.process(anything, root=root) == 0


class TestCliAndDoctor:
    def test_cli_register_claim_conflict_status_roundtrip(
            self, env, monkeypatch, capsys):
        from coordination.cli import main as cli_main
        root, repo = env
        monkeypatch.chdir(repo)

        assert cli_main(["--json", "register", "--provider", "claude-code",
                         "--task", "TC-T1"]) == 0
        out_a = json.loads(capsys.readouterr().out)
        aid, tok = out_a["data"]["agent_id"], out_a["data"]["token"]

        assert cli_main(["--json", "--agent", aid, "--token", tok, "claim",
                         "--resource", "src/a.py"]) == 0
        capsys.readouterr()

        assert cli_main(["--json", "register", "--provider", "codex"]) == 0
        out_b = json.loads(capsys.readouterr().out)
        bid, btok = out_b["data"]["agent_id"], out_b["data"]["token"]

        assert cli_main(["--json", "--agent", bid, "--token", btok, "claim",
                         "--resource", "src/a.py"]) == 2
        err = json.loads(capsys.readouterr().out)
        assert aid in err["error"]

        assert cli_main(["--json", "--agent", bid, "--token", btok,
                         "preflight", "--file", "src/a.py"]) == 2
        capsys.readouterr()

        # Open conflict -> status exits 1 and lists it.
        assert cli_main(["--json", "status"]) == 1
        snap = json.loads(capsys.readouterr().out)
        assert snap["data"]["open_conflicts"]
        cid = snap["data"]["open_conflicts"][0]["conflict_id"]

        assert cli_main(["--json", "conflicts", "resolve", "--id", cid,
                         "--state", "ACKNOWLEDGED",
                         "--note", "B waits for A"]) == 0
        capsys.readouterr()
        assert cli_main(["--json", "status"]) == 0
        capsys.readouterr()

        assert cli_main(["--json", "--agent", aid, "--token", tok,
                         "complete"]) == 0
        capsys.readouterr()

    def test_cli_never_tracebacks_on_malformed_db(self, env, monkeypatch,
                                                  capsys):
        from coordination.cli import main as cli_main
        root, repo = env
        monkeypatch.chdir(repo)
        (root / "coordination.db").write_text("garbage", encoding="utf-8")
        code = cli_main(["--json", "status"])
        out = json.loads(capsys.readouterr().out)
        assert code == 1 and out["error"]

    def test_doctor_healthy_then_selftest(self, env, monkeypatch, capsys):
        from coordination.doctor import run_doctor
        root, repo = env
        monkeypatch.chdir(repo)
        report = run_doctor(root, selftest=True)
        assert report["healthy"] is True
        assert report["selftest"]["passed"] is True

    def test_doctor_fix_safe_releases_orphans(self, env, monkeypatch):
        from coordination.doctor import run_doctor
        root, repo = env
        monkeypatch.chdir(repo)
        ra = _register(root, repo)
        _claim_file(root, repo, ra, "src/a.py")
        # Terminal agent with a live lease = orphan (simulated crash edge).
        conn = cdb.connect(root)
        with cdb.immediate(conn):
            conn.execute("UPDATE agents SET status='COMPLETED'")
        conn.close()
        report = run_doctor(root, fix_safe=True)
        assert any("orphan" in f for f in report["fixes"])
        conn = cdb.connect(root)
        try:
            assert conn.execute("SELECT status FROM leases").fetchone()[
                "status"] == "RELEASED"
        finally:
            conn.close()
