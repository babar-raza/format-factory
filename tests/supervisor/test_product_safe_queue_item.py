"""
Tests that PRODUCT_GAP_CLASSIFICATION_READONLY is product-safe.
Sprint: FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

PRODUCT_PILOT = _repo_root / "reports" / "h6-queue-product-loop" / "product-pilot" / "product-gap-classification.json"


def test_product_gap_classification_not_in_forbidden_actions():
    from tools.supervisor.product_action_guard import FORBIDDEN_ACTION_TYPES
    assert "PRODUCT_GAP_CLASSIFICATION_READONLY" not in FORBIDDEN_ACTION_TYPES


def test_product_gap_classification_in_safe_set():
    from tools.supervisor.product_action_guard import SAFE_PRODUCT_PILOT_ACTIONS
    assert "PRODUCT_GAP_CLASSIFICATION_READONLY" in SAFE_PRODUCT_PILOT_ACTIONS


def test_product_gap_classification_check_action_passes():
    from tools.supervisor.product_action_guard import check_action
    action = {
        "action_type": "PRODUCT_GAP_CLASSIFICATION_READONLY",
        "external_gate": False,
    }
    check_action(action)  # Should not raise


def test_product_gap_classification_cannot_write_src():
    from tools.supervisor.product_action_guard import check_action, GuardViolation
    action = {
        "action_type": "WRITE_TO_SRC",
        "target_path": "src/net/something.cs",
        "external_gate": False,
    }
    with pytest.raises(GuardViolation):
        check_action(action)


def test_product_gap_classification_cannot_mutate_poc_targets():
    from tools.supervisor.product_action_guard import check_action, GuardViolation
    action = {
        "action_type": "MUTATE_POC_TARGETS",
        "external_gate": False,
    }
    with pytest.raises(GuardViolation):
        check_action(action)


def test_product_gap_classification_result_exists():
    """Product classification result was written during orchestrator run."""
    assert PRODUCT_PILOT.exists(), f"Product pilot result not found: {PRODUCT_PILOT}"


def test_product_gap_classification_result_valid():
    """Product pilot result has required fields."""
    if not PRODUCT_PILOT.exists():
        pytest.skip("Product pilot result not present")
    data = json.loads(PRODUCT_PILOT.read_text())
    assert data.get("action_type") == "PRODUCT_GAP_CLASSIFICATION_READONLY"
    assert data.get("status") == "SUCCESS"
    assert data.get("product_source_mutated") is False
    assert data.get("poc_targets_mutated") is False


def test_run_product_gap_classification_readonly_writes_result(tmp_path):
    """run_product_gap_classification_readonly writes a valid JSON result."""
    from tools.supervisor.product_action_guard import run_product_gap_classification_readonly
    output = tmp_path / "gap-classification.json"
    result = run_product_gap_classification_readonly(output_path=output)
    assert result.get("status") == "SUCCESS"
    assert result.get("product_source_mutated") is False
    assert output.exists()
    data = json.loads(output.read_text())
    assert data.get("action_type") == "PRODUCT_GAP_CLASSIFICATION_READONLY"


def test_run_product_gap_classification_readonly_result_not_in_src(tmp_path):
    """run_product_gap_classification_readonly writes output ONLY to specified path (not src/)."""
    from tools.supervisor.product_action_guard import run_product_gap_classification_readonly
    output = tmp_path / "gap-result.json"
    result = run_product_gap_classification_readonly(output_path=output)
    # Output must be in tmp_path, not src/
    assert output.exists(), "Output should be written to specified path"
    result_path = result.get("result_path") or ""
    src_dir = str(_repo_root / "src")
    assert not str(result_path).startswith(src_dir), \
        f"Output path must not be under src/: {result_path}"


def test_local_deterministic_backend_supports_product_gap_classification():
    """LOCAL_DETERMINISTIC backend declares PRODUCT_GAP_CLASSIFICATION_READONLY support."""
    from tools.supervisor.backends.local_deterministic_backend import LocalDeterministicBackend
    backend = LocalDeterministicBackend()
    action = {"action_type": "PRODUCT_GAP_CLASSIFICATION_READONLY"}
    assert backend.can_execute(action)


def test_local_deterministic_executes_product_gap_classification(tmp_path):
    """LOCAL_DETERMINISTIC backend can execute PRODUCT_GAP_CLASSIFICATION_READONLY."""
    from tools.supervisor.backends.local_deterministic_backend import LocalDeterministicBackend
    backend = LocalDeterministicBackend()
    out = str(tmp_path / "result.json")
    action = {
        "action_id": "test-pgc-001",
        "action_type": "PRODUCT_GAP_CLASSIFICATION_READONLY",
        "result_path": out,
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "objective": "test",
    }
    result = backend.execute(action, allowed_write_roots=[str(tmp_path)])
    assert result.status == "SUCCESS"
    assert Path(out).exists()
