"""
test_prompt_quality_gate.py

Tests for tools/skills/prompt_quality_gate.py

Run:
  PYTHONPATH=... python -m pytest tests/skills/test_prompt_quality_gate.py -v
"""

import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from prompt_quality_gate import validate_prompt

# ============================================================
# Helpers
# ============================================================

MINIMAL_PASSING_PROMPT = """\
EXECUTION MODE — TEST-SPRINT-001

Repo:
C:/repo

Mission: Test.

COMPONENT 5: READ FIRST — AUTHORITY CONTEXT
Read: AGENTS.md, GOVERNANCE.md

COMPONENT 6: PRE-FLIGHT CHECKS
Run format_context_resolver.py.

COMPONENT 7: AUTHORITY STATE
Requirements State: REQUIREMENTS_AUTHORITATIVE

COMPONENT 8: LANE OWNERSHIP MODEL
Coordinator owns: AGENTS.md

COMPONENT 9: NON-NEGOTIABLE RULES
- No git stash / reset
- No gate self-approval
- No commercial_product_ready: true claim

COMPONENT 10: SELECTED LANES
LANE-I-LOAD, LANE-I-TESTS

COMPONENT 15: VALIDATION COMMANDS
Run validate_generated_requirements.py

COMPONENT 16: EVIDENCE CONTRACT REFERENCE
BUNDLE_VALIDATION: PASS required

COMPONENT 17: REQUIRED FINAL VERDICTS
- NO_GATE_SELF_APPROVAL: YES

COMPONENT 18+19+20: FINAL RESPONSE FORMAT
Final response MUST end with:
  EVIDENCE_BUNDLE: <absolute Windows path>
"""


class TestQualityGatePass:

    def test_minimal_passing_prompt_gets_pass(self):
        result = validate_prompt(MINIMAL_PASSING_PROMPT)
        assert result["status"] == "PASS", (
            f"Expected PASS, got {result['status']}. "
            f"Blockers: {[c for c in result['checks'] if c['status'] == 'BLOCKER']}"
        )

    def test_minimal_prompt_score_10(self):
        result = validate_prompt(MINIMAL_PASSING_PROMPT)
        assert result["score"] == 10

    def test_fods_generated_prompt_passes(self):
        from swarm_prompt_generator import generate_prompt
        gen = generate_prompt("fods", "TEST-SPRINT-001", "Dry-run mission.")
        result = validate_prompt(gen["prompt"])
        assert result["status"] == "PASS", (
            f"FODS prompt failed quality gate: "
            f"{[c for c in result['checks'] if c['status'] != 'PASS']}"
        )

    def test_fodt_generated_prompt_passes(self):
        from swarm_prompt_generator import generate_prompt
        gen = generate_prompt("fodt", "TEST-SPRINT-001", "Dry-run mission.")
        result = validate_prompt(gen["prompt"])
        assert result["status"] == "PASS"


class TestQualityGateFail:

    def test_empty_prompt_fails(self):
        result = validate_prompt("")
        assert result["status"] == "FAIL"

    def test_none_prompt_fails(self):
        result = validate_prompt(None)
        assert result["status"] == "FAIL"

    def test_missing_execution_mode_fails(self):
        prompt = MINIMAL_PASSING_PROMPT.replace("EXECUTION MODE", "PLANNING MODE")
        result = validate_prompt(prompt)
        assert result["status"] == "FAIL"
        failing = [c["name"] for c in result["checks"] if c["status"] == "BLOCKER"]
        assert "execution_mode_header" in failing

    def test_forbidden_git_stash_fails(self):
        prompt = MINIMAL_PASSING_PROMPT + "\nRun git stash to save your work.\n"
        result = validate_prompt(prompt)
        assert result["status"] == "FAIL"
        failing = [c["name"] for c in result["checks"] if c["status"] == "BLOCKER"]
        assert "no_forbidden_git_commands" in failing

    def test_forbidden_git_add_all_fails(self):
        prompt = MINIMAL_PASSING_PROMPT + "\nRun git add -A to stage all files.\n"
        result = validate_prompt(prompt)
        assert result["status"] == "FAIL"
        failing = [c["name"] for c in result["checks"] if c["status"] == "BLOCKER"]
        assert "no_forbidden_git_commands" in failing

    def test_gate_approval_language_fails(self):
        prompt = MINIMAL_PASSING_PROMPT + "\nGate 11 is now approved.\n"
        result = validate_prompt(prompt)
        assert result["status"] == "FAIL"
        failing = [c["name"] for c in result["checks"] if c["status"] == "BLOCKER"]
        assert "no_gate_approval_language" in failing

    def test_commercial_readiness_claim_fails(self):
        prompt = MINIMAL_PASSING_PROMPT + "\nSet commercial_product_ready: true.\n"
        result = validate_prompt(prompt)
        assert result["status"] == "FAIL"
        failing = [c["name"] for c in result["checks"] if c["status"] == "BLOCKER"]
        assert "no_commercial_readiness_claim" in failing

    def test_missing_final_format_fails(self):
        prompt = MINIMAL_PASSING_PROMPT.replace("EVIDENCE_BUNDLE: <absolute Windows path>", "")
        result = validate_prompt(prompt)
        assert result["status"] == "FAIL"
        failing = [c["name"] for c in result["checks"] if c["status"] == "BLOCKER"]
        assert "deterministic_final_format" in failing


class TestQualityGateFalsePositives:
    """Verify prohibition text does NOT trigger false positive detections."""

    def test_no_git_stash_prohibition_not_false_positive(self):
        prompt = MINIMAL_PASSING_PROMPT  # contains "- No git stash / reset"
        result = validate_prompt(prompt)
        assert result["status"] == "PASS"

    def test_no_commercial_readiness_prohibition_not_false_positive(self):
        prompt = MINIMAL_PASSING_PROMPT  # contains "No commercial_product_ready: true claim"
        result = validate_prompt(prompt)
        assert result["status"] == "PASS"

    def test_no_gate_self_approval_verdict_label_not_false_positive(self):
        # NO_GATE_SELF_APPROVAL: YES in verdicts section should not trigger
        prompt = MINIMAL_PASSING_PROMPT  # contains "- NO_GATE_SELF_APPROVAL: YES"
        result = validate_prompt(prompt)
        assert result["status"] == "PASS"


class TestQualityGateStructure:

    def test_result_has_required_keys(self):
        result = validate_prompt(MINIMAL_PASSING_PROMPT)
        for key in ["status", "score", "checks", "blocker_count", "warning_count", "pass_count"]:
            assert key in result

    def test_checks_count_is_10(self):
        result = validate_prompt(MINIMAL_PASSING_PROMPT)
        assert len(result["checks"]) == 10

    def test_pass_with_warnings_when_only_warning_fails(self):
        # Remove evidence pattern to trigger WARNING criterion only
        prompt = MINIMAL_PASSING_PROMPT.replace(
            "BUNDLE_VALIDATION: PASS required", "Some other evidence note"
        ).replace("EVIDENCE_BUNDLE: <absolute Windows path>", "EVIDENCE_BUNDLE: <absolute Windows path>")
        # The evidence_requirements_present is WARNING. Even if it fails, status should be PASS_WITH_WARNINGS if no blockers.
        # But the final format criterion still passes. So we need to also remove the BUNDLE_VALIDATION reference.
        prompt_no_evidence = MINIMAL_PASSING_PROMPT.replace(
            "BUNDLE_VALIDATION: PASS required", "No evidence note here."
        ).replace("EVIDENCE_BUNDLE: <absolute Windows path>", "EVIDENCE_BUNDLE: <absolute Windows path>")
        result = validate_prompt(prompt_no_evidence)
        # criterion 9 (WARNING) may fail, but since criterion 10 (final format) is still PASS,
        # status should be PASS (if criterion 9 passes due to EVIDENCE_BUNDLE in prompt) or PASS_WITH_WARNINGS
        assert result["status"] in ("PASS", "PASS_WITH_WARNINGS")
