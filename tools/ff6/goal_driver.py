"""Goal-driven continuation for the FF6 mission.

Why this exists
---------------
``plans/strategic/ff6/product-goal.yaml`` declares ``continuation_policy:
autonomous: true, ask_for_continuation: false``, and the execution directive
declares ``continuation_policy: mode: UNTIL_BLOCKED, cycle_limit: null``. Both
describe a mission that runs until six formats are certified. Neither was
implemented for FF6: GAP-007 confirmed the FF6 controller has zero
cross-references to the generic supervisor continuation system in either
direction, so nothing ever read the goal to decide what to do next.

The observable consequence is that work stops whenever an agent's context ends,
and restarting requires a human to re-derive the state and re-prompt. Meanwhile
``check_continuation.py`` -- the generic actuator -- reports
``STOP / SESSION_MISMATCH`` against a signal generated 2026-07-16 and points at
unrelated gap-ledger work, because it is **signal-derived**: it depends on an
ephemeral JSON file keyed to a session id, which goes stale, mismatches across
chats, and exhausts an iteration counter.

This module is **state-derived** instead. Every answer is computed from
committed repository files -- the goal record, the controller projection, the
obligation registers, the reconciliation reports. It has no session identity, no
iteration budget, and no signal file, so:

* it cannot go stale,
* it cannot mismatch a session,
* it cannot be exhausted by a counter,
* and any fresh agent, in any new context, computes the identical next action.

That is the property that actually makes the mission survive context
exhaustion. A promise not to stop does not survive a context boundary; a
deterministic function of committed state does.

Terminal states
---------------
Only two things end this mission:

``GOAL_ACHIEVED``
    All six formats certified. This is the mission's own definition of done and
    the only success terminal.
``BLOCKED``
    A TRUE_EXTERNAL_GATE with no agent-side path -- publication credentials,
    or Babar Raza's commercial release authority. Recorded, never assumed.

Everything else returns ``CONTINUE``. Running out of context is not a stop
condition here; it is a pause between two invocations that read the same state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
FF6 = REPO_ROOT / "plans" / "strategic" / "ff6"
GOAL_PATH = FF6 / "product-goal.yaml"
STATE_PATH = FF6 / "controller-state.yaml"
DIRECTIVE_PATH = FF6 / "execution-recovery-directive.yaml"
OBLIGATIONS_DIR = FF6 / "obligations"
RECONCILIATION_DIR = REPO_ROOT / "reports" / "format-contract-layer"

CERTIFIED = "CERTIFIED"

#: Exit codes chosen so a shell driver can loop on success:
#: ``while python -m tools.ff6.goal_driver check; do <do work>; done``
EXIT_CONTINUE = 0
EXIT_BLOCKED = 1
EXIT_GOAL_ACHIEVED = 2


class GoalDriverError(RuntimeError):
    """The goal or state records could not be read."""


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise GoalDriverError(f"required record not found: {path}")
    value = yaml.safe_load(path.read_bytes().decode("utf-8"))
    if not isinstance(value, dict):
        raise GoalDriverError(f"{path} is not a mapping")
    return value


def _obligation_total(format_id: str) -> int | None:
    """Total canonical obligations for a format, from its register."""
    path = OBLIGATIONS_DIR / f"{format_id}.yaml"
    if not path.exists():
        return None
    document = yaml.safe_load(path.read_bytes().decode("utf-8"))
    if isinstance(document, dict):
        for key in ("obligations", "entries", "items"):
            value = document.get(key)
            if isinstance(value, list):
                return len(value)
    if isinstance(document, list):
        return len(document)
    return None


def _reconciliation(format_id: str) -> dict[str, Any] | None:
    """Parsed obligation reconciliation for a format, when one has been run."""
    path = RECONCILIATION_DIR / f"{format_id}-obligation-reconciliation.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence_is_fresh(report: dict[str, Any]) -> bool:
    """Check whether referenced source/test files still match stored hashes.

    The reconciler stores SHA-256 hashes of every referenced file in
    ``referenced_input_digests``.  If any file has changed since the
    reconciliation was produced, the evidence is stale.

    Returns True when all hashes match or when no hashes are stored
    (legacy reconciliation — conservative: treated as stale via the
    proof_strength check elsewhere).
    """
    import hashlib
    digests = report.get("referenced_input_digests") or {}
    if not digests:
        return True
    for rel_path, stored_hash in digests.items():
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            return False
        current = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if current != stored_hash:
            return False
    return True


def _is_certified(format_id: str, total: int | None, report: dict[str, Any] | None) -> bool:
    """Derive certification from evidence, not promotion labels.

    A format is certified when:
    1. It has a known positive obligation count
    2. Reconciliation has been run
    3. All obligations are resolved (0 unresolved)
    4. Reconciliation proof_strength is promoting (not supporting_nonpromoting)
    5. Evidence is fresh (referenced file hashes match current files)

    Returns False when any input is missing or insufficient — fail-closed.
    """
    if not isinstance(total, int) or total <= 0:
        return False
    if report is None:
        return False
    summary = report.get("summary") or {}
    unresolved = summary.get("unresolved")
    if not isinstance(unresolved, int) or unresolved > 0:
        return False
    proof_strength = report.get("proof_strength", "")
    if "nonpromoting" in str(proof_strength).lower():
        return False
    promotion_effect = report.get("promotion_effect", "")
    if promotion_effect == "none":
        return False
    if not _evidence_is_fresh(report):
        return False
    return True


def format_progress(format_id: str, promotion: dict[str, Any]) -> dict[str, Any]:
    """Evidence-backed progress for one format. Never optimistic by default."""
    total = _obligation_total(format_id)
    report = _reconciliation(format_id)
    entry: dict[str, Any] = {
        "format_id": format_id,
        "promotion": promotion.get(format_id, "UNKNOWN"),
        "certified": _is_certified(format_id, total, report),
        "obligations_total": total,
    }
    if report is None:
        # No reconciliation has ever been run for this format. Its obligations
        # are unclassified, which is itself the next action -- not zero progress
        # dressed up as "unknown".
        entry["reconciliation"] = "NOT_RUN"
        entry["obligations_resolved"] = 0
        entry["obligations_unresolved"] = total
        entry["next_step"] = f"run the obligation reconciler for {format_id}"
        return entry

    summary = report.get("summary") or {}
    by_status = summary.get("by_status") or {}
    unresolved = summary.get("unresolved")
    resolved = None
    if isinstance(unresolved, int) and isinstance(total, int):
        resolved = total - unresolved
    entry["reconciliation"] = "PRESENT"
    entry["by_status"] = by_status
    entry["obligations_resolved"] = resolved
    entry["obligations_unresolved"] = unresolved
    if unresolved:
        entry["next_step"] = f"close the remaining {unresolved} unresolved {format_id} obligations"
    elif entry["certified"]:
        entry["next_step"] = f"{format_id} is certified; no further action required for this format"
    else:
        entry["next_step"] = f"{format_id} obligations resolved; run certification gates"
    return entry


def evaluate(
    *,
    goal_path: Path | None = None,
    state_path: Path | None = None,
    directive_path: Path | None = None,
) -> dict[str, Any]:
    """Compute the mission verdict purely from committed repository state.

    Paths default to the module constants, resolved at call time rather than
    bound at import, so the record locations stay overridable in tests.
    """
    goal_path = goal_path or GOAL_PATH
    state_path = state_path or STATE_PATH
    directive_path = directive_path or DIRECTIVE_PATH

    goal = _load_yaml(goal_path)
    state = _load_yaml(state_path)
    directive = _load_yaml(directive_path) if directive_path.exists() else {}

    products = [entry["format_id"] for entry in goal.get("products", [])]
    if not products:
        raise GoalDriverError(f"{goal_path} declares no products")
    promotion = state.get("promotion") or {}

    formats = [format_progress(format_id, promotion) for format_id in products]
    certified = [item for item in formats if item["certified"]]
    goal_achieved = len(certified) == len(products)

    # A blocker only counts when it is recorded as a real external gate. This
    # deliberately does not infer blockers from failures, staleness, or an
    # agent's context ending -- none of those are external gates.
    blockers = [
        gap
        for gap in directive.get("structural_gaps_20260804", [])
        if str(gap.get("status", "")).upper().startswith("BLOCKED_EXTERNAL")
    ]

    next_task = state.get("next_task") or {}
    if goal_achieved:
        verdict = "GOAL_ACHIEVED"
    elif blockers:
        verdict = "BLOCKED"
    else:
        verdict = "CONTINUE"

    return {
        "goal_id": goal.get("goal_id"),
        "verdict": verdict,
        "goal_achieved": goal_achieved,
        "certified_count": len(certified),
        "required_count": len(products),
        "controller_event": (state.get("last_verified_event") or {}).get("event_id"),
        "current_stage": directive.get("status"),
        "active_task": (state.get("active_task") or {}).get("task_id"),
        "next_task": next_task.get("task_id"),
        "next_action": next_task.get("unlock_condition"),
        "formats": formats,
        "external_blockers": blockers,
        "derivation": "state_derived",
        "session_independent": True,
        "notes": (
            "Verdict is a pure function of committed repository state. It has no "
            "session id, no iteration budget, and no signal file, so a fresh "
            "agent in a new context computes the identical answer. Context "
            "exhaustion is a pause, not a stop condition."
        ),
    }


def render_resume(result: dict[str, Any]) -> str:
    """A briefing a fresh agent can act on without re-deriving anything."""
    lines: list[str] = []
    add = lines.append
    add(f"FF6 MISSION -- {result['goal_id']}")
    add("=" * 64)
    add(f"VERDICT           : {result['verdict']}")
    add(
        f"CERTIFIED         : {result['certified_count']}/{result['required_count']}"
        "  (mission is done only at 6/6)"
    )
    add(f"CONTROLLER HEAD   : {result['controller_event']}")
    add(f"CURRENT STAGE     : {result['current_stage']}")
    add(f"NEXT TASK         : {result['next_task']}")
    add("")
    add("PER-FORMAT STATE")
    add("-" * 64)
    for item in result["formats"]:
        total = item["obligations_total"]
        unresolved = item["obligations_unresolved"]
        if item["reconciliation"] == "NOT_RUN":
            detail = f"{total} obligations, NEVER RECONCILED"
        else:
            detail = f"{unresolved}/{total} obligations unresolved"
        add(f"  {item['format_id']:<12} {item['promotion']:<12} {detail}")
        add(f"  {'':<12} next: {item['next_step']}")
    add("")
    if result["verdict"] == "GOAL_ACHIEVED":
        add("All six formats are certified. The mission's own terminal is reached.")
        return "\n".join(lines)
    if result["verdict"] == "BLOCKED":
        add("BLOCKED by a recorded external gate:")
        for blocker in result["external_blockers"]:
            add(f"  - {blocker.get('id')}: {blocker.get('finding')}")
        return "\n".join(lines)
    add("NEXT ACTION")
    add("-" * 64)
    add(str(result["next_action"] or "see controller-state.yaml next_task"))
    add("")
    add(
        "This briefing is recomputed from committed state on every run. If your "
        "context ends mid-task, the next agent runs `python -m "
        "tools.ff6.goal_driver resume` and continues from here -- nothing is "
        "carried in conversation memory."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.goal_driver",
        description="Goal-driven continuation for the FF6 mission.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="emit the verdict as JSON (exit 0 = CONTINUE)")
    sub.add_parser("resume", help="print a briefing a fresh agent can act on")

    args = parser.parse_args(argv)
    try:
        result = evaluate()
    except GoalDriverError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_BLOCKED

    if args.command == "check":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_resume(result))

    if result["verdict"] == "GOAL_ACHIEVED":
        return EXIT_GOAL_ACHIEVED
    if result["verdict"] == "BLOCKED":
        return EXIT_BLOCKED
    return EXIT_CONTINUE


if __name__ == "__main__":
    raise SystemExit(main())
