"""
Format Factory — Autonomous Orchestrator
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

Persistent/restartable orchestrator. Reads machine-readable continuation state,
executes next actions via next_action_runner, generates subsequent actions,
writes heartbeat and state, and can resume after process stop.

Usage:
  python autonomous_orchestrator.py [options]

Modes:
  --once                Run exactly one cycle then stop
  --max-cycles N        Run at most N cycles (default: 3)
  --watch               Run in watch mode (not implemented — blocks on external gate)
  --interval-seconds N  Seconds between cycles in watch mode (default: 10)
  --stop-after-idle N   Stop if N consecutive cycles had no runnable action (default: 1)

Backends:
  --backend auto        Select best available backend (default)
  --backend local       Force LOCAL_DETERMINISTIC
  --backend llm-api     Force LLM_API

Other:
  --dry-run             Validate but do not execute
  --resume              Resume from orchestrator-state.json
  --seed-action PATH    Path to seed next-action.json (used if no active continuation)
  --sprint-id ID        Sprint ID for generated actions
  --write-root PATH     Allowed write root (repeatable)
  --json                Output final state as JSON
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.continuation_state import (
    NEXT_ACTION_PATH,
    STOP_REASON_PATH,
    STATE_DIR,
    STOP_MAX_CYCLES,
    STOP_NO_SAFE_ACTION,
    STOP_DRY_RUN,
    STOP_LOCK_HELD,
    STOP_REPEATED_FAILURE,
    is_advisory_prompt,
    load_active_continuation,
    load_next_action,
    load_orchestrator_state,
    make_active_continuation,
    make_orchestrator_state,
    save_active_continuation,
    save_next_action,
    save_orchestrator_state,
    write_heartbeat,
    write_stop_reason,
    STREAM_AUTONOMY,
)
from tools.supervisor.continuation_router import route
from tools.supervisor.next_action_generator import generate_next_action, save_generation_trace
from tools.supervisor.next_action_runner import run_action
from tools.supervisor.action_queue import (
    QUEUE_PATH,
    dequeue_next,
    mark_done as queue_mark_done,
    mark_failed as queue_mark_failed,
)

# ── Lock file ─────────────────────────────────────────────────────────────────

LOCK_PATH = STATE_DIR / "orchestrator.lock"
DEFAULT_SPRINT_ID = "FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001"
DEFAULT_WRITE_ROOTS = ["reports/autonomous-orchestrator", ".local/supervisor"]
MAX_CONSECUTIVE_FAILURES = 3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _acquire_lock(run_id: str) -> bool:
    """Try to write lock file. Return True if acquired."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            lock_data = json.loads(LOCK_PATH.read_text())
            existing_pid = lock_data.get("pid")
            # Check if that process is still alive
            if existing_pid and existing_pid != os.getpid():
                try:
                    os.kill(int(existing_pid), 0)
                    # Process exists — lock is held
                    return False
                except (OSError, ProcessLookupError):
                    pass  # Process dead — stale lock, overwrite
        except Exception:
            pass  # Corrupt lock — overwrite

    LOCK_PATH.write_text(json.dumps({
        "run_id": run_id,
        "pid": os.getpid(),
        "acquired_at": _now_iso(),
    }), encoding="utf-8")
    return True


def _release_lock() -> None:
    if LOCK_PATH.exists():
        LOCK_PATH.unlink(missing_ok=True)


# ── Orchestrator ──────────────────────────────────────────────────────────────

class OrchestratorResult:
    def __init__(
        self,
        run_id: str,
        cycles_completed: int,
        stop_code: str,
        stop_detail: str,
        results: List[Dict[str, Any]],
        resumed: bool = False,
        dry_run: bool = False,
    ):
        self.run_id = run_id
        self.cycles_completed = cycles_completed
        self.stop_code = stop_code
        self.stop_detail = stop_detail
        self.results = results
        self.resumed = resumed
        self.dry_run = dry_run

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "cycles_completed": self.cycles_completed,
            "stop_code": self.stop_code,
            "stop_detail": self.stop_detail,
            "results": self.results,
            "resumed": self.resumed,
            "dry_run": self.dry_run,
        }


def _queue_item_to_next_action(item: Dict[str, Any], cycle_index: int, sprint_id: str) -> Dict[str, Any]:
    """Convert an action queue item to a next-action.json compatible dict."""
    action_id = item.get("action_id", f"q-{cycle_index:03d}")
    action_type = item.get("action_type", "RUN_JSON_VALIDATION")
    # Build a result_path for this cycle if not already set in the item
    result_path = item.get("result_path") or (
        f"reports/autonomous-orchestrator/queue-run/queue-item-{action_id}-result.json"
    )
    # Compute allowed_write_roots: merge item's roots + repo defaults + result_path's parent
    base_roots = list(item.get("allowed_write_roots") or DEFAULT_WRITE_ROOTS)
    result_parent = str(Path(result_path).parent)
    write_roots = list({*base_roots, result_parent, "reports/autonomous-orchestrator/queue-run"})

    action = {
        "schema_version": 1,
        "action_id": action_id,
        "action_type": action_type,
        "objective": item.get("objective", f"Queue item {action_id}: {action_type}"),
        "preferred_backend": item.get("preferred_backend", "LOCAL_DETERMINISTIC"),
        "fallback_backends": item.get("fallback_backends", []),
        "external_gate": item.get("external_gate", False),
        "result_path": result_path,
        "allowed_write_roots": write_roots,
        "evidence_required": True,
        "cycle_number": cycle_index,
        "sprint_id": sprint_id,
        "queue_item_id": action_id,
        "from_queue": True,
    }
    # Carry over target/target_path
    if item.get("target"):
        action["target"] = item["target"]
    elif item.get("target_path"):
        action["target"] = item["target_path"]
    return action


class AutonomousOrchestrator:
    # TC-P2-007: stream filter — maps stream name to allowed item streams
    # machinery: refuses STREAM_PRODUCT actions (G3/G4/G5)
    # product:   refuses non-STREAM_PRODUCT actions
    # all/None:  no filter (current behavior)
    _STREAM_ALLOWED: Dict[str, set] = {
        "machinery": {"autonomy", "mainstream", "setup", "evidence", "autonomy_setup"},
        "product": {"product"},
        "all": set(),  # empty = accept all
    }

    def __init__(
        self,
        max_cycles: int = 3,
        backend: str = "auto",
        dry_run: bool = False,
        resume: bool = False,
        sprint_id: str = DEFAULT_SPRINT_ID,
        write_roots: Optional[List[str]] = None,
        seed_action_path: Optional[str] = None,
        interval_seconds: int = 10,
        stop_after_idle: int = 1,
        queue_first: bool = False,
        stream_filter: Optional[str] = None,
    ):
        self.max_cycles = max_cycles
        self.backend = backend
        self.dry_run = dry_run
        self.resume = resume
        self.sprint_id = sprint_id
        self.write_roots = write_roots or DEFAULT_WRITE_ROOTS
        self.seed_action_path = seed_action_path
        self.interval_seconds = interval_seconds
        self.stop_after_idle = stop_after_idle
        self.queue_first = queue_first
        self.stream_filter = stream_filter  # TC-P2-007: "machinery" | "product" | "all" | None
        self.run_id = str(uuid.uuid4())[:8]
        self.results: List[Dict[str, Any]] = []
        self._current_queue_item: Optional[Dict[str, Any]] = None
        # CCI: resolve session identity once at init (default behavior)
        try:
            from tools.supervisor.continuation_identity import get_or_create_session_identity
            self._session_id = get_or_create_session_identity(
                sprint_id=sprint_id,
            ).session_id
        except Exception as _cci_err:
            print(f"WARNING: CCI orchestrator identity fallback: {_cci_err}", file=sys.stderr)
            self._session_id = None

    def _init_state(self) -> int:
        """Initialize or resume orchestrator state. Returns starting cycle_index."""
        if self.resume:
            state = load_orchestrator_state()
            if state and state.get("status") in {"STOPPED", "IDLE", "BLOCKED", "COMPLETED"}:
                cycle_index = state.get("cycle_index", 0)
                # Resume: reuse same run_id if available
                self.run_id = state.get("orchestrator_run_id", self.run_id)
                # Clear old stop reason on resume
                if STOP_REASON_PATH.exists():
                    old = json.loads(STOP_REASON_PATH.read_text())
                    if old.get("stop_code") == STOP_MAX_CYCLES:
                        STOP_REASON_PATH.unlink(missing_ok=True)
                return cycle_index

        # Fresh start
        state = make_orchestrator_state(
            run_id=self.run_id,
            status="RUNNING",
            cycle_index=0,
            session_id=self._session_id,
        )
        save_orchestrator_state(state)
        return 0

    def _ensure_active_continuation(self, next_action_path: str) -> None:
        """Create or update active-continuation.json pointing at next-action."""
        cont = load_active_continuation()
        if cont is None or is_advisory_prompt(cont.get("next_action_path", "")):
            cont = make_active_continuation(
                source_sprint_id=self.sprint_id,
                proof_level="H4_PLUS",
                next_action_path=next_action_path,
                autonomous_continue=True,
                active_stream=STREAM_AUTONOMY,
                session_id=self._session_id,
            )
            save_active_continuation(cont)
        else:
            cont["next_action_path"] = next_action_path
            cont["autonomous_continue"] = True
            if self._session_id:
                cont["session_id"] = self._session_id
            save_active_continuation(cont)

    def _resolve_seed_action(self, cycle_index: int) -> Optional[str]:
        """Find or generate a seed next-action file.

        If queue_first=True, dequeue from action-queue before generating synthetic actions.
        """
        # 0. Queue-first: dequeue pending item before anything else
        if self.queue_first and QUEUE_PATH.exists():
            q_item = dequeue_next()
            if q_item is not None:
                # TC-P2-007: Stream filter — refuse wrong-track action types (REQ-TRK-011)
                if self.stream_filter and self.stream_filter != "all":
                    allowed = self._STREAM_ALLOWED.get(self.stream_filter, set())
                    item_stream = q_item.get("stream", "autonomy")
                    if item_stream not in allowed:
                        print(
                            f"  [stream-filter] REJECTED queue item {q_item.get('action_id','?')}: "
                            f"stream={item_stream!r} not allowed for --stream {self.stream_filter!r}. "
                            f"Re-queuing with 'wrong-track' annotation."
                        )
                        # Re-queue with wrong-track annotation (not consumed); item is preserved
                        q_item["_wrong_track_rejected"] = True
                        q_item["_rejected_by_stream"] = self.stream_filter
                        from action_queue import enqueue_front
                        enqueue_front(q_item)
                        return None  # Skip this item; cycle will go idle
                self._current_queue_item = q_item
                action = _queue_item_to_next_action(q_item, cycle_index + 1, self.sprint_id)
                save_next_action(action)
                return str(NEXT_ACTION_PATH.relative_to(_repo_root))

        # 1. Explicit seed override
        if self.seed_action_path:
            p = _repo_root / self.seed_action_path
            if p.exists():
                return str(NEXT_ACTION_PATH.relative_to(_repo_root))

        # 2. Existing next-action.json
        if NEXT_ACTION_PATH.exists():
            action = load_next_action()
            if action and not is_advisory_prompt(str(NEXT_ACTION_PATH)):
                return str(NEXT_ACTION_PATH.relative_to(_repo_root))

        # 3. Generate first action
        action = generate_next_action(
            prev_result=None,
            cycle_index=cycle_index + 1,
            sprint_id=self.sprint_id,
            allowed_write_roots=self.write_roots,
        )
        if action is None:
            return None
        save_next_action(action)
        return str(NEXT_ACTION_PATH.relative_to(_repo_root))

    def _execute_cycle(self, cycle_index: int, next_action_path: str) -> Dict[str, Any]:
        """Execute one orchestrator cycle. Returns action result dict."""
        # Dry run — validate only
        if self.dry_run:
            action = load_next_action(next_action_path)
            return {
                "status": "DRY_RUN",
                "cycle_index": cycle_index,
                "action_id": action.get("action_id") if action else "unknown",
                "result_path": None,
                "backend_used": "DRY_RUN",
                "proof_level": None,
                "dry_run": True,
            }

        # Map --backend to allowed_write_roots override
        backend_override = None
        if self.backend == "local":
            backend_override = "LOCAL_DETERMINISTIC"

        # Derive result_path for this cycle
        result_path = f"reports/autonomous-orchestrator/proof-run/cycle-{cycle_index:03d}-result.json"
        result_abs = _repo_root / result_path
        result_abs.parent.mkdir(parents=True, exist_ok=True)

        # Merge orchestrator write_roots with any extra roots declared in the action itself
        loaded_action = load_next_action(next_action_path)
        extra_roots: list = []
        if loaded_action and loaded_action.get("allowed_write_roots"):
            extra_roots = [
                str(_repo_root / r) if not Path(r).is_absolute() else r
                for r in loaded_action["allowed_write_roots"]
            ]
        merged_roots = list({str(_repo_root / r) for r in self.write_roots} | set(extra_roots))

        # Execute via runner
        result = run_action(
            action_path=str(_repo_root / next_action_path),
            allowed_write_roots=merged_roots,
            dry_run=False,
        )
        result["cycle_index"] = cycle_index
        return result

    def run(self, once: bool = False) -> OrchestratorResult:
        """Run the orchestrator loop."""
        cycles_done = 0
        consecutive_failures = 0

        # Acquire lock
        if not _acquire_lock(self.run_id):
            write_stop_reason(self.run_id, STOP_LOCK_HELD, "Another orchestrator holds the lock", 0, resumable=True)
            return OrchestratorResult(
                self.run_id, 0, STOP_LOCK_HELD, "Lock held by another process", [], resumed=self.resume
            )

        try:
            cycle_index = self._init_state()
            actual_max = 1 if once else self.max_cycles

            # Ensure seed action exists
            next_action_path = self._resolve_seed_action(cycle_index)
            if next_action_path is None:
                write_stop_reason(self.run_id, STOP_NO_SAFE_ACTION, "No seed action available", cycle_index)
                update_orch_state(self.run_id, "STOPPED", cycle_index, stop_reason=STOP_NO_SAFE_ACTION, session_id=self._session_id)
                return OrchestratorResult(
                    self.run_id, 0, STOP_NO_SAFE_ACTION, "No seed action", [], self.resume, self.dry_run
                )

            # If seed_action_path provided, copy it to next-action.json
            if self.seed_action_path:
                sp = _repo_root / self.seed_action_path
                if sp.exists():
                    import shutil
                    shutil.copy2(sp, NEXT_ACTION_PATH)
                    next_action_path = str(NEXT_ACTION_PATH.relative_to(_repo_root))

            while cycles_done < actual_max:
                write_heartbeat(self.run_id, cycle_index + cycles_done, "RUNNING")

                # Point active-continuation at current next-action
                self._ensure_active_continuation(next_action_path)

                # Route
                decision = route(self.run_id, cycle_index + cycles_done, next_action_path)
                if not decision.should_dispatch:
                    # Stop cleanly
                    stop_code = decision.stop_reason or STOP_NO_SAFE_ACTION
                    write_stop_reason(self.run_id, stop_code, decision.detail, cycle_index + cycles_done)
                    update_orch_state(self.run_id, "STOPPED", cycle_index + cycles_done, stop_reason=stop_code, session_id=self._session_id)
                    return OrchestratorResult(
                        self.run_id, cycles_done, stop_code, decision.detail,
                        self.results, self.resume, self.dry_run
                    )

                # Execute
                result = self._execute_cycle(cycle_index + cycles_done, next_action_path)
                self.results.append(result)

                # Update queue item status based on result
                if self._current_queue_item is not None:
                    qid = self._current_queue_item.get("action_id")
                    if result.get("status") in {"SUCCESS", "DRY_RUN"}:
                        queue_mark_done(qid, result_path=result.get("result_path"))
                    else:
                        queue_mark_failed(qid, error=str(result.get("errors", result.get("status", "FAILED"))))
                    self._current_queue_item = None

                if result.get("status") not in {"SUCCESS", "DRY_RUN"}:
                    consecutive_failures += 1
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        write_stop_reason(
                            self.run_id, STOP_REPEATED_FAILURE,
                            f"{consecutive_failures} consecutive failures",
                            cycle_index + cycles_done
                        )
                        update_orch_state(
                            self.run_id, "BLOCKED", cycle_index + cycles_done,
                            last_result=result.get("result_path"),
                            stop_reason=STOP_REPEATED_FAILURE,
                            session_id=self._session_id,
                        )
                        return OrchestratorResult(
                            self.run_id, cycles_done, STOP_REPEATED_FAILURE,
                            f"{consecutive_failures} consecutive failures",
                            self.results, self.resume, self.dry_run
                        )
                else:
                    consecutive_failures = 0

                cycles_done += 1

                update_orch_state(
                    self.run_id, "RUNNING", cycle_index + cycles_done,
                    last_action_id=result.get("action_id"),
                    last_result=result.get("result_path"),
                    session_id=self._session_id,
                )

                if cycles_done >= actual_max:
                    break

                # Generate next action for the following cycle (queue-first)
                next_action = None
                if self.queue_first and QUEUE_PATH.exists():
                    q_item = dequeue_next()
                    if q_item is not None:
                        self._current_queue_item = q_item
                        next_action = _queue_item_to_next_action(
                            q_item, cycle_index + cycles_done + 1, self.sprint_id
                        )

                if next_action is None:
                    next_action = generate_next_action(
                        prev_result=result,
                        cycle_index=cycle_index + cycles_done + 1,
                        sprint_id=self.sprint_id,
                        allowed_write_roots=self.write_roots,
                    )
                if next_action is None:
                    write_stop_reason(
                        self.run_id, STOP_NO_SAFE_ACTION, "Generator returned None",
                        cycle_index + cycles_done
                    )
                    update_orch_state(self.run_id, "STOPPED", cycle_index + cycles_done, stop_reason=STOP_NO_SAFE_ACTION, session_id=self._session_id)
                    return OrchestratorResult(
                        self.run_id, cycles_done, STOP_NO_SAFE_ACTION, "No more safe actions",
                        self.results, self.resume, self.dry_run
                    )

                save_next_action(next_action)
                next_action_path = str(NEXT_ACTION_PATH.relative_to(_repo_root))

            # Clean stop at max cycles
            if self.dry_run:
                stop_code = STOP_DRY_RUN
            else:
                stop_code = STOP_MAX_CYCLES

            write_stop_reason(
                self.run_id, stop_code,
                f"Completed {cycles_done} cycle(s) (max={actual_max})",
                cycle_index + cycles_done,
                resumable=True,
            )

            final_status = "COMPLETED" if not self.dry_run else "IDLE"
            update_orch_state(
                self.run_id, final_status, cycle_index + cycles_done,
                last_action_id=self.results[-1].get("action_id") if self.results else None,
                last_result=self.results[-1].get("result_path") if self.results else None,
                stop_reason=stop_code,
                session_id=self._session_id,
            )

            # Update active-continuation: point to newly written next-action
            cont = load_active_continuation() or {}
            cont["autonomous_continue"] = True
            cont["stop_reason"] = stop_code
            cont["next_action_path"] = next_action_path
            save_active_continuation(cont)

            save_generation_trace("reports/autonomous-orchestrator/next-action-generation/generation-trace.json")

            write_heartbeat(self.run_id, cycle_index + cycles_done, final_status)

            return OrchestratorResult(
                self.run_id, cycles_done, stop_code,
                f"{cycles_done} cycles completed",
                self.results, self.resume, self.dry_run
            )

        finally:
            _release_lock()


def update_orch_state(
    run_id: str, status: str, cycle_index: int,
    last_action_id: Optional[str] = None,
    last_result: Optional[str] = None,
    stop_reason: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    state = load_orchestrator_state() or make_orchestrator_state(run_id, session_id=session_id)
    state["status"] = status
    state["cycle_index"] = cycle_index
    if last_action_id:
        state["last_action_id"] = last_action_id
    if last_result:
        state["last_result_path"] = last_result
    if stop_reason:
        state["stop_reason"] = stop_reason
    save_orchestrator_state(state)


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Format Factory Autonomous Orchestrator")
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--once", action="store_true", help="Run exactly one cycle")
    grp.add_argument("--max-cycles", type=int, default=3, metavar="N", help="Max cycles (default: 3)")
    grp.add_argument("--watch", action="store_true", help="Watch mode (stop at external gate)")
    p.add_argument("--backend", choices=["auto", "local", "llm-api"], default="auto")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--resume", action="store_true", help="Resume from orchestrator-state.json")
    p.add_argument("--seed-action", metavar="PATH", help="Path to seed next-action.json")
    p.add_argument("--sprint-id", default=DEFAULT_SPRINT_ID)
    p.add_argument("--write-root", action="append", dest="write_roots", metavar="PATH")
    p.add_argument("--interval-seconds", type=int, default=10)
    p.add_argument("--stop-after-idle", type=int, default=1)
    p.add_argument("--queue-first", action="store_true", dest="queue_first",
                   help="Dequeue from action-queue.jsonl before generating synthetic actions")
    p.add_argument("--stream", type=str, choices=["machinery", "product", "all"], default=None,
                   dest="stream_filter",
                   help=(
                       "TC-P2-007: Stream filter for two-track separation. "
                       "'machinery' only processes non-product streams (REQ-TRK-011). "
                       "'product' only processes STREAM_PRODUCT actions. "
                       "'all' (default) processes all streams (backward compat)."
                   ))
    p.add_argument("--json", action="store_true", dest="json_output", help="Print result as JSON")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    max_cycles = 1 if args.once else args.max_cycles

    orch = AutonomousOrchestrator(
        max_cycles=max_cycles,
        backend=args.backend,
        dry_run=args.dry_run,
        resume=args.resume,
        sprint_id=args.sprint_id,
        write_roots=args.write_roots or DEFAULT_WRITE_ROOTS,
        seed_action_path=args.seed_action,
        interval_seconds=args.interval_seconds,
        stop_after_idle=args.stop_after_idle,
        queue_first=args.queue_first,
        stream_filter=args.stream_filter,  # TC-P2-007
    )

    result = orch.run(once=args.once)

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Orchestrator {result.run_id}: {result.cycles_completed} cycle(s) — {result.stop_code}")
        if result.stop_detail:
            print(f"  Detail: {result.stop_detail}")
        for i, r in enumerate(result.results, 1):
            status = r.get("status", "?")
            aid = r.get("action_id", "?")
            print(f"  Cycle {i}: [{status}] {aid}")

    # Exit 0 on success or max cycles (resumable); non-zero on unsafe stop
    if result.stop_code in {STOP_MAX_CYCLES, STOP_DRY_RUN, STOP_NO_SAFE_ACTION}:
        return 0
    if result.stop_code == STOP_LOCK_HELD:
        return 2
    return 0 if result.cycles_completed > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
