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


def _resolve_via_coordination(track_type: str) -> Optional[str]:
    """TC-MACH-001 (F1 mitigation — cross-chat session_id collision).

    F1's root problem: `.local/supervisor/session-{track}.id` is a single file
    shared by every process touching this repo, so two genuinely-concurrent
    chats can mint/read the SAME session_id within the same TTL window,
    silently defeating the isolation this whole module exists to provide. The
    full fix needs the harness to pipe its real per-conversation session_id
    into every subprocess invocation; no such channel currently exists here
    (`CLAUDE_SESSION_ID` is never set by any hook or settings.json in this
    repo, and the PreToolUse hook that DOES receive the real session_id
    (`coordination/hooks/gate.py`) has no mechanism to inject env vars into
    the Bash command it is gating — confirmed by reading the hook, not
    assumed).

    This is the safely-achievable partial mitigation instead: the Section CO
    coordination plane's SQLite registry already durably records each live
    agent's real harness-assigned `claude_session_id` (via the same hook, on
    every tool call). When exactly ONE agent is genuinely fresh (status
    ACTIVE AND heartbeat within its own TTL — not merely "not yet reaped") for
    THIS worktree, there is zero ambiguity about which conversation a
    subprocess spawned right now belongs to: use that agent's real
    claude_session_id instead of minting a self-generated nonce. With zero or
    multiple fresh agents, this returns None and the caller falls through to
    the existing (unchanged) nonce-based behavior — never worse than before.

    Any failure (coordination plane absent/uninitialized, DB locked, schema
    mismatch, etc.) is swallowed and treated as "no answer" — this is a purely
    additive enhancement to identity resolution, never a new point of
    fragility for it.
    """
    def _norm_path(p: str) -> str:
        # Same comparable form coordination/root.py's (private) _norm() produces
        # — reimplemented locally rather than importing a `_`-prefixed name from
        # another module, so this stays correct even if that internal helper
        # changes shape.
        return os.path.normcase(os.path.realpath(str(p))).replace("\\", "/")

    try:
        import sys as _sys_ci
        _coord_parent = str(Path(__file__).resolve().parent)
        if _coord_parent not in _sys_ci.path:
            _sys_ci.path.insert(0, _coord_parent)
        from coordination.db import connect
        from coordination.root import resolve_coordination_root, worktree_identity

        _, my_worktree = worktree_identity(str(_REPO_ROOT))
        my_worktree_norm = _norm_path(my_worktree)

        root = resolve_coordination_root(str(_REPO_ROOT))
        conn = connect(root)
        try:
            rows = conn.execute(
                "SELECT claude_session_id, last_heartbeat, heartbeat_ttl_s,"
                " worktree_path FROM agents WHERE status='ACTIVE'"
            ).fetchall()
        finally:
            conn.close()
    except Exception:
        return None

    now = datetime.now(timezone.utc)
    fresh_session_ids: set[str] = set()
    for row in rows:
        csid = row["claude_session_id"]
        wt = row["worktree_path"]
        if not csid or not wt:
            continue
        try:
            if _norm_path(wt) != my_worktree_norm:
                continue
            hb = datetime.fromisoformat(row["last_heartbeat"])
            ttl = row["heartbeat_ttl_s"] or 1800
            if (now - hb).total_seconds() <= ttl:
                fresh_session_ids.add(csid)
        except Exception:
            continue

    if len(fresh_session_ids) == 1:
        return next(iter(fresh_session_ids))
    return None  # zero or ambiguous (>1) fresh agents — defer to nonce fallback


def _derive_stable_session_id(track_type: str = "product") -> str:
    """Derive a stable session identity for this chat session.

    Priority order:
    1. CLAUDE_SESSION_ID env var — external control, always wins
    2. Runtime session file .local/supervisor/session-{track}.id with a
       sliding 4h sees-activity TTL — stable across commits and across the
       full lifetime of a continuously-active chat (TC-MACH-001, F2)
    3. Coordination-plane resolution (TC-MACH-001, F1 mitigation) — on cache
       miss only: if the Section CO coordination registry shows EXACTLY ONE
       genuinely-fresh live agent for this worktree, adopt its real
       harness-assigned claude_session_id instead of minting a nonce
    4. Git HEAD + per-chat nonce derivation — used to WRITE the session file
       when neither of the above resolved anything
    5. UUID4 fallback — when git unavailable; no hyphens (pure hex via replace)

    The session file is the key change: it prevents HEAD changes from
    invalidating the session_id mid-chat after a commit.
    """
    # Priority 1: env var
    env_id = os.environ.get("CLAUDE_SESSION_ID")
    if env_id:
        return env_id

    # Priority 2: runtime session file (stable across commits within same chat)
    session_file = _REPO_ROOT / ".local" / "supervisor" / f"session-{track_type}.id"
    if session_file.exists():
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            # TC-MACH-001 (partial fix for F2 — same-chat identity drift): the TTL's
            # purpose is to guess "is this probably still the same chat, or a new
            # one" when no better signal exists (see module docstring). A hard
            # cliff measured from `created_at` fails that goal for a long-running,
            # continuously-active session — the exact workload this identity exists
            # to support (e.g. an autonomous continuation loop) — which silently
            # rotates its own session_id mid-conversation once 4 wall-clock hours
            # pass, regardless of ongoing activity (confirmed live: this exact
            # session's session-product.id rotated 71d6552a09a4 → 4d50707c8ce0
            # after 4h30m of continuous, non-idle use). Track `last_seen_at`
            # (sliding) instead of measuring purely from `created_at` (fixed): only
            # a genuine >4h GAP with no activity mints a new ID. Old session files
            # without `last_seen_at` fall back to `created_at` — backward compatible.
            #
            # This does NOT address cross-chat cache-hit collision (F1) — two
            # concurrent chats can still resolve to the same session_id if both
            # read this file within the same active window. That requires
            # consuming the harness-assigned session_id (already used by the
            # separate Section CO coordination plane) and remains open pending a
            # design spike on how to pipe that identity into non-hook invocations.
            last_seen_str = data.get("last_seen_at") or data.get("created_at", "1970-01-01")
            last_seen = datetime.fromisoformat(last_seen_str)
            age_hours = (datetime.now(timezone.utc) - last_seen).total_seconds() / 3600
            if age_hours < 4.0:
                data["last_seen_at"] = datetime.now(timezone.utc).isoformat()
                try:
                    session_file.write_text(json.dumps(data), encoding="utf-8")
                except Exception:
                    pass  # renewal is best-effort — the cached ID is still valid and returned
                return data["session_id"]
        except Exception:
            pass  # fall through to create new session file

    # Priority 3 (TC-MACH-001, F1 mitigation): coordination-plane resolution.
    # Only reached on cache miss (no valid Priority-2 hit above) — so this adds
    # no per-call overhead to the common warm-cache path, and only engages
    # exactly when ambiguity would otherwise be resolved by an arbitrary nonce.
    coord_session_id = _resolve_via_coordination(track_type)
    if coord_session_id:
        try:
            session_file.parent.mkdir(parents=True, exist_ok=True)
            _now_iso = datetime.now(timezone.utc).isoformat()
            session_file.write_text(json.dumps({
                "session_id": coord_session_id,
                "track_type": track_type,
                "created_at": _now_iso,
                "last_seen_at": _now_iso,
                "source": "coordination_plane",
            }), encoding="utf-8")
        except Exception:
            pass  # write is best-effort — the resolved id is still returned
        return coord_session_id

    # Priority 4/5: git HEAD or UUID fallback — write to session file.
    # TC-SESSION-NONCE-001 (SC-005): add a per-chat nonce to the hash input so that
    # distinct chat sessions on the same git HEAD produce different session_ids.
    # Without this, sha256(track:branch:HEAD) is identical across all sessions until
    # a new commit is made, causing plan locks from session A to fire in session B.
    chat_nonce = str(uuid.uuid4()).replace("-", "")[:8]
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
            cwd=str(_REPO_ROOT), timeout=5
        ).decode().strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL,
            cwd=str(_REPO_ROOT), timeout=5
        ).decode().strip()
        new_id = hashlib.sha256(
            f"{track_type}:{branch}:{head}:{chat_nonce}".encode()
        ).hexdigest()[:12]
        source = "git_nonce"
    except Exception:
        # UUID4 without hyphens — pure hex, no hyphen ambiguity with UUID fallback detection
        new_id = str(uuid.uuid4()).replace("-", "")[:12]
        source = "uuid_fallback"
        chat_nonce = "n/a"

    # Write session file so this ID is stable for the rest of this chat
    try:
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text(json.dumps({
            "session_id": new_id,
            "track_type": track_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "chat_nonce": chat_nonce,  # stored for provenance; not re-used
        }), encoding="utf-8")
    except Exception:
        pass  # non-fatal — ID still returned

    return new_id


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


def get_or_create_product_chat_id() -> str:
    """Get or create a persistent chat_id for the product track.

    Unlike machinery track (which generates a fresh UUID4 each call),
    this persists the chat_id to a file so it remains stable within a session.
    """
    chat_id_path = _REPO_ROOT / ".local" / "supervisor" / "product" / "current-chat-id.json"
    if chat_id_path.exists():
        try:
            data = json.loads(chat_id_path.read_text(encoding="utf-8"))
            existing_id = data.get("chat_id")
            if existing_id:
                return existing_id
        except Exception:
            pass
    # Generate new chat_id and persist
    new_id = str(uuid.uuid4())
    chat_id_path.parent.mkdir(parents=True, exist_ok=True)
    chat_id_path.write_text(json.dumps({
        "chat_id": new_id,
        "track_type": "product",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }), encoding="utf-8")
    return new_id
