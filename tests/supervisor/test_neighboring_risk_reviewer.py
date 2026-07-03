"""TC-FG-006: Tests for the neighboring risk reviewer.

Verifies that review_neighboring_risks() correctly identifies:
- Weaker sibling test files
- Duplicate test function names across files
- Misleading assertions (constant-zero, empty-return patterns)
- Authorized exclusion suppressing entries from results
"""
import sys
import textwrap
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from neighboring_risk_reviewer import review_neighboring_risks


def _write_test(directory: Path, name: str, code: str) -> str:
    directory.mkdir(parents=True, exist_ok=True)
    f = directory / name
    f.write_text(textwrap.dedent(code))
    return str(f)


def test_finds_weaker_sibling(tmp_path):
    """Target has exact value assertions (level 3); neighbor has only isinstance() (level 2).
    Neighbor should appear in weaker_sibling_tests."""
    test_dir = tmp_path / "tests"

    target = _write_test(test_dir, "test_target_strong.py", """\
        def test_exact_value():
            result = compute()
            assert result == [0, 0, 0, 1]
    """)

    _write_test(test_dir, "test_neighbor_weak.py", """\
        def test_type_only():
            result = compute()
            assert isinstance(result, list)
    """)

    result = review_neighboring_risks(
        target_test_path=target,
        target_module="compute",
        test_dir=str(test_dir),
    )

    weak_siblings = result.get("weaker_sibling_tests", [])
    assert len(weak_siblings) > 0, (
        f"Expected weaker sibling tests, got: {result}"
    )
    # Each entry is a dict with "file" key
    weak_files = [w.get("file", "") for w in weak_siblings]
    assert any("test_neighbor_weak" in f for f in weak_files), (
        f"Expected test_neighbor_weak.py in weaker siblings, got: {weak_files}"
    )


def test_finds_duplicate_tests(tmp_path):
    """Same function name 'test_exact_value' in two files → duplicate_tests populated."""
    test_dir = tmp_path / "tests"

    target = _write_test(test_dir, "test_file_a.py", """\
        def test_exact_value():
            result = compute()
            assert result == [1, 2, 3]
    """)

    _write_test(test_dir, "test_file_b.py", """\
        def test_exact_value():
            result = compute()
            assert result == [4, 5, 6]
    """)

    result = review_neighboring_risks(
        target_test_path=target,
        target_module="compute",
        test_dir=str(test_dir),
    )

    duplicates = result.get("duplicate_tests", [])
    assert len(duplicates) > 0, (
        f"Expected duplicate test names, got: {result}"
    )
    # duplicate_tests entries are strings like "test_file_a.py::test_exact_value also in test_file_b.py"
    assert any("test_exact_value" in d for d in duplicates), (
        f"Expected 'test_exact_value' in duplicate_tests, got: {duplicates}"
    )


def test_misleading_evidence_detection(tmp_path):
    """assert result == [0, 0, 0, 0] passes constant-zero impl → in misleading_evidence."""
    test_dir = tmp_path / "tests"

    target = _write_test(test_dir, "test_misleading.py", """\
        def test_constant_zero_passthrough():
            result = compute_histogram()
            assert result == [0, 0, 0, 0]
    """)

    result = review_neighboring_risks(
        target_test_path=target,
        target_module="compute_histogram",
        test_dir=str(test_dir),
    )

    misleading = result.get("misleading_evidence", [])
    assert len(misleading) > 0, (
        f"Expected misleading evidence (constant-zero assertion), got: {result}"
    )
    # Each entry is a dict with "function" key
    misleading_fns = [m.get("function", "") if isinstance(m, dict) else str(m) for m in misleading]
    assert any("test_constant_zero_passthrough" in fn for fn in misleading_fns), (
        f"Expected test_constant_zero_passthrough in misleading, got: {misleading}"
    )


def test_authorized_exclusion_clears_must_fix(tmp_path):
    """Weak neighbor with authorized_exclusion by test_name → function excluded from weaker_siblings."""
    test_dir = tmp_path / "tests"

    target = _write_test(test_dir, "test_strong.py", """\
        def test_exact():
            result = compute()
            assert result == [1, 2, 3]
    """)

    _write_test(test_dir, "test_weak_excluded.py", """\
        def test_type_check():
            result = compute()
            assert isinstance(result, list)
    """)

    # Without exclusion: test_type_check appears in weaker_sibling_tests
    result_without = review_neighboring_risks(
        target_test_path=target,
        target_module="compute",
        test_dir=str(test_dir),
    )

    # With exclusion by test_name: test_type_check should NOT appear in weaker_sibling_tests
    exclusion = {
        "test_name": "test_type_check",
        "reason": "Auxiliary smoke check — behavioral coverage in test_strong.py",
        "authority": "TC-FG-006",
    }

    result_with = review_neighboring_risks(
        target_test_path=target,
        target_module="compute",
        test_dir=str(test_dir),
        authorized_exclusions=[exclusion],
    )

    # Without exclusion: the weak function should appear
    weak_without = result_without.get("weaker_sibling_tests", [])
    assert any("test_type_check" in w.get("name", "") for w in weak_without), (
        f"Without exclusion: test_type_check should appear in weaker_sibling_tests: {weak_without}"
    )

    # With exclusion: test_type_check should NOT appear in weaker_sibling_tests
    weak_with = result_with.get("weaker_sibling_tests", [])
    assert not any("test_type_check" in w.get("name", "") for w in weak_with), (
        f"With exclusion: test_type_check should NOT appear in weaker_sibling_tests: {weak_with}"
    )
