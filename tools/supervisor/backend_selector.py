"""
Format Factory — Backend Selector
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Selects the highest-priority available backend for a given action.
Priority: SUPERPOWERS → SESSION_SKILL_TOOL → CLAUDE_AGENT_SUBAGENT → REPO_LOCAL_SKILL
          → TASK_MASTER_MCP / MCP_SUPERPOWERS → LLM_API → LOCAL_DETERMINISTIC
          → CLAUDE_CLI_OPTIONAL (external only) → MANUAL_EXTERNAL_GATE
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from tools.supervisor.execution_backend import BackendStatus, BackendType, ExecutionBackend
from tools.supervisor.forbidden_actions import TRUE_EXTERNAL_GATE_ACTION_TYPES

# Forbidden action types that the selector must refuse to execute.
# This was the widest of four independently-drifted copies (see
# tools/supervisor/forbidden_actions.py); it is now the canonical source,
# imported here rather than redefined.
FORBIDDEN_ACTION_TYPES = TRUE_EXTERNAL_GATE_ACTION_TYPES


class BackendSelectionTrace:
    """Records why each backend was accepted or skipped."""

    def __init__(self):
        self.skipped: List[Dict] = []
        self.selected: Optional[str] = None
        self.selection_reason: str = ""
        self.blocked: bool = False
        self.block_reason: str = ""

    def skip(self, backend: str, reason: str):
        self.skipped.append({"backend": backend, "reason": reason})

    def select(self, backend: str, reason: str):
        self.selected = backend
        self.selection_reason = reason

    def block(self, reason: str):
        self.blocked = True
        self.block_reason = reason

    def to_dict(self) -> dict:
        return {
            "selected": self.selected,
            "selection_reason": self.selection_reason,
            "skipped": self.skipped,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
        }


def select_backend(
    action: Dict[str, Any],
    backends: List[ExecutionBackend],
    runtime_status: Optional[Dict] = None,
) -> Tuple[Optional[ExecutionBackend], BackendSelectionTrace]:
    """
    Select the best backend for the action.

    Returns (backend, trace). backend is None if blocked or no suitable backend found.
    """
    trace = BackendSelectionTrace()
    action_type = action.get("action_type", "")
    preferred = action.get("preferred_backend", "")
    fallbacks = action.get("fallback_backends", [])

    # Hard block: forbidden action types
    if action_type in FORBIDDEN_ACTION_TYPES:
        trace.block(f"Action type {action_type} is forbidden — requires human authorization")
        return None, trace

    # Hard block: external_gate
    if action.get("external_gate"):
        trace.block("external_gate=true — requires human intervention")
        return None, trace

    # Build priority list: preferred first, then fallbacks, then all backends in priority order
    preferred_list: List[str] = []
    if preferred:
        preferred_list.append(preferred)
    preferred_list.extend(fallbacks)

    # Build a dict of backends by type name
    backend_map: Dict[str, ExecutionBackend] = {b.backend_type.value: b for b in backends}

    # Check CLAUDECODE env — CLI backend forbidden inside session
    in_claudecode = os.environ.get("CLAUDECODE", "").strip() not in ("", "0")

    # Try preferred/fallback order first, then remaining backends by priority
    all_type_names = [
        BackendType.SUPERPOWERS_LOCAL_PLUGIN.value,
        BackendType.SESSION_SKILL_TOOL.value,
        BackendType.CLAUDE_AGENT_SUBAGENT.value,
        BackendType.REPO_LOCAL_SKILL.value,
        BackendType.MCP_SUPERPOWERS.value,
        BackendType.TASK_MASTER_MCP.value,
        BackendType.LLM_API.value,
        BackendType.LOCAL_DETERMINISTIC.value,
        BackendType.CLAUDE_CLI_OPTIONAL.value,
        BackendType.MANUAL_EXTERNAL_GATE.value,
    ]

    ordered = preferred_list + [t for t in all_type_names if t not in preferred_list]

    for type_name in ordered:
        backend = backend_map.get(type_name)
        if backend is None:
            trace.skip(type_name, "backend not registered")
            continue

        # Special rule: CLAUDE_CLI_OPTIONAL forbidden inside CLAUDECODE
        if type_name == BackendType.CLAUDE_CLI_OPTIONAL.value and in_claudecode:
            trace.skip(type_name, "CLAUDE_CLI_OPTIONAL forbidden inside CLAUDECODE session")
            continue

        status = backend.discover()

        if status == BackendStatus.VERIFIED_CALLABLE:
            if backend.can_execute(action):
                trace.select(type_name, "discover()=VERIFIED_CALLABLE; can_execute=True")
                return backend, trace
            else:
                trace.skip(type_name, f"discover()=VERIFIED_CALLABLE but can_execute=False for action_type={action_type}")
        elif status in (BackendStatus.CONFIG_PRESENT, BackendStatus.CONFIG_ONLY):
            trace.skip(type_name, f"discover()={status.value} — config only, not callable")
        elif status == BackendStatus.SETUP_REQUIRED:
            trace.skip(type_name, "discover()=SETUP_REQUIRED — install needed")
        elif status == BackendStatus.BLOCKED_BY_CREDENTIALS:
            trace.skip(type_name, "discover()=BLOCKED_BY_CREDENTIALS — credential missing")
        elif status == BackendStatus.NOT_FOUND:
            trace.skip(type_name, "discover()=NOT_FOUND")
        elif status == BackendStatus.FORBIDDEN_IN_SESSION:
            trace.skip(type_name, "discover()=FORBIDDEN_IN_SESSION")
        else:
            trace.skip(type_name, f"discover()={status.value}")

    # No suitable backend found
    trace.block("No available backend can execute this action")
    return None, trace
