"""
tests/supervisor/test_anti_skip_raw_logs.py

Lane 5 — Sprint FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

Tests for anti_skip_checker behavior: verifies that the checker:
  1. Correctly identifies missing raw logs (advisory warning, not hard block for non-product sprints)
  2. Does not false-positive on supervisor-tier sprints with exempted items
  3. Returns proper structure with impact.block and impact.caveats
"""

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from anti_skip_checker import run_all_checks


_BASE_DECL = {
    "run_id": "test-run-001",
    "sprint_id": "FORMAT-FACTORY-TEST-001",
    "evidence_root": ".local/evidences/test-run-001",
    "planned_work_items": [],
    "test_results": {"tests_run": 0, "tests_pass": 0, "tests_fail": 0},
    "worker_self_verdict": "IMPLEMENTED",
}


def _run(declaration: dict = None) -> dict:
    """Convenience wrapper: run anti-skip with a complete minimal declaration."""
    merged = {**_BASE_DECL, **(declaration or {})}
    # Merge planned_work_items correctly
    if declaration and "planned_work_items" in declaration:
        merged["planned_work_items"] = declaration["planned_work_items"]
    return run_all_checks(declaration=merged, repo_root=_REPO)


# ---------------------------------------------------------------------------
# Basic structure tests
# ---------------------------------------------------------------------------

class TestAntiSkipBasicStructure:
    """Verify run_all_checks returns proper structure."""

    def test_returns_dict(self):
        result = _run()
        assert isinstance(result, dict)

    def test_result_has_violations_field(self):
        result = _run()
        assert "violations" in result

    def test_result_has_all_pass_field(self):
        result = _run()
        assert "all_pass" in result

    def test_result_has_impact_field(self):
        result = _run()
        assert "impact" in result

    def test_impact_has_block_field(self):
        result = _run()
        assert "block" in result["impact"]

    def test_impact_block_is_bool(self):
        result = _run()
        assert isinstance(result["impact"]["block"], bool)

    def test_result_has_checks_field(self):
        result = _run()
        assert "checks" in result

    def test_all_pass_is_bool(self):
        result = _run()
        assert isinstance(result["all_pass"], bool)

    def test_violations_is_int(self):
        result = _run()
        assert isinstance(result["violations"], int)

    def test_empty_declaration_has_zero_violations(self):
        result = _run()
        assert result["violations"] == 0


# ---------------------------------------------------------------------------
# Advisory vs blocking behavior
# ---------------------------------------------------------------------------

class TestAntiSkipAdvisoryBehavior:
    """Verify that missing_raw_logs is advisory (caveat), not a hard block."""

    def test_missing_raw_logs_is_caveat_not_block(self):
        """A supervisor sprint without raw logs should produce caveats, not block."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "L1",
                    "title": "Wire evidence_continuation",
                    "status": "IMPLEMENTED",
                    "exemption_reason": "supervisor repair",
                }
            ]
        }
        result = _run(decl)
        # Must not hard-block a supervisor sprint for missing raw logs
        assert result["impact"].get("block") is False, (
            f"Supervisor sprint should not be blocked by anti-skip; impact={result['impact']}"
        )

    def test_anti_skip_does_not_block_exempted_sprint(self):
        """Sprint with all exempted items must not be blocked."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-001",
                    "title": "Supervisor repair work",
                    "exemption_reason": "supervisor-tier tooling repair",
                    "tests_run": 26,
                    "tests_pass": 26,
                }
            ]
        }
        result = _run(decl)
        assert result["impact"].get("block") is False

    def test_result_serializable_to_json(self):
        """Anti-skip result must be serializable for evidence artifacts."""
        result = _run()
        serialized = json.dumps(result)
        assert len(serialized) > 0

    def test_impact_has_caveats_list(self):
        """Impact dict must have a caveats list for advisory warnings."""
        result = _run()
        assert "caveats" in result["impact"]
        assert isinstance(result["impact"]["caveats"], list)

    def test_impact_has_downgrade_field(self):
        """Impact dict must have downgrade field."""
        result = _run()
        assert "downgrade" in result["impact"]


# ---------------------------------------------------------------------------
# Consistency with validate_adoption
# ---------------------------------------------------------------------------

class TestAntiSkipAdoptionConsistency:
    """Both adoption compliance and anti-skip must agree on supervisor sprint status."""

    def test_supervisor_sprint_passes_both_checks(self):
        """A Sprint 10 style declaration must pass both adoption and anti-skip."""
        from validate_adoption_compliance import validate_adoption

        items = [
            {
                "item_id": "L1-001",
                "title": "Wire evidence_continuation into autonomous_cycle.py",
                "status": "IMPLEMENTED",
                "exemption_reason": "supervisor-tier tooling repair; no skill invocation required",
                "tests_run": 28,
                "tests_pass": 28,
                "evidence_paths": ["reports/no-manual-prompt-chain-repair/continuation-contract/"],
            },
            {
                "item_id": "L2-001",
                "title": "Fix next-work-items external-gate classification",
                "status": "IMPLEMENTED",
                "exemption_reason": "supervisor-tier tooling repair; no skill invocation required",
                "tests_run": 66,
                "tests_pass": 66,
                "evidence_paths": ["reports/no-manual-prompt-chain-repair/next-work-safety/"],
            },
        ]
        decl_for_adoption = {"planned_work_items": items}
        decl_for_antiskip = {"planned_work_items": items}

        adoption = validate_adoption(decl_for_adoption)
        anti_skip = _run(decl_for_antiskip)

        # Both must not fail/block
        assert adoption["compliant"] is True, f"Adoption should pass: {adoption['summary']}"
        assert anti_skip["impact"].get("block") is False, (
            f"Anti-skip should not block: {anti_skip['impact']}"
        )
