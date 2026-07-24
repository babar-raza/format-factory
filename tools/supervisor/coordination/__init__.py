"""Multi-agent shared-state coordination (Mission AGENT-COORD-2026-07-15).

Ambient coordination plane for concurrent autonomous agents sharing one
working tree: agent registration, atomic leases with parent/child overlap
detection, baseline fingerprints + write attribution, structured conflicts,
recoverable stale-agent takeover, and enforcement hooks.

Subsumes tools/supervisor/concurrency/ (mission CONC-HARDENING-2026-07-02):
MissionLock and WorkerClaims delegate here; CheckpointManager is unchanged.

CLI: python -m tools.supervisor.coordination <verb>   (see verbs.py)
"""

PROTOCOL_VERSION = 1

from .coordinated_io import coordinated_write
from .errors import CoordinationDenied

__all__ = [
    "PROTOCOL_VERSION",
    "coordinated_write",
    "CoordinationDenied",
]
