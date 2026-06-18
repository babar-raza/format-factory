"""
Format Factory — Continuation State
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

Machine-readable continuation state management.
Replaces advisory Markdown with executable state files.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from atomic_io import atomic_write_json

# Repo root detection
_here = Path(__file__).resolve().parent       # tools/supervisor/
_repo_root = _here.parent.parent              # repo root

STATE_DIR = _repo_root / ".local" / "supervisor"

# State file paths
ACTIVE_CONTINUATION_PATH = STATE_DIR / "active-continuation.json"
NEXT_ACTION_PATH = STATE_DIR / "next-action.json"
ORCHESTRATOR_STATE_PATH = STATE_DIR / "orchestrator-state.json"
ORCHESTRATOR_HEARTBEAT_PATH = STATE_DIR / "orchestrator-heartbeat.json"
STOP_REASON_PATH = STATE_DIR / "stop-reason.json"

SCHEMA_VERSION = 1

ADVISORY_MARKER = "advisory_only"

# Streams
STREAM_AUTONOMY = "autonomy"
STREAM_PRODUCT = "product"
STREAM_MAINSTREAM = "mainstream"

# Product/advisory next-sprint patterns — never executable
UNSAFE_ADVISORY_PATTERNS = [
    "reports/supervisor/next-sprint.md",
    "reports/supervisor/combined-next-worker-prompt.md",
    "review/next-work-items.json",
    "reports/supervisor/latest-next-worker-prompt.md",
]

FORBIDDEN_TASK_KEYWORDS = [
    "git commit", "git push", "gate 8", "gate 11",
    "npm publish", "nuget push", "pypi publish",
    "approval-blocked", "[blocked]",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    atomic_write_json(path, data)


# ── Active Continuation ───────────────────────────────────────────────────────

def load_active_continuation() -> Optional[Dict[str, Any]]:
    return _load_json(ACTIVE_CONTINUATION_PATH)


def save_active_continuation(data: Dict[str, Any]) -> None:
    data.setdefault("schema_version", SCHEMA_VERSION)
    data["updated_at"] = _now_iso()
    _save_json(ACTIVE_CONTINUATION_PATH, data)


def make_active_continuation(
    source_sprint_id: str,
    proof_level: str,
    next_action_path: str,
    autonomous_continue: bool = True,
    requires_external_host: bool = False,
    stop_reason: Optional[str] = None,
    last_evidence_package: Optional[str] = None,
    active_stream: str = STREAM_AUTONOMY,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "active_stream": active_stream,
        "source_sprint_id": source_sprint_id,
        "proof_level": proof_level,
        "next_action_path": next_action_path,
        "advisory_prompt_path": "reports/supervisor/next-sprint.md",
        "advisory_prompt_executable": False,
        "autonomous_continue": autonomous_continue,
        "requires_external_host": requires_external_host,
        "stop_reason": stop_reason,
        "last_evidence_package": last_evidence_package,
        "unsafe_advisory_prompts_quarantined": True,
        "session_id": session_id,
        "updated_at": _now_iso(),
    }


def is_advisory_prompt(path: str) -> bool:
    """Return True if path is an advisory Markdown prompt that must not be executed."""
    for pattern in UNSAFE_ADVISORY_PATTERNS:
        if pattern.lower() in path.lower():
            return True
    if path.lower().endswith(".md"):
        return True
    return False


def validate_active_continuation(data: Dict[str, Any]) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    if not isinstance(data, dict):
        return ["active-continuation is not a dict"]
    if data.get("autonomous_continue") is True:
        nap = data.get("next_action_path")
        if not nap:
            errors.append("autonomous_continue=true but next_action_path is missing")
        elif is_advisory_prompt(str(nap)):
            errors.append(
                f"autonomous_continue=true but next_action_path is advisory prompt: {nap}"
            )
        else:
            p = _repo_root / nap
            if not p.exists():
                errors.append(f"next_action_path does not exist: {nap}")
    if data.get("advisory_prompt_executable") is True:
        errors.append("advisory_prompt_executable must not be true")
    # CCI: validate session_id if present (TC-CCI-204)
    sid = data.get("session_id")
    if sid is not None and (not isinstance(sid, str) or not sid.strip()):
        errors.append("session_id is present but empty or not a string")
    return errors


# ── Orchestrator State ────────────────────────────────────────────────────────

def load_orchestrator_state() -> Optional[Dict[str, Any]]:
    return _load_json(ORCHESTRATOR_STATE_PATH)


def save_orchestrator_state(data: Dict[str, Any]) -> None:
    data.setdefault("schema_version", SCHEMA_VERSION)
    data["updated_at"] = _now_iso()
    _save_json(ORCHESTRATOR_STATE_PATH, data)


def make_orchestrator_state(
    run_id: str,
    status: str = "RUNNING",
    cycle_index: int = 0,
    last_action_id: Optional[str] = None,
    last_result_path: Optional[str] = None,
    next_action_path: str = str(NEXT_ACTION_PATH),
    stop_reason: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "orchestrator_run_id": run_id,
        "status": status,
        "cycle_index": cycle_index,
        "last_action_id": last_action_id,
        "last_result_path": last_result_path,
        "next_action_path": next_action_path,
        "last_heartbeat": _now_iso(),
        "stop_reason": stop_reason,
        "resume_supported": True,
        "session_id": session_id,
        "updated_at": _now_iso(),
    }


VALID_STATUSES = {"RUNNING", "IDLE", "STOPPED", "BLOCKED", "COMPLETED"}


def update_orchestrator_status(status: str, stop_reason: Optional[str] = None) -> None:
    state = load_orchestrator_state() or {}
    state["status"] = status
    if stop_reason:
        state["stop_reason"] = stop_reason
    save_orchestrator_state(state)


# ── Heartbeat ─────────────────────────────────────────────────────────────────

def write_heartbeat(run_id: str, cycle_index: int, status: str = "RUNNING") -> None:
    data = {
        "schema_version": SCHEMA_VERSION,
        "orchestrator_run_id": run_id,
        "status": status,
        "cycle_index": cycle_index,
        "heartbeat_at": _now_iso(),
    }
    _save_json(ORCHESTRATOR_HEARTBEAT_PATH, data)


# ── Stop Reason ───────────────────────────────────────────────────────────────

STOP_MAX_CYCLES = "MAX_CYCLES_REACHED"
STOP_EXTERNAL_GATE = "EXTERNAL_GATE_REQUIRED"
STOP_UNSAFE_WORKSPACE = "UNSAFE_WORKSPACE"
STOP_INVALID_NEXT_ACTION = "INVALID_NEXT_ACTION"
STOP_NO_SAFE_ACTION = "NO_SAFE_ACTION"
STOP_REPEATED_FAILURE = "REPEATED_FAILURE_THRESHOLD"
STOP_ADVISORY_PROMPT = "ADVISORY_PROMPT_NOT_EXECUTABLE"
STOP_LOCK_HELD = "ORCHESTRATOR_LOCK_HELD"
STOP_DRY_RUN = "DRY_RUN_COMPLETE"
STOP_SESSION_MISMATCH = "SESSION_MISMATCH"


def write_stop_reason(
    run_id: str,
    code: str,
    detail: str = "",
    cycle_index: int = 0,
    resumable: bool = True,
) -> None:
    data = {
        "schema_version": SCHEMA_VERSION,
        "orchestrator_run_id": run_id,
        "stop_code": code,
        "detail": detail,
        "cycle_index": cycle_index,
        "resumable": resumable and code not in {STOP_UNSAFE_WORKSPACE},
        "stopped_at": _now_iso(),
    }
    _save_json(STOP_REASON_PATH, data)


def load_stop_reason() -> Optional[Dict[str, Any]]:
    return _load_json(STOP_REASON_PATH)


# ── Next Action ───────────────────────────────────────────────────────────────

def load_next_action(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    p = Path(path) if path else NEXT_ACTION_PATH
    if not p.is_absolute():
        p = _repo_root / p
    return _load_json(p)


def save_next_action(action: Dict[str, Any], path: Optional[str] = None) -> None:
    p = Path(path) if path else NEXT_ACTION_PATH
    if not p.is_absolute():
        p = _repo_root / p
    _save_json(p, action)


def is_action_safe(action: Dict[str, Any]) -> tuple[bool, str]:
    """Return (safe, reason). Checks action_type and content for forbidden patterns."""
    action_type = action.get("action_type", "")
    forbidden_types = {
        "GIT_PUSH", "GIT_COMMIT", "GIT_RESET", "GIT_CLEAN", "GIT_STASH",
        "GATE_8_APPROVAL", "GATE_11_APPROVAL", "PACKAGE_PUBLISH",
        "MCP_ACTIVATE", "MUTATE_POC_TARGETS",
    }
    if action_type in forbidden_types:
        return False, f"Forbidden action_type: {action_type}"
    if action.get("external_gate") is True:
        return False, "external_gate=true requires human intervention"
    desc = str(action.get("description", "")).lower()
    for kw in FORBIDDEN_TASK_KEYWORDS:
        if kw.lower() in desc:
            return False, f"Forbidden keyword in description: '{kw}'"
    return True, ""
