"""Tests for closure_challenger.py — 6 behavioral tests (TC-FG-004)."""
import sys
import json
import textwrap
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from closure_challenger import run_closure_challenge

_PGM_TEST = str(_REPO / "tests" / "python" / "pgm" / "test_r259_pgm_brightness_histogram.py")


def _write(tmp_path, name: str, code: str) -> str:
    f = tmp_path / name
    f.write_text(textwrap.dedent(code))
    return str(f)


def test_challenge_type_only_assertions_found_rework(tmp_path):
    """File with only isinstance() assertions → FOUND_REWORK."""
    p = _write(tmp_path, "test_weak.py", """\
        def test_type_only():
            result = compute()
            assert isinstance(result, list)
    """)
    item = {
        "item_id": "I-WEAK-001",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [p],
        "item_type": "PRODUCT_TEST",
    }
    result = run_closure_challenge(item, str(tmp_path), str(_REPO))
    assert result["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK", f"Expected FOUND_REWORK: {result}"
    assert len(result["new_findings"]) > 0


def test_challenge_exact_value_assertions_passed(tmp_path):
    """File with exact value assertions → PASSED."""
    p = _write(tmp_path, "test_strong.py", """\
        def test_exact1():
            result = compute()
            assert result == [0, 0, 0, 1]

        def test_exact2():
            r = compute2()
            assert r == [1, 1, 1, 1]
    """)
    item = {
        "item_id": "I-STRONG-001",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [p],
        "item_type": "PRODUCT_TEST",
    }
    result = run_closure_challenge(item, str(tmp_path), str(_REPO))
    assert result["verdict"] == "CLOSURE_CHALLENGE_PASSED", f"Expected PASSED: {result}"


def test_challenge_inferred_contract(tmp_path):
    """No explicit contract → infer default → challenge works correctly."""
    # Weak proof file — should fail with inferred PRODUCT_TEST contract (target=3)
    p = _write(tmp_path, "test_no_contract.py", """\
        def test_shape():
            result = compute()
            assert len(result) == 4
    """)
    item = {
        "item_id": "I-INFER-001",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [p],
        "item_type": "PRODUCT_TEST",
    }
    result = run_closure_challenge(item, str(tmp_path), str(_REPO), proof_contracts=None)
    # Inferred contract has proof_target=EXACT_BEHAVIOR_VERIFIED (3), len() is level 2 → FOUND_REWORK
    assert result["verdict"] == "CLOSURE_CHALLENGE_FOUND_REWORK"
    assert result["required_level"] == 3


def test_challenge_idempotency(tmp_path):
    """Running twice on same inputs produces identical verdict."""
    p = _write(tmp_path, "test_idem.py", """\
        def test_exact():
            result = compute()
            assert result == [1, 2, 3]
    """)
    item = {
        "item_id": "I-IDEM-001",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [p],
        "item_type": "PRODUCT_TEST",
    }
    r1 = run_closure_challenge(item, str(tmp_path), str(_REPO))
    r2 = run_closure_challenge(item, str(tmp_path), str(_REPO))
    assert r1["verdict"] == r2["verdict"], "Idempotency violated: verdicts differ"
    assert r1["assessed_level"] == r2["assessed_level"]


def test_challenge_writes_result_json(tmp_path):
    """Result JSON is written to evidence_root."""
    p = _write(tmp_path, "test_json_out.py", """\
        def test_exact():
            assert compute() == 42
    """)
    item = {
        "item_id": "I-JSON-001",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [p],
        "item_type": "PRODUCT_TEST",
    }
    run_closure_challenge(item, str(tmp_path), str(_REPO))
    result_file = tmp_path / "closure-challenge-I-JSON-001.json"
    assert result_file.exists(), "Result JSON not written to evidence_root"
    data = json.loads(result_file.read_text())
    assert data["item_id"] == "I-JSON-001"
    assert "verdict" in data


def test_challenge_pgm_histogram_passes_with_weak_tests_reported(tmp_path):
    """PGM histogram challenge: PASSED (strong tests present) + weak tests in output."""
    if not Path(_PGM_TEST).exists():
        import pytest
        pytest.skip("PGM histogram test file not found")
    item = {
        "item_id": "TEST-PGM-BRIGHTNESS-HIST-001",
        "supervisor_grade": "ACCEPTED_VERIFIED",
        "tests_supporting": [_PGM_TEST],
        "item_type": "PRODUCT_TEST",
    }
    result = run_closure_challenge(item, str(tmp_path), str(_REPO))
    # Strong behavioral tests exist (result==[0,0,0,1], result==[1,1,1,1]) → PASSED
    assert result["verdict"] == "CLOSURE_CHALLENGE_PASSED", (
        f"PGM histogram should PASS (has behavioral assertions), got: {result['verdict']}\n"
        f"findings: {result['new_findings']}"
    )
    # Weak tests must be identified even though they don't block
    weak_names = [t["name"] for t in result.get("weak_tests", [])]
    assert "test_return_type" in weak_names, f"test_return_type not in weak_tests: {weak_names}"
    assert "test_default_bins_is_4" in weak_names, f"test_default_bins_is_4 not in weak_tests: {weak_names}"
