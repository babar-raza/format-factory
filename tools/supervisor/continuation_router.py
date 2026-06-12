"""
Format Factory — Continuation Router
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

Routes orchestrator to the next executable action.
Rejects advisory Markdown, product prompts, and unsafe items.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.continuation_state import (
    STOP_ADVISORY_PROMPT,
    STOP_INVALID_NEXT_ACTION,
    STOP_NO_SAFE_ACTION,
    is_advisory_prompt,
    is_action_safe,
    load_active_continuation,
    load_next_action,
    validate_active_continuation,
    write_stop_reason,
)
from tools.supervisor.next_action_schema import validate_next_action, NextActionValidationError


# ── Decision codes ────────────────────────────────────────────────────────────
ROUTE_DISPATCH = "DISPATCH_NEXT_ACTION"
ROUTE_STOP_ADVISORY = "STOP_ADVISORY_PROMPT_QUARANTINED"
ROUTE_STOP_INVALID = "STOP_INVALID_NEXT_ACTION"
ROUTE_STOP_NO_ACTION = "STOP_NO_SAFE_ACTION"
ROUTE_STOP_UNSAFE = "STOP_UNSAFE_ACTION"
ROUTE_STOP_NO_CONTINUATION = "STOP_NO_ACTIVE_CONTINUATION"


class RoutingDecision:
    def __init__(
        self,
        decision: str,
        action: Optional[Dict[str, Any]] = None,
        stop_reason: Optional[str] = None,
        detail: str = "",
    ):
        self.decision = decision
        self.action = action
        self.stop_reason = stop_reason
        self.detail = detail
        self.should_dispatch = decision == ROUTE_DISPATCH

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "should_dispatch": self.should_dispatch,
            "stop_reason": self.stop_reason,
            "detail": self.detail,
            "action_id": self.action.get("action_id") if self.action else None,
        }


def route(
    run_id: str = "orchestrator",
    cycle_index: int = 0,
    next_action_override: Optional[str] = None,
) -> RoutingDecision:
    """
    Determine what the orchestrator should do next.

    Returns RoutingDecision with:
    - DISPATCH_NEXT_ACTION: safe action ready, call runner
    - STOP_*: must stop, reason encoded
    """
    # 1. Load active continuation
    cont = load_active_continuation()
    if cont is None:
        return RoutingDecision(
            ROUTE_STOP_NO_CONTINUATION,
            stop_reason=STOP_NO_SAFE_ACTION,
            detail="active-continuation.json does not exist",
        )

    # 2. Check autonomous_continue
    if not cont.get("autonomous_continue", False):
        sr = cont.get("stop_reason", "autonomous_continue=false")
        return RoutingDecision(
            ROUTE_STOP_NO_CONTINUATION,
            stop_reason=STOP_NO_SAFE_ACTION,
            detail=f"autonomous_continue=false: {sr}",
        )

    # 3. Validate continuation
    errors = validate_active_continuation(cont)
    if errors:
        write_stop_reason(run_id, STOP_INVALID_NEXT_ACTION, str(errors), cycle_index)
        return RoutingDecision(
            ROUTE_STOP_INVALID,
            stop_reason=STOP_INVALID_NEXT_ACTION,
            detail=str(errors),
        )

    # 4. Resolve next-action path
    nap = next_action_override or cont.get("next_action_path")
    if not nap:
        write_stop_reason(run_id, STOP_NO_SAFE_ACTION, "next_action_path missing", cycle_index)
        return RoutingDecision(ROUTE_STOP_NO_ACTION, stop_reason=STOP_NO_SAFE_ACTION, detail="next_action_path missing")

    # 5. Reject advisory prompts
    if is_advisory_prompt(str(nap)):
        write_stop_reason(run_id, STOP_ADVISORY_PROMPT, f"path is advisory: {nap}", cycle_index)
        return RoutingDecision(
            ROUTE_STOP_ADVISORY,
            stop_reason=STOP_ADVISORY_PROMPT,
            detail=f"Advisory prompt cannot be executed: {nap}",
        )

    # 6. Load next-action
    action = load_next_action(nap)
    if action is None:
        write_stop_reason(run_id, STOP_INVALID_NEXT_ACTION, f"next-action not found: {nap}", cycle_index)
        return RoutingDecision(ROUTE_STOP_INVALID, stop_reason=STOP_INVALID_NEXT_ACTION, detail=f"File not found: {nap}")

    # 7. Schema validation
    try:
        validate_next_action(action)
    except NextActionValidationError as e:
        write_stop_reason(run_id, STOP_INVALID_NEXT_ACTION, str(e), cycle_index)
        return RoutingDecision(ROUTE_STOP_INVALID, stop_reason=STOP_INVALID_NEXT_ACTION, detail=str(e))

    # 8. Safety check
    safe, reason = is_action_safe(action)
    if not safe:
        write_stop_reason(run_id, STOP_INVALID_NEXT_ACTION, reason, cycle_index)
        return RoutingDecision(ROUTE_STOP_UNSAFE, stop_reason=STOP_INVALID_NEXT_ACTION, detail=reason)

    return RoutingDecision(ROUTE_DISPATCH, action=action)


if __name__ == "__main__":
    decision = route()
    print(json.dumps(decision.to_dict(), indent=2))
    sys.exit(0 if decision.should_dispatch else 1)
