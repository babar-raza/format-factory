"""Enforcement pilot tests — governance validators through real pipeline (Lane K, GRE-TC-011).

Tests that the governance validators correctly block false claims and pass honest ones
when called via run_all_governance_validators() (the same function wired into autonomous_cycle.py).

Pilots:
  001 — False REPLAYABLE claim without replay_recipe_path → FAIL
  002 — PRODUCT_SOURCE missing execution_method → FAIL
  003 — Forbidden state jump DISCOVERED→GOVERNANCE_ACCEPTED for PRODUCT_SOURCE → FAIL
  004 — MANUAL_UNGOVERNED with non-legacy claim → FAIL
  005 — Governance-only sprint → PASS
  006 — Legacy backfill properly formed → PASS
  007 — Mixed sprint: governance doc OK, product item bad → FAIL (overall)
  008 — GOVERNED_BUT_NOT_REPLAYED (honest claim) → PASS
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "governance-enforcement-pilots"

# Declaration-scoped validators: only inspect declaration dict contents, not repo state.
# Repo-scanning validators (README freshness, source architecture, etc.) may fail in CI
# due to missing .local/ files or state — exclude them from "should pass" assertions.
_DECL_SCOPED_VALIDATORS = frozenset({
    "execution_method_required_validator",
    "source_diff_required_validator",
    "idempotency_key_required_validator",
    "replay_recipe_required_validator",
    "claim_classification_validator",
    "legacy_backfill_validator",
    "manual_ungoverned_rejection_validator",
    "governed_direct_execution_validator",
    "taskcard_state_transitions_validator",
    "route_decision_required_validator",
})


def _decl_scoped_failures(summary: dict) -> list[str]:
    """Return names of declaration-scoped validators that FAILed."""
    return [
        v["validator"] for v in summary.get("validators", [])
        if v.get("result") == "FAIL" and v.get("validator") in _DECL_SCOPED_VALIDATORS
    ]


def _decl_scoped_blocks(summary: dict) -> bool:
    """Return True if any declaration-scoped validator FAILs with blocks_sprint."""
    return any(
        v.get("blocks_sprint", False)
        for v in summary.get("validators", [])
        if v.get("result") == "FAIL" and v.get("validator") in _DECL_SCOPED_VALIDATORS
    )


def _load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestEnfPilot001FalseReplayableClaim:
    """Pilot 001: REPLAYABLE claim without replay_recipe_path must FAIL."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-001-false-replayable-claim.yaml")
        assert isinstance(decl, dict)

    def test_replay_recipe_validator_blocks(self):
        from governance_validators import validate_replay_recipe_required
        decl = _load_fixture("enf-pilot-001-false-replayable-claim.yaml")
        result = validate_replay_recipe_required(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for missing replay_recipe_path, got {result}"
        )

    def test_overall_validators_fail(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-001-false-replayable-claim.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert summary.get("fail_count", 0) > 0, (
            f"Expected fail_count > 0, got {summary}"
        )

    def test_blocks_sprint(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-001-false-replayable-claim.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert summary.get("blocks_sprint", False), (
            f"Expected blocks_sprint=True, got {summary}"
        )


class TestEnfPilot002MissingExecutionMethod:
    """Pilot 002: Missing execution_method on PRODUCT_SOURCE must FAIL."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-002-missing-execution-method.yaml")
        assert isinstance(decl, dict)

    def test_execution_method_validator_blocks(self):
        from governance_validators import validate_execution_method_required
        decl = _load_fixture("enf-pilot-002-missing-execution-method.yaml")
        result = validate_execution_method_required(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for missing execution_method, got {result}"
        )

    def test_overall_validators_fail(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-002-missing-execution-method.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert summary.get("fail_count", 0) > 0, (
            f"Expected fail_count > 0, got {summary}"
        )


class TestEnfPilot003ForbiddenStateJump:
    """Pilot 003: PRODUCT_SOURCE DISCOVERED→GOVERNANCE_ACCEPTED must FAIL."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-003-forbidden-state-jump.yaml")
        assert isinstance(decl, dict)

    def test_state_transition_validator_blocks(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = _load_fixture("enf-pilot-003-forbidden-state-jump.yaml")
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for forbidden state jump, got {result}"
        )

    def test_forbidden_in_issue_text(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = _load_fixture("enf-pilot-003-forbidden-state-jump.yaml")
        result = validate_taskcard_state_transitions(decl)
        issue_text = " ".join(str(i.get("issue", "")) for i in result.get("items", []))
        assert "FORBIDDEN" in issue_text, (
            f"Expected 'FORBIDDEN' in issue text, got: {issue_text}"
        )

    def test_overall_validators_fail(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-003-forbidden-state-jump.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert summary.get("fail_count", 0) > 0, (
            f"Expected fail_count > 0, got {summary}"
        )


class TestEnfPilot004ManualUngoverned:
    """Pilot 004: MANUAL_UNGOVERNED with non-legacy claim must FAIL."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-004-manual-ungoverned-product.yaml")
        assert isinstance(decl, dict)

    def test_manual_ungoverned_validator_blocks(self):
        from governance_validators import validate_manual_ungoverned_rejection
        decl = _load_fixture("enf-pilot-004-manual-ungoverned-product.yaml")
        result = validate_manual_ungoverned_rejection(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for MANUAL_UNGOVERNED without LEGACY_BACKFILLED, got {result}"
        )

    def test_overall_validators_fail(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-004-manual-ungoverned-product.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert summary.get("fail_count", 0) > 0, (
            f"Expected fail_count > 0, got {summary}"
        )


class TestEnfPilot005GovernanceDocPasses:
    """Pilot 005: Governance-only sprint must PASS all validators."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-005-governance-doc-passes.yaml")
        assert isinstance(decl, dict)

    def test_overall_validators_pass(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-005-governance-doc-passes.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        failures = _decl_scoped_failures(summary)
        assert not failures, (
            f"Expected no declaration-scoped FAIL for governance-only sprint, got {failures}"
        )

    def test_does_not_block_sprint(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-005-governance-doc-passes.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert not _decl_scoped_blocks(summary), (
            "Expected no declaration-scoped blocks_sprint for governance-only sprint"
        )

    def test_no_execution_method_required(self):
        from governance_validators import validate_execution_method_required
        decl = _load_fixture("enf-pilot-005-governance-doc-passes.yaml")
        result = validate_execution_method_required(decl)
        assert result["result"] != "FAIL", (
            f"Governance docs should not require execution_method, got {result}"
        )


class TestEnfPilot006LegacyBackfillPasses:
    """Pilot 006: BACKFILLED_LEGACY_EXECUTION with LEGACY_BACKFILLED must PASS."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-006-legacy-backfill-passes.yaml")
        assert isinstance(decl, dict)

    def test_overall_validators_pass(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-006-legacy-backfill-passes.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        failures = _decl_scoped_failures(summary)
        assert not failures, (
            f"Expected no declaration-scoped FAIL for proper legacy backfill, got {failures}"
        )

    def test_does_not_block_sprint(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-006-legacy-backfill-passes.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert not _decl_scoped_blocks(summary), (
            "Expected no declaration-scoped blocks_sprint for proper legacy backfill"
        )

    def test_manual_ungoverned_does_not_fire(self):
        from governance_validators import validate_manual_ungoverned_rejection
        decl = _load_fixture("enf-pilot-006-legacy-backfill-passes.yaml")
        result = validate_manual_ungoverned_rejection(decl)
        assert result["result"] != "FAIL", (
            f"BACKFILLED_LEGACY_EXECUTION should not trigger manual_ungoverned rejection, got {result}"
        )


class TestEnfPilot007MixedSprintProductBlocked:
    """Pilot 007: Mixed sprint with bad product item — overall FAIL."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-007-mixed-sprint-product-blocked.yaml")
        assert isinstance(decl, dict)

    def test_governance_doc_item_passes_execution_method(self):
        from governance_validators import validate_execution_method_required
        decl = _load_fixture("enf-pilot-007-mixed-sprint-product-blocked.yaml")
        # This only checks the one product item which has execution_method set
        result = validate_execution_method_required(decl)
        # The product item HAS execution_method, so execution_method validator should PASS
        assert result["result"] != "FAIL", (
            f"execution_method validator should not fail (product item has method), got {result}"
        )

    def test_replay_recipe_validator_blocks_product(self):
        from governance_validators import validate_replay_recipe_required
        decl = _load_fixture("enf-pilot-007-mixed-sprint-product-blocked.yaml")
        result = validate_replay_recipe_required(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for product item with missing replay_recipe_path, got {result}"
        )

    def test_overall_validators_fail(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-007-mixed-sprint-product-blocked.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert summary.get("fail_count", 0) > 0, (
            f"Expected fail_count > 0 (one bad product item), got {summary}"
        )


class TestEnfPilot008GovernedNotReplayedPasses:
    """Pilot 008: GOVERNED_BUT_NOT_REPLAYED (honest claim) must PASS."""

    def test_fixture_loads(self):
        decl = _load_fixture("enf-pilot-008-governed-not-replayed-passes.yaml")
        assert isinstance(decl, dict)

    def test_overall_validators_pass(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-008-governed-not-replayed-passes.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        failures = _decl_scoped_failures(summary)
        assert not failures, (
            f"Expected no declaration-scoped FAIL for GOVERNED_BUT_NOT_REPLAYED, got {failures}"
        )

    def test_does_not_block_sprint(self):
        from governance_validators import run_all_governance_validators
        decl = _load_fixture("enf-pilot-008-governed-not-replayed-passes.yaml")
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert not _decl_scoped_blocks(summary), (
            "Expected no declaration-scoped blocks_sprint for honest governed claim"
        )

    def test_replay_recipe_validator_does_not_fail_for_governed_not_replayed(self):
        from governance_validators import validate_replay_recipe_required
        decl = _load_fixture("enf-pilot-008-governed-not-replayed-passes.yaml")
        result = validate_replay_recipe_required(decl)
        # GOVERNED_BUT_NOT_REPLAYED does not claim REPLAYABLE — should PASS
        assert result["result"] != "FAIL", (
            f"GOVERNED_BUT_NOT_REPLAYED should not fail replay_recipe validator, got {result}"
        )
