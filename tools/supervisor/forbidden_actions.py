"""
Format Factory — Canonical Forbidden Action Types

Single source of truth for action types that must never be executed by
autonomous machinery under any circumstance: destructive git operations,
human-only business/publication gates, and MCP activation. Four modules
previously each defined their own independent copy of this set
(product_action_guard.py, action_queue.py, continuation_state.py,
backend_selector.py); they had already drifted — backend_selector.py's copy
included PYPI_PUBLISH/NUGET_PUBLISH, the other three did not, so an action
of either type could be accepted by the queue and the continuation-state
safety check while only being caught later, at backend selection.

Consume this set by import; do not redefine it locally.
"""
from __future__ import annotations

TRUE_EXTERNAL_GATE_ACTION_TYPES = frozenset({
    "GIT_PUSH", "GIT_COMMIT", "GIT_RESET", "GIT_CLEAN", "GIT_STASH",
    "GATE_8_APPROVAL", "GATE_11_APPROVAL",
    "PACKAGE_PUBLISH", "PYPI_PUBLISH", "NUGET_PUBLISH",
    "MCP_ACTIVATE", "MUTATE_POC_TARGETS",
})
