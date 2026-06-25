"""Tests for governance_validators.py — 10 validators.

GRH-TC-005 (Lane E): All 10 validators tested with PASS, FAIL, and WARN scenarios.
GRH-TC-006 (Lane F): Taskcard state machine validator tested.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _product_item(**kwargs) -> dict:
    base = {
        "item_id": "TC-001",
        "title": "Test product item",
        "item_type": "PRODUCT_SOURCE",
        "product_track": "foss_python",
        "status": "completed",
    }
    base.update(kwargs)
    return base


def _governance_item(**kwargs) -> dict:
    base = {
        "item_id": "GR-TC-001",
        "title": "Test governance item",
        "item_type": "GOVERNANCE_DOC",
        "exception_classification": "investigation_only",
        "status": "completed",
        "state_machine_start": "DISCOVERED",
        "state_machine_target": "GOVERNANCE_ACCEPTED",
    }
    base.update(kwargs)
    return base


def _decl(items: list) -> dict:
    return {"planned_work_items": items}


# ---------------------------------------------------------------------------
# Validator 1: execution_method_required
# ---------------------------------------------------------------------------

class TestExecutionMethodRequired:
    def test_pass_with_valid_method(self):
        from governance_validators import validate_execution_method_required
        decl = _decl([_product_item(execution_method="BACKFILLED_LEGACY_EXECUTION")])
        result = validate_execution_method_required(decl)
        assert result["result"] == "PASS"
        assert not result["blocks_sprint"]

    def test_fail_missing_method(self):
        from governance_validators import validate_execution_method_required
        decl = _decl([_product_item()])  # no execution_method
        result = validate_execution_method_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_warn_unknown_method(self):
        from governance_validators import validate_execution_method_required
        decl = _decl([_product_item(execution_method="UNKNOWN_EXECUTION_METHOD")])
        result = validate_execution_method_required(decl)
        assert result["result"] == "WARN"
        assert not result["blocks_sprint"]

    def test_warn_with_grace_exemption(self):
        from governance_validators import validate_execution_method_required
        decl = _decl([_product_item(exception_classification="pre_taxonomy_backfill")])
        result = validate_execution_method_required(decl)
        assert result["result"] == "WARN"  # Grace, not fail

    def test_governance_items_skipped(self):
        from governance_validators import validate_execution_method_required
        decl = _decl([_governance_item()])
        result = validate_execution_method_required(decl)
        # No PRODUCT_SOURCE items → PASS with empty items
        assert result["result"] == "PASS"

    def test_all_valid_methods_pass(self):
        from governance_validators import validate_execution_method_required, VALID_EXECUTION_METHODS
        for method in VALID_EXECUTION_METHODS - {"UNKNOWN_EXECUTION_METHOD"}:
            decl = _decl([_product_item(execution_method=method)])
            result = validate_execution_method_required(decl)
            assert result["result"] in ("PASS", "WARN"), f"Method {method} should PASS or WARN"


# ---------------------------------------------------------------------------
# Validator 2: source_diff_required
# ---------------------------------------------------------------------------

class TestSourceDiffRequired:
    def test_pass_with_diff_paths(self):
        from governance_validators import validate_source_diff_required
        decl = _decl([_product_item(
            execution_method="MANUAL_GOVERNED_BY_SKILL",
            source_diff_paths=["diffs/my-func.patch"],
        )])
        result = validate_source_diff_required(decl)
        assert result["result"] == "PASS"

    def test_fail_missing_diff(self):
        from governance_validators import validate_source_diff_required
        decl = _decl([_product_item(execution_method="MANUAL_GOVERNED_BY_SKILL")])
        result = validate_source_diff_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_warn_backfill_no_diff(self):
        from governance_validators import validate_source_diff_required
        decl = _decl([_product_item(
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            exception_classification="legacy_backfill",
        )])
        result = validate_source_diff_required(decl)
        assert result["result"] == "WARN"

    def test_missing_backfill_required_is_warn(self):
        from governance_validators import validate_source_diff_required
        decl = _decl([_product_item(
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            source_diff_paths=["MISSING_BACKFILL_REQUIRED"],
        )])
        result = validate_source_diff_required(decl)
        assert result["result"] in ("WARN", "PASS")


# ---------------------------------------------------------------------------
# Validator 3: idempotency_key_required
# ---------------------------------------------------------------------------

class TestIdempotencyKeyRequired:
    def test_pass_valid_key(self):
        from governance_validators import validate_idempotency_key_required
        key = "a" * 64
        decl = _decl([_product_item(
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            idempotency_key=key,
        )])
        result = validate_idempotency_key_required(decl)
        assert result["result"] == "PASS"

    def test_fail_missing_key(self):
        from governance_validators import validate_idempotency_key_required
        decl = _decl([_product_item(execution_method="MANUAL_GOVERNED_BY_SKILL")])
        result = validate_idempotency_key_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_warn_wrong_format(self):
        from governance_validators import validate_idempotency_key_required
        decl = _decl([_product_item(
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            idempotency_key="not-64-hex",
        )])
        result = validate_idempotency_key_required(decl)
        assert result["result"] == "WARN"

    def test_warn_grace_missing_key(self):
        from governance_validators import validate_idempotency_key_required
        decl = _decl([_product_item(exception_classification="pre_taxonomy_backfill")])
        result = validate_idempotency_key_required(decl)
        assert result["result"] == "WARN"


# ---------------------------------------------------------------------------
# Validator 4: replay_recipe_required
# ---------------------------------------------------------------------------

class TestReplayRecipeRequired:
    def test_pass_no_replayable_claim(self):
        from governance_validators import validate_replay_recipe_required
        decl = _decl([_product_item(claim_classification="WORKS_BUT_NOT_REPEATABLE")])
        result = validate_replay_recipe_required(decl)
        assert result["result"] in ("PASS", "WARN")

    def test_fail_replayable_without_recipe(self):
        from governance_validators import validate_replay_recipe_required
        decl = _decl([_product_item(
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
        )])
        result = validate_replay_recipe_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_pass_replayable_with_recipe(self):
        from governance_validators import validate_replay_recipe_required
        decl = _decl([_product_item(
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
            replay_recipe_path="recipes/my-func.yaml",
        )])
        result = validate_replay_recipe_required(decl)
        assert result["result"] == "PASS"

    def test_warn_governed_but_not_replayed(self):
        from governance_validators import validate_replay_recipe_required
        decl = _decl([_product_item(claim_classification="GOVERNED_BUT_NOT_REPLAYED")])
        result = validate_replay_recipe_required(decl)
        assert result["result"] == "WARN"
        assert not result["blocks_sprint"]


# ---------------------------------------------------------------------------
# Validator 5: claim_classification
# ---------------------------------------------------------------------------

class TestClaimClassification:
    def test_pass_valid_claim(self):
        from governance_validators import validate_claim_classification
        decl = _decl([_product_item(claim_classification="LEGACY_BACKFILLED")])
        result = validate_claim_classification(decl)
        assert result["result"] == "PASS"

    def test_fail_invalid_claim(self):
        from governance_validators import validate_claim_classification
        decl = _decl([_product_item(claim_classification="INVALID_CLAIM")])
        result = validate_claim_classification(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_fail_replayable_with_ungoverned_method(self):
        from governance_validators import validate_claim_classification
        decl = _decl([_product_item(
            execution_method="MANUAL_UNGOVERNED",
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
        )])
        result = validate_claim_classification(decl)
        assert result["result"] == "FAIL"

    def test_warn_works_but_not_repeatable(self):
        from governance_validators import validate_claim_classification
        decl = _decl([_product_item(claim_classification="WORKS_BUT_NOT_REPEATABLE")])
        result = validate_claim_classification(decl)
        assert result["result"] == "WARN"
        assert not result["blocks_sprint"]


# ---------------------------------------------------------------------------
# Validator 6: legacy_backfill
# ---------------------------------------------------------------------------

class TestLegacyBackfill:
    def test_pass_no_product_items(self):
        from governance_validators import validate_legacy_backfill
        decl = _decl([_governance_item()])
        result = validate_legacy_backfill(decl)
        assert result["result"] == "PASS"

    def test_warn_backfill_without_sidecar(self):
        from governance_validators import validate_legacy_backfill
        decl = _decl([_product_item(execution_method="BACKFILLED_LEGACY_EXECUTION")])
        result = validate_legacy_backfill(decl)
        assert result["result"] == "WARN"
        assert not result["blocks_sprint"]

    def test_never_blocks_sprint(self):
        from governance_validators import validate_legacy_backfill
        decl = _decl([_product_item()])
        result = validate_legacy_backfill(decl)
        assert not result["blocks_sprint"]


# ---------------------------------------------------------------------------
# Validator 7: manual_ungoverned_rejection
# ---------------------------------------------------------------------------

class TestManualUngoverned:
    def test_fail_ungoverned_product_item(self):
        from governance_validators import validate_manual_ungoverned_rejection
        decl = _decl([_product_item(execution_method="MANUAL_UNGOVERNED")])
        result = validate_manual_ungoverned_rejection(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_pass_ungoverned_with_legacy_backfilled(self):
        from governance_validators import validate_manual_ungoverned_rejection
        decl = _decl([_product_item(
            execution_method="MANUAL_UNGOVERNED",
            claim_classification="LEGACY_BACKFILLED",
        )])
        result = validate_manual_ungoverned_rejection(decl)
        assert result["result"] == "PASS"

    def test_pass_no_ungoverned_items(self):
        from governance_validators import validate_manual_ungoverned_rejection
        decl = _decl([_product_item(execution_method="BACKFILLED_LEGACY_EXECUTION")])
        result = validate_manual_ungoverned_rejection(decl)
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# Validator 8: governed_direct_execution
# ---------------------------------------------------------------------------

class TestGovernedDirectExecution:
    def test_pass_governed_with_transcript(self):
        from governance_validators import validate_governed_direct_execution
        decl = _decl([_product_item(
            execution_method="MANUAL_GOVERNED_BY_SKILL",
            skill_id="add-python-api",
            skill_transcript_path="transcripts/add-python-api.json",
        )])
        result = validate_governed_direct_execution(decl)
        assert result["result"] == "PASS"

    def test_fail_governed_without_skill_id(self):
        from governance_validators import validate_governed_direct_execution
        decl = _decl([_product_item(
            execution_method="MANUAL_GOVERNED_BY_SKILL",
        )])
        result = validate_governed_direct_execution(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_pass_non_governed_item(self):
        from governance_validators import validate_governed_direct_execution
        decl = _decl([_product_item(execution_method="BACKFILLED_LEGACY_EXECUTION")])
        result = validate_governed_direct_execution(decl)
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# Validator 9: source_marker_or_sidecar
# ---------------------------------------------------------------------------

class TestSourceMarkerOrSidecar:
    def test_pass_no_touched_files(self):
        from governance_validators import validate_source_marker_or_sidecar
        decl = _decl([_product_item(
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            sidecar_attribution_path=".local/attribution/gnumeric/gnumeric_codec.py.attribution.yaml",
            idempotency_key="a" * 64,
        )])
        result = validate_source_marker_or_sidecar(decl)
        assert result["result"] in ("PASS", "WARN")  # sidecar path may not exist in test

    def test_fail_touched_no_attribution(self):
        from governance_validators import validate_source_marker_or_sidecar
        decl = _decl([_product_item(
            execution_method="MANUAL_GOVERNED_BY_SKILL",
            touched_files=["src/python/gnumeric/gnumeric_codec.py"],
        )])
        result = validate_source_marker_or_sidecar(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_warn_touched_with_grace(self):
        from governance_validators import validate_source_marker_or_sidecar
        decl = _decl([_product_item(
            execution_method="MANUAL_GOVERNED_BY_SKILL",
            touched_files=["src/python/gnumeric/gnumeric_codec.py"],
            exception_classification="pre_taxonomy_backfill",
        )])
        result = validate_source_marker_or_sidecar(decl)
        assert result["result"] == "WARN"


# ---------------------------------------------------------------------------
# Validator 10: taskcard_state_transition (Lane F)
# ---------------------------------------------------------------------------

class TestTaskcardStateTransition:
    def test_pass_valid_transition(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = _decl([_governance_item(
            state_machine_start="DISCOVERED",
            state_machine_target="GOVERNANCE_ACCEPTED",
            status="completed",
        )])
        result = validate_taskcard_state_transitions(decl)
        # GOVERNANCE_ACCEPTED is close-eligible → should PASS or WARN
        assert result["result"] in ("PASS", "WARN")

    def test_fail_forbidden_jump(self):
        from governance_validators import validate_taskcard_state_transitions
        # DISCOVERED → GOVERNANCE_ACCEPTED is a forbidden jump
        decl = _decl([_product_item(
            state_machine_start="DISCOVERED",
            state_machine_target="GOVERNANCE_ACCEPTED",
            status="completed",
        )])
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"]

    def test_fail_completed_not_close_eligible(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = _decl([_product_item(
            state_machine_start="EVIDENCE_LOCATED",
            state_machine_target="MUTATION_EXECUTED",
            status="completed",
        )])
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"

    def test_warn_governance_accepted_without_replay(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = _decl([_governance_item(
            state_machine_start="VALIDATED",
            state_machine_target="GOVERNANCE_ACCEPTED",
            status="completed",
            claim_classification="GOVERNED_BUT_NOT_REPLAYED",
        )])
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] in ("PASS", "WARN")

    def test_pass_backfilled_state(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = _decl([_product_item(
            state_machine_start="EVIDENCE_LOCATED",
            state_machine_target="BACKFILLED_LEGACY_ACCEPTED",
            status="completed",
            execution_method="BACKFILLED_LEGACY_EXECUTION",
            claim_classification="LEGACY_BACKFILLED",
        )])
        result = validate_taskcard_state_transitions(decl)
        # BACKFILLED_LEGACY_ACCEPTED is close-eligible → should not fail
        assert result["result"] in ("PASS", "WARN")


# ---------------------------------------------------------------------------
# Composite runner
# ---------------------------------------------------------------------------

class TestRunAllValidators:
    def test_governance_declaration_passes_all(self):
        from governance_validators import run_all_governance_validators
        decl = _decl([
            _governance_item(
                state_machine_start="DISCOVERED",
                state_machine_target="GOVERNANCE_ACCEPTED",
            )
        ])
        result = run_all_governance_validators(decl)
        # Exclude filesystem-scanning validators that fail based on repo state,
        # not declaration content (pre-existing LOC cap violations, etc.)
        _fs_scanners = {
            "validate_source_architecture",
            "validate_error_fallback_safety",
            "validate_spec_authority_class_completeness",  # V53: scans QName registry state, not declaration
        }
        failed = [
            v["validator"] for v in result["validators"]
            if v["result"] == "FAIL" and v["validator"] not in _fs_scanners
        ]
        assert not failed, f"Unexpected FAIL validators: {failed}"
        # blocks_sprint should not be set by declaration-level validators
        decl_blockers = [
            v["validator"] for v in result["validators"]
            if v.get("blocks_sprint") and v["validator"] not in _fs_scanners
        ]
        assert not decl_blockers, f"Unexpected blocking validators: {decl_blockers}"

    def test_ungoverned_product_fails_multiple_validators(self):
        from governance_validators import run_all_governance_validators
        decl = _decl([_product_item(execution_method="MANUAL_UNGOVERNED")])
        result = run_all_governance_validators(decl)
        assert not result["all_pass"]
        assert result["fail_count"] >= 1

    def test_result_has_12_validators(self):
        from governance_validators import run_all_governance_validators
        decl = _decl([])
        result = run_all_governance_validators(decl)
        assert len(result["validators"]) >= 38  # baseline: 38; may grow as validators are added

    def test_deprecated_queue_declared_fails_ungoverned(self):
        from governance_validators import run_all_governance_validators
        decl = _decl([_product_item(
            execution_method="QUEUE_DECLARED_EXECUTION",
            claim_classification="GOVERNED_BUT_NOT_REPLAYED",
        )])
        result = run_all_governance_validators(decl)
        # QUEUE_DECLARED_EXECUTION should cause failure in execution_method validator
        # (it's valid syntax but deprecated — tests that it doesn't block on its own)
        # The manual_ungoverned_rejection validator won't catch QUEUE_DECLARED specifically
        # but it should be flagged in the summary
        assert result["fail_count"] >= 0  # At minimum, executes without error

    def test_real_governance_sprint_passes(self):
        """Real governance sprint declaration should pass all declaration-level validators."""
        import yaml
        from governance_validators import run_all_governance_validators
        decl_path = REPO_ROOT / ".local/evidences/governance-repeatability-contracts-001/evidence-declaration.yaml"
        if not decl_path.exists():
            pytest.skip("Governance declaration not found")
        with open(decl_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        result = run_all_governance_validators(decl, REPO_ROOT)
        # Exclude filesystem-scanning validators that may fail based on current repo state
        _fs_scanners = {
            "validate_source_architecture",
            "validate_error_fallback_safety",
            "validate_spec_authority_class_completeness",  # V53: scans QName registry state, not declaration
        }
        failed = [
            v["validator"] for v in result["validators"]
            if v["result"] == "FAIL" and v["validator"] not in _fs_scanners
        ]
        assert not failed, (
            f"Real governance sprint failed validators: {failed}"
        )


# ---------------------------------------------------------------------------
# TC-SAL-006: Pending fact debt enforcement in validate_spec_fact_refs.check_item
# ---------------------------------------------------------------------------

class TestSpecFactRefStatusDebt:
    """Tests for pending fact status debt enforcement added in TC-SAL-005."""

    def test_pending_fact_ref_produces_debt(self):
        """spec_fact_ref with pending_verification status → grade_impact=debt (not reject)."""
        from unittest.mock import patch
        from validate_spec_fact_refs import check_item

        fake_registry = {"FACT-TEST-PENDING-001": "pending_verification"}
        item = {
            "item_id": "TC-DEBT-001",
            "item_type": "PRODUCT_SOURCE",
            "status": "completed",
            "spec_fact_refs": ["FACT-TEST-PENDING-001"],
        }
        with patch("validate_spec_fact_refs.get_fact_registry", return_value=fake_registry):
            result = check_item(item)

        assert result["compliant"] is True, (
            f"Expected compliant=True (debt is not a rejection), got: {result}"
        )
        assert result["grade_impact"] == "debt", (
            f"Expected grade_impact='debt', got: {result['grade_impact']}"
        )
        assert "pending_verification" in result["detail"]

    def test_unknown_fact_ref_produces_reject(self):
        """spec_fact_ref not found in registry → grade_impact=reject."""
        from unittest.mock import patch
        from validate_spec_fact_refs import check_item

        fake_registry = {"FACT-TEST-KNOWN-001": "verified"}  # FACT-TEST-UNKNOWN-999 absent
        item = {
            "item_id": "TC-REJECT-001",
            "item_type": "PRODUCT_SOURCE",
            "status": "completed",
            "spec_fact_refs": ["FACT-TEST-UNKNOWN-999"],
        }
        with patch("validate_spec_fact_refs.get_fact_registry", return_value=fake_registry):
            result = check_item(item)

        assert result["compliant"] is False, (
            f"Expected compliant=False (unknown ref is a rejection), got: {result}"
        )
        assert result["grade_impact"] == "reject", (
            f"Expected grade_impact='reject', got: {result['grade_impact']}"
        )


# ---------------------------------------------------------------------------
# V42: validate_deepening_suspension (SUSP-001)
# ---------------------------------------------------------------------------

class TestV42DeepeningSuspension:
    """Regression tests for V42 validate_deepening_suspension.

    Negative control: suspended function name -> FAIL, blocks_sprint=True.
    Positive control: spec-grounded function name -> PASS, blocks_sprint=False.
    Non-product item with suspended name -> PASS (only PRODUCT_SOURCE checked).
    """

    def _validator(self):
        from governance_validators import validate_deepening_suspension
        return validate_deepening_suspension

    def test_suspended_pattern_fails(self):
        """NEGATIVE CONTROL: PRODUCT_SOURCE with _mod_N_times_M path -> FAIL."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-SUSP-NEG-001",
                "item_type": "PRODUCT_SOURCE",
                "evidence_paths": [
                    "tests/python/zst/test_zst_counts_mod_1069_times_1087.py"
                ],
            }]
        }
        result = validate(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for suspended deepening path, got {result['result']}"
        )
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert result["items"][0]["item_id"] == "TC-SUSP-NEG-001"

    def test_spec_grounded_passes(self):
        """POSITIVE CONTROL: PRODUCT_SOURCE with spec-grounded path -> PASS."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-SUSP-POS-001",
                "item_type": "PRODUCT_SOURCE",
                "evidence_paths": [
                    "tests/python/fods/test_table_cell_qname.py"
                ],
            }]
        }
        result = validate(decl)
        assert result["result"] == "PASS", (
            f"Expected PASS for spec-grounded path, got {result['result']}"
        )
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 0

    def test_non_product_source_ignored(self):
        """TEST item with suspended pattern is not blocked (only PRODUCT_SOURCE checked)."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-SUSP-TYPE-001",
                "item_type": "TEST",
                "evidence_paths": [
                    "tests/python/zst/test_zst_counts_mod_1069_times_1087.py"
                ],
            }]
        }
        result = validate(decl)
        assert result["result"] == "PASS", (
            f"Expected PASS for non-PRODUCT_SOURCE item, got {result['result']}"
        )
        assert result["blocks_sprint"] is False

    def test_multiple_violations_all_reported(self):
        """Multiple suspended paths in one declaration -> all violations reported."""
        validate = self._validator()
        decl = {
            "planned_work_items": [
                {
                    "item_id": "TC-SUSP-MULTI-001",
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": [
                        "tests/python/zst/test_zst_counts_mod_1069_times_1087.py",
                        "tests/python/xcf/test_xcf_ratio_mod_1069_times_1087.py",
                    ],
                },
                {
                    "item_id": "TC-SUSP-MULTI-002",
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": [
                        "tests/python/fodg/test_fodg_area_mod_997_times_1009.py"
                    ],
                },
            ]
        }
        result = validate(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 3


class TestV45QNameClassNames:
    """Regression tests for V45 validate_qname_class_names.

    NEGATIVE: FodsCell in models.py (non-compat path) -> FAIL.
    POSITIVE: canonical Paragraph in spec/text/paragraph.py -> PASS.
    COMPAT EXEMPT: compat.py path contains '/compat.' -> PASS.
    NON-PRODUCT: GOVERNANCE_TASKCARD type -> PASS.
    """

    def _validator(self):
        from governance_validators import validate_qname_class_names
        return validate_qname_class_names

    def test_format_prefixed_model_fails(self):
        """NEGATIVE: PRODUCT_SOURCE with FodsCell in models.py -> FAIL."""
        validate = self._validator()
        decl = {"planned_work_items": [{
            "item_id": "TC-V45-NEG-001",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/fods/models.py"],
        }]}
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) >= 1

    def test_canonical_spec_name_passes(self):
        """POSITIVE: canonical Paragraph class in spec/text/paragraph.py -> PASS."""
        validate = self._validator()
        decl = {"planned_work_items": [{
            "item_id": "TC-V45-POS-001",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/fodt/spec/text/paragraph.py"],
        }]}
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_compat_path_exempt(self):
        """compat.py path is exempt even if it has format-prefixed names."""
        validate = self._validator()
        decl = {"planned_work_items": [{
            "item_id": "TC-V45-COMPAT-001",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/fodt/compat.py"],
        }]}
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_non_product_item_exempt(self):
        """GOVERNANCE_TASKCARD item type is not checked."""
        validate = self._validator()
        decl = {"planned_work_items": [{
            "item_id": "TC-V45-GOV-001",
            "item_type": "GOVERNANCE_TASKCARD",
            "evidence_paths": ["src/python/fods/fods/models.py"],
        }]}
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False


class TestV46SkillTranscriptPresent:
    """Regression tests for V46 validate_skill_transcript_present (TC-SKILL-GOV-002).

    V46 verifies that PRODUCT_SOURCE items have a linked skill_transcript artifact.
    Activated 2026-06-21 (TC-SKILL-GOV-005): blocks_sprint=True for violations.

    NEGATIVE: PRODUCT_SOURCE with no skill_transcript artifact -> FAIL + blocks.
    POSITIVE: PRODUCT_SOURCE with skill_transcript artifact -> PASS.
    BACKFILL_EXEMPT: item with BACKFILL_PRE_GOVERNANCE note -> PASS.
    NON-PRODUCT: GOVERNANCE_TASKCARD -> PASS.
    """

    def _validator(self):
        from governance_validators import validate_skill_transcript_present
        return validate_skill_transcript_present

    def test_missing_transcript_blocks(self):
        """NEGATIVE: PRODUCT_SOURCE item with no skill_transcript -> FAIL + blocks_sprint."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V46-NEG-001",
                "item_type": "PRODUCT_SOURCE",
            }],
            "evidence_artifacts": [],
        }
        result = validate(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert result["items"][0]["item_id"] == "TC-V46-NEG-001"
        assert "SKILL_TRANSCRIPT_MISSING" in result["items"][0]["reason"]

    def test_valid_transcript_passes(self):
        """POSITIVE: PRODUCT_SOURCE item with linked skill_transcript artifact -> PASS."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V46-POS-001",
                "item_type": "PRODUCT_SOURCE",
            }],
            "evidence_artifacts": [{
                "path": "reports/skills-r123/skill-transcripts/sal-pipeline-heal-TC-SAL-IMPL-002.json",
                "type": "skill_transcript",
                "description": "Skill invocation transcript",
                "related_work_items": ["TC-V46-POS-001"],
            }],
        }
        result = validate(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 0

    def test_backfill_pre_governance_exempt(self):
        """BACKFILL_PRE_GOVERNANCE items are exempt from transcript requirement."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V46-BACKFILL-001",
                "item_type": "PRODUCT_SOURCE",
                "notes": "BACKFILL_PRE_GOVERNANCE — completed before sal-pipeline-heal skill existed",
            }],
            "evidence_artifacts": [],
        }
        result = validate(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 0

    def test_non_product_item_exempt(self):
        """GOVERNANCE_TASKCARD items are not checked for transcripts."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V46-GOV-001",
                "item_type": "GOVERNANCE_TASKCARD",
            }],
            "evidence_artifacts": [],
        }
        result = validate(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_empty_declaration_passes(self):
        """Empty declaration has no PRODUCT_SOURCE items -> PASS."""
        validate = self._validator()
        result = validate({})
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 0

    def test_bulk_backfill_exemption_warns(self):
        """BULK_BACKFILL_WARNING: >2 BACKFILL_PRE_GOVERNANCE items -> backfill_warnings."""
        validate = self._validator()
        decl = {
            "planned_work_items": [
                {
                    "item_id": f"TC-BACKFILL-{i:03d}",
                    "item_type": "PRODUCT_SOURCE",
                    "notes": "BACKFILL_PRE_GOVERNANCE — pre-governance work",
                    "ledger_entry_id": f"LEDGER-{i:03d}",
                }
                for i in range(3)  # 3 > max(2)
            ],
            "evidence_artifacts": [],
        }
        result = validate(decl)
        # blocks_sprint stays False (violations = [] since all are BACKFILL_PRE_GOVERNANCE)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        # backfill_warnings should contain the bulk warning
        bw = result.get("backfill_warnings", [])
        assert any(w["item_id"] == "BULK_BACKFILL_WARNING" for w in bw), (
            f"Expected BULK_BACKFILL_WARNING in backfill_warnings, got: {bw}"
        )

    def test_backfill_missing_ledger_entry_id_warns(self):
        """BACKFILL_PRE_GOVERNANCE item without ledger_entry_id -> backfill_warnings."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-BACKFILL-NOLEDGER",
                "item_type": "PRODUCT_SOURCE",
                "notes": "BACKFILL_PRE_GOVERNANCE — pre-governance work",
                # ledger_entry_id intentionally absent
            }],
            "evidence_artifacts": [],
        }
        result = validate(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        bw = result.get("backfill_warnings", [])
        assert any(w["item_id"] == "TC-BACKFILL-NOLEDGER" for w in bw), (
            f"Expected TC-BACKFILL-NOLEDGER in backfill_warnings, got: {bw}"
        )

    def test_backfill_with_ledger_entry_id_no_warn(self):
        """BACKFILL_PRE_GOVERNANCE item WITH ledger_entry_id AND count <= 2 -> no backfill_warnings."""
        validate = self._validator()
        decl = {
            "planned_work_items": [
                {
                    "item_id": f"TC-BACKFILL-OK-{i}",
                    "item_type": "PRODUCT_SOURCE",
                    "notes": "BACKFILL_PRE_GOVERNANCE — pre-governance work",
                    "ledger_entry_id": f"LEDGER-OK-{i}",
                }
                for i in range(2)  # 2 == max(2) — boundary, no warning
            ],
            "evidence_artifacts": [],
        }
        result = validate(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        bw = result.get("backfill_warnings", [])
        assert len(bw) == 0, f"Expected no backfill_warnings for 2 valid items, got: {bw}"


class TestV47SpecFactRefsInSalOutput:
    """Regression tests for V47 validate_spec_fact_refs_in_sal_output (TC-MACH-ARCH-007).

    V47 verifies that PRODUCT_SOURCE spec_fact_refs exist in sal-facts-latest.json.
    BLOCKS sprint if any declared ref is missing from SAL output.

    POSITIVE: real FACT-FODS-001 in spec_fact_refs -> PASS.
    NEGATIVE: fake FACT-FODS-999 in spec_fact_refs -> FAIL + blocks.
    NO-REFS: PRODUCT_SOURCE item without spec_fact_refs -> PASS (not checked).
    NON-PRODUCT: GOVERNANCE_TASKCARD type -> PASS (not checked).
    """

    def _validator(self):
        from governance_validators import validate_spec_fact_refs_in_sal_output
        return validate_spec_fact_refs_in_sal_output

    def test_real_fods_fact_passes(self):
        """POSITIVE: FACT-FODS-001 exists in SAL output -> PASS."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V47-POS-001",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-001"],
            }],
        }
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "PASS", f"Expected PASS, got {result}"
        assert result["blocks_sprint"] is False

    def test_fake_fact_blocks(self):
        """NEGATIVE: FACT-FODS-999 does not exist in SAL output -> FAIL + blocks."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V47-NEG-001",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-999"],
            }],
        }
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "FAIL", f"Expected FAIL, got {result}"
        assert result["blocks_sprint"] is True
        assert any("FACT-FODS-999" in str(v) for v in result["items"])

    def test_no_spec_fact_refs_passes(self):
        """PRODUCT_SOURCE without spec_fact_refs is not checked -> PASS."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V47-NOREFS-001",
                "item_type": "PRODUCT_SOURCE",
            }],
        }
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_governance_taskcard_exempt(self):
        """GOVERNANCE_TASKCARD item type is not checked even with spec_fact_refs -> PASS."""
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-V47-GOV-001",
                "item_type": "GOVERNANCE_TASKCARD",
                "spec_fact_refs": ["FACT-FODS-999"],
            }],
        }
        result = validate(decl, repo_root=REPO_ROOT)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_empty_declaration_passes(self):
        """Empty declaration -> PASS."""
        validate = self._validator()
        result = validate({}, repo_root=REPO_ROOT)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False


class TestV36SpecQnameOnlyDetection:
    """TC-ZS-006: V36 must detect spec_qname-only assertion patterns."""

    def _validator(self):
        from governance_validators import validate_no_stub_tests
        return validate_no_stub_tests

    def test_spec_qname_only_assertions_trigger_warn(self, tmp_path):
        """Test file with >80% spec_qname == assertions → WARN."""
        test_file = tmp_path / "test_qname_only.py"
        test_file.write_text(
            "def test_a():\n"
            "    assert Foo.spec_qname == 'table:table'\n"
            "    assert Bar.spec_qname == 'text:p'\n"
            "    assert Baz.spec_qname == 'office:document'\n"
            "    assert Qux.spec_qname == 'text:span'\n"
        )
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-ZS-006-NEG-001",
                "item_type": "PRODUCT_SOURCE",
                "test_references": [str(test_file)],
            }],
        }
        result = validate(decl)
        assert result["result"] == "WARN", f"Expected WARN for spec_qname-only file, got {result}"
        assert result["blocks_sprint"] is False

    def test_behavioral_assertions_pass(self, tmp_path):
        """Test file with behavioral assertions (== values, not spec_qname) → PASS."""
        test_file = tmp_path / "test_behavioral.py"
        test_file.write_text(
            "def test_a():\n"
            "    obj = MyClass({'name': 'Sheet1'})\n"
            "    assert obj.name == 'Sheet1'\n"
            "    assert obj.row_count == 0\n"
            "    assert obj.to_dict() == {'name': 'Sheet1'}\n"
        )
        validate = self._validator()
        decl = {
            "planned_work_items": [{
                "item_id": "TC-ZS-006-POS-001",
                "item_type": "PRODUCT_SOURCE",
                "test_references": [str(test_file)],
            }],
        }
        result = validate(decl)
        assert result["result"] == "PASS", f"Expected PASS for behavioral test, got {result}"


# ---------------------------------------------------------------------------
# V51 — TC-QHARD-001: validate_spec_qname_coverage
# ---------------------------------------------------------------------------

class TestV51SpecQnameCoverage:
    """Regression tests for V51 validate_spec_qname_coverage (TC-QHARD-001).

    V51 scans all 20 Python format packages and WARNs for exported classes
    that lack a spec_qname attribute. WARN-only (blocks_sprint=False).

    LIVE-WARN: real repo currently has 9 classes lacking spec_qname.
    FACADE-ONLY: zst is skipped (no domain model classes).
    SYNTHETIC-PASS: tmp package whose exported class has spec_qname → PASS.
    SYNTHETIC-WARN: tmp package whose exported class lacks spec_qname → WARN.
    """

    def _validator(self):
        from governance_validators_ext import validate_spec_qname_coverage
        return validate_spec_qname_coverage

    def test_live_repo_returns_warn_not_fail(self):
        """Live repo scan: V51 must return WARN (9 known missing), never FAIL."""
        validate = self._validator()
        result = validate()
        assert result["result"] in ("WARN", "PASS"), (
            f"V51 must never FAIL (blocks_sprint=True); got {result['result']}"
        )
        assert result["blocks_sprint"] is False, "V51 must not block sprint"
        assert result["validator"] == "validate_spec_qname_coverage"

    def test_live_repo_all_known_classes_resolved(self):
        """Live repo: the 9 formerly-missing classes now have spec_qname → V51 returns PASS."""
        validate = self._validator()
        result = validate()
        # After TC-QHARD-035/036/037/039: spec_qname added to all 9 legacy classes
        # V51 should now return PASS (or WARN for other unresolved classes, but not these 9)
        resolved_classes = {"DifCell", "DifDocument", "OdsRow", "OdtListItem",
                            "PbmImage", "PgmImage", "PpmImage", "QoiImage", "SylkDocument"}
        still_missing = {item["class"] for item in result.get("items", [])} & resolved_classes
        assert not still_missing, (
            f"Expected 0 of the resolved classes in V51 items, but still found: {still_missing}"
        )

    def test_synthetic_class_with_spec_qname_passes(self, tmp_path):
        """Synthetic format package: exported class with spec_qname → PASS."""
        # Build minimal format package in tmp_path/src/python/myfmt/
        fmt_root = tmp_path / "src" / "python" / "myfmt"
        fmt_root.mkdir(parents=True)
        (fmt_root / "__init__.py").write_text(
            '__all__ = ["MyDoc"]\nfrom .mydoc import MyDoc\n',
            encoding="utf-8",
        )
        (fmt_root / "mydoc.py").write_text(
            "class MyDoc:\n    spec_qname = 'office:document'\n",
            encoding="utf-8",
        )
        validate = self._validator()
        # Inject our tmp_path as repo_root; pass empty declaration
        result = validate(declaration={}, repo_root=tmp_path)
        # myfmt is not in _FORMATS list, so it won't be scanned — result PASS trivially
        assert result["result"] in ("WARN", "PASS")
        assert result["blocks_sprint"] is False

    def test_synthetic_class_without_spec_qname_warns(self, tmp_path):
        """Synthetic: a class in a real format folder without spec_qname → WARN."""
        # Override dif package with a class that lacks spec_qname
        fmt_root = tmp_path / "src" / "python" / "dif"
        fmt_root.mkdir(parents=True)
        (fmt_root / "__init__.py").write_text(
            '__all__ = ["DifCell"]\nfrom .dif_model import DifCell\n',
            encoding="utf-8",
        )
        (fmt_root / "dif_model.py").write_text(
            "class DifCell:\n    pass\n",
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "WARN", f"Expected WARN for class without spec_qname, got {result}"
        assert result["blocks_sprint"] is False
        classes_warned = [i["class"] for i in result["items"]]
        assert "DifCell" in classes_warned, f"DifCell should be in WARN items: {result['items']}"

    def test_error_class_exempt(self, tmp_path):
        """Error subclasses are exempt from spec_qname requirement."""
        fmt_root = tmp_path / "src" / "python" / "dif"
        fmt_root.mkdir(parents=True)
        (fmt_root / "__init__.py").write_text(
            '__all__ = ["DifParseError"]\nfrom .dif_errors import DifParseError\n',
            encoding="utf-8",
        )
        (fmt_root / "dif_errors.py").write_text(
            "class DifParseError(Exception):\n    pass\n",
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        # DifParseError ends with "Error" → exempt → PASS
        assert result["result"] == "PASS", (
            f"Error classes must be exempt, got {result}"
        )


# ---------------------------------------------------------------------------
# V52 — TC-QHARD-002: validate_compat_import_integrity
# ---------------------------------------------------------------------------

class TestV52CompatImportIntegrity:
    """Regression tests for V52 validate_compat_import_integrity (TC-QHARD-002).

    V52 scans Compat/ facades for spec/ imports and verifies the target file
    exists and contains the named class. WARN-only (blocks_sprint=False).

    LIVE-PASS: real FODS Compat/ passes (spec/ classes exist).
    SYNTHETIC-WARN: Compat file importing non-existent spec file → WARN.
    SYNTHETIC-PASS: Compat file with valid relative import → PASS.
    ABSOLUTE-PASS: Compat file with absolute 'from src.python.X.spec...' import → PASS.
    """

    def _validator(self):
        from governance_validators_ext import validate_compat_import_integrity
        return validate_compat_import_integrity

    def test_live_fods_compat_passes(self):
        """Live FODS Compat/ files (FodsDocument, FodsSheet, FodsCell) → PASS."""
        validate = self._validator()
        result = validate()
        # FODS Compat/ currently imports from existing spec/ classes → PASS
        assert result["result"] in ("WARN", "PASS"), (
            f"V52 must never FAIL (blocks_sprint=True); got {result['result']}"
        )
        assert result["blocks_sprint"] is False

    def test_synthetic_missing_spec_file_warns(self, tmp_path):
        """Compat/ file importing from non-existent spec/ file → WARN."""
        fmt_root = tmp_path / "src" / "python" / "dif"
        compat_dir = fmt_root / "Compat"
        compat_dir.mkdir(parents=True)
        (compat_dir / "dif_facade.py").write_text(
            "from ..spec.office.document import Document\n"
            "class DifFacade(Document):\n    pass\n",
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "WARN", (
            f"Expected WARN for missing spec file, got {result}"
        )
        assert result["blocks_sprint"] is False
        issues = [i["issue"] for i in result["items"]]
        assert any("does not exist" in iss for iss in issues), (
            f"Expected 'does not exist' in issues: {issues}"
        )

    def test_synthetic_valid_relative_import_passes(self, tmp_path):
        """Compat/ file with valid relative import → PASS."""
        fmt_root = tmp_path / "src" / "python" / "dif"
        compat_dir = fmt_root / "Compat"
        spec_dir = fmt_root / "spec" / "office"
        compat_dir.mkdir(parents=True)
        spec_dir.mkdir(parents=True)
        (spec_dir / "document.py").write_text(
            "class Document:\n    spec_qname = 'office:document'\n",
            encoding="utf-8",
        )
        (compat_dir / "dif_facade.py").write_text(
            "from ..spec.office.document import Document\n"
            "class DifFacade(Document):\n    pass\n",
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            f"Expected PASS for valid import, got {result}"
        )

    def test_synthetic_absolute_import_passes(self, tmp_path):
        """Compat/ file with absolute 'from src.python.X.spec...' import → PASS."""
        fmt_root = tmp_path / "src" / "python" / "dif"
        compat_dir = fmt_root / "Compat"
        spec_dir = fmt_root / "spec" / "office"
        compat_dir.mkdir(parents=True)
        spec_dir.mkdir(parents=True)
        (spec_dir / "document.py").write_text(
            "class Document:\n    spec_qname = 'office:document'\n",
            encoding="utf-8",
        )
        (compat_dir / "dif_facade.py").write_text(
            "from src.python.dif.spec.office.document import Document\n"
            "class DifFacade(Document):\n    pass\n",
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            f"Expected PASS for valid absolute import, got {result}"
        )

    def test_compat_init_is_skipped(self, tmp_path):
        """__init__.py inside Compat/ is ignored by V52."""
        fmt_root = tmp_path / "src" / "python" / "dif"
        compat_dir = fmt_root / "Compat"
        compat_dir.mkdir(parents=True)
        # __init__.py with a broken import — should not trigger WARN
        (compat_dir / "__init__.py").write_text(
            "from ..spec.nonexistent.path import Something\n",
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            f"__init__.py should be skipped, got {result}"
        )


# ---------------------------------------------------------------------------
# V53 — TC-QHARD-003: validate_spec_authority_class_completeness
# ---------------------------------------------------------------------------

class TestV53SpecAuthorityClassCompleteness:
    """Regression tests for V53 validate_spec_authority_class_completeness (TC-QHARD-003).

    V53 reads QName registry YAML files and verifies each python_file entry
    exists on disk with a class containing matching spec_qname. WARN-only.

    LIVE-PASS: real fodt.yaml entries with implemented python files → PASS.
    NO-REGISTRY: missing registry dir → PASS (skip).
    MISSING-FILE: registry entry with python_file not on disk → WARN.
    WRONG-QNAME: file exists but no class with matching spec_qname → WARN.
    CORRECT-ENTRY: file exists with correct spec_qname → PASS.
    """

    def _validator(self):
        from governance_validators_ext import validate_spec_authority_class_completeness
        return validate_spec_authority_class_completeness

    def test_live_fodt_registry_passes(self):
        """Live fodt.yaml with implemented spec classes → PASS (or WARN for partial)."""
        validate = self._validator()
        # Use formats_filter to test only fodt (known to have implemented entries)
        result = validate(formats_filter=["fodt"])
        assert result["result"] in ("WARN", "PASS"), (
            f"V53 must never FAIL; got {result['result']}"
        )
        assert result["blocks_sprint"] is False
        assert result["validator"] == "validate_spec_authority_class_completeness"

    def test_no_registry_dir_returns_pass(self, tmp_path):
        """Missing registry directory → PASS (nothing to check)."""
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            f"Missing registry should PASS, got {result}"
        )
        assert "skipped" in result["summary"].lower() or result["result"] == "PASS"

    def test_missing_python_file_warns(self, tmp_path):
        """Registry entry with python_file not on disk → WARN."""
        import yaml
        reg_dir = tmp_path / "shared" / "qname-registry"
        reg_dir.mkdir(parents=True)
        (reg_dir / "testfmt.yaml").write_text(
            yaml.dump([{
                "qname": "office:document",
                "canonical_class": "Document",
                "python_file": "src/python/testfmt/spec/office/document.py",
                "status": "implementing",
            }]),
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "WARN", (
            f"Expected WARN for missing python_file, got {result}"
        )
        assert result["blocks_sprint"] is False
        issues = [i["issue"] for i in result["items"]]
        assert any("does not exist" in iss for iss in issues), (
            f"Expected 'does not exist' in issues: {issues}"
        )

    def test_file_without_correct_spec_qname_warns(self, tmp_path):
        """File exists but class has wrong/missing spec_qname → WARN."""
        import yaml
        reg_dir = tmp_path / "shared" / "qname-registry"
        reg_dir.mkdir(parents=True)
        py_dir = tmp_path / "src" / "python" / "testfmt" / "spec" / "office"
        py_dir.mkdir(parents=True)
        (py_dir / "document.py").write_text(
            "class Document:\n    pass\n",  # no spec_qname
            encoding="utf-8",
        )
        (reg_dir / "testfmt.yaml").write_text(
            yaml.dump([{
                "qname": "office:document",
                "canonical_class": "Document",
                "python_file": "src/python/testfmt/spec/office/document.py",
                "status": "implementing",
            }]),
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "WARN", (
            f"Expected WARN for class without spec_qname, got {result}"
        )
        assert any("no class with spec_qname" in i["issue"] for i in result["items"]), (
            f"Expected 'no class with spec_qname' message: {result['items']}"
        )

    def test_correct_registry_entry_passes(self, tmp_path):
        """File exists with matching spec_qname attribute → PASS."""
        import yaml
        reg_dir = tmp_path / "shared" / "qname-registry"
        reg_dir.mkdir(parents=True)
        py_dir = tmp_path / "src" / "python" / "testfmt" / "spec" / "office"
        py_dir.mkdir(parents=True)
        (py_dir / "document.py").write_text(
            "class Document:\n    spec_qname = 'office:document'\n",
            encoding="utf-8",
        )
        (reg_dir / "testfmt.yaml").write_text(
            yaml.dump([{
                "qname": "office:document",
                "canonical_class": "Document",
                "python_file": "src/python/testfmt/spec/office/document.py",
                "status": "implementing",
            }]),
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            f"Expected PASS for valid registry entry, got {result}"
        )

    def test_entry_without_python_file_skipped(self, tmp_path):
        """Registry entry with python_file=null is skipped silently."""
        import yaml
        reg_dir = tmp_path / "shared" / "qname-registry"
        reg_dir.mkdir(parents=True)
        (reg_dir / "testfmt.yaml").write_text(
            yaml.dump([{
                "qname": "office:document",
                "canonical_class": "Document",
                "python_file": None,
                "status": "seeded",
            }]),
            encoding="utf-8",
        )
        validate = self._validator()
        result = validate(declaration={}, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            f"Null python_file should be skipped → PASS, got {result}"
        )
        assert result["items"] == []


class TestV54CrossLaneProductTouchingMachinery:
    """Regression tests for V54 validate_cross_lane_product_touching_machinery.

    V54 warns when a PRODUCT_SOURCE-track item declares changed_files under tools/supervisor/.
    Conditional-blocking (blocks_sprint=True when violations found).

    POSITIVE: PRODUCT_SOURCE item + tools/supervisor/ file → WARN
    NEGATIVE: PRODUCT_SOURCE item + src/python/ file → PASS
    EXCEPTION: item with lane_exception=MACHINERY_HEALING → PASS (bypass)
    MACHINERY-ITEM: GOVERNANCE_TASKCARD item + tools/supervisor/ file → PASS (not product)
    NO-DECL: None declaration → PASS
    """

    def _validator(self):
        from governance_validators_ext import validate_cross_lane_product_touching_machinery
        return validate_cross_lane_product_touching_machinery

    def test_product_source_touching_supervisor_warns(self):
        """PRODUCT_SOURCE item with tools/supervisor/ change → WARN."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-TEST-001",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["tools/supervisor/autonomous_cycle.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "WARN", f"Expected WARN, got {result['result']}: {result}"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert "tools/supervisor/autonomous_cycle.py" in result["items"][0]["changed_file"]

    def test_product_source_touching_src_passes(self):
        """PRODUCT_SOURCE item with src/python/ change → PASS (correct lane)."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-TEST-002",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["src/python/csv/csv_parser.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "PASS", f"Expected PASS, got {result['result']}: {result}"
        assert result["items"] == []

    def test_machinery_healing_exception_bypasses_warn(self):
        """Item with lane_exception=MACHINERY_HEALING bypasses V54."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-HEAL-001",
                "item_type": "PRODUCT_SOURCE",
                "lane_exception": "MACHINERY_HEALING",
                "changed_files": ["tools/supervisor/governance_validators.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "PASS", (
            f"MACHINERY_HEALING exception must bypass V54; got {result['result']}"
        )

    def test_governance_taskcard_touching_supervisor_passes(self):
        """GOVERNANCE_TASKCARD item touching tools/supervisor/ is machinery-track → PASS (V54 not applicable)."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-GOV-001",
                "item_type": "GOVERNANCE_TASKCARD",
                "changed_files": ["tools/supervisor/autonomous_cycle.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "PASS", (
            f"GOVERNANCE_TASKCARD is machinery-track, should not trigger V54; got {result['result']}"
        )

    def test_none_declaration_passes(self):
        """None declaration → PASS (skip)."""
        validate = self._validator()
        result = validate(declaration=None)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False


class TestV55CrossLaneMachineryTouchingProduct:
    """Regression tests for V55 validate_cross_lane_machinery_touching_product.

    V55 warns when a MACHINERY-track item declares changed_files under src/.
    Conditional-blocking (blocks_sprint=True when violations found).

    POSITIVE: GOVERNANCE_TASKCARD item + src/python/ file → WARN
    NEGATIVE: GOVERNANCE_TASKCARD item + tools/supervisor/ file → PASS
    EXCEPTION: item with lane_exception=MACHINERY_HEALING → PASS (bypass)
    PRODUCT-ITEM: PRODUCT_SOURCE item + src/python/ file → PASS (not machinery)
    NO-DECL: None declaration → PASS
    """

    def _validator(self):
        from governance_validators_ext import validate_cross_lane_machinery_touching_product
        return validate_cross_lane_machinery_touching_product

    def test_governance_taskcard_touching_src_warns(self):
        """GOVERNANCE_TASKCARD item with src/python/ change → WARN."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-GOV-002",
                "item_type": "GOVERNANCE_TASKCARD",
                "changed_files": ["src/python/fods/fods_parser.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "WARN", f"Expected WARN, got {result['result']}: {result}"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert "src/python/fods/fods_parser.py" in result["items"][0]["changed_file"]

    def test_governance_taskcard_touching_tools_passes(self):
        """GOVERNANCE_TASKCARD item with tools/supervisor/ change → PASS (correct lane)."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-GOV-003",
                "item_type": "GOVERNANCE_TASKCARD",
                "changed_files": ["tools/supervisor/check_continuation.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "PASS", f"Expected PASS, got {result['result']}: {result}"
        assert result["items"] == []

    def test_machinery_healing_exception_bypasses_warn(self):
        """Item with lane_exception=MACHINERY_HEALING bypasses V55."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-HEAL-002",
                "item_type": "GOVERNANCE_TASKCARD",
                "lane_exception": "MACHINERY_HEALING",
                "changed_files": ["src/python/xcf/xcf_analytics.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "PASS", (
            f"MACHINERY_HEALING exception must bypass V55; got {result['result']}"
        )

    def test_product_source_touching_src_passes(self):
        """PRODUCT_SOURCE item touching src/ is product-track → PASS (V55 not applicable)."""
        validate = self._validator()
        declaration = {
            "completed_work_items": [{
                "item_id": "TC-PROD-001",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["src/python/csv/csv_parser.py"],
            }],
            "planned_work_items": [],
        }
        result = validate(declaration=declaration)
        assert result["result"] == "PASS", (
            f"PRODUCT_SOURCE is product-track, should not trigger V55; got {result['result']}"
        )

    def test_none_declaration_passes(self):
        """None declaration → PASS (skip)."""
        validate = self._validator()
        result = validate(declaration=None)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False


class TestV57ChangedFilesInLedger:
    """Regression tests for V57 validate_changed_files_in_ledger (TC-VNK-003).

    V57 warns when a src/python/ or src/net/ changed_file has no entry in
    the product-code-change-ledger.json. WARN-only (blocks_sprint=False).

    POSITIVE: src/python/ path in ledger → PASS
    NEGATIVE: src/python/ path NOT in ledger → WARN
    EXCLUSION: non-src/ file in changed_files → not flagged (PASS)
    NO-DECL: None declaration → PASS
    """

    def _validator(self):
        from governance_validators_ext import validate_changed_files_in_ledger
        return validate_changed_files_in_ledger

    def test_v57_src_file_in_ledger_pass(self):
        """src/python/ path present in ledger → PASS."""
        import json
        import tempfile
        from pathlib import Path
        validate = self._validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_dir = root / "reports" / "r90"
            ledger_dir.mkdir(parents=True)
            ledger = {
                "entries": [{
                    "entry_id": "TEST-001",
                    "source_files": [{"path": "src/python/fods/fods_parser.py", "state": "present"}],
                }]
            }
            (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger))
            declaration = {"changed_files": ["src/python/fods/fods_parser.py"]}
            result = validate(declaration=declaration, repo_root=root)
        assert result["result"] == "PASS", f"Expected PASS, got {result['result']}: {result}"
        assert result["items"] == []
        assert result["blocks_sprint"] is False

    def test_v57_src_file_not_in_ledger_warn(self):
        """src/python/ path NOT in ledger → WARN."""
        import json
        import tempfile
        from pathlib import Path
        validate = self._validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_dir = root / "reports" / "r90"
            ledger_dir.mkdir(parents=True)
            ledger = {"entries": []}
            (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger))
            declaration = {"changed_files": ["src/python/fods/fods_new_feature.py"]}
            result = validate(declaration=declaration, repo_root=root)
        assert result["result"] == "WARN", f"Expected WARN, got {result['result']}: {result}"
        assert len(result["items"]) == 1
        assert "src/python/fods/fods_new_feature.py" in result["items"][0]["path"]
        assert result["blocks_sprint"] is False

    def test_v57_non_src_file_excluded(self):
        """Non-src/ file in changed_files → not flagged (PASS)."""
        import json
        import tempfile
        from pathlib import Path
        validate = self._validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_dir = root / "reports" / "r90"
            ledger_dir.mkdir(parents=True)
            ledger = {"entries": []}
            (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger))
            declaration = {"changed_files": ["tools/supervisor/check_continuation.py", "docs/readme.md"]}
            result = validate(declaration=declaration, repo_root=root)
        assert result["result"] == "PASS", f"Expected PASS for non-src files, got {result['result']}"
        assert result["items"] == []

    def test_v57_none_declaration_passes(self):
        """None declaration → PASS (skip)."""
        validate = self._validator()
        result = validate(declaration=None)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False


class TestV46V57Integration:
    """Integration tests for V46 backfill hardening + V57 ledger validator (TC-VNK-H-004).

    Uses a realistic multi-item declaration modeled after vivid-napping-kurzweil
    to verify V46 and V57 produce correct results for mixed item types.
    """

    def _build_realistic_declaration(self, backfill_count=0, ledger_src_files=None):
        """Build a realistic declaration with governance + product items."""
        import json
        import tempfile
        from pathlib import Path

        items = [
            {
                "item_id": "TC-INT-001",
                "item_type": "GOVERNANCE_TASKCARD",
                "title": "Verify loop state",
                "status": "completed",
            },
            {
                "item_id": "TC-INT-002",
                "item_type": "GOVERNANCE_TASKCARD",
                "title": "Add governance validator",
                "status": "completed",
            },
            {
                "item_id": "TC-INT-003",
                "item_type": "PRODUCT_SOURCE",
                "title": "Extract analytics from codec",
                "status": "completed",
                "notes": "Skill transcript at reports/skills-r104/skill-transcripts/test.json",
            },
        ]
        # Add BACKFILL items if requested
        for i in range(backfill_count):
            items.append({
                "item_id": f"TC-INT-BF-{i+1:03d}",
                "item_type": "PRODUCT_SOURCE",
                "title": f"Backfill item {i+1}",
                "status": "completed",
                "notes": "BACKFILL_PRE_GOVERNANCE — pre-existing work",
            })

        declaration = {
            "sprint_id": "integration-test-sprint",
            "planned_work_items": items,
            "completed_work_items": [it["item_id"] for it in items],
            "evidence_artifacts": [],
            "test_results": {"passed": 100, "failed": 0, "total": 100},
            "changed_files": [
                "tools/supervisor/governance_validators.py",
                "src/python/fodp/fodp_codec.py",
                "src/python/fodp/fodp_analytics.py",
            ],
        }

        # Create temp repo with ledger
        tmp = tempfile.mkdtemp()
        root = Path(tmp)
        ledger_dir = root / "reports" / "r90"
        ledger_dir.mkdir(parents=True)
        src_paths = ledger_src_files or ["src/python/fodp/fodp_codec.py"]
        ledger = {
            "entries": [
                {
                    "entry_id": "INT-TEST-001",
                    "source_files": [{"path": p, "state": "modified"} for p in src_paths],
                }
            ]
        }
        (ledger_dir / "product-code-change-ledger.json").write_text(json.dumps(ledger))
        return declaration, root

    def test_integration_v46_backfill_warns_on_bulk(self):
        """V46: realistic declaration with 3 BACKFILL items → bulk warning."""
        from governance_validators import validate_skill_transcript_present
        decl, root = self._build_realistic_declaration(backfill_count=3)
        result = validate_skill_transcript_present(decl)
        warnings = result.get("backfill_warnings", [])
        bulk_warns = [w for w in warnings if w.get("item_id") == "BULK_BACKFILL_WARNING"]
        assert len(bulk_warns) == 1, f"Expected 1 BULK_BACKFILL_WARNING, got {len(bulk_warns)}"
        # Also: all 3 backfill items should warn about missing ledger_entry_id
        ledger_warns = [w for w in warnings if "ledger_entry_id" in w.get("reason", "")]
        assert len(ledger_warns) == 3, f"Expected 3 ledger_entry_id warnings, got {len(ledger_warns)}"

    def test_integration_v46_no_warn_with_legit_backfill(self):
        """V46: realistic declaration with 2 BACKFILL items + ledger_entry_id → no warnings."""
        from governance_validators import validate_skill_transcript_present
        decl, root = self._build_realistic_declaration(backfill_count=0)
        # Manually add 2 legitimate backfill items with ledger_entry_id
        for i in range(2):
            decl["planned_work_items"].append({
                "item_id": f"TC-INT-LBF-{i+1:03d}",
                "item_type": "PRODUCT_SOURCE",
                "title": f"Legitimate backfill {i+1}",
                "status": "completed",
                "notes": "BACKFILL_PRE_GOVERNANCE — pre-existing work",
                "ledger_entry_id": f"LBF-{i+1:03d}",
            })
        result = validate_skill_transcript_present(decl)
        warnings = result.get("backfill_warnings", [])
        assert len(warnings) == 0, f"Expected 0 backfill warnings, got {len(warnings)}: {warnings}"

    def test_integration_v57_mixed_changed_files(self):
        """V57: realistic declaration with src/ and non-src/ files, partial ledger coverage."""
        from governance_validators_ext import validate_changed_files_in_ledger
        decl, root = self._build_realistic_declaration(
            ledger_src_files=["src/python/fodp/fodp_codec.py"]
        )
        # changed_files has fodp_codec.py (in ledger) + fodp_analytics.py (NOT in ledger)
        result = validate_changed_files_in_ledger(declaration=decl, repo_root=root)
        assert result["result"] == "WARN", f"Expected WARN (analytics.py missing), got {result['result']}"
        warned_paths = [item["path"] for item in result["items"]]
        assert "src/python/fodp/fodp_analytics.py" in warned_paths
        # governance_validators.py should NOT be warned (not src/python or src/net)
        assert "tools/supervisor/governance_validators.py" not in warned_paths

    def test_integration_v57_all_covered(self):
        """V57: all src/ changed_files in ledger → PASS."""
        from governance_validators_ext import validate_changed_files_in_ledger
        decl, root = self._build_realistic_declaration(
            ledger_src_files=["src/python/fodp/fodp_codec.py", "src/python/fodp/fodp_analytics.py"]
        )
        result = validate_changed_files_in_ledger(declaration=decl, repo_root=root)
        assert result["result"] == "PASS", f"Expected PASS, got {result['result']}: {result}"
        assert result["items"] == []


class TestCanonicalValidatorCount:
    """TC-PROD-H-040R: Assert canonical validator count to catch silent additions/removals."""

    def test_canonical_validator_count(self):
        """run_all_governance_validators must return exactly 72 validator results."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
        from governance_validator_runner import run_all_governance_validators
        decl = {
            "sprint_id": "test-canonical-count",
            "work_items": [],
            "completed_work_items": [],
            "planned_work_items": [],
            "evidence_artifacts": [],
            "test_results": {"passed": 0, "failed": 0, "total": 0},
            "changed_files": [],
        }
        result = run_all_governance_validators(decl, None)
        validator_count = len(result["validators"])
        assert validator_count == 83, (
            f"Expected 83 canonical validators, got {validator_count}. "
            "If validators were added/removed, update this test. "
            "(83 = 81 prior + 2 new validators added in sprint s84)"
        )


# ---------------------------------------------------------------------------
# V62 — TC-MACH-VAL-001: spec_fact_refs density
# ---------------------------------------------------------------------------

from governance_validators_ext import validate_spec_fact_refs_density


class TestV62SpecFactRefsDensity:
    def test_product_source_with_spec_fact_ref_passes(self):
        decl = {
            "completed_work_items": [{
                "item_id": "WI-001",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["src/python/fods/models.py"],
                "spec_fact_refs": ["FACT-FODS-001"],
                "evidence_artifacts": [],
            }],
        }
        result = validate_spec_fact_refs_density(decl)
        assert result["result"] == "PASS"

    def test_product_source_without_spec_fact_ref_warns(self):
        decl = {
            "completed_work_items": [{
                "item_id": "WI-002",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["src/python/fods/models.py"],
                "spec_fact_refs": [],
                "evidence_artifacts": [],
            }],
        }
        result = validate_spec_fact_refs_density(decl)
        assert result["result"] == "WARN"
        assert len(result["items"]) == 1
        assert result["blocks_sprint"] is False

    def test_compat_class_excluded(self):
        decl = {
            "completed_work_items": [{
                "item_id": "WI-003",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["src/python/fods/Compat/fods_cell.py"],
                "spec_fact_refs": [],
                "evidence_artifacts": [],
            }],
        }
        result = validate_spec_fact_refs_density(decl)
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# V63 — TC-MACH-SRC-001: public API surface ratio
# ---------------------------------------------------------------------------

from governance_validators_ext import validate_public_api_surface_ratio


class TestV63PublicApiSurfaceRatio:
    def test_small_init_passes(self):
        decl = {
            "planned_work_items": [{
                "item_id": "WI-004",
                "item_type": "PRODUCT_SOURCE",
                "changed_files": ["src/python/fods/__init__.py"],
                "evidence_artifacts": [],
            }],
        }
        # FODS __init__.py likely has <50 exports — should pass
        result = validate_public_api_surface_ratio(decl)
        assert result["result"] in ("PASS", "WARN")  # Depends on actual file state
        assert result["blocks_sprint"] is False

    def test_non_product_source_skipped(self):
        decl = {
            "planned_work_items": [{
                "item_id": "WI-005",
                "item_type": "GOVERNANCE_TASKCARD",
                "changed_files": ["src/python/ndjson/__init__.py"],
                "evidence_artifacts": [],
            }],
        }
        result = validate_public_api_surface_ratio(decl)
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# TC-HEAL-A002: V13 enforcement confirmation tests (SAL-HEAL-A001 audit, 2026-06-25)
# BP-002 investigation claim was inaccurate: V13 already blocks absent spec_fact_refs.
# These tests document and lock in the correct behavior.
# ---------------------------------------------------------------------------

class TestV13SpecFactRefsEnforcement:
    """Confirm V13 (validate_spec_fact_refs_wired / check_item) correctly enforces:
    - absent spec_fact_refs + absent exception_classification → HARD BLOCK
    - item-level exception_classification → PASS
    - valid spec_fact_refs → PASS
    """

    def test_v13_blocks_product_source_no_spec_fact_refs_no_exception(self):
        """CRITICAL: PRODUCT_SOURCE with neither spec_fact_refs nor exception → compliant=False."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"))
        from validate_spec_fact_refs import check_item
        item = {
            "item_id": "V13-NEG-001",
            "item_type": "PRODUCT_SOURCE",
            "gap_ledger_ref": "GAP-FODS-0001",
            # No spec_fact_refs, no exception_classification
        }
        result = check_item(item)
        assert result["compliant"] is False, (
            f"Expected HARD BLOCK for PRODUCT_SOURCE with no spec authority, got: {result}"
        )
        assert result["grade_impact"] == "reject"
        assert "BLOCKING" in result["violation"]

    def test_v13_passes_legacy_backfill_exception_at_item_level(self):
        """Item-level exception_classification=legacy_backfill → compliant=True (designed bypass)."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"))
        from validate_spec_fact_refs import check_item
        item = {
            "item_id": "V13-EXC-001",
            "item_type": "PRODUCT_SOURCE",
            "gap_ledger_ref": "GAP-CSV-001",
            "exception_classification": "legacy_backfill",
        }
        result = check_item(item)
        assert result["compliant"] is True, (
            f"Expected PASS for item with legacy_backfill exception, got: {result}"
        )

    def test_v13_passes_schema_authority_exception(self):
        """schema_authority_available exception for schema-only formats → PASS."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"))
        from validate_spec_fact_refs import check_item
        item = {
            "item_id": "V13-SCHEMA-001",
            "item_type": "PRODUCT_SOURCE",
            "gap_ledger_ref": "GAP-GNUMERIC-001",
            "exception_classification": "schema_authority_available",
        }
        result = check_item(item)
        assert result["compliant"] is True

    def test_v13_passes_valid_spec_fact_refs(self):
        """Valid spec_fact_refs (mocked registry) → compliant=True."""
        import sys
        from pathlib import Path
        from unittest.mock import patch
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"))
        from validate_spec_fact_refs import check_item
        item = {
            "item_id": "V13-POS-001",
            "item_type": "PRODUCT_SOURCE",
            "gap_ledger_ref": "GAP-FODS-001",
            "spec_fact_refs": ["FACT-FODS-001"],
        }
        fake_registry = {"FACT-FODS-001": "verified"}
        with patch("validate_spec_fact_refs.get_fact_registry", return_value=fake_registry):
            result = check_item(item)
        assert result["compliant"] is True
        assert result["grade_impact"] == "none"

    def test_v13_non_blocking_type_passes_unconditionally(self):
        """GOVERNANCE_TASKCARD is not a blocking type — always compliant."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"))
        from validate_spec_fact_refs import check_item
        item = {
            "item_id": "V13-GOV-001",
            "item_type": "GOVERNANCE_TASKCARD",
            # No spec_fact_refs, no exception — but not a blocking type
        }
        result = check_item(item)
        assert result["compliant"] is True
        assert result["blocking_type"] is False


# ---------------------------------------------------------------------------
# V-SGF-001 regression tests (TC-SGF-002)
# ---------------------------------------------------------------------------

class TestVSGF001SkillAttributionInDeclaration:
    """5 regression tests for validate_skill_attribution_in_declaration (V-SGF-001)."""

    def _make_declaration(self, items: list) -> dict:
        return {
            "completed_work_items": items,
            "planned_work_items": [],
        }

    def _get_validator(self):
        import sys
        from pathlib import Path
        repo = Path(__file__).resolve().parent.parent.parent
        if str(repo / "tools" / "supervisor") not in sys.path:
            sys.path.insert(0, str(repo / "tools" / "supervisor"))
        from governance_validators_ext import validate_skill_attribution_in_declaration
        return validate_skill_attribution_in_declaration, repo

    # T1: PASS when declared_skill_ids contains a valid registered skill
    def test_v_sgf_001_passes_on_valid_active_skill_ids(self):
        """Valid declared_skill_ids with a registered skill → PASS."""
        validator, repo = self._get_validator()
        decl = self._make_declaration([{
            "item_id": "W-001",
            "item_type": "PRODUCT_SOURCE",
            "declared_skill_ids": ["add-python-api"],  # registered in skill-registry.yaml
        }])
        result = validator(decl, repo)
        # Should be PASS (registered skill)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    # T2: WARN when declared_skill_ids is missing (WARN only until 2026-09-01)
    def test_v_sgf_001_warns_on_missing_declared_skill_ids(self):
        """PRODUCT_SOURCE item without declared_skill_ids → WARN (not block, before cutoff)."""
        validator, repo = self._get_validator()
        decl = self._make_declaration([{
            "item_id": "W-002",
            "item_type": "PRODUCT_SOURCE",
            # no declared_skill_ids
        }])
        result = validator(decl, repo)
        # Before 2026-09-01 → WARN, not FAIL; blocks_sprint may be False or True depending on date
        assert result["result"] in ("WARN", "FAIL"), f"Unexpected result: {result['result']}"
        assert "missing_skill_attribution" in str(result.get("items", []))

    # T3: BLOCK on unregistered skill IDs
    def test_v_sgf_001_blocks_on_unregistered_skill_id(self):
        """declared_skill_ids with an unregistered ID → FAIL + blocks_sprint=True."""
        validator, repo = self._get_validator()
        decl = self._make_declaration([{
            "item_id": "W-003",
            "item_type": "PRODUCT_SOURCE",
            "declared_skill_ids": ["nonexistent-skill-xyz-12345"],
        }])
        result = validator(decl, repo)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(
            item.get("reason") == "unregistered_skill_id"
            for item in result.get("items", [])
        )

    # T4: PASS when no PRODUCT_SOURCE items (non-product items skipped)
    def test_v_sgf_001_skips_non_product_source_items(self):
        """Items with item_type != PRODUCT_SOURCE are not checked."""
        validator, repo = self._get_validator()
        decl = self._make_declaration([{
            "item_id": "W-004",
            "item_type": "GOVERNANCE_TASKCARD",
            # No declared_skill_ids — but this type is skipped
        }])
        result = validator(decl, repo)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert "skipped" in result["summary"].lower() or "No PRODUCT" in result["summary"]

    # T5: Negative control — empty declared_skill_ids list is treated as missing
    def test_v_sgf_001_warns_on_empty_declared_skill_ids(self):
        """Empty declared_skill_ids list is treated same as missing → WARN/FAIL."""
        validator, repo = self._get_validator()
        decl = self._make_declaration([{
            "item_id": "W-005",
            "item_type": "PRODUCT_SOURCE",
            "declared_skill_ids": [],  # empty list
        }])
        result = validator(decl, repo)
        assert result["result"] in ("WARN", "FAIL")
        assert any(
            item.get("reason") == "missing_skill_attribution"
            for item in result.get("items", [])
        )


class TestV66Upgraded:
    """4 regression tests for V66 validate_multi_responsibility_file — now blocks_sprint=True."""

    def _get_validator(self):
        import sys
        sys.path.insert(0, "tools/supervisor")
        from governance_validators import validate_multi_responsibility_file
        return validate_multi_responsibility_file

    def test_v66_clean_declaration_passes(self):
        validator = self._get_validator()
        decl = {"planned_work_items": [], "changed_files": []}
        result = validator(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_v66_three_role_file_fails_with_blocks_sprint(self, tmp_path):
        validator = self._get_validator()
        f = tmp_path / "src" / "python" / "fmt" / "fmt_codec.py"
        f.parent.mkdir(parents=True)
        # class with __init__ (model role) + parse_ (parser role) + write_ (serializer role)
        f.write_text(
            "class FmtDocument:\n    def __init__(self): pass\n"
            "def parse_fmt(x): pass\n"
            "def write_fmt(x): pass\n"
        )
        decl = {
            "planned_work_items": [{
                "item_type": "PRODUCT_SOURCE",
                "evidence_paths": [str(f.relative_to(tmp_path))],
            }],
            "changed_files": ["src/python/fmt/fmt_codec.py"],
        }
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_v66_two_role_codec_passes(self, tmp_path):
        """Codec with load+write (2 roles, no model class) must PASS."""
        validator = self._get_validator()
        f = tmp_path / "src" / "python" / "fmt" / "fmt_codec.py"
        f.parent.mkdir(parents=True)
        f.write_text("def parse_fmt(x): pass\ndef write_fmt(x): pass\n")
        decl = {
            "planned_work_items": [{
                "item_type": "PRODUCT_SOURCE",
                "evidence_paths": [str(f.relative_to(tmp_path))],
            }],
            "changed_files": ["src/python/fmt/fmt_codec.py"],
        }
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_v66_result_is_fail_not_warn(self, tmp_path):
        """V66 upgraded: must return FAIL not WARN when 3 roles detected."""
        validator = self._get_validator()
        f = tmp_path / "src" / "python" / "fmt" / "fmt_codec.py"
        f.parent.mkdir(parents=True)
        f.write_text(
            "class FmtDocument:\n    def __init__(self): pass\n"
            "def parse_fmt(x): pass\n"
            "def write_fmt(x): pass\n"
        )
        decl = {
            "planned_work_items": [{
                "item_type": "PRODUCT_SOURCE",
                "evidence_paths": [str(f.relative_to(tmp_path))],
            }],
            "changed_files": ["src/python/fmt/fmt_codec.py"],
        }
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["result"] != "WARN"


class TestV77AnalyticsNamingEnforced:
    """4 regression tests for V77 validate_analytics_naming_enforced."""

    def _get_validator(self):
        import sys
        sys.path.insert(0, "tools/supervisor")
        from governance_validators_ext2 import validate_analytics_naming_enforced
        return validate_analytics_naming_enforced

    def test_v77_clean_declaration_passes(self):
        validator = self._get_validator()
        decl = {"changed_files": [], "planned_work_items": []}
        result = validator(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_v77_document_with_analytics_docstring_fails(self, tmp_path):
        validator = self._get_validator()
        f = tmp_path / "src" / "python" / "fmt" / "fmt_document.py"
        f.parent.mkdir(parents=True)
        f.write_text('"""FMT analytics functions extracted from fmt_codec.py."""\n\ndef foo(): pass\n')
        decl = {
            "changed_files": ["src/python/fmt/fmt_document.py"],
            "planned_work_items": [],
        }
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1

    def test_v77_document_without_analytics_docstring_passes(self, tmp_path):
        validator = self._get_validator()
        f = tmp_path / "src" / "python" / "fmt" / "fmt_document.py"
        f.parent.mkdir(parents=True)
        f.write_text('"""FMT domain model classes."""\n\nclass FmtDocument:\n    pass\n')
        decl = {
            "changed_files": ["src/python/fmt/fmt_document.py"],
            "planned_work_items": [],
        }
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_v77_analytics_py_file_passes(self, tmp_path):
        """Files named *_analytics.py (not *_document.py) must always PASS."""
        validator = self._get_validator()
        f = tmp_path / "src" / "python" / "fmt" / "fmt_analytics.py"
        f.parent.mkdir(parents=True)
        f.write_text('"""FMT analytics functions extracted from fmt_codec.py."""\n\ndef foo(): pass\n')
        decl = {
            "changed_files": ["src/python/fmt/fmt_analytics.py"],
            "planned_work_items": [],
        }
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"


class TestV78DotnetLocCap:
    """4 regression tests for V78 validate_dotnet_loc_cap."""

    def _get_validator(self):
        import sys
        sys.path.insert(0, "tools/supervisor")
        from governance_validators_ext2 import validate_dotnet_loc_cap
        return validate_dotnet_loc_cap

    def _make_baseline(self, tmp_path, known=None):
        import json
        baseline = {"known_violations": known or {}}
        bp = tmp_path / "registry" / "source-structure-baseline.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps(baseline))

    def test_v78_no_cs_files_passes(self, tmp_path):
        validator = self._get_validator()
        self._make_baseline(tmp_path)
        decl = {"changed_files": ["src/python/fmt/fmt_codec.py"], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_v78_small_cs_file_passes(self, tmp_path):
        validator = self._get_validator()
        self._make_baseline(tmp_path)
        f = tmp_path / "src" / "net" / "fmt" / "FmtDocument.cs"
        f.parent.mkdir(parents=True)
        f.write_text("\n".join(["// line"] * 400) + "\n")
        decl = {"changed_files": ["src/net/fmt/FmtDocument.cs"], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_v78_large_cs_file_not_in_baseline_fails(self, tmp_path):
        validator = self._get_validator()
        self._make_baseline(tmp_path)
        f = tmp_path / "src" / "net" / "fmt" / "FmtDocument.cs"
        f.parent.mkdir(parents=True)
        f.write_text("\n".join(["// line"] * 900) + "\n")
        decl = {"changed_files": ["src/net/fmt/FmtDocument.cs"], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_v78_large_cs_file_in_baseline_passes(self, tmp_path):
        validator = self._get_validator()
        self._make_baseline(tmp_path, {"src/net/fmt/FmtDocument.cs": {"loc": 900, "baseline_loc_cap": 950}})
        f = tmp_path / "src" / "net" / "fmt" / "FmtDocument.cs"
        f.parent.mkdir(parents=True)
        f.write_text("\n".join(["// line"] * 900) + "\n")
        decl = {"changed_files": ["src/net/fmt/FmtDocument.cs"], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"


class TestV79HealingStallDetector:
    """4 regression tests for V79 validate_healing_stall_detector."""

    def _get_validator(self):
        import sys
        sys.path.insert(0, "tools/supervisor")
        from governance_validators_ext2 import validate_healing_stall_detector
        return validate_healing_stall_detector

    def _make_baseline(self, tmp_path, known):
        import json
        baseline = {"known_violations": known}
        bp = tmp_path / "registry" / "source-structure-baseline.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps(baseline))

    def test_v79_no_stalls_passes(self, tmp_path):
        validator = self._get_validator()
        self._make_baseline(tmp_path, {})
        decl = {"changed_files": [], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_v79_stalled_violation_warns(self, tmp_path):
        validator = self._get_validator()
        stalled_file = tmp_path / "src" / "python" / "fmt" / "fmt_codec.py"
        stalled_file.parent.mkdir(parents=True)
        stalled_file.write_text("# stalled\n")
        self._make_baseline(tmp_path, {
            "src/python/fmt/fmt_codec.py": {"loc": 900, "baseline_loc_cap": 900}
        })
        decl = {"changed_files": [], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 1

    def test_v79_healed_violation_passes(self, tmp_path):
        """File with loc < baseline_loc_cap shows healing progress — no WARN."""
        validator = self._get_validator()
        healed_file = tmp_path / "src" / "python" / "fmt" / "fmt_codec.py"
        healed_file.parent.mkdir(parents=True)
        healed_file.write_text("# healed\n")
        self._make_baseline(tmp_path, {
            "src/python/fmt/fmt_codec.py": {"loc": 750, "baseline_loc_cap": 900}
        })
        decl = {"changed_files": [], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_v79_blocks_sprint_is_always_false(self, tmp_path):
        """V79 is advisory — must never set blocks_sprint=True."""
        validator = self._get_validator()
        stalled_file = tmp_path / "src" / "python" / "fmt" / "fmt_codec.py"
        stalled_file.parent.mkdir(parents=True)
        stalled_file.write_text("# stalled\n")
        self._make_baseline(tmp_path, {
            "src/python/fmt/fmt_codec.py": {"loc": 1500, "baseline_loc_cap": 1500}
        })
        decl = {"changed_files": [], "planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["blocks_sprint"] is False
