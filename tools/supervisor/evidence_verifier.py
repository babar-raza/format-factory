"""Evidence verification utilities — independent check of declared test counts.

TC-OCRD-A5: Provides spot_check_test_count() to compare declared test counts
against actual test functions found in changed files via AST parsing.
"""
import ast
from pathlib import Path


def spot_check_test_count(
    repo_root: Path,
    changed_files: list[str],
    declared_passed: int,
    declared_failed: int,
) -> dict:
    """Count actual test functions in changed test files via AST.

    Compares the sum of (declared_passed + declared_failed) against the actual
    number of test_ functions found in changed test files.

    Args:
        repo_root: Repository root path.
        changed_files: List of relative paths to files changed in this sprint.
        declared_passed: Number of tests declared as passed.
        declared_failed: Number of tests declared as failed.

    Returns:
        Dict with keys:
          - actual_count: int — test_ functions found in changed test files
          - declared_count: int — declared_passed + declared_failed
          - ratio: float — actual_count / declared_count
          - warning: str | None — WARN message if ratio < 0.5 (and actual > 0)
    """
    total_declared = (declared_passed or 0) + (declared_failed or 0)
    if total_declared == 0:
        return {
            "actual_count": 0,
            "declared_count": 0,
            "ratio": 1.0,
            "warning": None,
        }

    test_files = [
        f for f in (changed_files or [])
        if f.endswith(".py") and "test_" in Path(f).name
    ]

    actual_count = 0
    for rel_path in test_files:
        abs_path = Path(repo_root) / rel_path
        if not abs_path.exists():
            continue
        try:
            tree = ast.parse(
                abs_path.read_text(encoding="utf-8", errors="replace")
            )
            actual_count += sum(
                1 for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("test_")
            )
        except SyntaxError:
            continue  # Broken files skipped gracefully

    ratio = actual_count / total_declared if total_declared > 0 else 1.0
    warning = None
    if actual_count > 0 and ratio < 0.5:
        warning = (
            f"WARN_TEST_COUNT_MISMATCH: declared {total_declared} tests "
            f"but found only {actual_count} test_ functions in changed files "
            f"(ratio: {ratio:.2f})"
        )

    return {
        "actual_count": actual_count,
        "declared_count": total_declared,
        "ratio": round(ratio, 3),
        "warning": warning,
    }
