"""
Format Factory — Action Queue
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001
Extended: TC-FF6-EXECUTION-RECOVERY-001 (atomic claim + immutable attempt
history, C2 — reuses the file-lock + atomic_io primitives already proven
elsewhere in this package instead of a new parallel SQLite store; see
execution-recovery-directive.yaml stage_1_scope for the recorded scope
reduction and its rationale).

Durable JSONL queue for the autonomous orchestrator.
Replaces advisory next-sprint.md as execution source.

Queue file: .local/supervisor/action-queue.jsonl
Each line is a JSON action queue item.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from atomic_io import atomic_write_text
from tools.supervisor.forbidden_actions import TRUE_EXTERNAL_GATE_ACTION_TYPES

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent

QUEUE_PATH = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"
QUEUE_LOCK_PATH = _repo_root / ".local" / "supervisor" / "action-queue.lock"
ATTEMPTS_PATH = _repo_root / ".local" / "supervisor" / "action-queue-attempts.jsonl"

_LOCK_STALE_SECONDS = 60
_LOCK_POLL_SECONDS = 0.01
_LOCK_TIMEOUT_SECONDS = 30


class _QueueLock:
    """Cross-process mutual exclusion for the JSONL queue's read-modify-write
    critical section, using an exclusive-create lock file. Guarantees exactly
    one winner per contended dequeue/enqueue under concurrent processes."""

    def __init__(self, path: Optional[Path] = None, timeout: float = _LOCK_TIMEOUT_SECONDS):
        self._path = path or QUEUE_LOCK_PATH
        self._timeout = timeout
        self._fd: Optional[int] = None

    def __enter__(self) -> "_QueueLock":
        self._path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self._timeout
        while True:
            try:
                self._fd = os.open(str(self._path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, str(os.getpid()).encode("utf-8"))
                return self
            except FileExistsError:
                try:
                    age = time.time() - self._path.stat().st_mtime
                    if age > _LOCK_STALE_SECONDS:
                        self._path.unlink(missing_ok=True)
                        continue
                except OSError:
                    pass
                if time.monotonic() > deadline:
                    raise TimeoutError(f"could not acquire queue lock at {self._path} within {self._timeout}s")
                time.sleep(_LOCK_POLL_SECONDS)

    def __exit__(self, *_exc: Any) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self._path.unlink(missing_ok=True)

# Item statuses
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_FAILED = "failed"
STATUS_BLOCKED = "blocked"

# Streams
STREAM_AUTONOMY = "autonomy"
STREAM_PRODUCT = "product"
STREAM_EVIDENCE = "evidence"
STREAM_SETUP = "setup"

# Canonical set (tools/supervisor/forbidden_actions.py) — was previously a
# local copy that had drifted from backend_selector.py's (missing
# PYPI_PUBLISH/NUGET_PUBLISH), meaning a publish action could sit in the
# durable queue as "safe" until reaching backend selection.
FORBIDDEN_IN_QUEUE = TRUE_EXTERNAL_GATE_ACTION_TYPES


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_queue() -> List[Dict[str, Any]]:
    if not QUEUE_PATH.exists():
        return []
    items = []
    for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return items


def _save_queue(items: List[Dict[str, Any]]) -> None:
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        QUEUE_PATH,
        "\n".join(json.dumps(item) for item in items) + "\n",
    )


def _append_attempt_record(item: Dict[str, Any]) -> str:
    """Append an immutable attempt record for a dequeued item. Never rewrites
    or truncates prior attempts — this is an append-only history, distinct
    from the mutable queue-item status."""
    attempt_id = f"attempt-{uuid.uuid4().hex[:12]}"
    record = {
        "attempt_id": attempt_id,
        "action_id": item.get("action_id"),
        "action_type": item.get("action_type"),
        "task_id": item.get("task_id"),
        "sprint_id": item.get("sprint_id"),
        "started_at": _now_iso(),
    }
    ATTEMPTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ATTEMPTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return attempt_id


def make_queue_item(
    action_type: str,
    stream: str = STREAM_AUTONOMY,
    priority: int = 5,
    preferred_backend: str = "LOCAL_DETERMINISTIC",
    target: Optional[str] = None,
    result_path: Optional[str] = None,
    allowed_write_roots: Optional[List[str]] = None,
    external_gate: bool = False,
    sprint_id: Optional[str] = None,
    objective: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    action_id = f"q-{uuid.uuid4().hex[:8]}"
    item = {
        "action_id": action_id,
        "stream": stream,
        "priority": priority,
        "action_type": action_type,
        "preferred_backend": preferred_backend,
        "fallback_backends": [],
        "allowed_write_roots": allowed_write_roots or ["reports/autonomous-system-acceptance", ".local/supervisor"],
        "external_gate": external_gate,
        "status": STATUS_PENDING,
        "objective": objective or f"{action_type} via queue",
        "queued_at": _now_iso(),
        "started_at": None,
        "completed_at": None,
        "result_path": result_path,
        "error": None,
        "sprint_id": sprint_id,
    }
    if target:
        item["target"] = target
    item.update(kwargs)
    return item


def enqueue(item: Dict[str, Any]) -> str:
    """Add item to queue. Returns action_id. Raises ValueError for forbidden types."""
    if item.get("action_type") in FORBIDDEN_IN_QUEUE:
        raise ValueError(f"Forbidden action type in queue: {item['action_type']}")
    # Assign action_id if not present
    if "action_id" not in item:
        item = dict(item)
        item["action_id"] = str(uuid.uuid4())[:8]
    if "status" not in item:
        item["status"] = STATUS_PENDING
    if "queued_at" not in item:
        item["queued_at"] = _now_iso()
    if item.get("external_gate") and item.get("action_type") not in FORBIDDEN_IN_QUEUE:
        item["status"] = STATUS_BLOCKED  # External gate items are pre-blocked
    with _QueueLock():
        items = _load_queue()
        items.append(item)
        _save_queue(items)
    return item["action_id"]


def enqueue_front(item: Dict[str, Any]) -> str:
    """Insert item at front of queue (before all pending items). Returns action_id.
    Used by stream filter to re-queue rejected wrong-track items without silent loss.
    TC-P2-007: REQ-TRK-011 — prevents item loss on stream filter rejection.
    """
    if item.get("action_type") in FORBIDDEN_IN_QUEUE:
        raise ValueError(f"Forbidden action type in queue: {item['action_type']}")
    if "action_id" not in item:
        item = dict(item)
        item["action_id"] = str(uuid.uuid4())[:8]
    if "status" not in item:
        item["status"] = STATUS_PENDING
    if "queued_at" not in item:
        item["queued_at"] = _now_iso()
    with _QueueLock():
        items = _load_queue()
        items.insert(0, item)
        _save_queue(items)
    return item["action_id"]


def dequeue_next() -> Optional[Dict[str, Any]]:
    """Atomically claim the highest-priority pending item (PENDING -> RUNNING
    compare-and-set under _QueueLock, so concurrent callers never claim the
    same item twice) and append an immutable attempt record."""
    with _QueueLock():
        items = _load_queue()
        pending = [i for i in items if i.get("status") == STATUS_PENDING
                   and not i.get("external_gate", False)]
        if not pending:
            return None
        # Sort by priority (lower = higher priority) then queued_at
        pending.sort(key=lambda i: (i.get("priority", 5), i.get("queued_at", "")))
        chosen = pending[0]
        # Mark as running
        for item in items:
            if item.get("action_id") == chosen["action_id"]:
                item["status"] = STATUS_RUNNING
                item["started_at"] = _now_iso()
                chosen = item
                break
        _save_queue(items)
        attempt_id = _append_attempt_record(chosen)
    chosen = dict(chosen)
    chosen["attempt_id"] = attempt_id
    return chosen


def mark_done(action_id: str, result_path: Optional[str] = None) -> None:
    with _QueueLock():
        items = _load_queue()
        for item in items:
            if item.get("action_id") == action_id:
                item["status"] = STATUS_DONE
                item["completed_at"] = _now_iso()
                if result_path:
                    item["result_path"] = result_path
                break
        _save_queue(items)


def mark_failed(action_id: str, error: str) -> None:
    with _QueueLock():
        items = _load_queue()
        for item in items:
            if item.get("action_id") == action_id:
                item["status"] = STATUS_FAILED
                item["completed_at"] = _now_iso()
                item["error"] = error
                break
        _save_queue(items)


def mark_blocked(action_id: str, reason: str) -> None:
    with _QueueLock():
        items = _load_queue()
        for item in items:
            if item.get("action_id") == action_id:
                item["status"] = STATUS_BLOCKED
                item["error"] = reason
                break
        _save_queue(items)


def get_queue_stats() -> Dict[str, int]:
    items = _load_queue()
    stats: Dict[str, int] = {STATUS_PENDING: 0, STATUS_RUNNING: 0,
                              STATUS_DONE: 0, STATUS_FAILED: 0, STATUS_BLOCKED: 0}
    for item in items:
        s = item.get("status", STATUS_PENDING)
        stats[s] = stats.get(s, 0) + 1
    stats["total"] = len(items)
    return stats


def iter_queue() -> Iterator[Dict[str, Any]]:
    for item in _load_queue():
        yield item


def clear_queue() -> None:
    with _QueueLock():
        if QUEUE_PATH.exists():
            atomic_write_text(QUEUE_PATH, "")


def seed_autonomy_queue(sprint_id: str) -> List[str]:
    """Seed the queue with default autonomy actions if it's empty."""
    items = _load_queue()
    if any(i.get("status") == STATUS_PENDING for i in items):
        return []  # Already has pending items

    defaults = [
        make_queue_item(
            "RUN_JSON_VALIDATION",
            stream=STREAM_AUTONOMY, priority=1,
            target=".local/supervisor/active-continuation.json",
            result_path="reports/autonomous-system-acceptance/queue/cycle-q01-result.json",
            objective="Validate active-continuation.json (queue seed cycle 1)",
            sprint_id=sprint_id,
        ),
        make_queue_item(
            "RUN_MD_NONEMPTY_CHECK",
            stream=STREAM_AUTONOMY, priority=2,
            target="reports/autonomous-system-acceptance/00-preflight.md",
            result_path="reports/autonomous-system-acceptance/queue/cycle-q02-result.json",
            objective="Validate 00-preflight.md non-empty (queue seed cycle 2)",
            sprint_id=sprint_id,
        ),
        make_queue_item(
            "RUN_JSON_VALIDATION",
            stream=STREAM_AUTONOMY, priority=3,
            target="reports/autonomous-system-acceptance/current-gap-analysis.json",
            result_path="reports/autonomous-system-acceptance/queue/cycle-q03-result.json",
            objective="Validate current-gap-analysis.json (queue seed cycle 3)",
            sprint_id=sprint_id,
        ),
    ]
    ids = []
    for item in defaults:
        ids.append(enqueue(item))
    return ids


# ---------------------------------------------------------------------------
# Queue item schema v2 validation
# ---------------------------------------------------------------------------

_V2_REQUIRED_FIELDS = {
    "action_id", "action_type", "stream", "priority", "status",
    "objective", "allowed_paths", "forbidden_paths",
    "human_approval_required", "evidence_required",
}

_VALID_STATUSES = {"pending", "running", "done", "failed", "blocked"}

_SOURCE_CHANGING_TYPES = {"IMPLEMENT_SMALL_PRODUCT_FEATURE", "PRODUCT_SOURCE_PATCH_BOUNDED"}

_OBJECTIVE_MIN_LEN = 10


def validate_item_schema_v2(item: dict) -> list:
    """Validate a queue item against the v2 schema.

    Returns a list of error strings; empty list means valid.
    """
    errors: list = []

    missing = _V2_REQUIRED_FIELDS - set(item.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    if "allowed_paths" in item and not isinstance(item["allowed_paths"], list):
        errors.append("allowed_paths must be a list")

    if "forbidden_paths" in item and not isinstance(item["forbidden_paths"], list):
        errors.append("forbidden_paths must be a list")

    if "human_approval_required" in item and not isinstance(item["human_approval_required"], bool):
        errors.append("human_approval_required must be a bool")

    if "priority" in item and not isinstance(item["priority"], int):
        errors.append("priority must be an int")

    if "status" in item and item["status"] not in _VALID_STATUSES:
        errors.append(f"status must be one of {sorted(_VALID_STATUSES)}, got {item['status']!r}")

    if "objective" in item and len(str(item["objective"])) < _OBJECTIVE_MIN_LEN:
        errors.append(f"objective must be at least {_OBJECTIVE_MIN_LEN} characters")

    action_type = item.get("action_type", "")
    if action_type in _SOURCE_CHANGING_TYPES:
        if "rollback_strategy" not in item:
            errors.append("rollback_strategy is required for source-changing action types")
        if "expected_tests" not in item:
            errors.append("expected_tests is required for source-changing action types")

    gate = item.get("gate_classification", "")
    if gate == "LOCAL_AUTONOMOUS" and item.get("human_approval_required") is True:
        errors.append("human_approval_required must be False for LOCAL_AUTONOMOUS gate items")

    errors.extend(validate_route_classification(item))

    return errors


def validate_route_classification(item: dict) -> list:
    """Check route metadata for machinery-category items.

    Returns list of error strings (empty = valid).
    Non-blocking for items without task_category (backward compat).
    Blocks for items WITH task_category in MACHINERY + no route_decision_id.
    """
    from tools.supervisor.autonomy_route_models import TASK_CATEGORIES_MACHINERY

    errors: list = []
    cat = item.get("task_category", "")
    if cat and cat in TASK_CATEGORIES_MACHINERY:
        if not item.get("route_decision_id"):
            errors.append(
                f"Machinery category {cat!r} requires route_decision_id. "
                "Classify via autonomy_route_decider.decide_route() first."
            )
    return errors
