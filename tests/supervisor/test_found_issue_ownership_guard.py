"""test_found_issue_ownership_guard.py — TC-STRUCT-001 (2026-07-17).

Isolated unit tests for lifecycle_audit.check_found_issue_ownership_guard
(G5), monkeypatching the fresh-audit call and the surfaced-findings log so
tests are deterministic and independent of the live, constantly-changing
repo state (~40-50 concurrent agents).
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO / "tools"))

import lifecycle_audit as la  # noqa: E402
from governance.skills_first import audit as sfc_audit  # noqa: E402
from governance.skills_first import surfaced_findings as sf  # noqa: E402


_A_FINDING = {
    "category": "stale_command_hash",
    "command_file": ".claude/commands/example.md",
    "severity": "HIGH",
    "detail": "command content diverged from baseline",
}


def _make_register(tmp_path: Path, issues: list[dict]) -> Path:
    import yaml
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(exist_ok=True)
    (reg_dir / "found-issue-register.yaml").write_text(
        yaml.dump({"version": 1, "issues": issues}), encoding="utf-8"
    )
    return tmp_path


@pytest.fixture(autouse=True)
def _isolated_surfaced_log(tmp_path, monkeypatch):
    """Never touch the real .local/supervisor/surfaced-findings.jsonl."""
    monkeypatch.setattr(sf, "SURFACED_FINDINGS_LOG", tmp_path / "surfaced-findings.jsonl")
    yield


def _recent_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


def _old_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=72)).isoformat()


def _just_under_48h_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=47)).isoformat()


def _seed_entry(fp: str, agent_id: str, ts: str, **extra):
    import json
    entry = {"ts": ts, "agent_id": agent_id, "fingerprint": fp,
              "severity": "HIGH", "category": "stale_command_hash",
              "command_file": ".claude/commands/example.md", **extra}
    with sf.SURFACED_FINDINGS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def test_no_violations_when_no_findings(tmp_path, monkeypatch):
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": []})
    _make_register(tmp_path, [])
    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None


def test_tier_a_blocks_own_reproducing_finding_with_no_register_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": [_A_FINDING]})
    _make_register(tmp_path, [])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-me", _recent_ts())

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is not None
    assert result["guard_id"] == "G5_FOUND_ISSUE_OWNERSHIP"
    assert result["severity"] == "CRITICAL"
    assert any("G5-A" in item for item in result["items"])


def test_tier_a_passes_when_register_entry_has_valid_disposition(tmp_path, monkeypatch):
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": [_A_FINDING]})
    _make_register(tmp_path, [{
        "issue_id": "FI-100", "status": "closed",
        "disposition": "BLOCKED_TRUE_EXTERNAL_DEPENDENCY",
        "affected_paths": [".claude/commands/example.md"],
    }])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-me", _recent_ts())

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None


def test_tier_a_passes_when_finding_no_longer_reproduces(tmp_path, monkeypatch):
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": []})  # fixed
    _make_register(tmp_path, [])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-me", _recent_ts())

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None


def test_tier_a_ignores_a_different_agents_finding(tmp_path, monkeypatch):
    """Not my finding, not old enough for Tier B either -> no violation from Tier A."""
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": [_A_FINDING]})
    _make_register(tmp_path, [])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-other", _recent_ts())  # recent, <48h

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None


def test_tier_b_blocks_old_ownerless_finding_from_any_agent(tmp_path, monkeypatch):
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": [_A_FINDING]})
    _make_register(tmp_path, [])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-other", _old_ts())  # >48h old, not mine

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is not None
    assert any("G5-B" in item for item in result["items"])


def test_tier_b_passes_when_any_register_entry_exists_even_undisposed(tmp_path, monkeypatch):
    """Tier B's bar is 'registered', not 'validly disposed' -- an in-flight
    entry (no disposition yet) still counts as being on the radar."""
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": [_A_FINDING]})
    _make_register(tmp_path, [{
        "issue_id": "FI-101", "status": "discovered",
        "affected_paths": [".claude/commands/example.md"],
    }])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-other", _old_ts())

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None


def test_tier_b_does_not_fire_before_48h(tmp_path, monkeypatch):
    monkeypatch.setattr(sfc_audit, "run_audit", lambda: {"findings": [_A_FINDING]})
    _make_register(tmp_path, [])
    fp = sf._fingerprint(_A_FINDING)
    _seed_entry(fp, "agent-other", _just_under_48h_ts())  # <48h old

    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None


def test_guard_never_raises_when_audit_module_broken(tmp_path, monkeypatch):
    def _boom():
        raise RuntimeError("audit crashed")
    monkeypatch.setattr(sfc_audit, "run_audit", _boom)
    _make_register(tmp_path, [])
    result = la.check_found_issue_ownership_guard(tmp_path, agent_id="agent-me")
    assert result is None  # swallowed, never propagates
