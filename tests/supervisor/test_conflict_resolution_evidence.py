"""test_conflict_resolution_evidence.py — TC-STRUCT-003 (2026-07-17).

`coordination conflicts resolve --state RESOLVED` used to accept a free-text
note with zero verification that remediation actually happened. This tests
the fix: RESOLVED now requires --evidence resolving to a real git commit, an
allowlisted found-issue-register entry, or a write_journal-verified
same-session-rebaseline. Hermetic: isolated coordination root + sandbox git
repo per test, following the existing test_coordination_guards.py pattern.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_SUPERVISOR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from coordination import db as cdb  # noqa: E402
from coordination import root as croot  # noqa: E402
from coordination.conflicts import ConflictLog  # noqa: E402
from coordination.registry import AgentRegistry  # noqa: E402


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    monkeypatch.delenv("FF_AGENT_ID", raising=False)
    monkeypatch.delenv("FF_AGENT_TOKEN", raising=False)
    monkeypatch.chdir(repo)
    cdb.ensure_db(root)
    return root, repo


def _record_conflict(root: Path, resource_key: str = "hot.py") -> str:
    conn = cdb.connect(root)
    with cdb.immediate(conn):
        cid = ConflictLog(root).record(
            conn, resource_key=resource_key, resource_display=resource_key,
            detected_by="agent-x", conflict_type="unknown-change",
            safe_action="preserve-and-rebaseline")
    conn.close()
    return cid


class TestResolvedRequiresEvidence:
    def test_resolved_with_no_evidence_is_rejected(self, env):
        root, repo = env
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="requires --evidence"):
            ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "fixed it")

    def test_resolved_with_garbage_evidence_is_rejected(self, env):
        root, repo = env
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="not a recognized"):
            ConflictLog(root).resolve(
                cid, "agent-me", "RESOLVED", "fixed it",
                evidence="just trust me")

    def test_resolved_with_real_commit_hash_is_accepted(self, env):
        root, repo = env
        (repo / "f.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "add", "f.txt"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                              capture_output=True, text=True, check=True).stdout.strip()
        cid = _record_conflict(root)
        ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "fixed, see commit",
                                   evidence=sha)
        rows = ConflictLog(root).list_conflicts(open_only=False)
        assert rows[0]["resolution_state"] == "RESOLVED"

    def test_resolved_with_fabricated_commit_hash_is_rejected(self, env):
        root, repo = env
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="does not resolve to a real commit"):
            ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "fixed",
                                       evidence="deadbeef1234567")

    def test_resolved_with_valid_found_issue_id_is_accepted(self, env, monkeypatch):
        root, repo = env
        (repo / "registry").mkdir()
        (repo / "registry" / "found-issue-register.yaml").write_text(
            "issues:\n"
            "  - issue_id: FI-900\n"
            "    disposition: HEALED_AND_VERIFIED\n",
            encoding="utf-8",
        )
        cid = _record_conflict(root)
        ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "see FI-900",
                                   evidence="FI-900")
        rows = ConflictLog(root).list_conflicts(open_only=False)
        assert rows[0]["resolution_state"] == "RESOLVED"

    def test_resolved_with_found_issue_id_missing_invalid_disposition_is_rejected(
            self, env):
        root, repo = env
        (repo / "registry").mkdir()
        (repo / "registry" / "found-issue-register.yaml").write_text(
            "issues:\n"
            "  - issue_id: FI-901\n"
            "    disposition: OPEN_OUT_OF_SCOPE\n",
            encoding="utf-8",
        )
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="not one of the 6 allowlisted"):
            ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "see FI-901",
                                       evidence="FI-901")

    def test_resolved_with_nonexistent_found_issue_id_is_rejected(self, env):
        root, repo = env
        (repo / "registry").mkdir()
        (repo / "registry" / "found-issue-register.yaml").write_text(
            "issues: []\n", encoding="utf-8")
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="no entry FI-999"):
            ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "note",
                                       evidence="FI-999")

    def test_same_session_rebaseline_accepted_when_agent_is_last_writer(self, env):
        root, repo = env
        cid = _record_conflict(root, resource_key="mine.py")
        conn = cdb.connect(root)
        with cdb.immediate(conn):
            from coordination.baselines import BaselineTracker
            BaselineTracker().journal(conn, "agent-me", None, "mine.py", "edit",
                                    "abc", "def", source="cli")
        conn.close()
        ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "own rebaseline",
                                   evidence="same-session-rebaseline")
        rows = ConflictLog(root).list_conflicts(open_only=False)
        assert rows[0]["resolution_state"] == "RESOLVED"

    def test_same_session_rebaseline_rejected_when_different_agent_wrote_last(
            self, env):
        root, repo = env
        cid = _record_conflict(root, resource_key="theirs.py")
        conn = cdb.connect(root)
        with cdb.immediate(conn):
            from coordination.baselines import BaselineTracker
            BaselineTracker().journal(conn, "agent-other", None, "theirs.py",
                                    "edit", "abc", "def", source="cli")
        conn.close()
        with pytest.raises(ValueError, match="does not match the resolving agent"):
            ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "claim",
                                       evidence="same-session-rebaseline")

    def test_same_session_rebaseline_rejected_with_no_journal_entry(self, env):
        root, repo = env
        cid = _record_conflict(root, resource_key="nobody-wrote-this.py")
        with pytest.raises(ValueError, match="no write_journal entry"):
            ConflictLog(root).resolve(cid, "agent-me", "RESOLVED", "claim",
                                       evidence="same-session-rebaseline")


class TestAcknowledgedAndWontFixStillRequireRealReason:
    def test_acknowledged_with_generic_reason_rejected(self, env):
        root, repo = env
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="too generic"):
            ConflictLog(root).resolve(cid, "agent-me", "ACKNOWLEDGED", "done")

    def test_wont_fix_with_generic_reason_rejected(self, env):
        root, repo = env
        cid = _record_conflict(root)
        with pytest.raises(ValueError, match="too generic"):
            ConflictLog(root).resolve(cid, "agent-me", "WONT_FIX", "ok")

    def test_acknowledged_with_real_reason_accepted(self, env):
        root, repo = env
        cid = _record_conflict(root)
        ConflictLog(root).resolve(
            cid, "agent-me", "ACKNOWLEDGED",
            "reviewed the diff, confirms an unrelated agent's WIP edit; "
            "not touching it, deferring")
        rows = ConflictLog(root).list_conflicts(open_only=False)
        assert rows[0]["resolution_state"] == "ACKNOWLEDGED"

    def test_wont_fix_does_not_require_evidence_param(self, env):
        """Lower bar than RESOLVED is intentional -- WONT_FIX is a legitimate,
        lower-friction disposition as long as the reason is real."""
        root, repo = env
        cid = _record_conflict(root)
        ConflictLog(root).resolve(
            cid, "agent-me", "WONT_FIX",
            "resource is a generated report artifact, safe to regenerate "
            "next run, not tracking further")
        rows = ConflictLog(root).list_conflicts(open_only=False)
        assert rows[0]["resolution_state"] == "WONT_FIX"
