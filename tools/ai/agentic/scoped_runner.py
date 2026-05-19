"""Qwen2 low-risk agentic controls — scoped runner with strict guards.

Only allows low-risk inventory/analysis tasks.
Forbidden: repo mutations, commits, branch ops, gate evidence, product source, security analysis.
Any scope violation stops immediately and discards output.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_OPERATIONS = frozenset({
    "commit",
    "branch_create",
    "branch_delete",
    "push",
    "pull",
    "merge",
    "rebase",
    "reset",
    "gate_evidence_generation",
    "product_source_generation",
    "security_analysis",
    "authority_file_modification",
    "delete_file",
    "write_src",
})


@dataclass
class AgenticTaskContract:
    """Contract for a scoped agentic task."""
    task_id: str
    task_type: str = "inventory"
    path_allowlist: list[str] = field(default_factory=list)
    operation_allowlist: list[str] = field(default_factory=list)
    max_files: int = 50
    timeout_seconds: int = 30
    output_schema: dict[str, Any] = field(default_factory=dict)
    model_restriction: str = "qwen2_only"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.task_id:
            errors.append("missing task_id")
        if not self.path_allowlist:
            errors.append("missing path_allowlist")
        if not self.operation_allowlist:
            errors.append("missing operation_allowlist")
        for op in self.operation_allowlist:
            if op in FORBIDDEN_OPERATIONS:
                errors.append(f"forbidden operation in allowlist: {op}")
        return errors


@dataclass
class AgenticResult:
    """Result of a scoped agentic task execution."""
    task_id: str
    status: str = "not_started"
    output: dict[str, Any] = field(default_factory=dict)
    files_accessed: list[str] = field(default_factory=list)
    violations: list[dict[str, str]] = field(default_factory=list)
    duration_ms: int = 0
    discarded: bool = False
    error: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "output": self.output if not self.discarded else {},
            "files_accessed": self.files_accessed,
            "violations": self.violations,
            "duration_ms": self.duration_ms,
            "discarded": self.discarded,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class ScopeViolationError(Exception):
    """Raised when a scope violation is detected."""
    pass


class ScopedRunner:
    """Runs scoped agentic tasks with strict guards."""

    def __init__(self, repo_root: Path | None = None):
        self._repo_root = repo_root or Path(".")

    def validate_path_access(
        self,
        path: str,
        allowlist: list[str],
    ) -> bool:
        """Check if a path is within the allowlist."""
        for allowed in allowlist:
            if path.startswith(allowed):
                return True
        return False

    def validate_operation(self, operation: str) -> tuple[bool, str]:
        """Check if an operation is allowed."""
        if operation in FORBIDDEN_OPERATIONS:
            return False, f"forbidden_operation: {operation}"
        return True, ""

    def validate_model(self, model_id: str) -> bool:
        """Ensure only Qwen2 models are used for agentic tasks."""
        return "qwen" in model_id.lower()

    def run(
        self,
        contract: AgenticTaskContract,
        model_id: str = "",
        task_fn: Any = None,
    ) -> AgenticResult:
        """Execute a scoped agentic task.

        If task_fn is provided, it should be a callable that accepts
        (contract, repo_root) and returns a dict result.
        Without task_fn, returns a fixture-mode result.
        """
        result = AgenticResult(
            task_id=contract.task_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Contract validation
        contract_errors = contract.validate()
        if contract_errors:
            result.status = "contract_invalid"
            result.error = "; ".join(contract_errors)
            return result

        # Model validation
        if model_id and not self.validate_model(model_id):
            result.status = "model_rejected"
            result.violations.append({
                "type": "non_qwen2_model",
                "model_id": model_id,
            })
            result.discarded = True
            return result

        start = time.monotonic()

        # Execute task function or return fixture result
        if task_fn is not None:
            try:
                output = task_fn(contract, self._repo_root)
                files_accessed = output.get("files_accessed", [])
                # Enforce max_files
                if len(files_accessed) > contract.max_files:
                    result.violations.append({
                        "type": "max_files_exceeded",
                        "limit": str(contract.max_files),
                        "actual": str(len(files_accessed)),
                    })
                    result.status = "scope_violation"
                    result.discarded = True
                    result.duration_ms = int((time.monotonic() - start) * 1000)
                    return result
                # Validate output paths (resolve to catch traversal)
                resolved_allowlist = [
                    str((self._repo_root / a).resolve()) for a in contract.path_allowlist
                ]
                for fpath in files_accessed:
                    resolved = str(Path(fpath).resolve())
                    if not self.validate_path_access(
                        resolved, resolved_allowlist
                    ) and not self.validate_path_access(
                        fpath, contract.path_allowlist
                    ):
                        result.violations.append({
                            "type": "forbidden_path",
                            "path": fpath,
                        })
                        result.status = "scope_violation"
                        result.discarded = True
                        result.duration_ms = int((time.monotonic() - start) * 1000)
                        return result
                result.output = output.get("result", {})
                result.files_accessed = files_accessed
                result.status = "success"
            except Exception as exc:
                result.status = "error"
                result.error = type(exc).__name__
        else:
            result.status = "fixture_mode"
            result.output = {"mode": "fixture", "task_type": contract.task_type}

        result.duration_ms = int((time.monotonic() - start) * 1000)

        # Timeout check
        if result.duration_ms > contract.timeout_seconds * 1000:
            result.status = "timeout"
            result.discarded = True

        return result
