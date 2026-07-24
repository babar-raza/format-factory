"""Coordination error types. Each carries the CLI exit code it maps to.

Exit-code contract (stable; documented in AGENTS.md Section CO):
  0 ok / 1 error / 2 conflict / 3 not-registered / 4 stale-expired
  5 baseline-drift-preserve / 6 takeover-denied
"""
from __future__ import annotations


class CoordinationError(RuntimeError):
    exit_code = 1


class ResourceEscape(CoordinationError):
    """Resource path resolves outside the worktree (symlink / .. bypass)."""

    exit_code = 2

    def __init__(self, path: str, resolved: str):
        super().__init__(f"resource escapes worktree: {path} -> {resolved}")
        self.path = path
        self.resolved = resolved


class NotRegistered(CoordinationError):
    exit_code = 3

    def __init__(self, detail: str = "no registered agent identity"):
        super().__init__(detail)


class LeaseConflict(CoordinationError):
    exit_code = 2

    def __init__(self, resource_key: str, holder_agent_id: str,
                 holder_lease_id: str, holder_task_id: str | None = None,
                 holder_mode: str = "EXCLUSIVE_WRITE",
                 lease_expires_hint: str | None = None):
        super().__init__(
            f"resource '{resource_key}' is held by agent {holder_agent_id} "
            f"(lease {holder_lease_id}, mode {holder_mode})"
        )
        self.resource_key = resource_key
        self.holder_agent_id = holder_agent_id
        self.holder_lease_id = holder_lease_id
        self.holder_task_id = holder_task_id
        self.holder_mode = holder_mode
        self.lease_expires_hint = lease_expires_hint


class LeaseStale(CoordinationError):
    exit_code = 4

    def __init__(self, lease_id: str, detail: str = "lease is STALE/expired"):
        super().__init__(f"{detail}: {lease_id}")
        self.lease_id = lease_id


class BaselineDrift(CoordinationError):
    """Target file changed underneath the lease -- refuse and preserve."""

    exit_code = 5

    def __init__(self, file_key: str, classification: str,
                 conflict_id: str | None = None,
                 apparent_owner: str | None = None):
        super().__init__(
            f"refusing write to '{file_key}': concurrent change classified "
            f"{classification} (preserve; see conflict {conflict_id})"
        )
        self.file_key = file_key
        self.classification = classification
        self.conflict_id = conflict_id
        self.apparent_owner = apparent_owner


class TakeoverDenied(CoordinationError):
    exit_code = 6

    def __init__(self, lease_id: str, reason: str):
        super().__init__(f"takeover of {lease_id} denied: {reason}")
        self.lease_id = lease_id
        self.reason = reason


class CoordinationDenied(CoordinationError):
    """Preflight refused a coordinated write (conflict, drift, or no identity).

    The ``exit_code`` is set per-instance because the underlying preflight
    deny reason varies (2 = conflict, 3 = not-registered, 5 = baseline-drift).
    """

    def __init__(self, resource: str, reason: str, exit_code: int = 2,
                 conflict_id: str | None = None):
        super().__init__(
            f"coordinated write denied for '{resource}': {reason}")
        self.exit_code = exit_code  # type: ignore[assignment]  # instance override
        self.resource = resource
        self.reason = reason
        self.conflict_id = conflict_id


class GeneratorBlocked(CoordinationError):
    """Generator output manifest overlaps a foreign live lease."""

    exit_code = 2

    def __init__(self, generator_id: str, detail: str):
        super().__init__(f"generator '{generator_id}' blocked: {detail}")
        self.generator_id = generator_id
