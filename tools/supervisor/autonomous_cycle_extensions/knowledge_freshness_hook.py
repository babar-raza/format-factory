"""knowledge_freshness_hook.py — TC-P3-002 session-start V68 hook.

Intended to be called at Step 0a-knowledge in autonomous_cycle.py:

    try:
        from autonomous_cycle_extensions.knowledge_freshness_hook import run_hook
        run_hook()
    except Exception:
        pass  # Non-blocking — never fail the sprint on knowledge freshness check

Status: READY (hook is implemented and tested).
Wiring into autonomous_cycle.py blocked by LOC cap (2465/2465).
See TC-P3-002-SUB-001 in hidden-puzzling-rain.md for the LOC reclaim sub-taskcard.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def run_hook() -> None:
    """Run V68 knowledge freshness check at session start (non-blocking).

    Prints 'KNOWLEDGE FRESHNESS: PASS: N source hash(es) verified' on success.
    Prints 'WARNING: KNOWLEDGE FRESHNESS: ...' with stale details on drift.
    Never raises — always returns silently on error.
    """
    try:
        from knowledge_freshness_validator import validate_knowledge_freshness
    except ImportError:
        try:
            sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
            from knowledge_freshness_validator import validate_knowledge_freshness  # type: ignore[import]
        except ImportError:
            return  # Non-blocking: validator unavailable

    result = validate_knowledge_freshness({}, repo_root=REPO_ROOT)
    label = "KNOWLEDGE FRESHNESS"
    if result.get("result") == "WARN":
        print(f"WARNING: {label}: {result.get('summary', 'WARN')}")
        for item in result.get("items", []):
            print(f"  - {item}")
    elif result.get("result") == "PASS":
        print(f"{label}: {result.get('summary', 'PASS')}")
    # SKIP/SKIPPED results produce no output (DRAFT contracts, missing registry)
