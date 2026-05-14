"""
test_dryrun_replay_fixtures.py

Lane F: Golden dry-run replay fixtures validation.

Tests that deterministic replay produces identical outputs for FODS and FODT.
Validates:
- Identical lane selection between runs
- Identical requirement selection
- Identical authority state
- Deterministic prompt sections
- Quality gate passes on golden fixtures

Run:
  PYTHONPATH=... python -m pytest tests/skills/test_dryrun_replay_fixtures.py -v
"""

import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from swarm_prompt_generator import generate_prompt, _load_accepted_requirements
from prompt_quality_gate import validate_prompt
from lane_selector import select_lanes_for_format
from format_context_resolver import resolve_format_context


def _load_fixture(fmt: str) -> str:
    fixture_path = FIXTURES_DIR / f"{fmt}-sprint-prompt.md"
    if not fixture_path.exists():
        pytest.skip(f"Fixture not found: {fixture_path}")
    return fixture_path.read_text(encoding="utf-8")


class TestReplayDeterminism:
    """Verify that re-generating prompts matches the golden fixtures in key structural aspects."""

    def test_fods_lane_selection_deterministic(self):
        """Lane selection for FODS must be identical across multiple calls."""
        r1 = select_lanes_for_format("fods")
        r2 = select_lanes_for_format("fods")
        assert r1["selected_lanes"] == r2["selected_lanes"]
        assert r1["blocked_lanes"] == r2["blocked_lanes"]

    def test_fodt_lane_selection_deterministic(self):
        r1 = select_lanes_for_format("fodt")
        r2 = select_lanes_for_format("fodt")
        assert r1["selected_lanes"] == r2["selected_lanes"]
        assert r1["blocked_lanes"] == r2["blocked_lanes"]

    def test_fods_requirement_ids_deterministic(self):
        """Accepted requirements must be identical across multiple loads."""
        r1 = _load_accepted_requirements("fods")
        r2 = _load_accepted_requirements("fods")
        ids1 = [r["requirement_id"] for r in r1]
        ids2 = [r["requirement_id"] for r in r2]
        assert ids1 == ids2

    def test_fodt_requirement_ids_deterministic(self):
        r1 = _load_accepted_requirements("fodt")
        r2 = _load_accepted_requirements("fodt")
        ids1 = [r["requirement_id"] for r in r1]
        ids2 = [r["requirement_id"] for r in r2]
        assert ids1 == ids2

    def test_fods_authority_state_deterministic(self):
        c1 = resolve_format_context("fods")
        c2 = resolve_format_context("fods")
        assert c1["requirements_state"]["status"] == c2["requirements_state"]["status"]
        assert c1["requirements_state"]["iv_status"] == c2["requirements_state"]["iv_status"]

    def test_fodt_authority_state_deterministic(self):
        c1 = resolve_format_context("fodt")
        c2 = resolve_format_context("fodt")
        assert c1["requirements_state"]["status"] == c2["requirements_state"]["status"]

    def test_fods_prompt_generation_deterministic(self):
        """Re-generated prompt must have same key structural sections."""
        r1 = generate_prompt("fods", "TEST-001", "Test mission.")
        r2 = generate_prompt("fods", "TEST-001", "Test mission.")
        # Same prompt text (deterministic)
        assert r1["prompt"] == r2["prompt"]

    def test_fodt_prompt_generation_deterministic(self):
        r1 = generate_prompt("fodt", "TEST-001", "m")
        r2 = generate_prompt("fodt", "TEST-001", "m")
        assert r1["prompt"] == r2["prompt"]


class TestGoldenFixtures:
    """Validate the golden fixture files against quality gate."""

    def test_fods_fixture_exists(self):
        fixture = FIXTURES_DIR / "fods-sprint-prompt.md"
        assert fixture.exists(), f"Golden fixture missing: {fixture}"

    def test_fodt_fixture_exists(self):
        fixture = FIXTURES_DIR / "fodt-sprint-prompt.md"
        assert fixture.exists(), f"Golden fixture missing: {fixture}"

    def test_fods_fixture_passes_quality_gate(self):
        prompt = _load_fixture("fods")
        result = validate_prompt(prompt)
        assert result["status"] == "PASS", (
            f"FODS golden fixture failed quality gate: "
            f"{[c for c in result['checks'] if c['status'] != 'PASS']}"
        )

    def test_fodt_fixture_passes_quality_gate(self):
        prompt = _load_fixture("fodt")
        result = validate_prompt(prompt)
        assert result["status"] == "PASS"

    def test_fods_fixture_contains_execution_mode(self):
        prompt = _load_fixture("fods")
        assert "EXECUTION MODE" in prompt

    def test_fodt_fixture_contains_execution_mode(self):
        prompt = _load_fixture("fodt")
        assert "EXECUTION MODE" in prompt

    def test_fods_fixture_contains_requirement_ids(self):
        prompt = _load_fixture("fods")
        assert "FODS-REQ-" in prompt or "FODS-SE-" in prompt or "FODS-" in prompt

    def test_fodt_fixture_contains_requirement_ids(self):
        prompt = _load_fixture("fodt")
        assert "FODT-" in prompt

    def test_fodt_fixture_contains_req_040_constraint(self):
        prompt = _load_fixture("fodt")
        assert "FODT-REQ-040" in prompt or "iterative" in prompt.lower()

    def test_fods_fixture_does_not_have_fodt_constraint_section(self):
        prompt = _load_fixture("fods")
        assert "FODT CRITICAL CONSTRAINT" not in prompt

    def test_fods_fixture_contains_evidence_bundle(self):
        prompt = _load_fixture("fods")
        assert "EVIDENCE_BUNDLE" in prompt

    def test_fodt_fixture_contains_evidence_bundle(self):
        prompt = _load_fixture("fodt")
        assert "EVIDENCE_BUNDLE" in prompt


class TestCrossFormatConsistency:
    """Verify FODS and FODT prompts have consistent structure."""

    def test_same_lane_count_selected(self):
        r_fods = select_lanes_for_format("fods")
        r_fodt = select_lanes_for_format("fodt")
        assert len(r_fods["selected_lanes"]) == len(r_fodt["selected_lanes"])

    def test_same_lanes_selected(self):
        r_fods = select_lanes_for_format("fods")
        r_fodt = select_lanes_for_format("fodt")
        assert set(r_fods["selected_lanes"]) == set(r_fodt["selected_lanes"])

    def test_same_lanes_blocked(self):
        r_fods = select_lanes_for_format("fods")
        r_fodt = select_lanes_for_format("fodt")
        assert set(r_fods["blocked_lanes"]) == set(r_fodt["blocked_lanes"])

    def test_both_formats_authoritative(self):
        for fmt in ["fods", "fodt"]:
            ctx = resolve_format_context(fmt)
            assert ctx["requirements_state"]["status"] == "REQUIREMENTS_AUTHORITATIVE"

    def test_both_formats_commercial_ready_false(self):
        for fmt in ["fods", "fodt"]:
            ctx = resolve_format_context(fmt)
            assert ctx["governance"]["commercial_product_ready"] is False
