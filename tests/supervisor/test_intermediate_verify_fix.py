"""TC-FG-002b: Tests for the grade_intermediate_verify foundation fix.

Verifies that intermediate_verify_item() now uses AST assertion-strength
analysis instead of blanket string-search adequate=True.
"""
import sys
import textwrap
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from grade_intermediate_verify import intermediate_verify_item

_PGM_TEST = str(_REPO / "tests" / "python" / "pgm" / "test_r259_pgm_brightness_histogram.py")


def _write_test(tmp_path, name: str, code: str) -> str:
    f = tmp_path / name
    f.write_text(textwrap.dedent(code))
    return str(f)


def test_intermediate_verify_weak_suite_returns_false(tmp_path):
    """isinstance-only assertions → adequate=False, classification=WEAK_PROOF."""
    p = _write_test(tmp_path, "test_weak.py", """\
        def test_type_only():
            result = compute()
            assert isinstance(result, list)
    """)
    r = intermediate_verify_item([p])
    assert r["adequate"] is False, f"WEAK_PROOF should be adequate=False, got {r}"
    assert r.get("overall_classification") == "WEAK_PROOF"
    assert r.get("strong_ratio") == 0.0


def test_intermediate_verify_strong_suite_returns_true(tmp_path):
    """Exact value assertions → adequate=True, classification=STRONG_PROOF."""
    p = _write_test(tmp_path, "test_strong.py", """\
        def test_exact1():
            result = compute()
            assert result == [0, 0, 0, 1]

        def test_exact2():
            r = compute2()
            assert r == [1, 1, 1, 1]
    """)
    r = intermediate_verify_item([p])
    assert r["adequate"] is True, f"STRONG_PROOF should be adequate=True, got {r}"
    assert r.get("overall_classification") == "STRONG_PROOF"
    assert r.get("strong_ratio") == 1.0


def test_intermediate_verify_mixed_suite_partial_proof(tmp_path):
    """4 strong / 4 weak (ratio=0.5) → adequate=True, classification=STRONG_PROOF (at threshold)."""
    # 4 strong + 4 weak → strong_ratio=0.5, which equals STRONG_RATIO_THRESHOLD
    code = ""
    for i in range(4):
        code += f"def test_strong_{i}():\n    assert compute() == [0, 0, 0, {i}]\n\n"
    for i in range(4):
        code += f"def test_weak_{i}():\n    assert isinstance(compute(), list)\n\n"
    p = _write_test(tmp_path, "test_mixed.py", code)
    r = intermediate_verify_item([p])
    assert r["adequate"] is True
    assert r.get("strong_ratio") == 0.5
    # At threshold → STRONG_PROOF (boundary: >= threshold)
    assert r.get("overall_classification") == "STRONG_PROOF"


def test_intermediate_verify_shape_only_is_weak(tmp_path):
    """len()==N assertions → adequate=False (SHAPE counts as WEAK, not EXACT)."""
    p = _write_test(tmp_path, "test_shape.py", """\
        def test_shape_only():
            result = compute()
            assert len(result) == 4
            assert sum(result) == 10
    """)
    r = intermediate_verify_item([p])
    assert r["adequate"] is False
    assert r.get("overall_classification") == "WEAK_PROOF"


def test_intermediate_verify_nonexistent_file():
    """Non-existent file → adequate=False."""
    r = intermediate_verify_item(["/nonexistent/test_fake.py"])
    assert r["adequate"] is False


def test_intermediate_verify_pgm_histogram_is_adequate():
    """PGM histogram (4/8 strong=0.5) → adequate=True (at threshold)."""
    r = intermediate_verify_item([_PGM_TEST])
    assert r["adequate"] is True
    assert r.get("strong_ratio") == 0.5
    assert r.get("overall_classification") in ("STRONG_PROOF",)
    # Weak tests must be identified
    weak_names = [t["name"] for t in r.get("weak_tests", [])]
    assert "test_return_type" in weak_names
    assert "test_default_bins_is_4" in weak_names


def test_intermediate_verify_returns_intermediate_verified_true(tmp_path):
    """Result must always have intermediate_verified=True and source=intermediate_content_check."""
    p = _write_test(tmp_path, "test_any.py", """\
        def test_something():
            assert True
    """)
    r = intermediate_verify_item([p])
    assert r.get("intermediate_verified") is True
    assert r.get("source") == "intermediate_content_check"
    assert r.get("llm_used") is False
