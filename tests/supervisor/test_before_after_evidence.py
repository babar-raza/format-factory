"""TC-FG-005: Tests for the before/after evidence module.

Verifies that build_before_after_proof() correctly compares test assertion
strength before vs after a sprint, handles git failures gracefully, and
produces correct verdicts.
"""
import sys
import textwrap
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from before_after_evidence import build_before_after_proof


def _write_test(tmp_path: Path, name: str, code: str) -> str:
    f = tmp_path / name
    f.write_text(textwrap.dedent(code))
    return str(f)


def test_new_file_verdict(tmp_path):
    """baseline_git_sha='NO_BASELINE' → verdict='NEW_FILE' (always improvement)."""
    test_file = _write_test(tmp_path, "test_new.py", """\
        def test_exact():
            result = compute()
            assert result == [1, 2, 3]
    """)
    proof = build_before_after_proof(
        requirement_id="R-001",
        baseline_git_sha="NO_BASELINE",
        final_git_sha="abc123",
        test_paths=[test_file],
        evidence_root=str(tmp_path),
        repo_root=str(_REPO),
    )
    assert proof.verdict == "NEW_FILE", f"Expected NEW_FILE, got {proof.verdict}"
    assert proof.baseline_revision == "NO_BASELINE"
    assert proof.requirement_id == "R-001"


def test_unknown_baseline_treated_as_new_file(tmp_path):
    """baseline_git_sha='UNKNOWN' → verdict='NEW_FILE' (no git sha available)."""
    test_file = _write_test(tmp_path, "test_unknown.py", """\
        def test_exact():
            result = compute()
            assert result == [0, 1, 2]
    """)
    proof = build_before_after_proof(
        requirement_id="R-002",
        baseline_git_sha="UNKNOWN",
        final_git_sha="HEAD",
        test_paths=[test_file],
        evidence_root=str(tmp_path),
        repo_root=str(_REPO),
    )
    assert proof.verdict == "NEW_FILE", f"Expected NEW_FILE, got {proof.verdict}"


def test_git_show_failure_fallback(tmp_path):
    """git show failure (e.g. file not in baseline) → NO_BASELINE fallback, no crash."""
    test_file = _write_test(tmp_path, "test_git_fail.py", """\
        def test_exact():
            result = compute()
            assert result == [5, 6, 7]
    """)
    # Use a real-looking SHA that won't exist, causing git show to fail
    proof = build_before_after_proof(
        requirement_id="R-003",
        baseline_git_sha="deadbeef00000000000000000000000000000000",
        final_git_sha="HEAD",
        test_paths=[test_file],
        evidence_root=str(tmp_path),
        repo_root=str(_REPO),
    )
    # git show will fail (no such commit or file) — must not crash
    # verdict = NEW_FILE because baseline retrieval failed
    assert proof.verdict in ("NEW_FILE", "IMPROVEMENT", "UNCHANGED"), (
        f"Unexpected verdict: {proof.verdict}"
    )
    assert isinstance(proof.requirement_id, str)


def test_improvement_verdict(tmp_path):
    """Before: level 2 (type-only); After: level 3 (exact value) → IMPROVEMENT."""
    # The AFTER file is already written on disk (current state)
    after_file = _write_test(tmp_path, "test_after.py", """\
        def test_exact_value():
            result = compute()
            assert result == [0, 0, 0, 1]

        def test_exact_value2():
            result = compute2()
            assert result == [1, 1, 1, 1]
    """)

    # Simulate baseline (before) content — level 2 only
    before_content = textwrap.dedent("""\
        def test_type_only():
            result = compute()
            assert isinstance(result, list)
    """)

    # Patch _get_baseline_content to return the weak "before" content
    import before_after_evidence as bae
    original_fn = bae._get_baseline_content

    def _mock_get_baseline(git_sha, rel_path, repo_root):
        return before_content

    bae._get_baseline_content = _mock_get_baseline
    try:
        proof = build_before_after_proof(
            requirement_id="R-004",
            baseline_git_sha="aaa111",
            final_git_sha="bbb222",
            test_paths=[after_file],
            evidence_root=str(tmp_path),
            repo_root=str(tmp_path),
        )
    finally:
        bae._get_baseline_content = original_fn

    assert proof.verdict == "IMPROVEMENT", (
        f"Expected IMPROVEMENT (before=level2, after=level3), got {proof.verdict}"
    )


def test_regression_verdict(tmp_path):
    """Before: level 3 (exact); After: level 2 (type-only) → REGRESSION."""
    # The AFTER (current) file has only weak assertions
    after_file = _write_test(tmp_path, "test_regressed.py", """\
        def test_type_only():
            result = compute()
            assert isinstance(result, list)
    """)

    # Baseline was strong
    before_content = textwrap.dedent("""\
        def test_exact_value():
            result = compute()
            assert result == [0, 0, 0, 1]

        def test_exact_value2():
            result = compute2()
            assert result == [1, 1, 1, 1]
    """)

    import before_after_evidence as bae
    original_fn = bae._get_baseline_content

    def _mock_get_baseline(git_sha, rel_path, repo_root):
        return before_content

    bae._get_baseline_content = _mock_get_baseline
    try:
        proof = build_before_after_proof(
            requirement_id="R-005",
            baseline_git_sha="ccc333",
            final_git_sha="ddd444",
            test_paths=[after_file],
            evidence_root=str(tmp_path),
            repo_root=str(tmp_path),
        )
    finally:
        bae._get_baseline_content = original_fn

    assert proof.verdict == "REGRESSION", (
        f"Expected REGRESSION (before=level3, after=level2), got {proof.verdict}"
    )
