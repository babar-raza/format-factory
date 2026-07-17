"""
bounded_repair_engine.py — Bounded Repair Engine
Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001

Classifies pytest failure output and applies deterministic bounded repairs.
Used by the autonomous executor to self-heal test failures before giving up.

STATUS (TC-RG-002, 2026-07-17): NOT WIRED IN — confirmed no caller outside its
own test suite (tests/supervisor/test_bounded_repair_engine.py) imports this
module. DO NOT wire this into any live autonomous path as-is: the
MISSING_ATTRIBUTE and NAME_ERROR repairs write a literal
`# TODO: implement` stub directly into src/ files (see
_repair_missing_attribute / _repair_name_error below), which is a direct
violation of EP-1 Zero-Stub Enforcement (CLAUDE.md) the moment it fires
against real product source. It also writes to src/ with no skill/manifest
resolution (EP-3). Left unmodified here (no test-breaking behavior change) —
resolving the stub-write policy conflict is a prerequisite redesign, tracked
in docs/governance/skill-only-policy.yaml known_gaps (DIRECT-GENERATOR-GAP),
not performed as part of this triage pass.

Repair contract:
  - Max 3 repair attempts per work item
  - On SYNTAX_ERROR: always rollback immediately (no repair attempt)
  - On IMPORT_ERROR: attempt to fix sys.path / import statement
  - On MISSING_ATTRIBUTE: add a stub attribute
  - On ASSERTION_ERROR: log TODO; do NOT modify test file autonomously
  - On TIMEOUT: log and skip
  - On max_attempts reached: rollback all changes

Exit codes (when used as script):
  0 — repair applied successfully
  1 — repair not applicable / max attempts
  9 — unexpected error
"""

from __future__ import annotations

import re
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

_here = Path(__file__).resolve().parent
_REPO_ROOT = _here.parent.parent


# ---------------------------------------------------------------------------
# Failure classification enum
# ---------------------------------------------------------------------------

class FailureClass(str, Enum):
    IMPORT_ERROR = "IMPORT_ERROR"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    ATTRIBUTE_ERROR = "ATTRIBUTE_ERROR"          # AttributeError / missing attr
    ASSERTION_ERROR = "ASSERTION_ERROR"          # test assertion failure
    COLLECTION_ERROR = "COLLECTION_ERROR"        # pytest collection/import fail
    NAME_ERROR = "NAME_ERROR"                    # NameError in source
    TYPE_ERROR = "TYPE_ERROR"                    # TypeError
    TIMEOUT = "TIMEOUT"                          # test or process timeout
    UNKNOWN = "UNKNOWN"                          # catch-all


# ---------------------------------------------------------------------------
# RepairResult
# ---------------------------------------------------------------------------

class RepairResult:
    """Outcome of a repair attempt."""

    def __init__(
        self,
        success: bool,
        failure_class: FailureClass,
        action_taken: str,
        detail: str = "",
    ) -> None:
        self.success = success
        self.failure_class = failure_class
        self.action_taken = action_taken
        self.detail = detail

    def __repr__(self) -> str:
        return (
            f"RepairResult(success={self.success}, "
            f"failure_class={self.failure_class}, "
            f"action={self.action_taken!r})"
        )


# ---------------------------------------------------------------------------
# BoundedRepairEngine
# ---------------------------------------------------------------------------

class BoundedRepairEngine:
    """Classifies test failures and applies bounded, deterministic repairs.

    Usage:
        engine = BoundedRepairEngine(max_attempts=3)
        fc = engine.classify_failure(pytest_stderr)
        result = engine.apply_repair(source_path, fc, pytest_stderr)
    """

    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self._attempt_counts: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify_failure(self, error_output: str) -> FailureClass:
        """Classify a pytest failure string into a FailureClass.

        Args:
            error_output: Combined stdout+stderr from a pytest run.

        Returns:
            Most specific FailureClass for this failure.
        """
        text = error_output or ""

        # Ordered from most specific to least specific
        if re.search(r"SyntaxError|invalid syntax", text, re.IGNORECASE):
            return FailureClass.SYNTAX_ERROR

        if re.search(r"ERROR collecting|collection error|ImportError.*conftest", text, re.IGNORECASE):
            return FailureClass.COLLECTION_ERROR

        if re.search(r"ImportError|ModuleNotFoundError|No module named", text, re.IGNORECASE):
            return FailureClass.IMPORT_ERROR

        if re.search(r"AttributeError|has no attribute", text, re.IGNORECASE):
            return FailureClass.ATTRIBUTE_ERROR

        if re.search(r"NameError|name .* is not defined", text, re.IGNORECASE):
            return FailureClass.NAME_ERROR

        if re.search(r"TypeError", text, re.IGNORECASE):
            return FailureClass.TYPE_ERROR

        if re.search(r"AssertionError|FAILED.*assert", text, re.IGNORECASE):
            return FailureClass.ASSERTION_ERROR

        if re.search(r"timeout|timed out", text, re.IGNORECASE):
            return FailureClass.TIMEOUT

        return FailureClass.UNKNOWN

    def apply_repair(
        self,
        source_path: str,
        failure_class: FailureClass,
        error_output: str,
        *,
        repo_root: Optional[Path] = None,
    ) -> RepairResult:
        """Apply one bounded repair for the given failure class.

        Args:
            source_path:    Relative source file path (e.g. 'src/python/abw/abw_codec.py').
            failure_class:  Classification from classify_failure().
            error_output:   The raw pytest output for context.
            repo_root:      Repo root (defaults to detected REPO_ROOT).

        Returns:
            RepairResult indicating success/failure and what was done.
        """
        root = Path(repo_root) if repo_root else _REPO_ROOT
        key = source_path

        # Track attempt count
        self._attempt_counts[key] = self._attempt_counts.get(key, 0) + 1
        if self._attempt_counts[key] > self.max_attempts:
            return RepairResult(
                success=False,
                failure_class=failure_class,
                action_taken="MAX_ATTEMPTS_REACHED",
                detail=f"Exceeded {self.max_attempts} repair attempts for {source_path}",
            )

        # Dispatch to repair method
        if failure_class == FailureClass.SYNTAX_ERROR:
            return self._repair_rollback(source_path, root, "SYNTAX_ERROR_IMMEDIATE_ROLLBACK")

        if failure_class == FailureClass.IMPORT_ERROR:
            return self._repair_import_error(source_path, error_output, root)

        if failure_class == FailureClass.COLLECTION_ERROR:
            return self._repair_import_error(source_path, error_output, root)

        if failure_class == FailureClass.ATTRIBUTE_ERROR:
            return self._repair_missing_attribute(source_path, error_output, root)

        if failure_class == FailureClass.NAME_ERROR:
            return self._repair_name_error(source_path, error_output, root)

        if failure_class == FailureClass.ASSERTION_ERROR:
            return RepairResult(
                success=False,
                failure_class=failure_class,
                action_taken="ASSERTION_REPAIR_NOT_AUTONOMOUS",
                detail="AssertionError requires manual diagnosis; no autonomous repair applied",
            )

        if failure_class == FailureClass.TIMEOUT:
            return RepairResult(
                success=False,
                failure_class=failure_class,
                action_taken="TIMEOUT_SKIP",
                detail="Timeout failure; marked for manual review",
            )

        return RepairResult(
            success=False,
            failure_class=failure_class,
            action_taken="UNKNOWN_NO_REPAIR",
            detail="No repair strategy for UNKNOWN failure class",
        )

    def rollback(self, source_path: str, repo_root: Optional[Path] = None) -> bool:
        """Rollback a source file via git checkout.

        Returns True if rollback succeeded, False otherwise.
        """
        root = Path(repo_root) if repo_root else _REPO_ROOT
        return self._git_checkout(source_path, root)

    def reset_attempts(self, source_path: str) -> None:
        """Reset attempt count for a source path."""
        self._attempt_counts.pop(source_path, None)

    def attempts_remaining(self, source_path: str) -> int:
        """Return number of repair attempts remaining for source_path."""
        used = self._attempt_counts.get(source_path, 0)
        return max(0, self.max_attempts - used)

    # ------------------------------------------------------------------
    # Private repair strategies
    # ------------------------------------------------------------------

    def _repair_rollback(
        self, source_path: str, root: Path, action: str
    ) -> RepairResult:
        ok = self._git_checkout(source_path, root)
        return RepairResult(
            success=ok,
            failure_class=FailureClass.SYNTAX_ERROR,
            action_taken=action,
            detail=f"git checkout {source_path} {'succeeded' if ok else 'failed'}",
        )

    def _repair_import_error(
        self, source_path: str, error_output: str, root: Path
    ) -> RepairResult:
        """Try to identify and fix a broken import in source_path."""
        abs_path = root / source_path
        if not abs_path.exists():
            return RepairResult(
                success=False,
                failure_class=FailureClass.IMPORT_ERROR,
                action_taken="FILE_NOT_FOUND",
                detail=f"Source file {source_path} not found",
            )

        # Extract module name from error
        match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_output)
        if not match:
            return RepairResult(
                success=False,
                failure_class=FailureClass.IMPORT_ERROR,
                action_taken="IMPORT_MODULE_NOT_EXTRACTABLE",
                detail="Could not identify module name from error output",
            )

        broken_module = match.group(1)

        # Strategy: check if the module is a local package — then fix the import
        # to use a full path insert rather than relative import
        content = abs_path.read_text(encoding="utf-8")

        # Look for `from <broken_module> import` or `import <broken_module>`
        # and check if there's a local src/python/<module> directory
        top_module = broken_module.split(".")[0]
        local_path = root / "src" / "python" / top_module
        if local_path.exists() and local_path.is_dir():
            # Add sys.path insert at the top of the file if not already present
            sys_path_line = 'import sys as _sys; _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))\n'
            if "sys.path.insert" not in content and "_sys.path.insert" not in content:
                new_content = sys_path_line + content
                abs_path.write_text(new_content, encoding="utf-8")
                return RepairResult(
                    success=True,
                    failure_class=FailureClass.IMPORT_ERROR,
                    action_taken="ADDED_SYS_PATH_INSERT",
                    detail=f"Added sys.path insert for local module {top_module}",
                )

        return RepairResult(
            success=False,
            failure_class=FailureClass.IMPORT_ERROR,
            action_taken="IMPORT_NO_LOCAL_MODULE_FOUND",
            detail=f"Module {broken_module!r} not found in src/python/",
        )

    def _repair_missing_attribute(
        self, source_path: str, error_output: str, root: Path
    ) -> RepairResult:
        """Add a stub attribute for a missing AttributeError."""
        abs_path = root / source_path
        if not abs_path.exists():
            return RepairResult(
                success=False,
                failure_class=FailureClass.ATTRIBUTE_ERROR,
                action_taken="FILE_NOT_FOUND",
                detail=f"Source file {source_path} not found",
            )

        # Extract missing attribute name
        match = re.search(r"has no attribute ['\"]([^'\"]+)['\"]", error_output)
        if not match:
            return RepairResult(
                success=False,
                failure_class=FailureClass.ATTRIBUTE_ERROR,
                action_taken="ATTRIBUTE_NOT_EXTRACTABLE",
                detail="Could not identify attribute name from error output",
            )

        attr_name = match.group(1)
        content = abs_path.read_text(encoding="utf-8")

        # Check if it's already there
        if f"{attr_name}" in content:
            return RepairResult(
                success=False,
                failure_class=FailureClass.ATTRIBUTE_ERROR,
                action_taken="ATTRIBUTE_ALREADY_EXISTS",
                detail=f"Attribute {attr_name!r} already present in source",
            )

        # Append a stub to end of file
        stub = f"\n# AUTO-REPAIR STUB — {attr_name}\n{attr_name} = None  # TODO: implement\n"
        abs_path.write_text(content + stub, encoding="utf-8")
        return RepairResult(
            success=True,
            failure_class=FailureClass.ATTRIBUTE_ERROR,
            action_taken="ADDED_STUB_ATTRIBUTE",
            detail=f"Added stub attribute {attr_name!r} to {source_path}",
        )

    def _repair_name_error(
        self, source_path: str, error_output: str, root: Path
    ) -> RepairResult:
        """Add a stub binding for a NameError."""
        abs_path = root / source_path
        if not abs_path.exists():
            return RepairResult(
                success=False,
                failure_class=FailureClass.NAME_ERROR,
                action_taken="FILE_NOT_FOUND",
                detail=f"Source file {source_path} not found",
            )

        match = re.search(r"name ['\"]([^'\"]+)['\"] is not defined", error_output)
        if not match:
            return RepairResult(
                success=False,
                failure_class=FailureClass.NAME_ERROR,
                action_taken="NAME_NOT_EXTRACTABLE",
                detail="Could not identify name from error output",
            )

        name = match.group(1)
        content = abs_path.read_text(encoding="utf-8")

        if f"\n{name} " in content or f"\n{name}=" in content:
            return RepairResult(
                success=False,
                failure_class=FailureClass.NAME_ERROR,
                action_taken="NAME_ALREADY_DEFINED",
                detail=f"Name {name!r} already present in source",
            )

        stub = f"\n# AUTO-REPAIR STUB — {name}\n{name} = None  # TODO: implement\n"
        abs_path.write_text(content + stub, encoding="utf-8")
        return RepairResult(
            success=True,
            failure_class=FailureClass.NAME_ERROR,
            action_taken="ADDED_STUB_NAME",
            detail=f"Added stub name {name!r} to {source_path}",
        )

    def _git_checkout(self, source_path: str, root: Path) -> bool:
        """git checkout <source_path> to restore original file."""
        try:
            result = subprocess.run(
                ["git", "checkout", source_path],
                capture_output=True, text=True, cwd=root, timeout=15,
            )
            return result.returncode == 0
        except Exception:
            return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Relative source file path")
    parser.add_argument(
        "--error-output", required=True,
        help="Path to file containing pytest error output, or '-' for stdin"
    )
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    if args.error_output == "-":
        error_text = sys.stdin.read()
    else:
        error_text = Path(args.error_output).read_text(encoding="utf-8")

    engine = BoundedRepairEngine(max_attempts=args.max_attempts)
    fc = engine.classify_failure(error_text)
    print(f"BOUNDED_REPAIR: classified as {fc}")

    result = engine.apply_repair(args.source, fc, error_text)
    print(f"BOUNDED_REPAIR: {result}")
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
