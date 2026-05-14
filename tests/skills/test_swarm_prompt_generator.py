"""
test_swarm_prompt_generator.py

Tests for tools/skills/swarm_prompt_generator.py

Run:
  PYTHONPATH=... python -m pytest tests/skills/test_swarm_prompt_generator.py -v
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from swarm_prompt_generator import generate_prompt, _load_accepted_requirements


class TestGeneratePromptLive:
    """Live tests using actual repo data for FODS and FODT."""

    def test_fods_generates_prompt(self):
        result = generate_prompt("fods", "TEST-SPRINT-001", "Test mission.")
        assert result["generator_status"] == "GENERATED"
        assert result["prompt"] is not None

    def test_fodt_generates_prompt(self):
        result = generate_prompt("fodt", "TEST-SPRINT-001", "Test mission.")
        assert result["generator_status"] == "GENERATED"
        assert result["prompt"] is not None

    def test_fods_accepted_count_is_20(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert result["accepted_count"] == 20

    def test_fodt_accepted_count_is_20(self):
        result = generate_prompt("fodt", "TEST-001", "m")
        assert result["accepted_count"] == 20

    def test_fods_requirements_state_authoritative(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert result["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"

    def test_fodt_requirements_state_authoritative(self):
        result = generate_prompt("fodt", "TEST-001", "m")
        assert result["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"

    def test_commercial_product_ready_always_false(self):
        for fmt in ["fods", "fodt"]:
            result = generate_prompt(fmt, "TEST-001", "m")
            assert result["governance"]["commercial_product_ready"] is False

    def test_prompt_contains_execution_mode(self):
        result = generate_prompt("fods", "TEST-SPRINT-001", "m")
        assert "EXECUTION MODE" in result["prompt"]

    def test_prompt_contains_sprint_id(self):
        result = generate_prompt("fods", "MY-SPRINT-ID-001", "m")
        assert "MY-SPRINT-ID-001" in result["prompt"]

    def test_prompt_contains_authority_files(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert "AGENTS.md" in result["prompt"]

    def test_prompt_contains_non_negotiable_rules(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert "NON-NEGOTIABLE" in result["prompt"]

    def test_prompt_contains_accepted_requirement_ids(self):
        result = generate_prompt("fods", "TEST-001", "m")
        # At least one FODS requirement ID should be in the prompt
        assert "FODS-REQ-" in result["prompt"]

    def test_prompt_contains_evidence_bundle_reference(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert "EVIDENCE_BUNDLE" in result["prompt"]

    def test_fodt_prompt_contains_req_040_constraint(self):
        result = generate_prompt("fodt", "TEST-001", "m")
        assert "FODT-REQ-040" in result["prompt"] or "iterative" in result["prompt"].lower()

    def test_fods_prompt_does_not_contain_req_040_in_constraint_block(self):
        """FODS should not surface FODT-specific constraint."""
        result = generate_prompt("fods", "TEST-001", "m")
        # FODT-REQ-040 should not appear as a critical constraint for FODS
        assert "FODT CRITICAL CONSTRAINT" not in result["prompt"]

    def test_prompt_contains_validation_commands(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert "validate_generated_requirements.py" in result["prompt"]

    def test_selected_lanes_in_result(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert "LANE-I-LOAD" in result["selected_lanes"]
        assert "LANE-I-TESTS" in result["selected_lanes"]

    def test_blocked_lanes_in_result(self):
        result = generate_prompt("fods", "TEST-001", "m")
        assert "LANE-R3" in result["blocked_lanes"]

    def test_result_json_serializable(self):
        result = generate_prompt("fods", "TEST-001", "m")
        # prompt may be long but must be serializable
        dumped = json.dumps(result)
        assert isinstance(dumped, str)


class TestGeneratePromptBlocked:
    """Tests for blocked states — prompt must not be generated."""

    def _make_mock_context(self, state: str):
        return {
            "format_id": "testfmt",
            "requirements_state": {
                "status": state,
                "iv_status": None,
                "verifier_result": None,
                "accepted_count": 0,
                "missing_files": [],
                "stale": None,
                "blocker_reason": f"State is {state}",
            },
            "gate_state": {
                "gates_passed": 10,
                "commercial_product_ready": False,
                "gate_11_status": "commercial_readiness_in_progress",
            },
            "known_constraints": [],
            "governance": {
                "commercial_product_ready": False,
                "gate_self_approval_allowed": False,
                "autonomous_implementation_allowed": False,
                "authority_files": [],
            },
        }

    def _make_mock_lanes(self, state: str):
        return {
            "format_id": "testfmt",
            "requirements_state": state,
            "selected_lanes": ["LANE-K", "LANE-C"],
            "blocked_lanes": ["LANE-I-LOAD"],
            "lane_details": {},
            "blocker": f"State is {state}",
            "governance": {"commercial_product_ready": False,
                           "gate_self_approval_allowed": False,
                           "autonomous_implementation_allowed": False},
            "selector_version": "1.0",
        }

    def test_requirements_missing_blocks_generation(self):
        import tools.skills.swarm_prompt_generator as gen_mod
        import tools.skills.format_context_resolver as resolver_mod
        import tools.skills.lane_selector as selector_mod
        ctx = self._make_mock_context("REQUIREMENTS_MISSING")
        lanes = self._make_mock_lanes("REQUIREMENTS_MISSING")
        with patch.object(resolver_mod, "resolve_format_context", return_value=ctx), \
             patch.object(selector_mod, "select_lanes", return_value=lanes):
            result = generate_prompt("testfmt", "TEST-001", "m")
        assert result["generator_status"].startswith("BLOCKED")
        assert result["prompt"] is None

    def test_verified_no_iv_blocks_generation(self):
        import tools.skills.swarm_prompt_generator as gen_mod
        import tools.skills.format_context_resolver as resolver_mod
        import tools.skills.lane_selector as selector_mod
        ctx = self._make_mock_context("REQUIREMENTS_VERIFIED_NO_IV")
        lanes = self._make_mock_lanes("REQUIREMENTS_VERIFIED_NO_IV")
        with patch.object(resolver_mod, "resolve_format_context", return_value=ctx), \
             patch.object(selector_mod, "select_lanes", return_value=lanes):
            result = generate_prompt("testfmt", "TEST-001", "m")
        assert result["generator_status"].startswith("BLOCKED")
        assert result["prompt"] is None


class TestLoadAcceptedRequirements:
    """Tests for _load_accepted_requirements helper."""

    def test_fods_accepted_requirements_count(self):
        accepted = _load_accepted_requirements("fods")
        assert len(accepted) == 20

    def test_fodt_accepted_requirements_count(self):
        accepted = _load_accepted_requirements("fodt")
        assert len(accepted) == 20

    def test_all_have_requirement_id(self):
        accepted = _load_accepted_requirements("fods")
        for req in accepted:
            assert req["requirement_id"].startswith("FODS-"), f"Expected FODS prefix, got {req["requirement_id"]!r}"

    def test_no_duplicate_ids(self):
        accepted = _load_accepted_requirements("fods")
        ids = [r["requirement_id"] for r in accepted]
        assert len(ids) == len(set(ids)), "Duplicate requirement IDs found"
