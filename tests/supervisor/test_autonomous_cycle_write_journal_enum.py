"""FI-028: autonomous_cycle.py's write_journal calls used op/source values outside the
write_journal table's CHECK constraints (op must be one of create/edit/append/regenerate/
delete; source must be one of hook/cli/guard). The invalid values raised
sqlite3.IntegrityError inside coordinated_write's `finally` block, silently aborting the
rest of the enclosing try/except in _write_signal_and_ancillary_outputs whenever a live
coordination identity was present -- skipping the CCI ledger append, stream signal write,
maturity signal emission, adversarial check, GOV_BLOCK directive, and evidence_continuation
bridging with only a swallowed "WARNING: Continuation signal failed" printed.

Mirrors the sibling fix already shipped to write_plan_lock.py, lifecycle_audit.py, and
sprint_executor.py: op="edit", source="cli".
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from coordination import db as cdb
from coordination import root as croot
from coordination.leases import LeaseManager
from coordination.preflight import record_write
from coordination.registry import AgentRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTONOMOUS_CYCLE_PY = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"

_VALID_OPS = {"create", "edit", "append", "regenerate", "delete"}
_VALID_SOURCES = {"hook", "cli", "guard"}


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path / "coord"
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "reports" / "supervisor").mkdir(parents=True)
    (repo / "reports" / "supervisor" / "continuation-signal.json").write_text(
        "{}\n", encoding="utf-8")
    monkeypatch.setenv(croot.ENV_ROOT, str(root))
    monkeypatch.delenv("FF_AGENT_ID", raising=False)
    monkeypatch.delenv("FF_AGENT_TOKEN", raising=False)
    cdb.ensure_db(root)
    return root, repo


def _register_and_claim(root, repo, path):
    ra = AgentRegistry(root, start=repo).register("claude-code")
    LeaseManager(root, start=repo).claim(ra.agent_id, ra.token, [path])
    return ra


class TestWriteJournalEnumConstraint:
    """Proves the root cause (invalid enum -> IntegrityError) and the fix (valid enum ->
    succeeds), using the real write_journal table -- not a synthetic stand-in schema."""

    def test_invalid_op_raises_integrity_error(self, env):
        root, repo = env
        ra = _register_and_claim(root, repo, "reports/supervisor/continuation-signal.json")
        with pytest.raises(sqlite3.IntegrityError):
            record_write(
                "reports/supervisor/continuation-signal.json",
                op="continuation_signal", root=root, start=repo,
                agent_id=ra.agent_id, token=ra.token, source="autonomous_cycle")

    def test_invalid_source_raises_integrity_error(self, env):
        root, repo = env
        ra = _register_and_claim(root, repo, "reports/supervisor/continuation-signal.json")
        with pytest.raises(sqlite3.IntegrityError):
            record_write(
                "reports/supervisor/continuation-signal.json",
                op="edit", root=root, start=repo,
                agent_id=ra.agent_id, token=ra.token, source="autonomous_cycle")

    def test_fixed_op_and_source_succeed(self, env):
        root, repo = env
        ra = _register_and_claim(root, repo, "reports/supervisor/continuation-signal.json")
        result = record_write(
            "reports/supervisor/continuation-signal.json",
            op="edit", root=root, start=repo,
            agent_id=ra.agent_id, token=ra.token, source="cli")
        assert result is not None
        assert result["agent_id"] == ra.agent_id


class TestAutonomousCycleCallSitesUseValidEnumValues:
    """Static guard against this exact bug pattern recurring: every _coordinated_write(...)
    call in autonomous_cycle.py must pass an op/source that the write_journal CHECK
    constraint actually accepts."""

    def test_all_coordinated_write_calls_use_valid_enum_values(self):
        text = AUTONOMOUS_CYCLE_PY.read_text(encoding="utf-8")
        calls = re.findall(
            r"_coordinated_write\([^)]*?op=\"([^\"]+)\"[^)]*?source=\"([^\"]+)\"",
            text, flags=re.DOTALL)
        assert calls, "expected at least one _coordinated_write(..., op=..., source=...) call"
        bad = [(op, src) for op, src in calls
               if op not in _VALID_OPS or src not in _VALID_SOURCES]
        assert not bad, f"invalid write_journal enum values found: {bad}"
