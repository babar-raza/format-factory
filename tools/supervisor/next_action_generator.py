"""
Format Factory — Next Action Generator
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

Generates the next safe executable action for the autonomy loop.
Never generates product work, commit/push, or gate approval actions.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
sys.path.insert(0, str(_repo_root))

# ── Safe action templates ─────────────────────────────────────────────────────

SAFE_ACTION_TYPES = [
    "RUN_JSON_VALIDATION",
    "RUN_MD_NONEMPTY_CHECK",
    "RUN_YAML_VALIDATION",
    "RUN_COMMAND_DISCOVERY",
    "GENERATE_EVIDENCE_STUB",
]

FORBIDDEN_STREAM_ACTIONS = {
    "GIT_PUSH", "GIT_COMMIT", "GIT_RESET", "GIT_CLEAN", "GIT_STASH",
    "GATE_8_APPROVAL", "GATE_11_APPROVAL", "PACKAGE_PUBLISH",
    "MCP_ACTIVATE", "MUTATE_POC_TARGETS",
}

# Default targets that are always safe to validate
DEFAULT_JSON_TARGETS = [
    ".local/supervisor/active-continuation.json",
    ".local/supervisor/orchestrator-state.json",
    "reports/autonomous-orchestrator/current-autonomy-baseline.json",
    "reports/autonomous-orchestrator/lane-claims.json",
]

DEFAULT_MD_TARGETS = [
    "reports/autonomous-orchestrator/00-preflight.md",
    "reports/autonomous-orchestrator/orchestrator/orchestrator-design.md",
    "reports/autonomous-orchestrator/next-action-generation/generation-policy.md",
]

DEFAULT_YAML_TARGETS = [
    ".local/evidences/autonomous-orchestrator/evidence-declaration.yaml",
    ".supervisor/policies.yaml",
]

DEFAULT_WRITE_ROOTS = ["reports/autonomous-orchestrator", ".local/supervisor"]


class GenerationTrace:
    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def record(self, cycle: int, action_type: str, target: str, reason: str) -> None:
        self.entries.append({
            "cycle": cycle,
            "action_type": action_type,
            "target": target,
            "reason": reason,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        return {"entries": self.entries}


_global_trace = GenerationTrace()


def _pick_target(action_type: str, cycle_index: int, prev_result: Optional[Dict[str, Any]]) -> str:
    """Pick a safe, existing target file for the given action type."""
    if action_type == "RUN_JSON_VALIDATION":
        targets = DEFAULT_JSON_TARGETS
    elif action_type == "RUN_MD_NONEMPTY_CHECK":
        targets = DEFAULT_MD_TARGETS
    elif action_type == "RUN_YAML_VALIDATION":
        targets = DEFAULT_YAML_TARGETS
    else:
        return ""

    # Try to find an existing file
    for t in targets:
        p = _repo_root / t
        if p.exists():
            return t

    # Fallback: use the first target regardless (will fail validation but not crash)
    return targets[0] if targets else ""


def _cycle_action_type(cycle_index: int) -> str:
    """Deterministically rotate through safe action types by cycle index."""
    types = ["RUN_JSON_VALIDATION", "RUN_MD_NONEMPTY_CHECK", "RUN_YAML_VALIDATION",
             "RUN_COMMAND_DISCOVERY", "GENERATE_EVIDENCE_STUB"]
    return types[cycle_index % len(types)]


def generate_next_action(
    prev_result: Optional[Dict[str, Any]],
    cycle_index: int,
    sprint_id: str,
    allowed_write_roots: Optional[List[str]] = None,
    action_type_override: Optional[str] = None,
    target_override: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generate the next safe action dict.

    Returns None if no safe action can be generated (orchestrator should stop).
    """
    roots = allowed_write_roots or DEFAULT_WRITE_ROOTS

    # Determine action type
    action_type = action_type_override or _cycle_action_type(cycle_index)

    if action_type in FORBIDDEN_STREAM_ACTIONS:
        _global_trace.record(cycle_index, action_type, "", "FORBIDDEN action type — stop generation")
        return None

    # Determine target
    if action_type == "RUN_COMMAND_DISCOVERY":
        target = ""
        result_path = f"reports/autonomous-orchestrator/proof-run/cycle-{cycle_index:03d}-result.json"
        action = {
            "action_id": f"orch-cycle-{cycle_index:03d}",
            "action_type": "RUN_COMMAND_DISCOVERY",
            "objective": f"Orchestrator cycle {cycle_index}: discover available commands",
            "preferred_backend": "LOCAL_DETERMINISTIC",
            "fallback_backends": [],
            "result_path": result_path,
            "allowed_write_roots": roots,
            "evidence_required": True,
            "cycle_number": cycle_index,
            "sprint_id": sprint_id,
            "previous_cycle_result": prev_result.get("result_path") if prev_result else None,
            "external_gate": False,
            "success_conditions": [
                "result_path written by runner",
                "backend_used=LOCAL_DETERMINISTIC",
            ],
        }
        _global_trace.record(cycle_index, action_type, "command_discovery", "Generated command discovery action")
        return action

    if action_type == "GENERATE_EVIDENCE_STUB":
        stub_path = f"reports/autonomous-orchestrator/proof-run/evidence-stub-{cycle_index:03d}.json"
        action = {
            "action_id": f"orch-cycle-{cycle_index:03d}",
            "action_type": "GENERATE_EVIDENCE_STUB",
            "objective": f"Orchestrator cycle {cycle_index}: generate evidence stub",
            "preferred_backend": "LOCAL_DETERMINISTIC",
            "fallback_backends": [],
            "stub_path": stub_path,
            "result_path": f"reports/autonomous-orchestrator/proof-run/cycle-{cycle_index:03d}-result.json",
            "allowed_write_roots": roots,
            "evidence_required": True,
            "cycle_number": cycle_index,
            "sprint_id": sprint_id,
            "previous_cycle_result": prev_result.get("result_path") if prev_result else None,
            "external_gate": False,
        }
        _global_trace.record(cycle_index, action_type, stub_path, "Generated evidence stub action")
        return action

    target = target_override or _pick_target(action_type, cycle_index, prev_result)
    if not target:
        _global_trace.record(cycle_index, action_type, "", "No valid target found — stop")
        return None

    result_path = f"reports/autonomous-orchestrator/proof-run/cycle-{cycle_index:03d}-result.json"

    action = {
        "action_id": f"orch-cycle-{cycle_index:03d}",
        "action_type": action_type,
        "objective": (
            f"Orchestrator cycle {cycle_index}: {action_type} on {target}"
        ),
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "fallback_backends": [],
        "target": target,
        "result_path": result_path,
        "allowed_write_roots": roots,
        "evidence_required": True,
        "cycle_number": cycle_index,
        "sprint_id": sprint_id,
        "previous_cycle_result": prev_result.get("result_path") if prev_result else None,
        "external_gate": False,
        "success_conditions": [
            f"target file validates as {action_type}",
            "result_path written by runner",
            "backend_used=LOCAL_DETERMINISTIC",
        ],
    }

    _global_trace.record(cycle_index, action_type, target, f"Generated {action_type} action")
    return action


def get_generation_trace() -> Dict[str, Any]:
    return _global_trace.to_dict()


def save_generation_trace(path: str) -> None:
    p = _repo_root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(_global_trace.to_dict(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    # Quick test
    action = generate_next_action(None, 1, "FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001")
    print(json.dumps(action, indent=2))
