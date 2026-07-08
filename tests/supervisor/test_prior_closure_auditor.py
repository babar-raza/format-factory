"""TC-FG-008: Tests for prior_closure_auditor.

Verifies that audit_prior_closures() correctly:
1. Scans evidence declarations in .local/evidences/
2. Flags file-existence-only proof as AT_RISK
3. Leaves adequate (exact-assertion) proof as ADEQUATE
4. Respects max lookback_runs limit
"""
import json
import sys
import textwrap
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from prior_closure_auditor import audit_prior_closures


def _make_evidence_dir(base: Path, run_id: str, items: list, test_content: str = "") -> Path:
    """Write a minimal evidence declaration under base/run_id/."""
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write test file if content provided
    test_path = ""
    if test_content:
        test_file = run_dir / f"test_{run_id}.py"
        test_file.write_text(textwrap.dedent(test_content))
        test_path = str(test_file)
        # Update test paths in items
        for item in items:
            if item.get("item_type") in ("PRODUCT_TEST", "PRODUCT_SOURCE") and not item.get("tests_supporting"):
                item["tests_supporting"] = [test_path]

    decl = {
        "sprint_id": run_id,
        "run_id": run_id,
        "git_head_end": "deadbeef",
        "planned_work_items": items,
    }
    decl_path = run_dir / "evidence-declaration.json"
    decl_path.write_text(json.dumps(decl, indent=2))
    return run_dir


def test_scans_evidence_declarations():
    """At least 1 declaration found in .local/evidences/ (the PGM histogram sprint)."""
    evidence_dir = _REPO / ".local" / "evidences"
    if not evidence_dir.exists():
        import pytest
        pytest.skip(".local/evidences/ does not exist — cannot scan declarations")

    # Check that at least one evidence subdirectory with a declaration exists
    decl_files = list(evidence_dir.rglob("evidence-declaration.*"))
    if not decl_files:
        import pytest
        pytest.skip(".local/evidences/ exists but contains no declarations (CI environment)")

    results = audit_prior_closures(
        evidence_dir=str(evidence_dir),
        lookback_runs=20,
    )
    assert len(results) >= 1, f"Expected at least 1 declaration scanned, got: {results}"


def test_flags_file_existence_only_proof(tmp_path):
    """Item with only isinstance() assertions → proof_adequacy=AT_RISK."""
    _make_evidence_dir(
        tmp_path, "run-weak-001",
        items=[{
            "item_id": "WI-001",
            "item_type": "PRODUCT_TEST",
            "status": "completed",
            "tests_supporting": [],  # will be filled by _make_evidence_dir
        }],
        test_content="""\
            def test_type_only():
                result = compute()
                assert isinstance(result, list)
        """,
    )

    results = audit_prior_closures(
        evidence_dir=str(tmp_path),
        lookback_runs=5,
    )

    assert len(results) >= 1
    at_risk = [r for r in results if r.get("proof_adequacy") == "AT_RISK"]
    assert len(at_risk) >= 1, (
        f"Expected AT_RISK for isinstance-only test, got: {results}"
    )


def test_adequate_proof_not_flagged(tmp_path):
    """Item with exact value assertions → proof_adequacy=ADEQUATE."""
    _make_evidence_dir(
        tmp_path, "run-strong-001",
        items=[{
            "item_id": "WI-002",
            "item_type": "PRODUCT_TEST",
            "status": "completed",
            "tests_supporting": [],  # will be filled by _make_evidence_dir
        }],
        test_content="""\
            def test_exact_value():
                result = compute()
                assert result == [0, 0, 0, 1]

            def test_exact_value2():
                result = compute2()
                assert result == [1, 1, 1, 1]

            def test_exact_value3():
                result = compute3()
                assert result == [2, 2, 2, 2]

            def test_exact_value4():
                result = compute4()
                assert result == [3, 3, 3, 3]
        """,
    )

    results = audit_prior_closures(
        evidence_dir=str(tmp_path),
        lookback_runs=5,
    )

    assert len(results) >= 1
    adequate = [r for r in results if r.get("proof_adequacy") == "ADEQUATE"]
    assert len(adequate) >= 1, (
        f"Expected ADEQUATE for exact-value tests, got: {results}"
    )


def test_max_lookback_respected(tmp_path):
    """lookback_runs=2 → at most 2 results even if more declarations exist."""
    for i in range(5):
        _make_evidence_dir(
            tmp_path, f"run-multi-{i:03d}",
            items=[{
                "item_id": f"WI-{i}",
                "item_type": "GOVERNANCE_DOC",
                "status": "completed",
                "tests_supporting": [],
            }],
        )

    results = audit_prior_closures(
        evidence_dir=str(tmp_path),
        lookback_runs=2,
    )

    assert len(results) <= 2, (
        f"Expected at most 2 results with lookback_runs=2, got {len(results)}: {results}"
    )
