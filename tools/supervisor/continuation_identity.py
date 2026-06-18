"""
continuation_identity.py — Cross-Chat Continuation Isolation (CCI) Identity Model

Provides the ContinuationIdentity dataclass that tags every continuation artifact
with enough context to determine which chat/session/mission produced it.

Design: session_id is the primary scoping key (git-based, stable across windows on
same branch+HEAD+track). track_type distinguishes product from machinery. chat_id is
optional, used for Track M per-chat isolation (fresh UUID4 each machinery chat).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _derive_stable_session_id(track_type: str = "product") -> str:
    """Derive stable session_id from git HEAD + branch + track. Falls back to UUID."""
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        return hashlib.sha256(f"{track_type}:{branch}:{head}".encode()).hexdigest()[:12]
    except Exception:
        return str(uuid.uuid4())[:12]


def _generate_chat_id() -> str:
    """Generate a fresh UUID4 chat_id for Track M per-chat isolation."""
    return str(uuid.uuid4())


@dataclass
class ContinuationIdentity:
    """Identity envelope for a continuation state artifact."""

    session_id: str = field(default_factory=lambda: os.environ.get(
        "CLAUDE_SESSION_ID") or _derive_stable_session_id()
    )
    track_type: str = field(default="product")
    chat_id: Optional[str] = None
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
    track_type: str = "product",
) -> ContinuationIdentity:
    """Get the active session identity, or create a new one.

    Uses git-based stable session_id (sha256(track:branch:HEAD)[:12]).
    Same branch+HEAD+track → identical session_id across chat windows.
    Falls back to UUID4 when git is unavailable.
    """
    stable_session_id = os.environ.get("CLAUDE_SESSION_ID") or _derive_stable_session_id(track_type)

    existing = ContinuationIdentity.load(ACTIVE_SESSION_PATH)
    if existing and not existing.is_stale():
        # Reuse if session_id and track_type match (git-stable identity)
        if existing.session_id == stable_session_id and existing.track_type == track_type:
            if mission_id:
                existing.mission_id = mission_id
            if sprint_id:
                existing.sprint_id = sprint_id
            existing.save(ACTIVE_SESSION_PATH)
            return existing

    # Create new identity with stable git-based session_id
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, cwd=str(_REPO_ROOT), timeout=5
        ).decode().strip()
    except Exception:
        branch = None

    identity = ContinuationIdentity(
        session_id=stable_session_id,
        track_type=track_type,
        mission_id=mission_id,
        sprint_id=sprint_id,
        branch=branch,
    )

    identity.save(ACTIVE_SESSION_PATH)
    return identity


def get_or_create_machinery_identity() -> ContinuationIdentity:
    """Create a fresh Track M identity with a new chat_id (per-chat isolation).

    Track M uses git-based session_id for human-readable cross-window identity,
    but generates a fresh UUID4 chat_id each call to enforce per-chat isolation.
    A new chat cannot consume a prior chat's Track M continuation state.
    """
    stable_session_id = _derive_stable_session_id("machinery")
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, cwd=str(_REPO_ROOT), timeout=5
        ).decode().strip()
    except Exception:
        branch = None

    identity = ContinuationIdentity(
        session_id=stable_session_id,
        track_type="machinery",
        chat_id=_generate_chat_id(),
        branch=branch,
    )
    return identity
