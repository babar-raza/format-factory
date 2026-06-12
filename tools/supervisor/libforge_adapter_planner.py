"""
libforge_adapter_planner.py — FF-native LibForge integration adapter planner.

Given the pattern registry, produce a JSON-serializable integration plan
covering which FF tools need extension, which need reimplementation, and
what the safe adoption path is for each pattern.

Sprint: FF-LIBFORGE-REFOCUS-INTEGRATION-001
No live LLM calls. No external repo imports. Pure deterministic logic.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from tools.supervisor.libforge_pattern_registry import (
    AdoptionMode,
    PatternRecord,
    PatternSource,
    get_all_patterns,
    get_ff_missing_gaps,
    get_pattern,
    get_patterns_by_adoption_mode,
    is_safe_to_import,
    to_dict_list,
)


@dataclass
class AdapterAction:
    action_id: str
    pattern_id: str
    action_type: str   # "extend", "implement", "wrap", "defer", "reject"
    target_file: str
    description: str
    blocked_by: str    # dependency or "" if unblocked
    priority: int      # 1=high, 2=medium, 3=low
    safe: bool


@dataclass
class AdapterPlan:
    plan_id: str
    generated_for: str   # sprint_id
    actions: list[AdapterAction]
    rejected_patterns: list[str]
    deferred_patterns: list[str]
    high_priority_gaps: list[str]
    unsafe_imports_blocked: list[str]
    summary: str


# ---------------------------------------------------------------------------
# Planner logic
# ---------------------------------------------------------------------------

def _action_for_record(rec: PatternRecord) -> AdapterAction:
    """Convert a PatternRecord to an AdapterAction."""
    if rec.adoption_mode == AdoptionMode.REJECT_UNSAFE:
        return AdapterAction(
            action_id=f"act-{rec.pattern_id.lower().replace('-', '_')}",
            pattern_id=rec.pattern_id,
            action_type="reject",
            target_file="(blocked)",
            description=f"Rejected: direct import unsafe ({', '.join(rec.unsafe_coupling)})",
            blocked_by="unsafe_coupling",
            priority=rec.priority,
            safe=False,
        )

    if rec.adoption_mode == AdoptionMode.DEFERRED:
        return AdapterAction(
            action_id=f"act-{rec.pattern_id.lower().replace('-', '_')}",
            pattern_id=rec.pattern_id,
            action_type="defer",
            target_file="(deferred)",
            description="Deferred: not needed in current sprint.",
            blocked_by="not_prioritized",
            priority=rec.priority,
            safe=True,
        )

    if rec.ff_mapping is None:
        target = "tools/supervisor/(new file)"
    elif rec.ff_mapping.status == "missing":
        target = rec.ff_mapping.path
    elif rec.ff_mapping.status == "partial":
        target = rec.ff_mapping.path
    else:
        target = rec.ff_mapping.path

    if rec.adoption_mode == AdoptionMode.FF_NATIVE_REIMPLEMENTATION:
        action_type = "implement"
    elif rec.adoption_mode == AdoptionMode.WRAPPER_REUSE_CANDIDATE:
        action_type = "wrap"
    else:
        action_type = "extend"

    has_unsafe = bool(rec.unsafe_coupling)
    return AdapterAction(
        action_id=f"act-{rec.pattern_id.lower().replace('-', '_')}",
        pattern_id=rec.pattern_id,
        action_type=action_type,
        target_file=target,
        description=rec.integration_notes or rec.description,
        blocked_by=(
            "unsafe_coupling_present_but_not_reject"
            if has_unsafe and rec.adoption_mode != AdoptionMode.REJECT_UNSAFE
            else ""
        ),
        priority=rec.priority,
        safe=not has_unsafe or rec.adoption_mode in (
            AdoptionMode.FF_NATIVE_REIMPLEMENTATION,
            AdoptionMode.WRAPPER_REUSE_CANDIDATE,
        ),
    )


def build_plan(
    plan_id: str = "ff-libforge-integration-plan-v1",
    sprint_id: str = "FF-LIBFORGE-REFOCUS-INTEGRATION-001",
) -> AdapterPlan:
    """Build a full integration plan from the pattern registry."""
    records = get_all_patterns()
    actions = []
    rejected = []
    deferred = []
    unsafe_blocked = []

    for rec in records:
        action = _action_for_record(rec)
        actions.append(action)
        if action.action_type == "reject":
            rejected.append(rec.pattern_id)
        elif action.action_type == "defer":
            deferred.append(rec.pattern_id)
        if rec.unsafe_coupling and rec.adoption_mode == AdoptionMode.REJECT_UNSAFE:
            unsafe_blocked.append(rec.pattern_id)

    high_gaps = [r.pattern_id for r in get_ff_missing_gaps()]
    n_high = sum(1 for a in actions if a.priority == 1)
    n_implement = sum(1 for a in actions if a.action_type == "implement")
    n_safe = sum(1 for a in actions if a.safe)

    summary = (
        f"Plan {plan_id}: {len(actions)} actions total. "
        f"{n_high} high-priority. {n_implement} FF-native implementations needed. "
        f"{n_safe} safe to proceed. "
        f"{len(rejected)} rejected (unsafe coupling). "
        f"{len(deferred)} deferred. "
        f"{len(high_gaps)} high-priority gaps in existing FF tools."
    )

    return AdapterPlan(
        plan_id=plan_id,
        generated_for=sprint_id,
        actions=actions,
        rejected_patterns=rejected,
        deferred_patterns=deferred,
        high_priority_gaps=high_gaps,
        unsafe_imports_blocked=unsafe_blocked,
        summary=summary,
    )


def plan_to_dict(plan: AdapterPlan) -> dict[str, Any]:
    """Convert an AdapterPlan to a JSON-serializable dict."""
    return {
        "plan_id": plan.plan_id,
        "generated_for": plan.generated_for,
        "summary": plan.summary,
        "high_priority_gaps": plan.high_priority_gaps,
        "unsafe_imports_blocked": plan.unsafe_imports_blocked,
        "rejected_patterns": plan.rejected_patterns,
        "deferred_patterns": plan.deferred_patterns,
        "actions": [
            {
                "action_id": a.action_id,
                "pattern_id": a.pattern_id,
                "action_type": a.action_type,
                "target_file": a.target_file,
                "description": a.description,
                "blocked_by": a.blocked_by,
                "priority": a.priority,
                "safe": a.safe,
            }
            for a in plan.actions
        ],
    }


def plan_to_json(plan: AdapterPlan, indent: int = 2) -> str:
    """Serialize an AdapterPlan to JSON string."""
    return json.dumps(plan_to_dict(plan), indent=indent)


def plan_for_pattern(pattern_id: str) -> AdapterAction | None:
    """Return the adapter action for a single pattern, or None if not found."""
    rec = get_pattern(pattern_id)
    if rec is None:
        return None
    return _action_for_record(rec)
