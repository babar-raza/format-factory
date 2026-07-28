from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class ExecutionState(StrEnum):
    DISCOVERED = "DISCOVERED"
    PENDING = "PENDING"
    READY = "READY"
    CLAIMED = "CLAIMED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
    ITERATION_REQUIRED = "ITERATION_REQUIRED"
    VERIFIED = "VERIFIED"
    COMPLETE = "COMPLETE"
    COMPLETION_CANDIDATE = "COMPLETION_CANDIDATE"
    TERMINAL_CLOSED = "TERMINAL_CLOSED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    EXTERNALLY_CLAIMED = "EXTERNALLY_CLAIMED"


class AuthorityMode(StrEnum):
    CANONICAL = "CANONICAL"
    CHILD = "CHILD"
    ADVISORY = "ADVISORY"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


TERMINAL_STATES = {
    ExecutionState.VERIFIED,
    ExecutionState.COMPLETE,
    ExecutionState.TERMINAL_CLOSED,
    ExecutionState.CANCELLED,
}

TRANSITIONS: dict[ExecutionState, set[ExecutionState]] = {
    ExecutionState.DISCOVERED: {
        ExecutionState.PENDING,
        ExecutionState.READY,
        ExecutionState.CLAIMED,
        ExecutionState.IN_PROGRESS,
        ExecutionState.BLOCKED,
        ExecutionState.EXTERNALLY_CLAIMED,
        ExecutionState.CANCELLED,
        ExecutionState.COMPLETION_CANDIDATE,
    },
    ExecutionState.PENDING: {
        ExecutionState.READY,
        ExecutionState.CLAIMED,
        ExecutionState.IN_PROGRESS,
        ExecutionState.BLOCKED,
        ExecutionState.EXTERNALLY_CLAIMED,
        ExecutionState.CANCELLED,
        ExecutionState.COMPLETION_CANDIDATE,
    },
    ExecutionState.READY: {
        ExecutionState.CLAIMED,
        ExecutionState.IN_PROGRESS,
        ExecutionState.BLOCKED,
        ExecutionState.EXTERNALLY_CLAIMED,
        ExecutionState.CANCELLED,
        ExecutionState.COMPLETION_CANDIDATE,
    },
    ExecutionState.CLAIMED: {
        ExecutionState.IN_PROGRESS,
        ExecutionState.READY,
        ExecutionState.BLOCKED,
    },
    ExecutionState.IN_PROGRESS: {
        ExecutionState.AWAITING_VERIFICATION,
        ExecutionState.ITERATION_REQUIRED,
        ExecutionState.BLOCKED,
        ExecutionState.READY,
    },
    ExecutionState.AWAITING_VERIFICATION: {
        ExecutionState.VERIFIED,
        ExecutionState.ITERATION_REQUIRED,
        ExecutionState.IN_PROGRESS,
        ExecutionState.BLOCKED,
    },
    ExecutionState.VERIFIED: {
        ExecutionState.COMPLETE,
        ExecutionState.TERMINAL_CLOSED,
        ExecutionState.IN_PROGRESS,
    },
    ExecutionState.COMPLETE: {
        ExecutionState.COMPLETION_CANDIDATE,
        ExecutionState.TERMINAL_CLOSED,
        ExecutionState.IN_PROGRESS,
    },
    ExecutionState.COMPLETION_CANDIDATE: {
        ExecutionState.TERMINAL_CLOSED,
        ExecutionState.ITERATION_REQUIRED,
        ExecutionState.IN_PROGRESS,
    },
    ExecutionState.ITERATION_REQUIRED: {
        ExecutionState.READY,
        ExecutionState.IN_PROGRESS,
        ExecutionState.BLOCKED,
    },
    ExecutionState.TERMINAL_CLOSED: {ExecutionState.IN_PROGRESS},
    ExecutionState.BLOCKED: {
        ExecutionState.READY,
        ExecutionState.IN_PROGRESS,
        ExecutionState.CANCELLED,
    },
    ExecutionState.CANCELLED: {ExecutionState.READY},
    ExecutionState.EXTERNALLY_CLAIMED: {
        ExecutionState.READY,
        ExecutionState.PENDING,
        ExecutionState.AWAITING_VERIFICATION,
    },
}


@dataclass(slots=True)
class Occurrence:
    path: str
    branch: str | None = None
    commit: str | None = None
    canonical: bool = True
    dirty: bool = False
    coordination_owner: str | None = None
    content_sha256: str | None = None


@dataclass(slots=True)
class PlanRecord:
    plan_id: str
    title: str
    aliases: list[str]
    authority_mode: AuthorityMode = AuthorityMode.CHILD
    execution_state: ExecutionState = ExecutionState.DISCOVERED
    parent_plan_id: str | None = None
    occurrences: list[dict[str, Any]] = field(default_factory=list)
    external_claimed: bool = False
    source: str = "canonical"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["authority_mode"] = self.authority_mode.value
        value["execution_state"] = self.execution_state.value
        return value


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    plan_id: str
    external_id: str
    title: str
    state: ExecutionState
    dependencies: list[str] = field(default_factory=list)
    severity: str = "MEDIUM"
    created_at: str = "9999-12-31T23:59:59Z"
    retry_count: int = 0
    retry_history: list[dict[str, Any]] = field(default_factory=list)
    retry_not_before: float | None = None
    external_blocker: bool = False
    evidence: list[dict[str, Any]] = field(default_factory=list)
    source_kind: str = "plan"
    source_path: str | None = None
    disposition: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["state"] = self.state.value
        return value


def parse_execution_state(value: str | None) -> tuple[ExecutionState, str | None]:
    raw = (value or "").strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "": ExecutionState.DISCOVERED,
        "NOT_STARTED": ExecutionState.PENDING,
        "TODO": ExecutionState.READY,
        "OPEN": ExecutionState.READY,
        "QUEUED": ExecutionState.READY,
        "ACTIVE": ExecutionState.IN_PROGRESS,
        "WIP": ExecutionState.IN_PROGRESS,
        "DONE": ExecutionState.COMPLETE,
        "CLOSED": ExecutionState.COMPLETE,
        "PASS": ExecutionState.VERIFIED,
        "PASSED": ExecutionState.VERIFIED,
        "DEFERRED": ExecutionState.BLOCKED,
        "STILL_OPEN": ExecutionState.READY,
    }
    if raw == "SUPERSEDED":
        return ExecutionState.BLOCKED, "SUPERSEDED_IS_AUTHORITY_NOT_EXECUTION_STATE"
    if raw in aliases:
        return aliases[raw], None
    try:
        return ExecutionState(raw), None
    except ValueError:
        return ExecutionState.DISCOVERED, f"UNKNOWN_EXECUTION_STATE:{raw}"


def validate_transition(current: ExecutionState, target: ExecutionState) -> None:
    if current == target:
        return
    if target not in TRANSITIONS[current]:
        raise ValueError(f"unsafe task transition {current.value} -> {target.value}")
