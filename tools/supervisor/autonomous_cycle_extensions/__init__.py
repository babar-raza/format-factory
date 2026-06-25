"""autonomous_cycle_extensions — optional session-start hooks for autonomous_cycle.py.

These hooks extend autonomous_cycle.py without modifying it (LOC cap workaround).
To activate a hook, add a 2-line try/import block at the desired step in autonomous_cycle.py:

    try:
        from autonomous_cycle_extensions.knowledge_freshness_hook import run_hook
        run_hook()
    except Exception:
        pass  # Non-blocking — never fail the sprint

TC-P3-002 note: wiring into autonomous_cycle.py requires LOC reclaim sprint first
(current cap: 2465/2465, zero headroom). See TC-P3-002-SUB-001.
"""
import json
from pathlib import Path


def enrich_goals_with_compiled_taskcards(all_goals: list, repo_root: Path) -> None:
    """TC-SH-003: Enrich gap-ledger goals with compiled taskcard metadata.

    Reads compiled-gap-taskcards.json and adds compiled_taskcard_id/path
    to matching goals by gap_id. Also sets gap_ledger_ref (TC-GUARD-001 requirement).
    Best-effort: errors are silently ignored.
    """
    try:
        compiled_path = repo_root / ".local" / "supervisor" / "compiled-gap-taskcards.json"
        if not compiled_path.exists():
            return
        cgd = json.loads(compiled_path.read_text(encoding="utf-8"))
        index = {}
        for cg in cgd.get("compiled", []):
            gid = cg.get("gap_id", "")
            if gid and cg.get("status") == "compiled":
                index[gid] = cg
        for goal in all_goals:
            gid = goal.get("gap_id", "")
            if gid in index:
                goal["compiled_taskcard_id"] = index[gid].get("taskcard_id")
                goal["compiled_taskcard_path"] = index[gid].get("taskcard_path")
                goal["gap_ledger_ref"] = gid  # TC-GUARD-001 requires this field
    except Exception:
        pass
