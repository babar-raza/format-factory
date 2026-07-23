"""FI-030 (TC-STRUCT-004): V252's WARN-level aging-visibility findings must be
surfaced into session-resume.md's generation step, not only visible when a
validator happens to be run explicitly. Tests _surface_v252_aging_findings()
directly, monkeypatching the V252 checker so no real coordination DB or aged
known_gaps fixture is needed to exercise the surfacing logic itself.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def repo_with_resume(tmp_path) -> Path:
    (tmp_path / "reports" / "supervisor").mkdir(parents=True)
    (tmp_path / "reports" / "supervisor" / "session-resume.md").write_text(
        "# Session Resume\n\nLast sprint: OK\n", encoding="utf-8")
    return tmp_path


def _patch_v252(monkeypatch, result: dict):
    import governance_validators_coordination as gvc

    monkeypatch.setattr(gvc, "validate_stale_lease_drift_and_gap_aging",
                        lambda declaration, repo_root=None: result)


class TestSurfaceV252AgingFindings:
    def test_warn_result_appends_section(self, repo_with_resume, monkeypatch):
        from autonomous_cycle import _surface_v252_aging_findings

        _patch_v252(monkeypatch, {
            "validator": "validate_stale_lease_drift_and_gap_aging",
            "result": "WARN", "blocks_sprint": False,
            "violations": [
                "STALE lease with real uncommitted drift: tools/supervisor/x.py",
                "known_gaps entry EP-001-GAP has been status: open for 22 days",
            ],
            "summary": "V252: 2 aging-visibility item(s)",
        })

        count = _surface_v252_aging_findings(repo_with_resume)

        assert count == 2
        text = (repo_with_resume / "reports" / "supervisor" / "session-resume.md").read_text(
            encoding="utf-8")
        assert "## Aging Visibility (V252)" in text
        assert "STALE lease with real uncommitted drift: tools/supervisor/x.py" in text
        assert "known_gaps entry EP-001-GAP has been status: open for 22 days" in text
        assert "Last sprint: OK" in text  # original content preserved, not overwritten

    def test_pass_result_appends_nothing(self, repo_with_resume, monkeypatch):
        from autonomous_cycle import _surface_v252_aging_findings

        _patch_v252(monkeypatch, {
            "validator": "validate_stale_lease_drift_and_gap_aging",
            "result": "PASS", "blocks_sprint": False,
            "violations": [], "summary": "V252: no aged items",
        })

        count = _surface_v252_aging_findings(repo_with_resume)

        assert count == 0
        text = (repo_with_resume / "reports" / "supervisor" / "session-resume.md").read_text(
            encoding="utf-8")
        assert "Aging Visibility" not in text

    def test_missing_resume_file_is_a_no_op(self, tmp_path, monkeypatch):
        from autonomous_cycle import _surface_v252_aging_findings

        _patch_v252(monkeypatch, {
            "validator": "validate_stale_lease_drift_and_gap_aging",
            "result": "WARN", "blocks_sprint": False,
            "violations": ["some finding"], "summary": "V252: 1 aging-visibility item(s)",
        })

        assert _surface_v252_aging_findings(tmp_path) == 0


class TestV252WiredIntoRunner:
    """FI-030's core wiring requirement: V252 must actually run as part of the
    full governance suite, not just exist standalone (V-numbered validators are
    not auto-discovered -- the runner explicitly imports and dispatches each one)."""

    def test_v252_registered_in_validator_id_authority(self):
        import yaml
        repo_root = Path(__file__).resolve().parents[2]
        authority = yaml.safe_load(
            (repo_root / "registry" / "governance" / "validator-id-authority.yaml")
            .read_text(encoding="utf-8"))
        entries = {e["rule_id"]: e for e in authority["registered_validators"]
                  if isinstance(e, dict) and "rule_id" in e}
        assert "V252" in entries
        assert entries["V252"]["function"] == "validate_stale_lease_drift_and_gap_aging"
        assert entries["V252"]["source_file"] == \
            "tools/supervisor/governance_validators_coordination.py"

    def test_v252_dispatched_by_run_all_governance_validators(self):
        # Static source check, not a live run: run_all_governance_validators()
        # executes the full ~250-validator suite (real filesystem/git/contract
        # compilation work) and is far too heavyweight for a unit test. What
        # matters here -- and what FI-030 was actually about -- is that the
        # dispatch call exists in source, matching the V194-V196/V251 pattern.
        repo_root = Path(__file__).resolve().parents[2]
        runner_src = (repo_root / "tools" / "supervisor" / "governance_validator_runner.py") \
            .read_text(encoding="utf-8")
        assert "validate_stale_lease_drift_and_gap_aging as _v252" in runner_src
        assert '_dispatch(_v252, "V252", declaration, repo_root)' in runner_src
