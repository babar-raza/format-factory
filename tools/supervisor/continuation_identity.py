"""
continuation_identity.py — Cross-Chat Continuation Isolation (CCI) Identity Model

Provides the ContinuationIdentity dataclass that tags every continuation artifact
with enough context to determine which chat/session/mission produced it.

Design: session_id is the primary scoping key (generated per-session). mission_id
is the secondary key for cross-window recovery. chat_id is optional (no native
source in Claude Code, so it degrades to session_id).
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class ContinuationIdentity:
    """Identity envelope for a continuation state artifact."""

    session_id: str = field(default_factory=lambda: os.environ.get(
        "CLAUDE_SESSION_ID", str(uuid.uuid4())[:12]
    ))
    mission_id: Optional[str] = None
    run_id: Optional[str] = None
    sprint_id: Optional[str] = None
    branch: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"  # active | consumed | superseded | quarantined

    def to_dict(self) -> dict:
        return asdict(self)

    def matches(self, other: ContinuationIdentity) -> bool:
        """Check if two identities refer to the same logical session."""
        if self.session_id and other.session_id:
            return self.session_id == other.session_id
        # Fallback: match by mission_id + branch
        if self.mission_id and other.mission_id:
            return self.mission_id == other.mission_id and self.branch == other.branch
        return False

    def is_stale(self, max_age_hours: float = 2.0) -> bool:
        """Check if this identity is older than max_age_hours."""
        try:
            created = datetime.fromisoformat(self.created_at)
            age = datetime.now(timezone.utc) - created
            return age.total_seconds() > max_age_hours * 3600
        except (ValueError, TypeError):
            return True

    @classmethod
    def from_dict(cls, data: dict) -> ContinuationIdentity:
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    @classmethod
    def load(cls, path: Path) -> Optional[ContinuationIdentity]:
        """Load identity from a JSON file, or None if missing/invalid."""
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except (json.JSONDecodeError, TypeError):
            return None

    def save(self, path: Path) -> None:
        """Persist identity to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


# --- Active session management ---

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACTIVE_SESSION_PATH = _REPO_ROOT / ".local" / "supervisor" / "active-session.json"


def get_or_create_session_identity(
    mission_id: Optional[str] = None,
    sprint_id: Optional[str] = None,
) -> ContinuationIdentity:
    """Get the active session identity, or create a new one.

    Reuses an existing identity if it's recent (< 2h old) and has the same
    session_id as the environment provides. Otherwise creates fresh.
    """
    env_session_id = os.environ.get("CLAUDE_SESSION_ID")

    existing = ContinuationIdentity.load(ACTIVE_SESSION_PATH)
    if existing and not existing.is_stale():
        # If env provides a session_id and it matches, reuse
        if not env_session_id or existing.session_id == env_session_id:
            # Update mission/sprint if provided
            if mission_id:
                existing.mission_id = mission_id
            if sprint_id:
                existing.sprint_id = sprint_id
            existing.save(ACTIVE_SESSION_PATH)
            return existing

    # Create new identity
    identity = ContinuationIdentity(
        session_id=env_session_id or str(uuid.uuid4())[:12],
        mission_id=mission_id,
        sprint_id=sprint_id,
    )

    # Try to get current branch
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT), timeout=5
        )
        if result.returncode == 0:
            identity.branch = result.stdout.strip()
    except Exception:
        pass

    identity.save(ACTIVE_SESSION_PATH)
    return identity
