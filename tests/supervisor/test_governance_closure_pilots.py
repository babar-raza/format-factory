"""Governance Enforcement Closure — Pipeline Pilot Tests (GEC-TC-008, Lane H).

Tests all 10 GEC pilot fixtures (gec-pilot-001 through gec-pilot-010) against
the governance validators pipeline. Each fixture declares its expected result
(PASS/FAIL/WARN) and expected_blocks_sprint flag.

The core question answered: can the governance layer block false claims
at the declaration level, using only the evidence declared in the YAML fixture?
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "governance-closure-pilots"
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / name
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# GEC-P001: Governance-only declaration → PASS
# ---------------------------------------------------------------------------

class TestGecPilot001GovernanceOnlyPass:
    """Pure governance sprint with GOVERNANCE_DOC items — all validators should PASS."""

    def test_execution_method_not_required_for_governance_items(self):
        from governance_validators import validate_execution_method_required
        fixture = _load_fixture("gec-pilot-001-governance-only-pass.yaml")
        result = validate_execution_method_required(fixture)
        assert result["result"] == "PASS", (
            f"governance-only sprint: execution_method validator must PASS, got {result}"
        )

    def test_no_blocks_sprint(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-001-governance-only-pass.yaml")
        result = run_all_governance_validators(fixture)
        blocking = [v for v in result["validators"] if v["blocks_sprint"]]
        assert len(blocking) == 0, (
            f"Governance-only pilot must not block sprint, blockers: {blocking}"
        )

    def test_overall_result_pass(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-001-governance-only-pass.yaml")
        result = run_all_governance_validators(fixture)
        assert result["all_pass"] is True, (
            f"Governance-only pilot must all_pass=True, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P002: PRODUCT_SOURCE missing execution_method → FAIL V1
# ---------------------------------------------------------------------------

class TestGecPilot002MissingExecutionMethodFail:
    """PRODUCT_SOURCE without execution_method must FAIL Validator 1."""

    def test_execution_method_required_fails(self):
        from governance_validators import validate_execution_method_required
        fixture = _load_fixture("gec-pilot-002-missing-execution-method-fail.yaml")
        result = validate_execution_method_required(fixture)
        assert result["result"] == "FAIL", (
            f"Missing execution_method must FAIL, got {result}"
        )

    def test_blocks_sprint(self):
        from governance_validators import validate_execution_method_required
        fixture = _load_fixture("gec-pilot-002-missing-execution-method-fail.yaml")
        result = validate_execution_method_required(fixture)
        assert result["blocks_sprint"] is True, (
            f"Missing execution_method must block sprint, got {result}"
        )

    def test_run_all_blocks_sprint(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-002-missing-execution-method-fail.yaml")
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is True, (
            f"run_all must block sprint for missing execution_method, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P003: PRODUCT_SOURCE missing idempotency_key → WARN (grace period)
# ---------------------------------------------------------------------------

class TestGecPilot003MissingIdempotencyKeyWarn:
    """Missing idempotency_key with legacy_backfill grace → WARN, not FAIL."""

    def test_idempotency_key_warns_with_grace(self):
        from governance_validators import validate_idempotency_key_required
        fixture = _load_fixture("gec-pilot-003-missing-idempotency-key-warn.yaml")
        result = validate_idempotency_key_required(fixture)
        # Grace period: WARN not FAIL
        assert result["result"] in ("WARN", "PASS"), (
            f"Legacy backfill with no idempotency_key must WARN (not FAIL), got {result}"
        )

    def test_does_not_block_sprint(self):
        from governance_validators import validate_idempotency_key_required
        fixture = _load_fixture("gec-pilot-003-missing-idempotency-key-warn.yaml")
        result = validate_idempotency_key_required(fixture)
        assert result["blocks_sprint"] is False, (
            f"Grace period must not block sprint, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P004: REPLAYED_AND_PROVEN without replay log → FAIL V4
# ---------------------------------------------------------------------------

class TestGecPilot004ReplayedProvenNoLogFail:
    """REPLAYED_AND_PROVEN claim without replay_recipe_path must FAIL Validator 4."""

    def test_replay_recipe_required_fails(self):
        from governance_validators import validate_replay_recipe_required
        fixture = _load_fixture("gec-pilot-004-replayed-proven-no-log-fail.yaml")
        result = validate_replay_recipe_required(fixture)
        assert result["result"] == "FAIL", (
            f"REPLAYED_AND_PROVEN without recipe must FAIL, got {result}"
        )

    def test_blocks_sprint(self):
        from governance_validators import validate_replay_recipe_required
        fixture = _load_fixture("gec-pilot-004-replayed-proven-no-log-fail.yaml")
        result = validate_replay_recipe_required(fixture)
        assert result["blocks_sprint"] is True, (
            f"False REPLAYED_AND_PROVEN must block sprint, got {result}"
        )

    def test_run_all_blocks_sprint(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-004-replayed-proven-no-log-fail.yaml")
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is True, (
            f"run_all must block sprint for false REPLAYED_AND_PROVEN, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P005: BACKFILLED_LEGACY_EXECUTION with sidecar → PASS
# ---------------------------------------------------------------------------

class TestGecPilot005BackfilledWithSidecarPass:
    """Properly backfilled item with sidecar and LEGACY_BACKFILLED claim must PASS."""

    def test_execution_method_passes(self):
        from governance_validators import validate_execution_method_required
        fixture = _load_fixture("gec-pilot-005-backfilled-with-sidecar-pass.yaml")
        result = validate_execution_method_required(fixture)
        assert result["result"] == "PASS", (
            f"BACKFILLED_LEGACY_EXECUTION must pass V1, got {result}"
        )

    def test_claim_classification_passes(self):
        from governance_validators import validate_claim_classification
        fixture = _load_fixture("gec-pilot-005-backfilled-with-sidecar-pass.yaml")
        result = validate_claim_classification(fixture)
        assert result["result"] in ("PASS", "WARN"), (
            f"LEGACY_BACKFILLED claim must pass V5, got {result}"
        )

    def test_run_all_does_not_block(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-005-backfilled-with-sidecar-pass.yaml")
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is False, (
            f"Backfilled-with-sidecar pilot must not block sprint, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P006: MANUAL_UNGOVERNED closing product taskcard → FAIL V7
# ---------------------------------------------------------------------------

class TestGecPilot006ManualUngoverned:
    """MANUAL_UNGOVERNED with non-LEGACY_BACKFILLED claim must FAIL Validator 7."""

    def test_manual_ungoverned_rejected(self):
        from governance_validators import validate_manual_ungoverned_rejection
        fixture = _load_fixture("gec-pilot-006-manual-ungoverned-product-fail.yaml")
        result = validate_manual_ungoverned_rejection(fixture)
        assert result["result"] == "FAIL", (
            f"MANUAL_UNGOVERNED must fail V7, got {result}"
        )

    def test_blocks_sprint(self):
        from governance_validators import validate_manual_ungoverned_rejection
        fixture = _load_fixture("gec-pilot-006-manual-ungoverned-product-fail.yaml")
        result = validate_manual_ungoverned_rejection(fixture)
        assert result["blocks_sprint"] is True, (
            f"MANUAL_UNGOVERNED must block sprint, got {result}"
        )

    def test_run_all_blocks_sprint(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-006-manual-ungoverned-product-fail.yaml")
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is True, (
            f"run_all must block sprint for MANUAL_UNGOVERNED, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P007: Governed direct execution with required evidence → PASS
# ---------------------------------------------------------------------------

class TestGecPilot007GovernedDirectExecution:
    """MANUAL_GOVERNED_BY_SKILL with all required fields must PASS all validators."""

    def test_execution_method_passes(self):
        from governance_validators import validate_execution_method_required
        fixture = _load_fixture("gec-pilot-007-governed-direct-execution-pass.yaml")
        result = validate_execution_method_required(fixture)
        assert result["result"] == "PASS", (
            f"Governed execution must pass V1, got {result}"
        )

    def test_replay_not_required_for_governed_but_not_replayed(self):
        from governance_validators import validate_replay_recipe_required
        fixture = _load_fixture("gec-pilot-007-governed-direct-execution-pass.yaml")
        result = validate_replay_recipe_required(fixture)
        # GOVERNED_BUT_NOT_REPLAYED does not need replay_recipe
        assert result["result"] in ("PASS", "WARN"), (
            f"GOVERNED_BUT_NOT_REPLAYED must not fail V4, got {result}"
        )

    def test_run_all_does_not_block(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-007-governed-direct-execution-pass.yaml")
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is False, (
            f"Governed-direct-execution pilot must not block sprint, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P008: Wrong-stream / unsafe prompt detection (prompt quality pilot)
# ---------------------------------------------------------------------------

class TestGecPilot008UnsafePromptDetection:
    """Unsafe 'Authorized git commit + push' wording must fail prompt quality check."""

    def test_unsafe_wording_fails_check(self):
        from validate_prompt_quality import validate_prompt_quality
        unsafe_prompt = (
            "Continue product advancement. "
            "Authorized git commit + push (requires user authorization). "
            "Run tests and push changes to remote."
        )
        result = validate_prompt_quality(unsafe_prompt, target_stream="mainstream")
        unsafe_check = next(
            (c for c in result["checks"] if c["check"] == "no_unsafe_commit_push_wording"),
            None,
        )
        assert unsafe_check is not None, "no_unsafe_commit_push_wording check must exist"
        assert unsafe_check["pass"] is False, (
            f"Unsafe wording must fail check, got {unsafe_check}"
        )

    def test_safe_prompt_passes_check(self):
        from validate_prompt_quality import validate_prompt_quality
        safe_prompt = (
            "## Advancement Lane\nContinue product work. Prepare commit-ready packet. "
            "Do not commit or push without explicit user authorization. "
            "Run tests and validate evidence. Product FODS advancement with gate checks."
        )
        result = validate_prompt_quality(safe_prompt, target_stream="mainstream")
        unsafe_check = next(
            (c for c in result["checks"] if c["check"] == "no_unsafe_commit_push_wording"),
            None,
        )
        assert unsafe_check is not None, "no_unsafe_commit_push_wording check must exist"
        assert unsafe_check["pass"] is True, (
            f"Safe prompt must pass wording check, got {unsafe_check}"
        )

    def test_commit_plus_push_variant_fails(self):
        from validate_prompt_quality import validate_prompt_quality
        prompt = (
            "## Phase 1\nImplement feature. "
            "commit + push (requires gate approval). "
            "Product netpbm src/python foss advancement train."
        )
        result = validate_prompt_quality(prompt, target_stream="mainstream")
        unsafe_check = next(
            (c for c in result["checks"] if c["check"] == "no_unsafe_commit_push_wording"),
            None,
        )
        assert unsafe_check is not None
        assert unsafe_check["pass"] is False, (
            f"'commit + push (requires' variant must fail, got {unsafe_check}"
        )


# ---------------------------------------------------------------------------
# GEC-P009: Missing lane ledger — anti-skip violation
# ---------------------------------------------------------------------------

class TestGecPilot009MissingLaneLedger:
    """Anti-skip must report missing_lane_ledger violation for empty evidence root."""

    def test_empty_dir_triggers_violation(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"] is True, (
            f"Empty evidence root must trigger lane-ledger violation, got {result}"
        )

    def test_violation_check_name_is_missing_lane_ledger(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        result = detect_missing_lane_ledger(tmp_path)
        assert result.get("check") == "missing_lane_ledger", (
            f"Check name must be missing_lane_ledger, got {result}"
        )

    def test_jsonl_ledger_satisfies_check(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger
        (tmp_path / "lane-execution-ledger.jsonl").write_text(
            '{"lane":"A","taskcard_id":"GEC-TC-001","status":"closed"}\n'
        )
        result = detect_missing_lane_ledger(tmp_path)
        assert result["is_violation"] is False, (
            f"lane-execution-ledger.jsonl must satisfy check, got {result}"
        )


# ---------------------------------------------------------------------------
# GEC-P010: REPLAYABLE_NOT_YET_REPLAYED without replay_recipe_path → FAIL V4
# ---------------------------------------------------------------------------

class TestGecPilot010ReplayableNoRecipeFail:
    """REPLAYABLE_NOT_YET_REPLAYED without replay_recipe_path must FAIL Validator 4."""

    def test_replay_recipe_required_fails(self):
        from governance_validators import validate_replay_recipe_required
        fixture = _load_fixture("gec-pilot-010-replayable-no-recipe-fail.yaml")
        result = validate_replay_recipe_required(fixture)
        assert result["result"] == "FAIL", (
            f"REPLAYABLE_NOT_YET_REPLAYED without recipe must FAIL V4, got {result}"
        )

    def test_blocks_sprint(self):
        from governance_validators import validate_replay_recipe_required
        fixture = _load_fixture("gec-pilot-010-replayable-no-recipe-fail.yaml")
        result = validate_replay_recipe_required(fixture)
        assert result["blocks_sprint"] is True, (
            f"False REPLAYABLE claim must block sprint, got {result}"
        )

    def test_run_all_blocks_sprint(self):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture("gec-pilot-010-replayable-no-recipe-fail.yaml")
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is True, (
            f"run_all must block sprint for REPLAYABLE claim without recipe, got {result}"
        )


# ---------------------------------------------------------------------------
# Cross-pilot: expected_result matches actual run_all result
# ---------------------------------------------------------------------------

class TestAllPilotsMatchExpectedResult:
    """Every fixture's expected_result must match the run_all validator outcome."""

    PASS_PILOTS = [
        "gec-pilot-001-governance-only-pass.yaml",
        "gec-pilot-005-backfilled-with-sidecar-pass.yaml",
        "gec-pilot-007-governed-direct-execution-pass.yaml",
    ]

    FAIL_PILOTS = [
        "gec-pilot-002-missing-execution-method-fail.yaml",
        "gec-pilot-004-replayed-proven-no-log-fail.yaml",
        "gec-pilot-006-manual-ungoverned-product-fail.yaml",
        "gec-pilot-010-replayable-no-recipe-fail.yaml",
    ]

    @pytest.mark.parametrize("fname", PASS_PILOTS)
    def test_pass_pilots_do_not_block_sprint(self, fname):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture(fname)
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is False, (
            f"{fname}: expected PASS (no block), got blocks_sprint={result['blocks_sprint']}, "
            f"validators={[v for v in result['validators'] if v['blocks_sprint']]}"
        )

    @pytest.mark.parametrize("fname", FAIL_PILOTS)
    def test_fail_pilots_do_block_sprint(self, fname):
        from governance_validators import run_all_governance_validators
        fixture = _load_fixture(fname)
        result = run_all_governance_validators(fixture)
        assert result["blocks_sprint"] is True, (
            f"{fname}: expected FAIL (blocks sprint), got blocks_sprint=False, "
            f"overall={result['overall']}"
        )
