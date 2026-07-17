"""test_surfaced_findings.py — TC-STRUCT-001 (2026-07-17).

Unit tests for tools/governance/skills_first/surfaced_findings.py: the
append-only, per-agent HIGH/CRITICAL findings log the new ambient
found-issue-ownership closure guard (lifecycle_audit.py's G5) reads.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance.skills_first import surfaced_findings as sf  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_log(tmp_path, monkeypatch):
    monkeypatch.setattr(sf, "SURFACED_FINDINGS_LOG", tmp_path / "surfaced-findings.jsonl")
    yield


def test_record_only_writes_high_and_critical():
    findings = [
        {"category": "a", "severity": "INFO", "detail": "x"},
        {"category": "b", "severity": "MEDIUM", "detail": "y"},
        {"category": "c", "severity": "HIGH", "detail": "z"},
        {"category": "d", "severity": "CRITICAL", "detail": "w"},
    ]
    n = sf.record_surfaced_findings(findings, agent_id="agent-x")
    assert n == 2
    entries = sf.read_surfaced_findings()
    assert {e["category"] for e in entries} == {"c", "d"}


def test_record_never_raises_on_write_failure(monkeypatch):
    monkeypatch.setattr(sf, "SURFACED_FINDINGS_LOG", Path("Z:/nonexistent/impossible/path.jsonl"))
    n = sf.record_surfaced_findings([{"severity": "HIGH", "detail": "x"}], agent_id="a")
    assert n == 0  # swallowed, never raises


def test_read_returns_empty_list_when_log_missing():
    assert sf.read_surfaced_findings() == []


def test_read_dedupes_by_fingerprint_keeping_earliest():
    finding = {"category": "a", "command_file": "f.py", "skill_id": None, "detail": "d"}
    fp = sf._fingerprint(finding)
    sf.SURFACED_FINDINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with sf.SURFACED_FINDINGS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": "2026-07-17T12:00:00+00:00", "agent_id": "a",
                              "fingerprint": fp, "severity": "HIGH"}) + "\n")
        fh.write(json.dumps({"ts": "2026-07-17T08:00:00+00:00", "agent_id": "a",
                              "fingerprint": fp, "severity": "HIGH"}) + "\n")
    entries = sf.read_surfaced_findings()
    assert len(entries) == 1
    assert entries[0]["ts"] == "2026-07-17T08:00:00+00:00"


def test_read_filters_by_agent_id():
    sf.SURFACED_FINDINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with sf.SURFACED_FINDINGS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": "t1", "agent_id": "a1", "fingerprint": "fp1",
                              "severity": "HIGH"}) + "\n")
        fh.write(json.dumps({"ts": "t2", "agent_id": "a2", "fingerprint": "fp2",
                              "severity": "HIGH"}) + "\n")
    assert len(sf.read_surfaced_findings(agent_id="a1")) == 1
    assert len(sf.read_surfaced_findings(agent_id="a2")) == 1
    assert len(sf.read_surfaced_findings()) == 2


def test_read_skips_malformed_lines_without_raising():
    sf.SURFACED_FINDINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
    sf.SURFACED_FINDINGS_LOG.write_text(
        "not json at all\n"
        + json.dumps({"ts": "t1", "agent_id": "a1", "fingerprint": "fp1", "severity": "HIGH"})
        + "\n",
        encoding="utf-8",
    )
    entries = sf.read_surfaced_findings()
    assert len(entries) == 1


def test_resolve_agent_id_prefers_env_var(monkeypatch):
    monkeypatch.setenv("FF_AGENT_ID", "agent-explicit-123")
    assert sf.resolve_agent_id() == "agent-explicit-123"


def test_fingerprint_is_stable_and_ignores_severity_and_timestamp():
    f1 = {"category": "a", "command_file": "x.py", "skill_id": None,
          "detail": "same detail", "severity": "HIGH"}
    f2 = {"category": "a", "command_file": "x.py", "skill_id": None,
          "detail": "same detail", "severity": "CRITICAL"}
    assert sf._fingerprint(f1) == sf._fingerprint(f2)


def test_fingerprint_differs_for_different_findings():
    f1 = {"category": "a", "command_file": "x.py", "detail": "d1"}
    f2 = {"category": "a", "command_file": "y.py", "detail": "d2"}
    assert sf._fingerprint(f1) != sf._fingerprint(f2)
