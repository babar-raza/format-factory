"""
Format Factory — Orchestrator Lifetime Model
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001

Defines stop reason taxonomy, resume policy, and post-closeout continuation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent

STATE_DIR = _repo_root / ".local" / "supervisor"

# ── Stop reason codes ─────────────────────────────────────────────────────────

STOP_TRUE_EXTERNAL_GATE = "TRUE_EXTERNAL_GATE"
STOP_CREDENTIAL_REQUIRED = "CREDENTIAL_REQUIRED"
STOP_UNSAFE_WORKSPACE = "UNSAFE_WORKSPACE"
STOP_REPEATED_FAILURE = "REPEATED_FAILURE"
STOP_NO_SAFE_ACTION = "NO_SAFE_ACTION"
STOP_MAX_CYCLES_RESUMABLE = "MAX_CYCLES_REACHED_RESUMABLE"
STOP_WATCH_IDLE = "WATCH_IDLE"
STOP_USER_STOPPED = "USER_STOPPED"
STOP_EVIDENCE_PACKAGE_FAILED = "EVIDENCE_PACKAGE_FAILED"
STOP_ORCHESTRATOR_ERROR = "ORCHESTRATOR_ERROR"
STOP_LOCK_HELD = "ORCHESTRATOR_LOCK_HELD"
STOP_DRY_RUN = "DRY_RUN_COMPLETE"
STOP_ADVISORY_PROMPT = "ADVISORY_PROMPT_NOT_EXECUTABLE"
STOP_QUEUE_EMPTY = "QUEUE_EMPTY_NO_PENDING"

# Stops that are always resumable (safe, no external authority needed)
RESUMABLE_STOPS = {
    STOP_MAX_CYCLES_RESUMABLE,
    STOP_WATCH_IDLE,
    STOP_DRY_RUN,
    STOP_QUEUE_EMPTY,
    STOP_LOCK_HELD,
}

# Stops that require external authority (non-resumable by orchestrator alone)
EXTERNAL_AUTHORITY_STOPS = {
    STOP_TRUE_EXTERNAL_GATE,
    STOP_CREDENTIAL_REQUIRED,
    STOP_UNSAFE_WORKSPACE,
}

# Stops that need diagnosis before resume
DIAGNOSIS_STOPS = {
    STOP_REPEATED_FAILURE,
    STOP_ORCHESTRATOR_ERROR,
    STOP_EVIDENCE_PACKAGE_FAILED,
    STOP_NO_SAFE_ACTION,
    STOP_ADVISORY_PROMPT,
}

STOP_TAXONOMY = {
    STOP_TRUE_EXTERNAL_GATE: {
        "description": "A true external gate (git push, Gate 11 approval, publication) was reached.",
        "resumable": False,
        "requires": "Human operator action (commit, push, gate approval, publish)",
        "resume_after": "After operator completes external action, restart orchestrator.",
    },
    STOP_CREDENTIAL_REQUIRED: {
        "description": "A required credential (API key) is absent.",
        "resumable": False,
        "requires": "Human operator sets credential env var.",
        "resume_after": "After credential is set, run: python autonomous_orchestrator.py --resume",
    },
    STOP_UNSAFE_WORKSPACE: {
        "description": "Uncommitted changes outside owned paths detected.",
        "resumable": False,
        "requires": "Human operator reviews and resolves dirty state.",
        "resume_after": "Resolve conflicts, then restart orchestrator.",
    },
    STOP_REPEATED_FAILURE: {
        "description": "Too many consecutive action failures.",
        "resumable": True,
        "requires": "Investigate root cause; may need to clear queue or fix action.",
        "resume_after": "Fix root cause, then: python autonomous_orchestrator.py --resume",
    },
    STOP_NO_SAFE_ACTION: {
        "description": "No safe executable action available in queue or generator.",
        "resumable": True,
        "requires": "Add safe actions to queue or seed via action_queue.seed_autonomy_queue().",
        "resume_after": "Seed queue, then: python autonomous_orchestrator.py --resume",
    },
    STOP_MAX_CYCLES_RESUMABLE: {
        "description": "Reached max cycles limit. Resumable — stop is by design.",
        "resumable": True,
        "requires": "Nothing — stop is normal.",
        "resume_after": "python autonomous_orchestrator.py --resume --max-cycles N",
    },
    STOP_QUEUE_EMPTY: {
        "description": "Action queue has no pending items.",
        "resumable": True,
        "requires": "Seed queue or generate next actions.",
        "resume_after": "python autonomous_orchestrator.py --resume",
    },
    STOP_DRY_RUN: {
        "description": "Dry run completed successfully.",
        "resumable": True,
        "requires": "Nothing — run without --dry-run to execute.",
        "resume_after": "python autonomous_orchestrator.py --max-cycles N",
    },
    STOP_USER_STOPPED: {
        "description": "User stopped the process (Ctrl+C or kill).",
        "resumable": True,
        "requires": "Nothing — user decides when to restart.",
        "resume_after": "python autonomous_orchestrator.py --resume",
    },
    STOP_EVIDENCE_PACKAGE_FAILED: {
        "description": "Evidence package build failed (missing artifacts or ZIP error).",
        "resumable": True,
        "requires": "Fix missing evidence artifacts.",
        "resume_after": "Fix artifacts, then re-run autonomous-cycle + orchestrator.",
    },
    STOP_ORCHESTRATOR_ERROR: {
        "description": "Unexpected orchestrator error.",
        "resumable": True,
        "requires": "Read logs and fix root cause.",
        "resume_after": "Fix error, then: python autonomous_orchestrator.py --resume",
    },
    STOP_ADVISORY_PROMPT: {
        "description": "Next action path pointed to advisory Markdown — not executable.",
        "resumable": True,
        "requires": "Seed queue with executable next-action.json.",
        "resume_after": "python autonomous_orchestrator.py --resume",
    },
    STOP_LOCK_HELD: {
        "description": "Another orchestrator instance holds the lock.",
        "resumable": True,
        "requires": "Wait for other instance to finish or clear stale lock.",
        "resume_after": "python autonomous_orchestrator.py --resume",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_resumable(stop_code: str) -> bool:
    entry = STOP_TAXONOMY.get(stop_code, {})
    return entry.get("resumable", False) or stop_code in RESUMABLE_STOPS


def get_resume_command(
    stop_code: str,
    max_cycles: int = 10,
    backend: str = "local",
    seed_action: Optional[str] = None,
) -> str:
    """Return the PowerShell command to resume the orchestrator."""
    base = (
        f"$env:CLAUDECODE=''; "
        f"cd 'C:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory'; "
        f".local\\venv\\Scripts\\python tools\\supervisor\\autonomous_orchestrator.py "
        f"--resume --max-cycles {max_cycles} --backend {backend}"
    )
    if seed_action:
        base += f" --seed-action \"{seed_action}\""
    return base


def write_lifetime_stop(
    run_id: str,
    stop_code: str,
    detail: str = "",
    cycle_index: int = 0,
    next_action_path: Optional[str] = None,
) -> None:
    """Write stop-reason.json with taxonomy and resume instructions."""
    entry = STOP_TAXONOMY.get(stop_code, {"resumable": False, "requires": "Unknown", "resume_after": "Investigate"})
    resumable = is_resumable(stop_code)
    data = {
        "schema_version": 1,
        "orchestrator_run_id": run_id,
        "stop_code": stop_code,
        "description": entry.get("description", stop_code),
        "detail": detail,
        "cycle_index": cycle_index,
        "resumable": resumable,
        "requires_external_authority": stop_code in EXTERNAL_AUTHORITY_STOPS,
        "requires": entry.get("requires", ""),
        "resume_command": get_resume_command(stop_code) if resumable else "",
        "next_action_path": next_action_path,
        "stopped_at": _now_iso(),
    }
    p = STATE_DIR / "stop-reason.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_post_closeout_state(
    sprint_id: str,
    next_action_path: Optional[str] = None,
    stop_code: Optional[str] = None,
) -> None:
    """After evidence closeout, write machine-readable next state (not Markdown advisory)."""
    if stop_code and stop_code in EXTERNAL_AUTHORITY_STOPS:
        # External authority required — write stop, not continuation
        data = {
            "post_closeout": True,
            "sprint_id": sprint_id,
            "next_action": None,
            "stop_code": stop_code,
            "stop_description": STOP_TAXONOMY.get(stop_code, {}).get("description", ""),
            "autonomous_continue": False,
            "generated_at": _now_iso(),
        }
    else:
        # Resumable — write next action path
        data = {
            "post_closeout": True,
            "sprint_id": sprint_id,
            "next_action": next_action_path,
            "stop_code": stop_code or STOP_MAX_CYCLES_RESUMABLE,
            "autonomous_continue": bool(next_action_path),
            "resume_command": get_resume_command(stop_code or STOP_MAX_CYCLES_RESUMABLE),
            "generated_at": _now_iso(),
        }
    p = _repo_root / "reports" / "autonomous-system-acceptance" / "evidence-continuation" / "post-closeout-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
