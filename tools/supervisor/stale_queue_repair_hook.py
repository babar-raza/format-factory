"""
stale_queue_repair_hook.py — Stale Queue Repair Hook

Integration bridge: connects rework_orchestrator.py to the supervisor/autonomous
rework path.  Intended to be called as a pre-cycle step or via the
supervisor_loop.py 'stale-repair' subcommand before autonomous-cycle is run.

Contract:
  - ONLY repairs STALE_QUEUE_ITEM defects (function already exists in source).
  - Stops immediately on any CAPABILITY_GAP (queued function genuinely missing).
  - Does NOT mutate product source files.
  - Does NOT write to taskcards/, .supervisor/, or reports/supervisor/.
  - Produces a repair log at .local/supervisor/stale-repair-log.json.
  - Idempotent: safe to run multiple times.
  - Advisory only: no LLM calls, no external services.

Exit codes:
  0 — no stale items found, or all stale items repaired successfully
  1 — CAPABILITY_GAP detected: queue has pending items with genuinely missing
      functions. Autonomous cycle should investigate before proceeding.
  2 — queue file not found or unreadable
  9 — unexpected error

Sprint: FORMAT-FACTORY-SELF-HEALING-PRODUCT-DEEPENING-RNEXT
Run ID: format-factory-self-healing-product-deepening-rnext-20260611-2000
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR_DIR = _REPO_ROOT / ".local" / "supervisor"


def _import_orchestrator():
    """Import rework_orchestrator from tools/supervisor/."""
    tools_sup = str(Path(__file__).parent)
    if tools_sup not in sys.path:
        sys.path.insert(0, tools_sup)
    import importlib
    return importlib.import_module("rework_orchestrator")


def run_stale_repair(
    repo_root: Path | None = None,
    dry_run: bool = False,
    log_path: Path | None = None,
) -> dict[str, Any]:
    """
    Detect and repair stale pending queue items.

    Returns a result dict:
      status: "OK" | "CAPABILITY_GAP_STOP" | "ERROR"
      stale_repaired: int
      capability_gaps: int
      dry_run: bool
      log_path: str
      details: list[dict]
    """
    root = repo_root or _REPO_ROOT
    log_dest = log_path or (_SUPERVISOR_DIR / "stale-repair-log.json")

    try:
        orch_mod = _import_orchestrator()
    except Exception as e:
        result = {"status": "ERROR", "error": f"Failed to import rework_orchestrator: {e}",
                  "stale_repaired": 0, "capability_gaps": 0, "dry_run": dry_run}
        _write_log(log_dest, result)
        return result

    try:
        from rework_orchestrator import run_healing_cycle
    except ImportError:
        # fall back to direct import via importlib
        run_healing_cycle = getattr(orch_mod, "run_healing_cycle", None)

    if run_healing_cycle is None:
        result = {"status": "ERROR", "error": "run_healing_cycle not found in rework_orchestrator",
                  "stale_repaired": 0, "capability_gaps": 0, "dry_run": dry_run}
        _write_log(log_dest, result)
        return result

    try:
        cycle = run_healing_cycle(repo_root=root, dry_run=dry_run)
    except Exception as e:
        result = {"status": "ERROR", "error": f"run_healing_cycle raised: {e}",
                  "stale_repaired": 0, "capability_gaps": 0, "dry_run": dry_run}
        _write_log(log_dest, result)
        return result

    # run_cycle returns: repairs_succeeded, gap_items, stop_condition_hit
    stale_repaired = cycle.get("repairs_succeeded", cycle.get("stale_repaired", 0))
    stop_condition = cycle.get("stop_condition_hit", False)
    gap_items = cycle.get("gap_items", [])
    capability_gaps = len(gap_items)

    if stop_condition or capability_gaps > 0:
        status = "CAPABILITY_GAP_STOP"
    else:
        status = "OK"

    result: dict[str, Any] = {
        "status": status,
        "stale_repaired": stale_repaired,
        "capability_gaps": capability_gaps,
        "dry_run": dry_run,
        "stop_condition_hit": stop_condition,
        "cycle_summary": cycle,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "log_path": str(log_dest),
    }
    _write_log(log_dest, result)
    return result


def _write_log(log_path: Path, data: dict) -> None:
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass  # log write failure never blocks repair


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Stale queue repair hook")
    parser.add_argument("--dry-run", action="store_true", help="Detect but do not repair")
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--log-path", type=Path, default=None)
    args = parser.parse_args()

    result = run_stale_repair(
        repo_root=args.repo_root,
        dry_run=args.dry_run,
        log_path=args.log_path,
    )

    status = result.get("status")
    stale = result.get("stale_repaired", 0)
    gaps = result.get("capability_gaps", 0)

    print(f"Status: {status}")
    print(f"Stale items repaired: {stale}")
    print(f"Capability gaps detected: {gaps}")
    if result.get("dry_run"):
        print("Mode: dry-run (no queue mutations)")
    print(f"Log: {result.get('log_path')}")

    if status == "CAPABILITY_GAP_STOP":
        print("WARNING: CAPABILITY_GAP detected — autonomous cycle should investigate before proceeding.")
        return 1
    if status == "ERROR":
        print(f"ERROR: {result.get('error')}", file=sys.stderr)
        return 9
    return 0


if __name__ == "__main__":
    sys.exit(main())
