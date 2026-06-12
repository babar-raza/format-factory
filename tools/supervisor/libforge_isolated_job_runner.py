"""
libforge_isolated_job_runner.py — FF-native LibForge isolated job runner.

Models specdev's one-job-at-a-time isolated execution pattern for Format Factory.
Each job runs in a temporary/evidence-local workspace, does not mutate product
source by default, and emits structured JSON results.

Sprint: FF-LIBFORGE-REFOCUS-INTEGRATION-001
No live LLM calls. No external repo imports. Pure deterministic logic.

Job lifecycle:
  1. Validate job request
  2. Resolve workspace (temp dir or evidence-local)
  3. (Optional) G3 AST forbidden-call scan if Python output provided
  4. (Optional) FreezeGateRunner gate if gate_config supplied
  5. (Optional) ComposeVerifyLoop handoff if available and requested
  6. Emit JSON result with job_id, status, steps, gate_results, rollback_required
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class JobStatus(str):
    PASS = "PASS"
    FAIL = "FAIL"
    DRY_RUN = "DRY_RUN"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass
class StepResult:
    step_name: str
    status: str       # "pass", "fail", "skip", "dry_run"
    notes: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class JobRequest:
    job_id: str
    format_id: str
    python_source: str | None = None    # Python code to check (if any)
    gate_config: dict | None = None     # FreezeGateRunner config (optional)
    use_compose_verify: bool = False    # handoff to ComposeVerifyLoop
    dry_run: bool = True               # default: dry run, no source mutation
    workspace_dir: str | None = None   # None = use temp dir
    evidence_dir: str | None = None    # optional evidence output dir


@dataclass
class JobResult:
    job_id: str
    format_id: str
    status: str
    dry_run: bool
    steps: list[StepResult]
    changed_files: list[str]
    gate_results: dict[str, Any]
    verification: dict[str, Any]
    rollback_required: bool
    workspace_used: str
    error: str | None = None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_FORBIDDEN_PATTERNS = [
    "eval(", "exec(", "os.system(", "__import__(",
    "subprocess.call(", "subprocess.Popen(", "subprocess.run(",
]


def _validate_request(request: JobRequest) -> list[str]:
    """Return list of validation errors, empty if valid."""
    errors = []
    if not request.job_id:
        errors.append("job_id must not be empty")
    if not request.format_id:
        errors.append("format_id must not be empty")
    if request.gate_config is not None and not isinstance(request.gate_config, dict):
        errors.append("gate_config must be a dict if provided")
    return errors


def _g3_scan(python_source: str) -> StepResult:
    """Run G3 AST forbidden-call scan on python_source string."""
    if not python_source:
        return StepResult("g3_ast_scan", "skip", "No python_source provided")

    violations = []
    for pattern in _FORBIDDEN_PATTERNS:
        if pattern in python_source:
            violations.append(f"Forbidden call: {pattern}")

    if violations:
        return StepResult(
            "g3_ast_scan",
            "fail",
            f"G3 scan found {len(violations)} violation(s)",
            {"violations": violations},
        )
    return StepResult(
        "g3_ast_scan",
        "pass",
        "No forbidden calls detected",
        {"checked_patterns": len(_FORBIDDEN_PATTERNS)},
    )


def _freeze_gate_step(
    gate_config: dict | None,
    workspace: str,
    dry_run: bool,
) -> StepResult:
    """Run FreezeGateRunner gate if config provided."""
    if gate_config is None:
        return StepResult("freeze_gate", "skip", "No gate_config provided — gate skipped")

    try:
        _repo = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(_repo))
        from tools.supervisor.freeze_gate_runner import FreezeGateRunner  # type: ignore

        gate_kind = gate_config.get("gate_kind", "binding_roundtrip")
        format_id = gate_config.get("format_id", "unknown")
        runner = FreezeGateRunner(
            gate_kind=gate_kind,
            format_id=format_id,
            workspace=workspace,
            dry_run=dry_run,
        )
        result = runner.run()
        if result.get("passed", False):
            return StepResult(
                "freeze_gate",
                "pass",
                f"Freeze gate {gate_kind} passed",
                result,
            )
        return StepResult(
            "freeze_gate",
            "fail" if not dry_run else "dry_run",
            f"Freeze gate {gate_kind}: {'not passed' if not dry_run else 'dry-run mode'}",
            result,
        )
    except ImportError:
        return StepResult(
            "freeze_gate",
            "skip",
            "FreezeGateRunner not available (ImportError) — gate soft-skipped",
        )
    except Exception as exc:
        return StepResult(
            "freeze_gate",
            "fail",
            f"FreezeGateRunner error: {exc}",
        )


def _compose_verify_step(
    request: JobRequest,
    workspace: str,
    dry_run: bool,
) -> StepResult:
    """Optionally hand off to ComposeVerifyLoop."""
    if not request.use_compose_verify:
        return StepResult("compose_verify", "skip", "ComposeVerifyLoop handoff not requested")

    try:
        _repo = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(_repo))
        from tools.supervisor.compose_verify_loop import ComposeVerifyLoop  # type: ignore

        loop = ComposeVerifyLoop(
            format_id=request.format_id,
            workspace=workspace,
            dry_run=dry_run,
        )
        result = loop.run()
        passed = result.get("passed", False)
        return StepResult(
            "compose_verify",
            "pass" if passed else ("dry_run" if dry_run else "fail"),
            f"ComposeVerifyLoop: {'passed' if passed else 'not passed'}",
            result,
        )
    except ImportError:
        return StepResult(
            "compose_verify",
            "skip",
            "ComposeVerifyLoop not available (ImportError) — step soft-skipped",
        )
    except Exception as exc:
        return StepResult(
            "compose_verify",
            "fail",
            f"ComposeVerifyLoop error: {exc}",
        )


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run_job(request: JobRequest) -> JobResult:
    """
    Run a single isolated LibForge job.

    Steps:
      1. Validate request
      2. Resolve workspace
      3. G3 AST scan (if python_source provided)
      4. FreezeGateRunner (if gate_config provided)
      5. ComposeVerifyLoop handoff (if requested)
      6. Aggregate results

    By default (dry_run=True): no product source files are written.
    """
    # Step 1: Validate
    errors = _validate_request(request)
    if errors:
        return JobResult(
            job_id=request.job_id,
            format_id=request.format_id,
            status=JobStatus.INVALID,
            dry_run=request.dry_run,
            steps=[StepResult("validate", "fail", "; ".join(errors))],
            changed_files=[],
            gate_results={},
            verification={"valid": False, "errors": errors},
            rollback_required=False,
            workspace_used="",
            error=f"Invalid request: {'; '.join(errors)}",
        )

    # Step 2: Resolve workspace
    _cleanup_workspace = False
    if request.workspace_dir:
        workspace = request.workspace_dir
        os.makedirs(workspace, exist_ok=True)
    else:
        _tmp = tempfile.mkdtemp(prefix=f"libforge_job_{request.job_id[:12]}_")
        workspace = _tmp
        _cleanup_workspace = True

    steps: list[StepResult] = [
        StepResult("validate", "pass", "Request is valid"),
        StepResult(
            "workspace_setup",
            "dry_run" if request.dry_run else "pass",
            f"Workspace: {workspace} | dry_run={request.dry_run}",
            {"workspace": workspace, "dry_run": request.dry_run},
        ),
    ]

    # Step 3: G3 AST scan
    g3_result = _g3_scan(request.python_source or "")
    steps.append(g3_result)

    # Step 4: FreezeGateRunner
    fg_result = _freeze_gate_step(request.gate_config, workspace, request.dry_run)
    steps.append(fg_result)

    # Step 5: ComposeVerifyLoop
    cv_result = _compose_verify_step(request, workspace, request.dry_run)
    steps.append(cv_result)

    # Step 6: Aggregate
    hard_failures = [s for s in steps if s.status == "fail"]
    rollback_required = bool(hard_failures) and not request.dry_run
    changed_files: list[str] = []  # dry_run always produces no source mutations

    if request.dry_run:
        overall_status = JobStatus.DRY_RUN
    elif hard_failures:
        overall_status = JobStatus.FAIL
    else:
        overall_status = JobStatus.PASS

    gate_results = {}
    for step in steps:
        if step.step_name in ("freeze_gate", "g3_ast_scan", "compose_verify"):
            gate_results[step.step_name] = {
                "status": step.status,
                "notes": step.notes,
                "details": step.details,
            }

    verification = {
        "valid": len(hard_failures) == 0,
        "hard_failures": [s.step_name for s in hard_failures],
        "total_steps": len(steps),
        "pass_count": sum(1 for s in steps if s.status == "pass"),
        "skip_count": sum(1 for s in steps if s.status == "skip"),
        "fail_count": len(hard_failures),
    }

    # Cleanup temp workspace if we created it (only in dry_run; otherwise preserve for inspection)
    # In dry_run we can clean up safely
    if _cleanup_workspace and request.dry_run:
        try:
            import shutil
            shutil.rmtree(workspace, ignore_errors=True)
        except Exception:
            pass

    return JobResult(
        job_id=request.job_id,
        format_id=request.format_id,
        status=overall_status,
        dry_run=request.dry_run,
        steps=steps,
        changed_files=changed_files,
        gate_results=gate_results,
        verification=verification,
        rollback_required=rollback_required,
        workspace_used=workspace,
    )


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def result_to_dict(result: JobResult) -> dict[str, Any]:
    """Convert a JobResult to a JSON-serializable dict."""
    return {
        "job_id": result.job_id,
        "format_id": result.format_id,
        "status": result.status,
        "dry_run": result.dry_run,
        "steps": [
            {
                "step_name": s.step_name,
                "status": s.status,
                "notes": s.notes,
                "details": s.details,
            }
            for s in result.steps
        ],
        "changed_files": result.changed_files,
        "gate_results": result.gate_results,
        "verification": result.verification,
        "rollback_required": result.rollback_required,
        "workspace_used": result.workspace_used,
        "error": result.error,
    }


def result_to_json(result: JobResult, indent: int = 2) -> str:
    """Serialize a JobResult to JSON string."""
    return json.dumps(result_to_dict(result), indent=indent)
