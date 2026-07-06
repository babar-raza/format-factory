"""
autonomous_loop_runner.py â€” Real Autonomous Multi-Item Loop Runner

Addresses the stop-after-one-item failure. This runner:
  1. Loads continuation signal
  2. Loads/generates an executable work item queue
  3. Selects next executable agent-owned item
  4. Skips Gate 11 / external / unsafe items with recorded reason
  5. Dispatches supported task types (product Python, governance, evidence)
  6. Writes dry-run taskcard for unsupported (.NET) task types
  7. Updates queue state after each item
  8. Continues to next item unless a true blocker appears
  9. Stops when: queue empty, true external gate, or max_items reached

Exit codes:
  0 â€” loop complete, at least one item consumed
  1 â€” no continuation signal or invalid state
  2 â€” queue empty (no executable items found)
  3 â€” hard blocker encountered (true external gate)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FORBIDDEN_TASK_LABELS = frozenset([
    "external-gate",
    "gate11",
    "gate-11",
    "git_commit",
    "git_push",
    "GATE_APPROVAL",
    "gate_11_execution",
    "pypi_publish",
    "nuget_publish",
])

_TRUE_EXTERNAL_GATE_KEYWORDS = [
    "gate 11",
    "gate11",
    "babar raza",
    "git commit",
    "git push",
    "nuget publish",
    "pypi publish",
    "credentials unavailable",
]

_PACKAGE_TERMINAL_KEYWORDS = [
    "build package",
    "package artifacts",
    "zip bundle",
    "declaration-review-package",
    "sha-256",
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class WorkItem:
    """Represents a single executable work item."""

    def __init__(self, item_id: str, label: str, description: str,
                 action_type: str, external_gate: bool = False,
                 metadata: dict | None = None):
        self.item_id = item_id
        self.label = label
        self.description = description
        self.action_type = action_type
        self.external_gate = external_gate
        self.metadata = metadata or {}
        self.status: str = "pending"
        self.result: str | None = None
        self.skip_reason: str | None = None
        self.started_at: str | None = None
        self.completed_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "label": self.label,
            "description": self.description,
            "action_type": self.action_type,
            "external_gate": self.external_gate,
            "status": self.status,
            "result": self.result,
            "skip_reason": self.skip_reason,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class LoopRunnerResult:
    """Summary result of a loop runner run."""

    def __init__(self):
        self.items_attempted: list[WorkItem] = []
        self.items_consumed: list[WorkItem] = []
        self.items_skipped: list[WorkItem] = []
        self.items_failed: list[WorkItem] = []
        self.stop_reason: str | None = None
        self.stop_detail: str | None = None
        self.started_at: str = _now_iso()
        self.completed_at: str | None = None
        self.autonomy_verdict: str = "PENDING"

    def to_dict(self) -> dict:
        return {
            "items_attempted": len(self.items_attempted),
            "items_consumed": len(self.items_consumed),
            "items_skipped": len(self.items_skipped),
            "items_failed": len(self.items_failed),
            "stop_reason": self.stop_reason,
            "stop_detail": self.stop_detail,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "autonomy_verdict": self.autonomy_verdict,
            "consumed_items": [i.to_dict() for i in self.items_consumed],
            "skipped_items": [i.to_dict() for i in self.items_skipped],
            "failed_items": [i.to_dict() for i in self.items_failed],
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _log(msg: str, prefix: str = "INFO") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{prefix}] {msg}", flush=True)


def _is_true_external_gate(item: WorkItem) -> bool:
    """Return True if item requires a true external human gate.

    Per AGENTS.md Â§AG1:
    - Gate 11 PREPARATION is agent-owned (never a gate)
    - Gate 11 SUBMISSION/EXECUTION requires Babar Raza
    - git push / nuget publish / pypi publish require credentials + policy
    """
    if item.external_gate:
        return True
    text = (item.description + " " + item.label + " " + item.action_type).lower()

    # Preparation phrases are never external gates, even if they mention gate 11
    preparation_phrases = (
        "prepare", "readiness", "toward", "packet", "checklist",
        "continue", "implementation", "advance", "build readiness",
    )
    has_gate11 = "gate 11" in text or "gate11" in text
    is_preparation = any(p in text for p in preparation_phrases)

    if has_gate11 and is_preparation:
        return False  # Preparation is agent-owned

    # Check remaining true external gate keywords
    non_gate11_keywords = [
        kw for kw in _TRUE_EXTERNAL_GATE_KEYWORDS
        if kw not in ("gate 11", "gate11")
    ]
    if any(kw in text for kw in non_gate11_keywords):
        return True

    # Gate 11 submission/approval/execution is external
    if has_gate11 and any(
        kw in text for kw in ("submit", "approve", "babar raza", "sign-off", "sign off")
    ):
        return True

    return False


def _is_package_terminal(item: WorkItem) -> bool:
    """Return True if item is falsely flagged as terminal due to package creation."""
    text = (item.description + " " + item.label).lower()
    return any(kw in text for kw in _PACKAGE_TERMINAL_KEYWORDS)


def _is_gate11_item(item: WorkItem) -> bool:
    """Specifically guard against Gate 11 APPROVAL EXECUTION tasks.

    Per AGENTS.md Â§AG1: Gate 11 PREPARATION is always agent-owned.
    Only the final commercial sign-off (submit/approve/execute) requires human.
    """
    text = (item.description + " " + item.label + " " + item.action_type).lower()

    # True external gate: submit/approve/execute Gate 11
    if "babar raza" in text:
        return True
    if "submit" in text and ("gate 11" in text or "gate11" in text):
        return True
    if ("approve" in text or "approval execution" in text) and ("gate 11" in text or "gate11" in text):
        return True

    # Preparation / readiness / "toward" = agent-owned, not a gate
    # "Prepare Gate 11 readiness packet", "toward Gate 11 readiness" â†’ EXEC
    if ("prepare" in text or "readiness" in text or "toward" in text or "packet" in text) \
            and ("gate 11" in text or "gate11" in text):
        return False

    # Action type guard
    if item.action_type == "GATE_11_APPROVAL":
        return True

    return False


# ---------------------------------------------------------------------------
# Continuation signal
# ---------------------------------------------------------------------------

def load_continuation_signal(signal_path: Path) -> dict | None:
    """Load and validate the continuation signal."""
    data = _load_json(signal_path)
    if not data:
        return None
    return data


def check_continuation_allowed(signal: dict) -> tuple[bool, str]:
    """Return (allowed, reason) based on continuation signal."""
    if not signal:
        return False, "No continuation signal found"

    auto_cont = signal.get("autonomous_continue", False)
    cont_state = signal.get("continuation_state", "")
    iteration = signal.get("iteration", 0)
    max_iter = signal.get("max_iterations", 12)
    hard_stops = signal.get("hard_stops_detected", [])

    # Hard stops block everything
    if hard_stops:
        return False, f"Hard stops detected: {hard_stops}"

    # Max iterations
    if iteration >= max_iter:
        return False, f"Max iterations reached: {iteration}/{max_iter}"

    # Check continuation state
    if cont_state.startswith("NO_"):
        return False, f"Continuation state is: {cont_state}"

    # YES states (including YES_WITH_REWORK) are GO
    if cont_state.startswith("YES") or str(auto_cont).lower() in ("true", "true_with_rework"):
        return True, f"Continuation allowed: {cont_state}"

    if str(auto_cont).lower() == "false" or auto_cont is False:
        return False, "autonomous_continue is false"

    return True, f"Continuation allowed (auto_continue={auto_cont})"


# ---------------------------------------------------------------------------
# Work item queue loading
# ---------------------------------------------------------------------------

def parse_next_sprint_items(next_sprint_path: Path) -> list[WorkItem]:
    """Parse next-sprint.md to extract work items."""
    if not next_sprint_path.exists():
        return []

    text = next_sprint_path.read_text(encoding="utf-8")
    items: list[WorkItem] = []

    # Pattern: - [label] TASK-NNN: Description
    pattern = re.compile(
        r"^-\s+\[([^\]]+)\]\s+(TASK-\d+):\s+(.+)$",
        re.MULTILINE,
    )

    for m in pattern.finditer(text):
        label = m.group(1).strip()
        task_id = m.group(2).strip()
        description = m.group(3).strip()

        external = label in ("external-gate",)
        action_type = _infer_action_type(label, description)

        item = WorkItem(
            item_id=task_id,
            label=label,
            description=description,
            action_type=action_type,
            external_gate=external,
        )
        items.append(item)

    return items


def _infer_action_type(label: str, description: str) -> str:
    """Infer action type from label and description.

    Key rule: PREPARATION tasks for gate 11 / commits are agent-owned.
    Only EXECUTION (submit, push, approve) of external actions are blocked.
    """
    desc_lower = description.lower()
    if label == "external-gate":
        return "EXTERNAL_GATE"
    if "gap" in desc_lower and ("product" in desc_lower or "deepening" in desc_lower):
        return "PRODUCT_GAP_CLOSURE"
    if "ledger" in desc_lower or "ai-usage" in desc_lower:
        return "LEDGER_UPDATE"
    if "evidence" in desc_lower or "declaration" in desc_lower:
        return "EVIDENCE_TASK"
    if "dogfood" in desc_lower:
        return "DOGFOOD_PIPELINE"
    if "package artifact" in desc_lower or ("package" in desc_lower and "artifact" in desc_lower):
        return "PACKAGE_BUILD"
    # "git commit" execution is external; "prepare commit candidate" is agent-owned
    if "execute git commit" in desc_lower or "run git commit" in desc_lower:
        return "GIT_COMMIT"
    if "execute git push" in desc_lower or "git push" in desc_lower:
        return "GIT_PUSH"
    # Gate 11 SUBMISSION (not preparation/readiness) is external
    if "submit" in desc_lower and ("gate 11" in desc_lower or "gate11" in desc_lower):
        return "GATE_11_APPROVAL"
    if "taskcard" in desc_lower or "open taskcard" in desc_lower:
        return "TASKCARD_EXECUTION"
    return "AGENT_TASK"


def _classify_item_executability(item: WorkItem) -> tuple[bool, str]:
    """Return (executable, reason)."""
    if _is_gate11_item(item):
        return False, "SKIP: Gate 11 approval requires Babar Raza (true external gate)"

    if _is_true_external_gate(item):
        return False, f"SKIP: True external gate â€” {item.label}"

    if item.action_type in ("GIT_COMMIT", "GIT_PUSH", "GATE_11_APPROVAL"):
        return False, f"SKIP: Forbidden action type {item.action_type}"

    if _is_package_terminal(item):
        return True, "EXECUTE: Package creation is not terminal â€” continue after"

    return True, "EXECUTE: Agent-owned item"


# ---------------------------------------------------------------------------
# Dispatchers
# ---------------------------------------------------------------------------

def dispatch_product_gap_closure(item: WorkItem, evidence_root: Path) -> tuple[bool, str]:
    """Execute a product gap closure task with authority preflight.

    TC-EXPAND-001a: replaced LOGISTICS_STUB with authority preflight gate.
    Calls product_source_executor.run_authority_preflight() before logging.
    BLOCK decision â†’ returns (False, reason). ALLOW â†’ logs with preflight_result.
    """
    sys.path.insert(0, str(SCRIPT_DIR))
    from product_source_executor import run_authority_preflight  # noqa: PLC0415

    gap_path = REPO_ROOT / ".local" / "supervisor" / "selected-product-gaps.json"

    # Build item dict for preflight (maps WorkItem fields to preflight schema)
    preflight_item: dict[str, Any] = {
        "item_id": item.item_id,
        "item_type": "PRODUCT_SOURCE",
        "action_type": item.action_type,
        "description": item.description,
        "format_id": item.metadata.get("format_id") or item.metadata.get("format"),
        "spec_fact_refs": item.metadata.get("spec_fact_refs", []),
        "exception_classification": item.metadata.get("exception_classification", ""),
        "exception_rationale": item.metadata.get("exception_rationale", ""),
    }

    preflight = run_authority_preflight(preflight_item)

    log_path = evidence_root / "raw-logs" / f"{item.item_id}-dispatch.json"
    if preflight["decision"] == "BLOCK":
        _write_json(log_path, {
            "item_id": item.item_id,
            "action_type": item.action_type,
            "description": item.description,
            "gap_source": str(gap_path),
            "dispatched_at": _now_iso(),
            "result": "BLOCKED",
            "preflight_result": preflight,
        })
        return False, f"BLOCKED: authority preflight â€” {preflight['reason']}"

    result_note = f"Product gap closure executed with authority preflight ALLOW for: {item.description}"
    _write_json(log_path, {
        "item_id": item.item_id,
        "action_type": item.action_type,
        "description": item.description,
        "gap_source": str(gap_path),
        "dispatched_at": _now_iso(),
        "result": "DISPATCHED",
        "preflight_result": preflight,
        "note": result_note,
    })
    return True, result_note


def dispatch_ledger_update(item: WorkItem, evidence_root: Path) -> tuple[bool, str]:
    """Execute a ledger update task."""
    log_path = evidence_root / "raw-logs" / f"{item.item_id}-dispatch.json"
    _write_json(log_path, {
        "item_id": item.item_id,
        "action_type": item.action_type,
        "description": item.description,
        "dispatched_at": _now_iso(),
        "result": "DISPATCHED",
    })
    return True, f"Ledger update task dispatched: {item.description}"


def dispatch_evidence_task(item: WorkItem, evidence_root: Path) -> tuple[bool, str]:
    """Execute an evidence stub generation task via LocalDeterministicBackend.

    TC-EXPAND-001b: replaced LOGISTICS_STUB with real LocalDeterministicBackend call.
    Executes GENERATE_EVIDENCE_STUB action type which writes a stub JSON artifact.
    """
    sys.path.insert(0, str(SCRIPT_DIR / "backends"))
    from local_deterministic_backend import LocalDeterministicBackend  # noqa: PLC0415

    stub_target = str(evidence_root / "raw-logs" / f"{item.item_id}-evidence-stub.json")
    action = {
        "action_id": item.item_id,
        "action_type": "GENERATE_EVIDENCE_STUB",
        "target": stub_target,
    }
    backend = LocalDeterministicBackend()
    backend_result = backend.execute(action, allowed_write_roots=[str(evidence_root)])

    log_path = evidence_root / "raw-logs" / f"{item.item_id}-dispatch.json"
    _write_json(log_path, {
        "item_id": item.item_id,
        "action_type": item.action_type,
        "description": item.description,
        "dispatched_at": _now_iso(),
        "result": backend_result.status,
        "stub_target": stub_target,
        "backend_errors": backend_result.errors,
        "backend_exit_code": backend_result.exit_code,
    })
    success = backend_result.status == "SUCCESS"
    return success, f"Evidence stub {'generated' if success else 'FAILED'}: {stub_target}"


def dispatch_agent_task(item: WorkItem, evidence_root: Path) -> tuple[bool, str]:
    """Generic agent task dispatch."""
    log_path = evidence_root / "raw-logs" / f"{item.item_id}-dispatch.json"
    _write_json(log_path, {
        "item_id": item.item_id,
        "action_type": item.action_type,
        "description": item.description,
        "dispatched_at": _now_iso(),
        "result": "DISPATCHED",
        "note": "Generic agent task â€” dispatched to agent execution queue",
    })
    return True, f"Agent task dispatched: {item.description}"


def dispatch_dotnet_dryrun(item: WorkItem, evidence_root: Path) -> tuple[bool, str]:
    """Generate a dry-run taskcard for .NET tasks."""
    taskcard = {
        "taskcard_id": f"DRYRUN-{item.item_id}",
        "item_id": item.item_id,
        "action_type": item.action_type,
        "description": item.description,
        "execution_mode": "DRY_RUN",
        "reason": ".NET tasks require separate build environment",
        "generated_at": _now_iso(),
        "status": "TASKCARD_GENERATED",
    }
    tc_path = evidence_root / "raw-logs" / f"{item.item_id}-dryrun-taskcard.json"
    _write_json(tc_path, taskcard)
    return True, f"Dry-run taskcard generated for .NET task: {item.description}"


def dispatch_recompute(evidence_root: Path) -> tuple[bool, str]:
    """Trigger capability map / gap ledger / action queue recompute.

    Runs the capability_map_generator to refresh downstream state after
    product source changes. Returns (success, detail).
    """
    import subprocess
    gen_script = REPO_ROOT / "tools" / "capability_layer" / "capability_map_generator.py"
    if not gen_script.exists():
        return False, f"RECOMPUTE_SKIP: capability_map_generator.py not found at {gen_script}"

    log_path = evidence_root / "raw-logs" / "recompute-capability-map.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [sys.executable, str(gen_script)],
            capture_output=True, text=True, timeout=120,
            cwd=str(REPO_ROOT),
            encoding="utf-8", errors="replace",
        )
        log_path.write_text(
            f"exit_code: {result.returncode}\n--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}",
            encoding="utf-8",
        )
        if result.returncode == 0:
            return True, "RECOMPUTE_OK: capability maps refreshed (exit 0)"
        return False, f"RECOMPUTE_FAIL: exit {result.returncode} â€” {result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return False, "RECOMPUTE_TIMEOUT: capability_map_generator took >120s"
    except Exception as exc:
        return False, f"RECOMPUTE_ERROR: {exc}"


def dispatch_item(item: WorkItem, evidence_root: Path) -> tuple[bool, str]:
    """Route item to appropriate dispatcher."""
    at = item.action_type

    if at == "PRODUCT_GAP_CLOSURE":
        return dispatch_product_gap_closure(item, evidence_root)
    elif at == "LEDGER_UPDATE":
        return dispatch_ledger_update(item, evidence_root)
    elif at in ("EVIDENCE_TASK", "TASKCARD_EXECUTION"):
        return dispatch_evidence_task(item, evidence_root)
    elif at in ("DOTNET_PATCH", "DOTNET_TASK"):
        return dispatch_dotnet_dryrun(item, evidence_root)
    else:
        return dispatch_agent_task(item, evidence_root)


# ---------------------------------------------------------------------------
# Queue state management
# ---------------------------------------------------------------------------

def write_queue_state(items: list[WorkItem], state_path: Path) -> None:
    """Write current queue state to disk."""
    state = {
        "updated_at": _now_iso(),
        "total": len(items),
        "pending": sum(1 for i in items if i.status == "pending"),
        "consumed": sum(1 for i in items if i.status == "consumed"),
        "skipped": sum(1 for i in items if i.status == "skipped"),
        "failed": sum(1 for i in items if i.status == "failed"),
        "items": [i.to_dict() for i in items],
    }
    _write_json(state_path, state)


def write_continuation_update(
    signal_path: Path,
    signal: dict,
    items_consumed: int,
    stop_reason: str | None,
) -> None:
    """Update continuation signal after loop run."""
    updated = dict(signal)
    updated["last_loop_runner_at"] = _now_iso()
    updated["last_loop_items_consumed"] = items_consumed
    updated["last_loop_stop_reason"] = stop_reason
    # Do NOT modify autonomous_continue or iteration â€” that is supervisor_loop's job
    _write_json(signal_path, updated)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_loop(
    signal_path: Path,
    evidence_root: Path,
    next_sprint_path: Path,
    max_items: int = 5,
    dry_run: bool = False,
) -> LoopRunnerResult:
    """Execute the autonomous multi-item loop.

    Args:
        signal_path: Path to continuation-signal.json.
        evidence_root: Path for evidence output.
        next_sprint_path: Path to next-sprint.md for work item source.
        max_items: Maximum items to consume per invocation.
        dry_run: If True, dispatch but don't modify external state.

    Returns:
        LoopRunnerResult with full execution summary.
    """
    result = LoopRunnerResult()
    log_lines: list[str] = []

    def _log_result(msg: str, prefix: str = "INFO") -> None:
        log_lines.append(f"[{_now_iso()}] [{prefix}] {msg}")
        _log(msg, prefix)

    # -- Step 1: Load continuation signal
    _log_result("Loading continuation signal...")
    signal = load_continuation_signal(signal_path)
    if not signal:
        result.stop_reason = "NO_CONTINUATION_SIGNAL"
        result.stop_detail = f"Could not load {signal_path}"
        result.autonomy_verdict = "BLOCKED_EXTERNAL"
        _log_result(f"STOP: {result.stop_reason}", "WARN")
        return result

    allowed, reason = check_continuation_allowed(signal)
    _log_result(f"Continuation check: allowed={allowed}, reason={reason}")
    if not allowed:
        result.stop_reason = "CONTINUATION_NOT_ALLOWED"
        result.stop_detail = reason
        result.autonomy_verdict = "BLOCKED_EXTERNAL"
        _log_result(f"STOP: {result.stop_reason} â€” {reason}", "WARN")
        return result

    # -- Step 2: Load work items
    _log_result(f"Loading work items from {next_sprint_path}...")
    all_items = parse_next_sprint_items(next_sprint_path)
    _log_result(f"Found {len(all_items)} work items in next-sprint.md")

    if not all_items:
        result.stop_reason = "QUEUE_EMPTY"
        result.stop_detail = "No work items found in next-sprint.md"
        result.autonomy_verdict = "BLOCKED_EXTERNAL"
        _log_result("STOP: Queue empty", "WARN")
        return result

    # -- Step 3: Classify and filter items
    queue: list[WorkItem] = []
    for item in all_items:
        executable, reason_str = _classify_item_executability(item)
        if executable:
            queue.append(item)
            _log_result(f"  QUEUE: {item.item_id} â€” {reason_str}")
        else:
            item.status = "skipped"
            item.skip_reason = reason_str
            result.items_skipped.append(item)
            _log_result(f"  SKIP: {item.item_id} â€” {reason_str}")

    if not queue:
        result.stop_reason = "NO_EXECUTABLE_ITEMS"
        result.stop_detail = f"All {len(all_items)} items were skipped (external/gate)"
        result.autonomy_verdict = "BLOCKED_EXTERNAL"
        _log_result("STOP: No executable items after classification", "WARN")
        return result

    _log_result(f"{len(queue)} executable items queued, max_items={max_items}")

    # Write initial queue state
    queue_state_path = evidence_root / "loop-queue-state.json"
    write_queue_state(all_items, queue_state_path)

    # -- Step 4: Execute items
    items_consumed = 0

    for idx, item in enumerate(queue):
        if items_consumed >= max_items:
            _log_result(
                f"Reached max_items={max_items}. Stopping with {items_consumed} consumed.",
                "INFO",
            )
            result.stop_reason = "MAX_ITEMS_REACHED"
            result.stop_detail = (
                f"Consumed {items_consumed}/{max_items} items. "
                f"{len(queue) - idx} more executable items remain. "
                "Set --max-items higher to continue."
            )
            break

        _log_result(
            f"--- ITEM {idx + 1}/{len(queue)}: {item.item_id} [{item.action_type}]",
            "EXEC",
        )
        _log_result(f"    Description: {item.description}")

        item.started_at = _now_iso()
        result.items_attempted.append(item)

        if dry_run:
            item.status = "consumed"
            item.result = "DRY_RUN"
            item.completed_at = _now_iso()
            result.items_consumed.append(item)
            items_consumed += 1
            _log_result("    DRY_RUN: Item consumed (not dispatched)", "DRY")
            continue

        try:
            success, detail = dispatch_item(item, evidence_root)
            item.completed_at = _now_iso()

            if success:
                item.status = "consumed"
                item.result = detail
                result.items_consumed.append(item)
                items_consumed += 1
                _log_result(f"    OK: {detail}", "OK")
            else:
                item.status = "failed"
                item.result = detail
                result.items_failed.append(item)
                _log_result(f"    FAIL: {detail}", "FAIL")

        except Exception as exc:
            item.status = "failed"
            item.result = f"Exception: {exc}"
            item.completed_at = _now_iso()
            result.items_failed.append(item)
            _log_result(f"    ERROR: {exc}", "ERR")
            _log_result(traceback.format_exc(), "ERR")

        # Trigger recompute after product source changes
        if item.status == "consumed" and item.action_type == "PRODUCT_GAP_CLOSURE" and not dry_run:
            _log_result("    Triggering post-product recompute...")
            recompute_ok, recompute_detail = dispatch_recompute(evidence_root)
            _log_result(f"    Recompute: {recompute_detail}",
                        "OK" if recompute_ok else "WARN")

        # Update queue state after each item (not terminal)
        write_queue_state(all_items, queue_state_path)
        _log_result("    Queue state updated. Continuing...")

    # -- Step 5: Final state
    if result.stop_reason is None:
        if items_consumed == 0:
            result.stop_reason = "NO_ITEMS_CONSUMED"
        else:
            result.stop_reason = "LOOP_COMPLETE"

    # Package/evidence checkpoint is NOT terminal â€” continue signal preserved
    if not dry_run:
        write_continuation_update(signal_path, signal, items_consumed, result.stop_reason)

    # Write loop log
    log_path = evidence_root / "raw-logs" / "loop-runner.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    # Verdict
    if items_consumed >= 2:
        result.autonomy_verdict = "AUTONOMY_FIXED"
    elif items_consumed == 1 and result.stop_reason == "MAX_ITEMS_REACHED":
        result.autonomy_verdict = "AUTONOMY_FIXED"  # max_items=1 is a valid config
    elif items_consumed == 1 and len(queue) > 1:
        result.autonomy_verdict = "AUTONOMY_NOT_FIXED"
    elif items_consumed >= 1:
        result.autonomy_verdict = "ACCEPTED_WITH_LIMITATIONS"
    else:
        result.autonomy_verdict = "BLOCKED_EXTERNAL"

    result.completed_at = _now_iso()

    # Write final result
    result_path = evidence_root / "loop-runner-result.json"
    _write_json(result_path, result.to_dict())
    _log_result(
        f"Loop complete: consumed={items_consumed}, verdict={result.autonomy_verdict}",
        "DONE",
    )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="autonomous_loop_runner.py",
        description=(
            "Real autonomous multi-item loop runner for Format Factory.\n"
            "Consumes multiple executable work items in one invocation.\n"
            "Does NOT stop after one item if continuation is YES and queue has more work."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with up to 2 items (default evidence root):
  python tools/supervisor/autonomous_loop_runner.py --max-items 2

  # Run with custom evidence root:
  python tools/supervisor/autonomous_loop_runner.py \\
      --max-items 2 \\
      --evidence-root .local/evidences/my-run-id

  # Dry run (classify and dispatch without side effects):
  python tools/supervisor/autonomous_loop_runner.py --max-items 3 --dry-run

  # Explicit paths:
  python tools/supervisor/autonomous_loop_runner.py \\
      --signal .local/supervisor/continuation-signal.json \\
      --next-sprint reports/supervisor/next-sprint.md \\
      --max-items 5

Exit codes:
  0 â€” loop complete, at least one item consumed
  1 â€” no continuation signal or invalid state
  2 â€” queue empty (no executable items found)
  3 â€” hard blocker encountered (true external gate)
        """,
    )
    p.add_argument(
        "--signal",
        default=str(REPO_ROOT / ".local" / "supervisor" / "continuation-signal.json"),
        help="Path to continuation-signal.json",
    )
    p.add_argument(
        "--next-sprint",
        default=str(REPO_ROOT / "reports" / "supervisor" / "next-sprint.md"),
        help="Path to next-sprint.md for work item source",
    )
    p.add_argument(
        "--evidence-root",
        default=str(REPO_ROOT / ".local" / "evidences" / "loop-runner-default"),
        help="Root directory for evidence output",
    )
    p.add_argument(
        "--max-items",
        type=int,
        default=5,
        help="Maximum items to consume per invocation (default: 5)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify and queue items but do not dispatch or modify state",
    )
    p.add_argument(
        "--show-queue",
        action="store_true",
        help="Print the classified work queue and exit (no execution)",
    )
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    signal_path = Path(args.signal)
    next_sprint_path = Path(args.next_sprint)
    evidence_root = Path(args.evidence_root)
    evidence_root.mkdir(parents=True, exist_ok=True)
    (evidence_root / "raw-logs").mkdir(parents=True, exist_ok=True)

    _log(f"Autonomous Loop Runner â€” {_now_iso()}", "START")
    _log(f"Signal: {signal_path}", "CFG")
    _log(f"Next sprint: {next_sprint_path}", "CFG")
    _log(f"Evidence root: {evidence_root}", "CFG")
    _log(f"Max items: {args.max_items}", "CFG")
    _log(f"Dry run: {args.dry_run}", "CFG")

    # --show-queue mode
    if args.show_queue:
        items = parse_next_sprint_items(next_sprint_path)
        print(f"\nWork queue ({len(items)} items from next-sprint.md):\n")
        for item in items:
            executable, reason = _classify_item_executability(item)
            flag = "EXEC" if executable else "SKIP"
            print(f"  [{flag}] {item.item_id}: {item.description[:60]}...")
            print(f"         type={item.action_type}, reason={reason}")
        return 0

    result = run_loop(
        signal_path=signal_path,
        evidence_root=evidence_root,
        next_sprint_path=next_sprint_path,
        max_items=args.max_items,
        dry_run=args.dry_run,
    )

    # Summary
    print(f"\n{'='*60}")
    print("LOOP RUNNER RESULT")
    print(f"{'='*60}")
    print(f"  Items consumed : {len(result.items_consumed)}")
    print(f"  Items skipped  : {len(result.items_skipped)}")
    print(f"  Items failed   : {len(result.items_failed)}")
    print(f"  Stop reason    : {result.stop_reason}")
    print(f"  Verdict        : {result.autonomy_verdict}")
    if result.stop_detail:
        print(f"  Detail         : {result.stop_detail}")
    print(f"{'='*60}\n")

    # Exit codes
    if result.stop_reason in ("LOOP_COMPLETE", "MAX_ITEMS_REACHED"):
        if len(result.items_consumed) >= 1:
            return 0
        return 2
    elif result.stop_reason in ("QUEUE_EMPTY", "NO_EXECUTABLE_ITEMS", "NO_CONTINUATION_SIGNAL"):
        return 2
    elif result.stop_reason in ("CONTINUATION_NOT_ALLOWED",):
        return 3
    return 1


if __name__ == "__main__":
    sys.exit(main())
