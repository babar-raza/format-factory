"""Event-sourced repository plan control.

RETIRED (FF6-RECONSTRUCTION-001 R14, 2026-08-31)
-------------------------------------------------
This subsystem was bootstrapped but never activated: 0 plans, 0 tasks,
0 journal entries, 0 projections.  Its schema is incompatible with the
FF6 controller.  The authority decision record
(docs/authority-decision-record.md §14) formally retires it.

The FF6 goal driver (tools/ff6/goal_driver.py) and its obligation/
reconciliation stores are the sole production authority.  Plan Control
concepts (journal, projection) are already implemented in the FF6
event journal (plans/strategic/ff6/events.jsonl).

This package is preserved in the repository for historical reference
but MUST NOT be used for new work.  No runtime path should import it.
"""

import warnings as _warnings

_warnings.warn(
    "tools.plan_control is retired (FF6-RECONSTRUCTION-001 R14). "
    "Use tools.ff6.goal_driver instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .engine import PlanControlEngine
from .models import AuthorityMode, ExecutionState

__all__ = ["AuthorityMode", "ExecutionState", "PlanControlEngine"]
__version__ = "0.1.0"
