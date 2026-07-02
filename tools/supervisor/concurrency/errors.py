"""Exception classes for the concurrency control package."""
from __future__ import annotations


class MissionLockConflict(RuntimeError):
    """Raised when a mission lock cannot be acquired due to an active live owner."""

    def __init__(
        self,
        mission_id: str,
        existing_lock_id: str,
        existing_controller: str,
        existing_pid: int,
        heartbeat_at: str,
    ) -> None:
        self.mission_id = mission_id
        self.existing_lock_id = existing_lock_id
        self.existing_controller = existing_controller
        self.existing_pid = existing_pid
        self.heartbeat_at = heartbeat_at
        super().__init__(
            f"Mission '{mission_id}' is locked by {existing_controller} "
            f"(PID {existing_pid}, heartbeat {heartbeat_at}). "
            f"lock_id={existing_lock_id}"
        )


class PathOwnershipConflict(RuntimeError):
    """Raised when a path claim conflicts with an existing WRITE claim."""

    def __init__(
        self,
        path: str,
        existing_worker_id: str,
        existing_task_id: str,
        existing_claim_id: str,
    ) -> None:
        self.path = path
        self.existing_worker_id = existing_worker_id
        self.existing_task_id = existing_task_id
        self.existing_claim_id = existing_claim_id
        super().__init__(
            f"Path '{path}' is owned by worker '{existing_worker_id}' "
            f"(task '{existing_task_id}', claim '{existing_claim_id}')"
        )


class StaleBaseRevision(UserWarning):
    """Emitted when a checkpoint's base_sha does not match current HEAD.

    This is a UserWarning (not an exception) so callers can decide
    whether to proceed (integration drift recovery) or abort.
    """

    def __init__(self, checkpoint_base_sha: str, current_sha: str) -> None:
        self.checkpoint_base_sha = checkpoint_base_sha
        self.current_sha = current_sha
        super().__init__(
            f"Checkpoint base {checkpoint_base_sha[:8]} != current HEAD {current_sha[:8]}. "
            f"Integration drift detected — applying patch may produce conflicts."
        )


class CheckpointError(RuntimeError):
    """Raised for checkpoint-related failures (missing file, apply failure, etc.)."""


class LockNotHeld(RuntimeError):
    """Raised when an operation requires a lock that is not ACTIVE."""
