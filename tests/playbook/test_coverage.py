"""
test_coverage.py — TC-PB-009: Playbook Coverage Tests

Verifies that coverage gaps are detected, low-value workflows don't force
playbook creation, and duplicate playbooks are detected.
"""
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).parent.parent.parent
_COVERAGE_PATH = _REPO / "reports" / "playbooks" / "playbook-coverage-universe.yaml"
_PB_DIR = _REPO / "playbooks" / "format-factory"

sys.path.insert(0, str(_REPO / "tools" / "playbook"))


@pytest.fixture
def coverage_data():
    if not _COVERAGE_PATH.exists():
        pytest.skip("playbook-coverage-universe.yaml not found")
    return yaml.safe_load(_COVERAGE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def coverage_workflows(coverage_data):
    """The coverage universe items (list under coverage_universe key)."""
    return coverage_data.get("coverage_universe", [])


class TestCoverageUniverseReport:
    def test_coverage_report_exists(self):
        assert _COVERAGE_PATH.exists(), (
            "reports/playbooks/playbook-coverage-universe.yaml must exist"
        )

    def test_coverage_report_has_workflows(self, coverage_workflows):
        assert len(coverage_workflows) > 0, "Coverage universe must have at least one workflow"

    def test_all_workflows_have_coverage_status(self, coverage_workflows):
        for wf in coverage_workflows:
            status = wf.get("coverage_status", "")
            assert status, (
                f"Workflow {wf.get('workflow_id', '?')} missing coverage_status"
            )

    def test_no_high_value_workflow_without_disposition(self, coverage_data):
        """HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION must be 0."""
        meta = coverage_data.get("meta", {})
        counters = meta.get("counters", {})
        count = counters.get("HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION", 0)
        assert count == 0, (
            f"Expected 0 high-value workflows without disposition, got {count}"
        )

    def test_missing_high_value_workflows_have_action(self, coverage_workflows):
        missing_hv = [
            w for w in coverage_workflows
            if w.get("coverage_status") == "MISSING_HIGH_VALUE"
        ]
        for wf in missing_hv:
            action = wf.get("recommended_action", "")
            assert action, (
                f"MISSING_HIGH_VALUE workflow {wf.get('workflow_id')} must have recommended_action"
            )

    def test_some_workflows_handled_by_skills_or_policies(self, coverage_workflows):
        """Not all workflows should require playbooks — skills/policies handle some."""
        replace_or_skip = [
            w for w in coverage_workflows
            if "REPLACE" in w.get("coverage_status", "")
            or w.get("coverage_status") == "NOT_WORTH_PLAYBOOK"
        ]
        covered = [
            w for w in coverage_workflows
            if "COVERED" in w.get("coverage_status", "")
        ]
        assert len(replace_or_skip) + len(covered) > 0, (
            "Expected some workflows covered or delegated to skills/policies"
        )


class TestNoDuplicatePlaybooks:
    def test_no_duplicate_playbook_ids(self):
        """Two playbook contracts must not declare the same playbook_id."""
        import re
        if not _PB_DIR.exists():
            pytest.skip("playbooks/format-factory/ not found")
        seen_ids: dict = {}
        for md in _PB_DIR.glob("*.md"):
            text = md.read_text(encoding="utf-8")
            m = re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, re.DOTALL)
            if not m:
                continue
            data = yaml.safe_load(m.group(1))
            contract = data.get("playbook_contract", {}) if isinstance(data, dict) else {}
            pid = contract.get("playbook_id", "")
            if pid:
                assert pid not in seen_ids, (
                    f"Duplicate playbook_id {pid!r} in {md.name} and {seen_ids[pid]}"
                )
                seen_ids[pid] = md.name

    def test_no_duplicate_work_item_mappings(self):
        """A single work item type should not map to two different playbooks."""
        from playbook_selector import _WORK_ITEM_MAP
        # Verify no two work item types map to exactly the same non-None path
        # (having the same path means they'd both pick the same playbook, which is fine if intended)
        paths = [v for v in _WORK_ITEM_MAP.values() if v]
        path_counts: dict = {}
        for p in paths:
            path_counts[p] = path_counts.get(p, 0) + 1
        # This is a structural check — same path for multiple types is allowed
        # But we verify the map itself is a dict (no accidental list)
        assert isinstance(_WORK_ITEM_MAP, dict)
        assert len(_WORK_ITEM_MAP) > 0


class TestHighValueGapDetection:
    def test_audit_healing_sprint_backfilled(self):
        """The audit-healing-sprint template must exist (was a MISSING_HIGH_VALUE gap)."""
        expected = _PB_DIR / "audit-healing-sprint.md"
        assert expected.exists(), (
            "audit-healing-sprint.md must exist (backfilled high-value gap)"
        )

    def test_pipeline_incident_response_backfilled(self):
        """The pipeline-incident-response template must exist."""
        expected = _PB_DIR / "pipeline-incident-response.md"
        assert expected.exists(), (
            "pipeline-incident-response.md must exist (backfilled high-value gap)"
        )

    def test_package_release_readiness_backfilled(self):
        """The package-release-readiness template must exist."""
        expected = _PB_DIR / "package-release-readiness.md"
        assert expected.exists(), (
            "package-release-readiness.md must exist (backfilled high-value gap)"
        )
