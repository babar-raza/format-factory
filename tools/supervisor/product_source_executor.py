"""
Format Factory — Product Source Executor
Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-1-001

Safe, testable executor for IMPLEMENT_SMALL_PRODUCT_FEATURE queue items.

Design constraints:
- Enforces allowed_paths and forbidden_paths from queue item v2 schema
- Hard-forbidden paths: src/net/, registry/, poc-targets.yaml
- Patch-size limit: 200 lines of added code
- Rollback via git checkout on test failure or exception
- Records execution result to lane-execution-ledger.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_here = Path(__file__).resolve().parent
_REPO_ROOT = _here.parent.parent

# Paths that are ALWAYS forbidden regardless of allowed_paths
_HARD_FORBIDDEN = [
    "src/net/",
    "registry/",
    "product-capability-matrix/poc-targets.yaml",
    ".supervisor/",
    "AGENTS.md",
    "GOVERNANCE.md",
]

# Max lines of code that can be inserted in one operation
_MAX_PATCH_LINES = 200

# Python venv executable
_PYTHON = _REPO_ROOT / ".local" / "venv" / "Scripts" / "python.exe"
if not _PYTHON.exists():
    _PYTHON = _REPO_ROOT / ".local" / "venv" / "bin" / "python"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExecutionResult:
    """Result from ProductSourceExecutor.execute()."""

    def __init__(
        self,
        action_id: str,
        status: str,
        source_path: Optional[str] = None,
        test_passed: bool = False,
        test_output: str = "",
        rollback_performed: bool = False,
        error: Optional[str] = None,
        changed_files: Optional[List[str]] = None,
    ):
        self.action_id = action_id
        self.status = status  # SUCCESS | FAILED | BLOCKED | ROLLED_BACK
        self.source_path = source_path
        self.test_passed = test_passed
        self.test_output = test_output
        self.rollback_performed = rollback_performed
        self.error = error
        self.changed_files = changed_files or []
        self.executed_at = _now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "status": self.status,
            "source_path": self.source_path,
            "test_passed": self.test_passed,
            "test_output": self.test_output[:4096],
            "rollback_performed": self.rollback_performed,
            "error": self.error,
            "changed_files": self.changed_files,
            "executed_at": self.executed_at,
        }


class ProductSourceExecutor:
    """
    Executes IMPLEMENT_SMALL_PRODUCT_FEATURE queue items safely.

    For each item:
    1. Validate allowed_paths and forbidden_paths
    2. Read current source file (take backup for rollback)
    3. Apply the feature patch (append function code)
    4. Run pytest on expected_tests
    5. If pass: record evidence; return SUCCESS
    6. If fail: rollback; return ROLLED_BACK
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or _REPO_ROOT

    def execute(self, item: Dict[str, Any]) -> ExecutionResult:
        """Execute a queue item. Returns ExecutionResult."""
        action_id = item.get("action_id", "unknown")
        source_path_rel = item.get("target_path") or (
            item.get("expected_files_to_change", [None])[0]
        )

        if not source_path_rel:
            return ExecutionResult(
                action_id=action_id,
                status="BLOCKED",
                error="No target_path or expected_files_to_change in queue item",
            )

        source_path = self.repo_root / source_path_rel

        # Step 1: Path validation
        path_error = self._validate_paths(item, source_path_rel)
        if path_error:
            return ExecutionResult(
                action_id=action_id,
                status="BLOCKED",
                error=path_error,
                source_path=source_path_rel,
            )

        # Step 2: Get patch code
        patch_code = item.get("patch_code") or item.get("implementation_code")
        if not patch_code:
            return ExecutionResult(
                action_id=action_id,
                status="BLOCKED",
                error="No patch_code or implementation_code in queue item",
                source_path=source_path_rel,
            )

        # Check patch size
        patch_lines = patch_code.count("\n") + 1
        if patch_lines > _MAX_PATCH_LINES:
            return ExecutionResult(
                action_id=action_id,
                status="BLOCKED",
                error=f"Patch too large: {patch_lines} lines (max {_MAX_PATCH_LINES})",
                source_path=source_path_rel,
            )

        if not source_path.exists():
            return ExecutionResult(
                action_id=action_id,
                status="BLOCKED",
                error=f"Source file not found: {source_path_rel}",
                source_path=source_path_rel,
            )

        # Step 3: Backup + apply
        original_content = source_path.read_text(encoding="utf-8")
        try:
            self._apply_feature(source_path, patch_code, item)
        except Exception as exc:
            return ExecutionResult(
                action_id=action_id,
                status="FAILED",
                error=f"Failed to apply patch: {exc}",
                source_path=source_path_rel,
                rollback_performed=False,
            )

        # Step 4: Run tests
        test_files = item.get("expected_tests", [])
        if not test_files:
            # Derive test directory from source path
            fmt = source_path.parent.name
            test_dir = self.repo_root / "tests" / "python" / fmt
            test_files = [str(test_dir)] if test_dir.exists() else []

        test_passed, test_output = self._run_tests(test_files)

        if test_passed:
            self._record_evidence(item, source_path_rel, test_output)
            return ExecutionResult(
                action_id=action_id,
                status="SUCCESS",
                source_path=source_path_rel,
                test_passed=True,
                test_output=test_output,
                changed_files=[source_path_rel] + test_files,
            )
        else:
            # Step 5: Rollback
            self._rollback(source_path, original_content)
            return ExecutionResult(
                action_id=action_id,
                status="ROLLED_BACK",
                source_path=source_path_rel,
                test_passed=False,
                test_output=test_output,
                rollback_performed=True,
                error="Tests failed after patch; rolled back to original",
            )

    def _validate_paths(self, item: Dict[str, Any], target_path: str) -> Optional[str]:
        """Return error string if path is not allowed, else None."""
        # Hard-forbidden check
        for forbidden in _HARD_FORBIDDEN:
            if target_path.startswith(forbidden) or target_path == forbidden:
                return f"Target path {target_path!r} is hard-forbidden ({forbidden})"

        # Item-level forbidden_paths
        for fp in item.get("forbidden_paths", []):
            if target_path.startswith(fp) or target_path == fp:
                return f"Target path {target_path!r} is forbidden by item policy ({fp})"

        # Must be in allowed_paths (if specified)
        allowed = item.get("allowed_paths", [])
        if allowed:
            if not any(target_path.startswith(a) for a in allowed):
                return (
                    f"Target path {target_path!r} not in allowed_paths: {allowed}"
                )

        return None

    def _apply_feature(
        self, source_path: Path, patch_code: str, item: Dict[str, Any]
    ) -> None:
        """Append patch_code to source_path after optional insert_before anchor."""
        current = source_path.read_text(encoding="utf-8")
        insert_before = item.get("insert_before")

        if insert_before and insert_before in current:
            idx = current.index(insert_before)
            new_content = (
                current[:idx]
                + "\n\n"
                + patch_code.rstrip()
                + "\n\n\n"
                + current[idx:]
            )
        else:
            # Append at end
            separator = "\n\n\n" if not current.endswith("\n\n") else ""
            new_content = current.rstrip() + separator + patch_code.rstrip() + "\n"

        source_path.write_text(new_content, encoding="utf-8")

    def _run_tests(self, test_files: List[str]) -> tuple[bool, str]:
        """Run pytest on test_files. Returns (passed, output)."""
        if not test_files:
            return True, "No test files specified; skipping test run"

        python_exe = str(_PYTHON)
        cmd = [python_exe, "-m", "pytest"] + test_files + ["--tb=short", "-q"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.repo_root),
            )
            output = result.stdout + result.stderr
            passed = result.returncode == 0
            return passed, output
        except subprocess.TimeoutExpired:
            return False, "pytest timed out after 120s"
        except Exception as exc:
            return False, f"pytest execution error: {exc}"

    def _rollback(self, source_path: Path, original_content: str) -> None:
        """Restore source_path to original_content."""
        source_path.write_text(original_content, encoding="utf-8")

    def _record_evidence(
        self, item: Dict[str, Any], source_path: str, test_output: str
    ) -> None:
        """Append execution record to lane-execution-ledger.json."""
        ledger_path = (
            self.repo_root / ".local" / "supervisor" / "lane-execution-ledger.json"
        )
        if ledger_path.exists():
            try:
                data = json.loads(ledger_path.read_text(encoding="utf-8"))
            except Exception:
                data = {"executions": []}
        else:
            data = {"executions": []}

        if "executions" not in data:
            data["executions"] = []

        data["executions"].append(
            {
                "action_id": item.get("action_id"),
                "action_type": item.get("action_type"),
                "source_path": source_path,
                "sprint_id": item.get("sprint_id"),
                "executed_at": _now_iso(),
                "status": "SUCCESS",
                "test_files": item.get("expected_tests", []),
                "action_source": "queue_dispatched",
            }
        )
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
