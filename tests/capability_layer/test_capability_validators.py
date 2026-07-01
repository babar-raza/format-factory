"""Tests for validate_capability_map.py — VAL-001 through VAL-018 (TC-CAP-015)."""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "capability_layer"))

CAP_DIR = REPO_ROOT / "reports" / "capability-layer"


@pytest.fixture(scope="module")
def validator_module():
    try:
        import validate_capability_map as vm
        return vm
    except ImportError as e:
        pytest.skip(f"validate_capability_map not importable: {e}")


@pytest.fixture(scope="module")
def validation_result(validator_module):
    result = validator_module.validate(
        unified_path=CAP_DIR / "unified-capability-map.json",
        commercial_path=CAP_DIR / "commercial-capability-map.json",
        foss_path=CAP_DIR / "foss-reduced-capability-map.json",
        gap_path=CAP_DIR / "gap-ledger-active.json",
        action_path=CAP_DIR / "action-queue.json",
        verbose=False,
    )
    return result


def test_val_001_no_schema_errors(validation_result):
    schema_errors = [e for e in validation_result.errors if "VAL-001" in e]
    assert schema_errors == [], f"VAL-001 schema errors: {schema_errors}"


def test_val_002_no_overclaim_errors(validation_result):
    overclaim = [e for e in validation_result.errors if "VAL-002" in e]
    assert overclaim == [], f"VAL-002 overclaim errors: {overclaim}"


def test_val_003_no_provenance_errors(validation_result):
    prov = [e for e in validation_result.errors if "VAL-003" in e]
    assert prov == [], f"VAL-003 provenance errors: {prov}"


def test_val_009_advisory_only_conflict_documented(validation_result):
    # VAL-009 produces 0 errors after TC-CAP-010 (all per-item advisory_only=True)
    val009_errors = [e for e in validation_result.errors if "VAL-009" in e]
    assert val009_errors == [], f"VAL-009 errors: {val009_errors}"


def test_val_013_queue_hash_fresh(validation_result):
    val013_errors = [e for e in validation_result.errors if "VAL-013" in e]
    assert val013_errors == [], f"VAL-013 stale queue: {val013_errors}"


def test_val_014_no_closed_in_active(validation_result):
    val014_errors = [e for e in validation_result.errors if "VAL-014" in e]
    assert val014_errors == [], f"VAL-014 closed in active: {val014_errors}"


def test_val_015_no_ready_gaps_without_taskcards(validation_result):
    val015_errors = [e for e in validation_result.errors if "VAL-015" in e]
    assert val015_errors == [], f"VAL-015 ready without taskcards: {val015_errors}"


def test_overall_validation_passes(validation_result):
    assert validation_result.passed, (
        f"Overall validation FAIL: {len(validation_result.errors)} errors\n"
        + "\n".join(f"  {e}" for e in validation_result.errors[:5])
    )


def test_validation_result_has_passes(validation_result):
    assert validation_result.checks_passed > 0, "No checks passed — validator may have errored"
