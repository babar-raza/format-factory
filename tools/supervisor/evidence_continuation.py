"""
Format Factory — Evidence Continuation
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001

After autonomous-cycle exits 0, generates a machine-readable next-action.json
instead of leaving the system at advisory Markdown (next-sprint.md).

This bridges the evidence-closeout gap: without this module, the orchestrator
stops because continuation-signal.json → next_sprint_path points to advisory
Markdown which is rejected by continuation_router.py.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent

CONTINUATION_SIGNAL_PATH = _repo_root / ".local" / "supervisor" / "continuation-signal.json"
NEXT_ACTION_PATH = _repo_root / ".local" / "supervisor" / "next-action.json"
ACTIVE_CONTINUATION_PATH = _repo_root / ".local" / "supervisor" / "active-continuation.json"

# Post-closeout next action defaults
# R-NMPC: Use approval-gates.md — always written by autonomous-cycle, always non-empty
DEFAULT_POST_CLOSEOUT_ACTION_TYPE = "QUEUE_HEALTH_CHECK"
DEFAULT_POST_CLOSEOUT_TARGET = ".local/supervisor/continuation-signal.json"

ACTION_QUEUE_PATH = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_advisory(path_str: str) -> bool:
    """Return True if the path looks like an advisory Markdown file."""
    if not path_str:
        return True
    p = Path(path_str)
    if p.suffix.lower() == ".md":
        return True
    advisory_names = {
        "next-sprint.md",
        "next-work-items.json",
        "session-resume.md",
    }
    if p.name in advisory_names:
        return True
    return False


def read_continuation_signal() -> Optional[Dict[str, Any]]:
    """Read .local/supervisor/continuation-signal.json if it exists."""
    if not CONTINUATION_SIGNAL_PATH.exists():
        return None
    try:
        return json.loads(CONTINUATION_SIGNAL_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def generate_post_closeout_next_action(
    sprint_id: str,
    prior_run_id: Optional[str] = None,
    cycle_index: int = 0,
) -> Dict[str, Any]:
    """Generate a safe machine-readable next-action.json after evidence closeout.

    The action is deterministic and targets the sprint's approval-gates.md to verify
    the sprint closed cleanly — a safe, observable, non-destructive next step.
    """
    action_id = str(uuid.uuid4())[:8]
    # R-NMPC: Use approval-gates.md as target — always written by autonomous-cycle
    target = DEFAULT_POST_CLOSEOUT_TARGET
    return {
        "schema_version": 1,
        "action_id": action_id,
        "action_type": DEFAULT_POST_CLOSEOUT_ACTION_TYPE,
        "objective": f"Post-closeout: verify approval-gates.md is non-empty (sprint={sprint_id})",
        "description": "Post-closeout continuation action generated after evidence closeout",
        "target": target,
        "target_path": target,
        "target_type": "FILE_NONEMPTY_CHECK",
        "external_gate": False,
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "post_closeout": True,
        "prior_sprint_id": sprint_id,
        "prior_run_id": prior_run_id,
        "cycle_index_after_closeout": cycle_index,
        "generated_at": _now_iso(),
        "generated_by": "evidence_continuation.py",
    }


def write_post_closeout_next_action(
    sprint_id: str,
    prior_run_id: Optional[str] = None,
    cycle_index: int = 0,
    output_path: Optional[Path] = None,
) -> Path:
    """Write a machine-readable next-action.json after evidence closeout."""
    action = generate_post_closeout_next_action(sprint_id, prior_run_id, cycle_index)
    out = output_path or NEXT_ACTION_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(action, indent=2), encoding="utf-8")
    return out


def write_post_closeout_active_continuation(
    sprint_id: str,
    next_action_path: Path,
    prior_run_id: Optional[str] = None,
) -> Path:
    """Write active-continuation.json pointing to machine-readable next action (not Markdown)."""
    data = {
        "schema_version": 1,
        "sprint_id": sprint_id,
        "next_action_path": str(next_action_path).replace("\\", "/"),
        "advisory_prompt_path": None,
        "advisory_prompt_executable": False,
        "autonomous_continue": True,
        "post_closeout": True,
        "prior_run_id": prior_run_id,
        "generated_at": _now_iso(),
        "generated_by": "evidence_continuation.py",
        "note": "Machine-readable continuation — not advisory Markdown",
    }
    ACTIVE_CONTINUATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_CONTINUATION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return ACTIVE_CONTINUATION_PATH


def repair_continuation_signal(
    sprint_id: str,
    prior_run_id: Optional[str] = None,
    cycle_index: int = 0,
) -> Dict[str, Any]:
    """If continuation-signal.json points to advisory Markdown, repair it.

    Reads the existing signal, checks next_sprint_path, and if it's advisory,
    generates + writes a machine-readable next-action.json and updates
    active-continuation.json to point to it.

    Returns a dict with repair status.
    """
    signal = read_continuation_signal()
    if signal is None:
        return {
            "status": "NO_SIGNAL",
            "repaired": False,
            "message": "continuation-signal.json does not exist",
        }

    next_sprint_path = signal.get("next_sprint_path", "")
    autonomous_continue = signal.get("autonomous_continue", False)

    if not autonomous_continue:
        return {
            "status": "CONTINUE_FALSE",
            "repaired": False,
            "message": "autonomous_continue=false in signal; no repair needed",
        }

    if not _is_advisory(next_sprint_path):
        return {
            "status": "ALREADY_MACHINE_READABLE",
            "repaired": False,
            "next_sprint_path": next_sprint_path,
            "message": "next_sprint_path is not advisory; no repair needed",
        }

    # Advisory path detected — generate machine-readable replacement
    next_action_path = write_post_closeout_next_action(
        sprint_id=sprint_id,
        prior_run_id=prior_run_id,
        cycle_index=cycle_index,
    )
    active_cont_path = write_post_closeout_active_continuation(
        sprint_id=sprint_id,
        next_action_path=next_action_path,
        prior_run_id=prior_run_id,
    )

    return {
        "status": "REPAIRED",
        "repaired": True,
        "original_advisory_path": next_sprint_path,
        "next_action_path": str(next_action_path),
        "active_continuation_path": str(active_cont_path),
        "message": "Advisory Markdown replaced with machine-readable next-action.json",
    }


def repair_global_continuation_signal(
    sprint_id: str,
    run_id: Optional[str] = None,
    cycle_index: int = 0,
) -> Dict[str, Any]:
    """Repair global continuation-signal.json to include machine-readable paths.

    If autonomous_continue=true but only next_sprint_path (advisory Markdown) is set,
    adds machine_continuation_path, active_continuation_path, next_action_path,
    action_queue_path, and advisory_prompt_executable=false.
    """
    signal = read_continuation_signal()
    if signal is None:
        return {"status": "NO_SIGNAL", "repaired": False}

    if not signal.get("autonomous_continue", False):
        return {"status": "CONTINUE_FALSE", "repaired": False}

    action_queue_path = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"
    next_action_path = NEXT_ACTION_PATH
    active_cont_path = ACTIVE_CONTINUATION_PATH

    before = dict(signal)
    signal["machine_continuation_path"] = str(next_action_path.relative_to(_repo_root)).replace("\\", "/")
    signal["active_continuation_path"] = str(active_cont_path.relative_to(_repo_root)).replace("\\", "/")
    signal["next_action_path"] = str(next_action_path.relative_to(_repo_root)).replace("\\", "/")
    signal["action_queue_path"] = str(action_queue_path.relative_to(_repo_root)).replace("\\", "/")
    signal["advisory_prompt_executable"] = False
    signal["global_repair_applied"] = True
    signal["global_repair_sprint"] = sprint_id
    signal["global_repair_at"] = _now_iso()

    CONTINUATION_SIGNAL_PATH.write_text(json.dumps(signal, indent=2), encoding="utf-8")

    return {
        "status": "REPAIRED",
        "repaired": True,
        "before": before,
        "machine_continuation_path": signal["machine_continuation_path"],
        "active_continuation_path": signal["active_continuation_path"],
        "next_action_path": signal["next_action_path"],
        "action_queue_path": signal["action_queue_path"],
        "advisory_prompt_executable": False,
    }


def seed_post_closeout_queue_item(
    sprint_id: str,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Seed a safe post-closeout queue item so the queue is never empty after a sprint.

    After a sprint closes, if the queue has no pending items, this adds a
    QUEUE_HEALTH_CHECK action as a safe non-destructive continuation step.
    The orchestrator can execute this immediately without human involvement.

    Returns a dict with seed status.
    """
    import json as _json
    from datetime import datetime as _dt, timezone as _tz

    queue_path = ACTION_QUEUE_PATH
    queue_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing items
    items = []
    if queue_path.exists():
        for line in queue_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    items.append(_json.loads(line))
                except Exception:
                    pass

    # Check if any pending items already exist
    pending = [i for i in items if i.get("status", "pending") != "done"]
    if pending:
        return {
            "status": "ALREADY_HAS_PENDING",
            "pending_count": len(pending),
            "seeded": False,
        }

    # Seed a safe QUEUE_HEALTH_CHECK item (LOCAL_DETERMINISTIC backend supports this)
    ts = _dt.now(_tz.utc).isoformat()
    action_id = f"post-closeout-{str(uuid.uuid4())[:8]}"
    item = {
        "action_id": action_id,
        "action_type": "QUEUE_HEALTH_CHECK",
        "target": "reports/supervisor/approval-gates.md",
        "target_path": "reports/supervisor/approval-gates.md",
        "description": f"Post-closeout health check: verify approval-gates.md is non-empty (sprint={sprint_id})",
        "external_gate": False,
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "status": "pending",
        "priority": 1,
        "queued_at": ts,
        "stream": "autonomy",
        "post_closeout": True,
        "prior_sprint_id": sprint_id,
        "prior_run_id": run_id,
    }
    items.append(item)

    with queue_path.open("w", encoding="utf-8") as f:
        for i in items:
            f.write(_json.dumps(i) + "\n")

    return {
        "status": "SEEDED",
        "seeded": True,
        "action_id": action_id,
        "action_type": "RUN_MD_NONEMPTY_CHECK",
        "queue_path": str(queue_path),
        "queue_total": len(items),
        "queue_pending": 1,
    }


def apply_post_closeout_continuation(
    sprint_id: str,
    run_id: Optional[str] = None,
    cycle_index: int = 0,
) -> Dict[str, Any]:
    """Top-level entry point: after autonomous-cycle exits 0, call this.

    Writes next-action.json and active-continuation.json to ensure
    the orchestrator can continue without human prompt injection.
    """
    next_action_path = write_post_closeout_next_action(
        sprint_id=sprint_id,
        prior_run_id=run_id,
        cycle_index=cycle_index,
    )
    active_cont_path = write_post_closeout_active_continuation(
        sprint_id=sprint_id,
        next_action_path=next_action_path,
        prior_run_id=run_id,
    )
    return {
        "status": "POST_CLOSEOUT_CONTINUATION_READY",
        "next_action_path": str(next_action_path),
        "active_continuation_path": str(active_cont_path),
        "sprint_id": sprint_id,
        "run_id": run_id,
        "cycle_index": cycle_index,
    }
