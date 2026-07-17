"""test_governance_validators_coordination_v252.py — TC-STRUCT-004 (2026-07-17).

Unit tests for V252 (validate_stale_lease_drift_and_gap_aging):
  Part A: a STALE lease whose file has real uncommitted git drift -> WARN.
  Part B: a known_gaps entry open longer than 14 days -> WARN.
Both parts are WARN-only by design (never FAIL/block) -- this validator makes
currently-invisible, indefinitely-dormant items visible, it does not force a
fix timeline. Hermetic: isolated coordination root + sandbox git repo,
subprocess.run mocked for the git calls the function makes internally.

NOTE: V194-V196 in the same module (governance_validators_coordination.py)
have no existing test coverage anywhere in this repo -- confirmed by search,
not assumed. Out of this taskcard's scope to backfill; noted for the record.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

_SUPERVISOR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from coordination import db as cdb  # noqa: E402
from coordination import root as croot  # noqa: E402
from coordination.registry import AgentRegistry  # noqa: E402
from governance_validators_coordination import (  # noqa: E402
    validate_stale_lease_drift_and_gap_aging as v252,
)


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    cdb.ensure_db(root)
    return root, repo


def _insert_stale_lease(root: Path, repo: Path, resource_key: str, display: str) -> None:
    agent = AgentRegistry(root, start=repo).register("claude-code")
    conn = cdb.connect(root)
    with cdb.immediate(conn):
        conn.execute(
            "INSERT INTO leases(lease_id, agent_id, resource_type,"
            " resource_key, resource_display, mode, origin, acquired_at,"
            " last_renewed_at, status)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            (f"lease-{resource_key}", agent.agent_id, "file", resource_key,
             display, "EXCLUSIVE_WRITE", "auto", "2026-07-01T00:00:00Z",
             "2026-07-01T00:00:00Z", "STALE"))
    conn.close()


class TestPartAStaleLeaseDrift:
    def test_no_db_no_leases_is_pass(self, env):
        root, repo = env
        result = v252({}, repo_root=repo)
        assert result["result"] == "PASS"

    def test_stale_lease_with_real_drift_warns(self, env):
        root, repo = env
        (repo / "f.py").write_text("v1\n", encoding="utf-8")
        subprocess.run(["git", "add", "f.py"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        (repo / "f.py").write_text("v2 -- uncommitted edit\n", encoding="utf-8")
        _insert_stale_lease(root, repo, "f.py", "f.py")
        result = v252({}, repo_root=repo)
        assert result["result"] == "WARN"
        assert any("real uncommitted drift" in w and "f.py" in w
                   for w in result["violations"])

    def test_stale_lease_with_no_drift_does_not_warn(self, env):
        root, repo = env
        (repo / "g.py").write_text("v1\n", encoding="utf-8")
        subprocess.run(["git", "add", "g.py"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
        _insert_stale_lease(root, repo, "g.py", "g.py")
        result = v252({}, repo_root=repo)
        assert result["result"] == "PASS"

    def test_stale_lease_on_nonexistent_file_does_not_warn(self, env):
        root, repo = env
        _insert_stale_lease(root, repo, "gone.py", "gone.py")
        result = v252({}, repo_root=repo)
        assert result["result"] == "PASS"


class TestPartBKnownGapsAging:
    def test_no_policy_file_is_pass(self, env):
        root, repo = env
        result = v252({}, repo_root=repo)
        assert result["result"] == "PASS"

    def test_old_open_gap_warns(self, env):
        root, repo = env
        (repo / "docs" / "governance").mkdir(parents=True)
        (repo / "docs" / "governance" / "skill-only-policy.yaml").write_text(
            "known_gaps:\n"
            "  - gap_id: EP-999-GAP\n"
            "    status: open\n",
            encoding="utf-8",
        )
        old_epoch = int(time.time() - 20 * 86400)  # 20 days ago

        real_run = subprocess.run

        def fake_run(cmd, *a, **kw):
            if cmd[:2] == ["git", "log"]:
                return subprocess.CompletedProcess(cmd, 0, stdout=f"{old_epoch}\n", stderr="")
            return real_run(cmd, *a, **kw)

        with patch("governance_validators_coordination.subprocess.run",
                   side_effect=fake_run):
            result = v252({}, repo_root=repo)
        assert result["result"] == "WARN"
        assert any("EP-999-GAP" in w and "20 days" in w for w in result["violations"])

    def test_recent_open_gap_does_not_warn(self, env):
        root, repo = env
        (repo / "docs" / "governance").mkdir(parents=True)
        (repo / "docs" / "governance" / "skill-only-policy.yaml").write_text(
            "known_gaps:\n"
            "  - gap_id: EP-998-GAP\n"
            "    status: open\n",
            encoding="utf-8",
        )
        recent_epoch = int(time.time() - 2 * 86400)  # 2 days ago

        real_run = subprocess.run

        def fake_run(cmd, *a, **kw):
            if cmd[:2] == ["git", "log"]:
                return subprocess.CompletedProcess(cmd, 0, stdout=f"{recent_epoch}\n", stderr="")
            return real_run(cmd, *a, **kw)

        with patch("governance_validators_coordination.subprocess.run",
                   side_effect=fake_run):
            result = v252({}, repo_root=repo)
        assert result["result"] == "PASS"

    def test_resolved_gap_not_flagged(self, env):
        root, repo = env
        (repo / "docs" / "governance").mkdir(parents=True)
        (repo / "docs" / "governance" / "skill-only-policy.yaml").write_text(
            "known_gaps:\n"
            "  - gap_id: EP-997-GAP\n"
            "    status: resolved\n",
            encoding="utf-8",
        )
        result = v252({}, repo_root=repo)
        assert result["result"] == "PASS"


def test_never_blocks_sprint_even_with_warnings(env):
    """WARN-only by design -- V252 must never set blocks_sprint=True."""
    root, repo = env
    (repo / "f.py").write_text("v1\n", encoding="utf-8")
    subprocess.run(["git", "add", "f.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    (repo / "f.py").write_text("v2\n", encoding="utf-8")
    _insert_stale_lease(root, repo, "f.py", "f.py")
    result = v252({}, repo_root=repo)
    assert result["blocks_sprint"] is False
