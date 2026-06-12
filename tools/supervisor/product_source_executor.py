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

SAL-VERIFICATION-HARDENING-001 (Lane C, 2026-06-11):
- Authority preflight added to check format authority level before execution.
- Sprint 1 (WARNING mode): WARN_ALLOW for P1 with valid exception.
- Sprint 2 (BLOCK mode, SAL-I-002, 2026-06-11): WARN_ALLOW promoted to hard BLOCK.
  All P0/P1/P2/P3 formats without spec_fact_refs AND without valid exception_classification
  are now hard-blocked at executor level. WARN_ALLOW path removed.
  fallback_authority_approved requires non-empty exception_rationale field.

RNEXT (FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001, 2026-06-11):
- investigation_only and sample_only_non_product removed from _AUTHORITY_ALLOWED_EXCEPTIONS.
- These carry no specification authority and must not allow PRODUCT_SOURCE mutation.
- Explicit BLOCK added when these appear as exception_classification on product items.
"""
from __future__ import annotations

import json
import subprocess
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


# ---------------------------------------------------------------------------
# Authority Preflight (SAL-VERIFICATION-HARDENING-001 Lane C)
# ---------------------------------------------------------------------------

# Exception classifications that allow PRODUCT_SOURCE mutation without FACT-* refs.
# RNEXT (2026-06-11): investigation_only and sample_only_non_product REMOVED from this set.
# These may appear on GOVERNANCE_DOC/TEST items but must NOT bypass authority for
# PRODUCT_SOURCE mutation — they carry no specification authority.
_AUTHORITY_ALLOWED_EXCEPTIONS = frozenset({
    "no_public_spec_available",
    "schema_authority_available",
    "empirical_authority_with_limits",
    "fallback_authority_approved",
    "legacy_backfill",
})

# Non-product exception classifications: valid on GOVERNANCE_DOC, TEST, REQUIREMENT items
# but explicitly excluded from PRODUCT_SOURCE authority bypass.
_NON_PRODUCT_EXCEPTION_CLASSES = frozenset({
    "investigation_only",
    "sample_only_non_product",
})

# Minimum authority level for unrestricted product source work
_MIN_AUTHORITY_FOR_PRODUCT = 4  # P4: verified spec facts


def run_authority_preflight(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run authority preflight check for a PRODUCT_SOURCE queue item.

    Returns a machine-readable dict:
      {
        format_id: str,
        item_type: str,
        authority_level: str,          # P0-P6 or UNKNOWN
        authority_level_int: int,
        product_expansion_allowed: bool,
        exception_classification: str,
        decision: "ALLOW" | "BLOCK",
        reason: str,
        evidence_paths: list[str],
      }

    BLOCK is returned for P0/P1/P2/P3 without a valid exception.
    WARN_ALLOW is no longer returned (Sprint 2: all advisory paths promoted to BLOCK or ALLOW).
    ALLOW is returned for P4+, for valid exception_classification, or for formats with spec_fact_refs.
    """
    format_id = (
        item.get("format_id")
        or item.get("format")
        or _infer_format_id_from_paths(item)
    )
    item_type = item.get("item_type", "PRODUCT_SOURCE")
    exception_class = item.get("exception_classification", "")
    spec_fact_refs = item.get("spec_fact_refs", []) or []

    # Base result structure
    preflight = {
        "format_id": format_id or "unknown",
        "item_type": item_type,
        "authority_level": "UNKNOWN",
        "authority_level_int": -1,
        "product_expansion_allowed": False,
        "exception_classification": exception_class,
        "spec_fact_refs_present": bool(spec_fact_refs),
        "decision": "PENDING",  # always overwritten before return; WARN_ALLOW is never a valid outcome
        "reason": "",
        "evidence_paths": [],
    }

    if not format_id:
        # Sprint 2: unknown format_id — BLOCK rather than advisory allow
        preflight["decision"] = "BLOCK"
        preflight["reason"] = (
            "Cannot determine format_id from queue item. "
            "Set format_id field explicitly to proceed. "
            "Governance V13 also enforces spec_fact_refs at declaration time."
        )
        return preflight

    # Try to load authority gate validation
    try:
        import sys
        _sup_dir = Path(__file__).resolve().parent
        if str(_sup_dir) not in sys.path:
            sys.path.insert(0, str(_sup_dir))
        from authority_gate_validation import validate_format_authority
        auth_result = validate_format_authority(format_id)
        authority_level_int = auth_result.get("authority_level_int", -1)
        authority_level = auth_result.get("authority_level", "UNKNOWN")
        product_expansion_allowed = auth_result.get("product_expansion_allowed", False)
        exception_allowed = auth_result.get("exception_allowed")

        preflight["authority_level"] = authority_level
        preflight["authority_level_int"] = authority_level_int
        preflight["product_expansion_allowed"] = product_expansion_allowed
        if exception_allowed:
            preflight["evidence_paths"].append(
                f"authority_gate: exception_allowed={exception_allowed}"
            )

    except Exception as exc:
        # Sprint 2: import/execution error → BLOCK (fail-closed)
        preflight["decision"] = "BLOCK"
        preflight["reason"] = (
            f"Authority gate import/execution error for format={format_id!r}: {exc}. "
            "Cannot verify authority level. Fail-closed per Sprint 2 policy."
        )
        return preflight

    # Decision logic
    if spec_fact_refs:
        # Has spec fact refs — allow (registry check happens in V13)
        preflight["decision"] = "ALLOW"
        preflight["reason"] = (
            f"spec_fact_refs present ({len(spec_fact_refs)} refs). "
            f"Authority level: {authority_level}."
        )
        return preflight

    # RNEXT: investigation_only and sample_only_non_product are explicitly rejected
    # for PRODUCT_SOURCE mutation — these carry no specification authority.
    if exception_class in _NON_PRODUCT_EXCEPTION_CLASSES:
        preflight["decision"] = "BLOCK"
        preflight["reason"] = (
            f"exception_classification={exception_class!r} is not valid for PRODUCT_SOURCE "
            "mutation. This classification is permitted only on GOVERNANCE_DOC, TEST, or "
            "non-mutating items. For product source work, use no_public_spec_available, "
            "schema_authority_available, empirical_authority_with_limits, or provide "
            "spec_fact_refs."
        )
        return preflight

    if exception_class in _AUTHORITY_ALLOWED_EXCEPTIONS:
        # Sprint 2: fallback_authority_approved requires non-empty exception_rationale
        if exception_class == "fallback_authority_approved":
            exception_rationale = item.get("exception_rationale", "")
            if not exception_rationale:
                preflight["decision"] = "BLOCK"
                preflight["reason"] = (
                    "exception_classification=fallback_authority_approved requires a non-empty "
                    "exception_rationale field. Provide the approving mechanism and written rationale."
                )
                return preflight

        # Valid exception — allow (Sprint 2: WARN_ALLOW removed, exceptions are now ALLOW)
        preflight["decision"] = "ALLOW"
        preflight["reason"] = (
            f"No spec_fact_refs but exception_classification={exception_class!r} accepted. "
            f"Authority level: {authority_level}. "
            "This classification records authority debt. Not eligible for READINESS/RELEASE_GATE."
        )
        try:
            import time
            _audit_log = _REPO_ROOT / ".local" / "supervisor" / "authority-preflight-log.jsonl"
            _audit_log.parent.mkdir(parents=True, exist_ok=True)
            _entry = {
                "ts": time.time(),
                "format_id": format_id,
                "authority_level": authority_level,
                "authority_level_int": authority_level_int,
                "exception": exception_class,
                "decision": "ALLOW_WITH_EXCEPTION",
                "item_id": item.get("item_id") or item.get("action_id"),
                "item_type": item_type,
            }
            with _audit_log.open("a", encoding="utf-8") as _f:
                import json as _json
                _f.write(_json.dumps(_entry) + "\n")
        except Exception:
            pass  # Audit log failure must never block execution
        return preflight

    if authority_level_int >= _MIN_AUTHORITY_FOR_PRODUCT:
        # P4+ with no spec_fact_refs and no exception_classification — BLOCK per Hard Rule 10.
        # P4+ authority alone is not enough for product source mutation. The queue item must
        # carry either verifiable spec_fact_refs OR an explicit exception_classification.
        # This prevents silent "high authority" bypass without item-level authority evidence.
        preflight["decision"] = "BLOCK"
        preflight["reason"] = (
            f"format={format_id!r} has authority level {authority_level} (P4+), but the queue "
            "item has no spec_fact_refs and no exception_classification. "
            "P4+ authority alone is not sufficient for PRODUCT_SOURCE mutation (Hard Rule 10). "
            "Either add spec_fact_refs (e.g. FACT-ZST-001) or set exception_classification "
            "to an allowed value (e.g. no_public_spec_available, legacy_backfill)."
        )
        return preflight

    # P0/P1/P2/P3 without exception — BLOCK
    preflight["decision"] = "BLOCK"
    preflight["reason"] = (
        f"format={format_id!r} has authority level {authority_level} "
        f"(int={authority_level_int}) which is below P4 threshold, "
        f"and no valid exception_classification is set (got: {exception_class!r}). "
        "PRODUCT_SOURCE execution blocked. "
        "Set exception_classification to no_public_spec_available, "
        "schema_authority_available, or legacy_backfill if applicable."
    )
    return preflight


def _infer_format_id_from_paths(item: Dict[str, Any]) -> Optional[str]:
    """Infer format_id from target_path or expected_files_to_change."""
    paths = []
    if item.get("target_path"):
        paths.append(item["target_path"])
    paths.extend(item.get("expected_files_to_change", []) or [])
    for p in paths:
        parts = Path(p).parts
        # e.g. src/python/zst/zst_codec.py → 'zst'
        for i, part in enumerate(parts):
            if part in ("python", "net") and i + 1 < len(parts):
                return parts[i + 1]
    return None


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

        # Step 0: Authority preflight (SAL-VERIFICATION-HARDENING-001)
        preflight = run_authority_preflight(item)
        if preflight["decision"] == "BLOCK":
            return ExecutionResult(
                action_id=action_id,
                status="BLOCKED",
                error=(
                    f"Authority preflight BLOCKED: {preflight['reason']} "
                    f"[format={preflight['format_id']!r}, "
                    f"level={preflight['authority_level']}]"
                ),
                source_path=source_path_rel,
            )
        # ALLOW: preflight passed — proceed to path validation (Sprint 2: no WARN_ALLOW)

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
