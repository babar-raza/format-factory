"""
Format Factory — Next Action Runner
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

CLI entry point and programmatic API for dispatching next-action.json files.
The runner (not the host/parent) writes the result file.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repo root is importable (tools.supervisor.* imports)
_here = Path(__file__).resolve().parent       # tools/supervisor/
_repo_root = _here.parent.parent              # repo root
for p in [str(_repo_root), str(_here), str(_here / "backends")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from tools.supervisor.execution_backend import BackendResult, BackendType, ProofLevel
from tools.supervisor.next_action_schema import (
    NextActionValidationError,
    load_and_validate,
)
from tools.supervisor.backend_selector import select_backend, BackendSelectionTrace
from tools.supervisor.backends.local_deterministic_backend import LocalDeterministicBackend


def _build_default_backends():
    """Return the default backend list in priority order."""
    backends = []
    # Always include LOCAL_DETERMINISTIC
    backends.append(LocalDeterministicBackend())

    # Try to import ecosystem stubs (gracefully)
    try:
        from tools.supervisor.backends.superpowers_skill_backend import SuperpowersSkillBackend
        backends.insert(0, SuperpowersSkillBackend())
    except ImportError:
        pass

    try:
        from tools.supervisor.backends.mcp_superpowers_backend import McpSuperpowersBackend
        backends.append(McpSuperpowersBackend())
    except ImportError:
        pass

    try:
        from tools.supervisor.backends.llm_api_backend import LlmApiBackend
        backends.append(LlmApiBackend())
    except ImportError:
        pass

    try:
        from tools.supervisor.backends.task_master_backend import TaskMasterBackend
        backends.append(TaskMasterBackend())
    except ImportError:
        pass

    return backends


def run_action(
    action_path: str,
    allowed_write_roots: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Load, validate, and execute a next-action.json.
    Returns a result dict. The runner writes the result file — NOT the caller.
    """
    if allowed_write_roots is None:
        allowed_write_roots = ["reports/", ".local/"]

    # Step 1: Load and validate
    try:
        action = load_and_validate(action_path)
    except NextActionValidationError as e:
        return {
            "status": "INVALID_ACTION",
            "error": str(e),
            "action_path": action_path,
            "proof_level": None,
        }

    # Step 2: Check for advisory-only (no result_path means generated but not dispatchable)
    result_path = action.get("result_path")

    # Step 3: Select backend
    backends = _build_default_backends()
    backend, trace = select_backend(action, backends)

    if trace.blocked:
        result = {
            "status": "BLOCKED",
            "block_reason": trace.block_reason,
            "action_id": action.get("action_id"),
            "action_type": action.get("action_type"),
            "selection_trace": trace.to_dict(),
            "proof_level": None,
        }
        # Write block result if result_path given
        if result_path and not dry_run:
            rp = Path(result_path)
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    if backend is None:
        result = {
            "status": "NO_BACKEND",
            "action_id": action.get("action_id"),
            "action_type": action.get("action_type"),
            "selection_trace": trace.to_dict(),
            "proof_level": None,
        }
        if result_path and not dry_run:
            rp = Path(result_path)
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    if dry_run:
        return {
            "status": "DRY_RUN",
            "action_id": action.get("action_id"),
            "action_type": action.get("action_type"),
            "selected_backend": backend.backend_type.value,
            "selection_trace": trace.to_dict(),
            "proof_level": "H3 (would be assigned on real run)",
        }

    # Step 4: Execute (backend writes result_path — not the host)
    backend_result = backend.execute(action, allowed_write_roots)

    # Step 5: Build and return execution record
    execution_record = {
        "status": backend_result.status,
        "action_id": backend_result.action_id,
        "action_type": action.get("action_type"),
        "backend_used": backend_result.backend_used.value,
        "proof_level": backend_result.proof_level.value if backend_result.proof_level else None,
        "exit_code": backend_result.exit_code,
        "result_path": backend_result.result_path,
        "evidence_paths": backend_result.evidence_paths,
        "errors": backend_result.errors,
        "warnings": backend_result.warnings,
        "selection_trace": trace.to_dict(),
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }

    return execution_record


def main():
    parser = argparse.ArgumentParser(
        description="Format Factory Next Action Runner — dispatches next-action.json via backend selector"
    )
    parser.add_argument("--action", required=True, help="Path to next-action.json")
    parser.add_argument(
        "--allow-write",
        action="append",
        default=[],
        metavar="ROOT",
        help="Allowed write root (repeatable). Default: reports/ .local/",
    )
    parser.add_argument("--dry-run", action="store_true", help="Select backend but do not execute")
    parser.add_argument("--json-out", metavar="PATH", help="Write execution record to this path")
    args = parser.parse_args()

    roots = args.allow_write if args.allow_write else ["reports/", ".local/"]

    result = run_action(args.action, allowed_write_roots=roots, dry_run=args.dry_run)

    if args.json_out:
        rp = Path(args.json_out)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))

    # Exit code: 0=success, 3=blocked/invalid, 9=error
    status = result.get("status", "")
    if status in ("SUCCESS", "DRY_RUN"):
        sys.exit(0)
    elif status in ("BLOCKED", "INVALID_ACTION", "NO_BACKEND"):
        sys.exit(3)
    else:
        sys.exit(9)


if __name__ == "__main__":
    main()
