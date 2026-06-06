"""
Format Factory — Cognee Memory Backend (Stub)
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Cognee recall = memory retrieval (proof level H1 only). NOT proof of execution.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend, ProofLevel
)


class CogneeMemoryBackend(ExecutionBackend):
    """
    Cognee memory backend.
    Even if callable, memory recall = H1 only (advisory, not proof).
    """

    @property
    def backend_type(self) -> BackendType:
        # Using LLM_API type as closest fit; Cognee is advisory memory
        return BackendType.LLM_API

    def discover(self) -> BackendStatus:
        try:
            import cognee  # noqa: F401
            return BackendStatus.INSTALLED_NOT_CONFIGURED if True else BackendStatus.VERIFIED_CALLABLE
        except ImportError:
            return BackendStatus.NOT_FOUND

    def can_execute(self, action: dict) -> bool:
        return False  # Memory recall is advisory only, not execution

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        return BackendResult(
            action_id=action.get("action_id", "unknown"),
            backend_used=BackendType.LLM_API,
            status="BLOCKED",
            exit_code=3,
            proof_level=ProofLevel.H1,
            errors=[
                "COGNEE_RECALL_IS_NOT_EVIDENCE: Cognee memory retrieval result is advisory (H1). "
                "Cannot be used as execution proof. Must re-verify against current file state."
            ],
        )


# Expose BackendStatus for use in stubs
BackendStatus.INSTALLED_NOT_CONFIGURED = BackendStatus.SETUP_REQUIRED  # alias
