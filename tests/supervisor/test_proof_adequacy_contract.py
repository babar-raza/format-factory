"""Tests for proof_adequacy_contract.py — 10 behavioral tests.

Validates:
- ProofLevel ordering
- AST assertion classification (TYPE, SHAPE, EXACT distinction)
- assess_proof_level on real and synthetic files
- infer_default_contract per item_type
- proof_sufficient_for_closure logic
- FaultSensitivity dataclass
"""
import sys
import textwrap
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from proof_adequacy_contract import (
    ProofLevel,
    ProofContract,
    FaultSensitivity,
    assess_proof_level,
    infer_default_contract,
    proof_sufficient_for_closure,
)

_PGM_TEST = _REPO / "tests" / "python" / "pgm" / "test_r259_pgm_brightness_histogram.py"


def test_proof_level_ordering():
    """ProofLevel ordering: EXACT > HAPPY_PATH > ARTIFACT."""
    assert ProofLevel.EXACT_BEHAVIOR_VERIFIED > ProofLevel.HAPPY_PATH_EXECUTED
    assert ProofLevel.HAPPY_PATH_EXECUTED > ProofLevel.ARTIFACT_PRESENT
    assert ProofLevel.ADVERSARIAL_AND_INTEGRATION_VERIFIED > ProofLevel.EXACT_BEHAVIOR_VERIFIED
    assert ProofLevel.NO_PROOF == 0


def test_assess_type_only_assertion(tmp_path):
    """isinstance(result, list) → level 2 (TYPE_ONLY)."""
    f = tmp_path / "test_type.py"
    f.write_text(textwrap.dedent("""\
        def test_type_only():
            result = [1, 2, 3]
            assert isinstance(result, list)
    """))
    result = assess_proof_level(str(f))
    assert result["level"] == 2, f"Expected level 2, got {result['level']}"
    assert result["strong_ratio"] == 0.0
    assert any(t["name"] == "test_type_only" for t in result["weak_tests"])


def test_assess_exact_value_assertion(tmp_path):
    """assert result == [0, 0, 0, 1] → level 3 (EXACT)."""
    f = tmp_path / "test_exact.py"
    f.write_text(textwrap.dedent("""\
        def test_exact_value():
            result = compute()
            assert result == [0, 0, 0, 1]
    """))
    result = assess_proof_level(str(f))
    assert result["level"] >= 3, f"Expected level >=3, got {result['level']}"
    assert result["strong_ratio"] == 1.0
    assert any(t["name"] == "test_exact_value" for t in result["strong_tests"])


def test_assess_shape_assertion_is_weak(tmp_path):
    """assert len(result) == 4 → level 2 (SHAPE, NOT EXACT)."""
    f = tmp_path / "test_shape.py"
    f.write_text(textwrap.dedent("""\
        def test_shape_only():
            result = compute()
            assert len(result) == 4
    """))
    result = assess_proof_level(str(f))
    # len(result)==4 must be SHAPE (level 2), not EXACT (level 3)
    assert result["level"] == 2, f"len(x)==4 should be level 2 (SHAPE), got {result['level']}"
    assert result["strong_ratio"] == 0.0
    assert any(t["name"] == "test_shape_only" for t in result["weak_tests"])


def test_assess_mixed_assertions(tmp_path):
    """File with both type-only and exact-value tests → overall level 3, weak_tests non-empty."""
    f = tmp_path / "test_mixed.py"
    f.write_text(textwrap.dedent("""\
        def test_type_check():
            result = compute()
            assert isinstance(result, list)

        def test_exact_check():
            result = compute()
            assert result == [1, 1, 1, 1]
    """))
    result = assess_proof_level(str(f))
    assert result["level"] >= 3
    assert result["strong_ratio"] == 0.5
    weak_names = [t["name"] for t in result["weak_tests"]]
    strong_names = [t["name"] for t in result["strong_tests"]]
    assert "test_type_check" in weak_names
    assert "test_exact_check" in strong_names


def test_infer_default_contract_product_test():
    """PRODUCT_TEST → proof_target=EXACT_BEHAVIOR_VERIFIED (3), non-empty plausible_faults."""
    item = {"item_id": "T-001", "item_type": "PRODUCT_TEST", "title": "test histogram"}
    contract = infer_default_contract(item)
    assert contract.proof_target == ProofLevel.EXACT_BEHAVIOR_VERIFIED
    assert len(contract.plausible_faults) > 0
    assert "constant_return" in contract.plausible_faults or "wrong_default" in contract.plausible_faults
    assert contract.risk == "HIGH"


def test_infer_default_contract_governance():
    """GOVERNANCE_DOC → proof_target=ARTIFACT_PRESENT (1)."""
    item = {"item_id": "G-001", "item_type": "GOVERNANCE_DOC", "title": "some doc"}
    contract = infer_default_contract(item)
    assert contract.proof_target == ProofLevel.ARTIFACT_PRESENT
    assert contract.risk == "LOW"


def test_proof_sufficient_below_target(tmp_path):
    """Assessed level 2 vs target 3 → (False, [gap message])."""
    f = tmp_path / "test_weak.py"
    f.write_text(textwrap.dedent("""\
        def test_weak():
            result = compute()
            assert isinstance(result, list)
    """))
    contract = ProofContract(
        requirement_id="R1", target="f", behavior_claim="returns list with correct values",
        risk="HIGH", proof_target=ProofLevel.EXACT_BEHAVIOR_VERIFIED
    )
    sufficient, gaps = proof_sufficient_for_closure(contract, [str(f)])
    assert not sufficient
    assert len(gaps) > 0
    assert any("level" in g.lower() or "ratio" in g.lower() for g in gaps)


def test_proof_sufficient_above_target(tmp_path):
    """Assessed level 3 vs target 3 → (True, [])."""
    f = tmp_path / "test_strong.py"
    f.write_text(textwrap.dedent("""\
        def test_exact1():
            result = compute()
            assert result == [0, 0, 0, 1]

        def test_exact2():
            result = compute_grad()
            assert result == [1, 1, 1, 1]
    """))
    contract = ProofContract(
        requirement_id="R2", target="f", behavior_claim="returns exact values",
        risk="MEDIUM", proof_target=ProofLevel.EXACT_BEHAVIOR_VERIFIED
    )
    sufficient, gaps = proof_sufficient_for_closure(contract, [str(f)])
    assert sufficient, f"Expected sufficient=True, gaps={gaps}"


def test_pgm_histogram_assessment():
    """
    assess_proof_level on the real PGM histogram test file must:
    - identify test_return_type and test_default_bins_is_4 as weak (level 2)
    - overall level >= 3 (exact assertions present)
    - strong_ratio == 0.5 (4 of 8)
    """
    if not _PGM_TEST.exists():
        import pytest
        pytest.skip("PGM histogram test file not found")

    result = assess_proof_level(str(_PGM_TEST))
    assert result["level"] >= 3, f"Expected level >=3, got {result['level']}"
    assert result["test_count"] == 8, f"Expected 8 tests, got {result['test_count']}"

    weak_names = [t["name"] for t in result["weak_tests"]]
    assert "test_return_type" in weak_names, f"test_return_type not in weak: {weak_names}"
    assert "test_default_bins_is_4" in weak_names, f"test_default_bins_is_4 not in weak: {weak_names}"

    strong_names = [t["name"] for t in result["strong_tests"]]
    assert "test_1x1_white_last_bin_gets_pixel" in strong_names, f"missing strong test, got {strong_names}"
    assert "test_2x2_gradient_uniform_distribution" in strong_names

    assert abs(result["strong_ratio"] - 0.5) < 0.01, f"Expected strong_ratio=0.5, got {result['strong_ratio']}"


def test_fault_sensitivity_record():
    """FaultSensitivity creation and field access."""
    fs = FaultSensitivity(
        requirement_id="R-001",
        plausible_fault="constant_zero_return",
        old_proof_verdict="PASS",
        new_proof_verdict="SURVIVES",
        detection_mechanism="assertion would pass constant-zero implementation",
        evidence="pilot-03",
    )
    assert fs.requirement_id == "R-001"
    assert fs.plausible_fault == "constant_zero_return"
    assert fs.new_proof_verdict == "SURVIVES"
    assert fs.old_proof_verdict == "PASS"
