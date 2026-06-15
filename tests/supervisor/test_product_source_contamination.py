"""Test that product source files are free from test scaffolding contamination.

Prevents recurrence of _dummy_sal_test() and similar placeholders in src/.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
_SRC_ROOT = _REPO / "src" / "python"

# Patterns that must never appear in product source
_FORBIDDEN_FUNCTION_PATTERNS = [
    re.compile(r"\b_dummy_sal_test\b"),
    re.compile(r"\b_dummy_test\b"),
    re.compile(r"\b_placeholder_fn\b"),
    re.compile(r"\b_todo_implement\b"),
    re.compile(r"def _dummy_"),
    re.compile(r"def _placeholder_"),
]


def _collect_python_product_files() -> list[Path]:
    """Return all .py files under src/python/."""
    return list(_SRC_ROOT.rglob("*.py"))


def test_no_dummy_sal_test_in_product_source():
    """Ensure _dummy_sal_test() does not appear in any product source file."""
    pattern = re.compile(r"_dummy_sal_test")
    violations: list[str] = []
    for path in _collect_python_product_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            occurrences = text.count("_dummy_sal_test")
            violations.append(f"{path.relative_to(_REPO)} ({occurrences} occurrences)")
    assert not violations, (
        f"Product source files contain forbidden _dummy_sal_test(): {violations}"
    )


def test_no_dummy_functions_in_product_source():
    """Ensure no forbidden dummy/placeholder function definitions appear in product source."""
    violations: list[str] = []
    for path in _collect_python_product_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for pat in _FORBIDDEN_FUNCTION_PATTERNS:
            if pat.search(text):
                violations.append(f"{path.relative_to(_REPO)}: matched {pat.pattern!r}")
    assert not violations, (
        f"Product source contains forbidden placeholder functions: {violations}"
    )


def test_product_source_files_compile():
    """Ensure all product source .py files are syntactically valid Python."""
    errors: list[str] = []
    for path in _collect_python_product_files():
        try:
            ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(_REPO)}: {exc}")
    assert not errors, f"Product source syntax errors: {errors}"


def test_zst_codec_no_contamination():
    """Specific guard: zst_codec.py must not contain _dummy_sal_test."""
    zst_path = _SRC_ROOT / "zst" / "zst_codec.py"
    assert zst_path.exists(), "zst_codec.py not found"
    text = zst_path.read_text(encoding="utf-8")
    assert "_dummy_sal_test" not in text, (
        "zst_codec.py still contains _dummy_sal_test() contamination"
    )


def test_zst_file_info_function_exists():
    """Verify zst_file_info() is still present and callable after contamination removal."""
    import sys
    sys.path.insert(0, str(_REPO / "src" / "python"))
    from zst.zst_codec import zst_file_info
    assert callable(zst_file_info), "zst_file_info() must be callable"
