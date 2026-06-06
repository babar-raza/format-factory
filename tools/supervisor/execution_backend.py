"""
Format Factory — Execution Backend Interface
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Defines the abstract base class and supporting types for all execution backends.
"""
from __future__ import annotations

import abc
import enum
from dataclasses import dataclass, field
from typing import List, Optional


class BackendType(enum.Enum):
    """Priority-ordered backend types."""
    SUPERPOWERS_LOCAL_PLUGIN = "SUPERPOWERS_LOCAL_PLUGIN"
    SESSION_SKILL_TOOL = "SESSION_SKILL_TOOL"
    CLAUDE_AGENT_SUBAGENT = "CLAUDE_AGENT_SUBAGENT"
    REPO_LOCAL_SKILL = "REPO_LOCAL_SKILL"
    MCP_SUPERPOWERS = "MCP_SUPERPOWERS"
    TASK_MASTER_MCP = "TASK_MASTER_MCP"
    LLM_API = "LLM_API"
    LOCAL_DETERMINISTIC = "LOCAL_DETERMINISTIC"
    CLAUDE_CLI_OPTIONAL = "CLAUDE_CLI_OPTIONAL"
    MANUAL_EXTERNAL_GATE = "MANUAL_EXTERNAL_GATE"


class BackendStatus(enum.Enum):
    """Runtime availability status of a backend."""
    VERIFIED_CALLABLE = "VERIFIED_CALLABLE"
    CONFIG_PRESENT = "CONFIG_PRESENT"
    CONFIG_ONLY = "CONFIG_ONLY"       # config exists but not callable
    SETUP_REQUIRED = "SETUP_REQUIRED"
    BLOCKED_BY_CREDENTIALS = "BLOCKED_BY_CREDENTIALS"
    NOT_FOUND = "NOT_FOUND"
    NOT_CHECKABLE = "NOT_CHECKABLE"
    FORBIDDEN_IN_SESSION = "FORBIDDEN_IN_SESSION"  # e.g. CLAUDE_CLI inside CLAUDECODE


class ProofLevel(enum.Enum):
    """Proof levels for execution evidence."""
    H1 = "H1"  # prompt/action generated
    H2 = "H2"  # next-action.json validated
    H3 = "H3"  # runner dispatched one action, result written
    H4 = "H4"  # two sequential runner cycles, state advanced
    H5 = "H5"  # agentic backend executed through runner
    H6 = "H6"  # external host continuation (CLAUDECODE=0 only)


@dataclass
class BackendResult:
    """Result of a backend execution."""
    action_id: str
    backend_used: BackendType
    status: str          # SUCCESS, FAILED, BLOCKED, SETUP_REQUIRED
    exit_code: int
    stdout_path: Optional[str] = None
    stderr_path: Optional[str] = None
    result_path: Optional[str] = None
    evidence_paths: List[str] = field(default_factory=list)
    proof_level: Optional[ProofLevel] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    skipped_backends: List[str] = field(default_factory=list)
    selection_reason: str = ""


class ExecutionBackend(abc.ABC):
    """Abstract base for all execution backends."""

    @property
    @abc.abstractmethod
    def backend_type(self) -> BackendType:
        """Return the backend type enum value."""

    @abc.abstractmethod
    def discover(self) -> BackendStatus:
        """Probe availability without executing. Never logs secret values."""

    @abc.abstractmethod
    def can_execute(self, action: dict) -> bool:
        """Return True if this backend can execute the given action."""

    @abc.abstractmethod
    def execute(self, action: dict, allowed_write_roots: List[str]) -> BackendResult:
        """
        Execute the action and return a BackendResult.
        - Must write result_path with execution evidence.
        - Must NOT allow host/parent to create the proof file.
        - Must enforce allowed_write_roots.
        - Must refuse forbidden_actions.
        """

    def is_callable(self) -> bool:
        """Convenience: True only if discover() returns VERIFIED_CALLABLE."""
        return self.discover() == BackendStatus.VERIFIED_CALLABLE
