"""
continuation_selector.py — Continuation Selection Algorithm (CCI)

Given the current session identity, selects the appropriate continuation state.
Implements fail-closed behavior: rejects ambiguous state rather than defaulting
to "latest file wins."

Selection priority:
1. Exact session_id match → use it
2. Mission_id + branch match → use it (cross-window recovery)
3. No match + legacy (no session_id in artifact) → warn, use it
4. No match + session_id present but different → REJECT (fail-closed)
5. Multiple matches → REJECT (conflict, need resolution)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from continuation_identity import ContinuationIdentity

# UUID4 truncated format: str(uuid.uuid4())[:12] → "xxxxxxxx-xxx" (8 hex + hyphen + 3 hex)
# This pattern detects signals written when git was unavailable (prior to Phase A).
# Such signals are anonymous (not foreign) and should be adopted, not rejected.
_UUID4_TRUNCATED_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{3}$")


@dataclass
class SelectionResult:
    """Result of the continuation selection algorithm."""

    verdict: str  # ACCEPT | REJECT | WARN_LEGACY | WARN_UUID_FALLBACK
    signal_path: Optional[Path] = None
    reason: Optional[str] = None
    signal_session_id: Optional[str] = None
    caller_session_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "signal_path": str(self.signal_path) if self.signal_path else None,
            "reason": self.reason,
            "signal_session_id": self.signal_session_id,
            "caller_session_id": self.caller_session_id,
        }


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def select_continuation(
    caller_identity: ContinuationIdentity,
    signal_path: Optional[Path] = None,
) -> SelectionResult:
    """Select the appropriate continuation state for the given identity.

    Args:
        caller_identity: The identity of the current session/caller
        signal_path: Path to continuation-signal.json (default: standard location)

    Returns:
        SelectionResult with verdict ACCEPT, REJECT, or WARN_LEGACY
    """
    if signal_path is None:
        signal_path = _REPO_ROOT / ".local" / "supervisor" / "continuation-signal.json"

    if not signal_path.exists():
        return SelectionResult(
            verdict="REJECT",
            signal_path=signal_path,
            reason="Signal file does not exist",
            caller_session_id=caller_identity.session_id,
        )

    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return SelectionResult(
            verdict="REJECT",
            signal_path=signal_path,
            reason=f"Signal file is invalid: {e}",
            caller_session_id=caller_identity.session_id,
        )

    signal_session_id = signal.get("session_id")

    # Case 3: Legacy signal (no session_id) → warn but accept
    if not signal_session_id:
        return SelectionResult(
            verdict="WARN_LEGACY",
            signal_path=signal_path,
            reason="Signal has no session_id (legacy artifact). Accepting with warning.",
            signal_session_id=None,
            caller_session_id=caller_identity.session_id,
        )

    # Case 3.5: UUID fallback signal — written when git was unavailable
    # str(uuid.uuid4())[:12] → "e587a603-097" (8 hex + hyphen + 3 hex, 12 chars)
    # Git-derived IDs are pure hex (no hyphen). UUID-format = anonymous, not foreign.
    # These are adoptable — we cannot verify they belong to another chat.
    if _UUID4_TRUNCATED_RE.match(signal_session_id):
        return SelectionResult(
            verdict="WARN_UUID_FALLBACK",
            signal_path=signal_path,
            reason=(
                "Signal session_id is UUID-format (git was unavailable when written). "
                "Treating as anonymous — not a foreign session. Adopting."
            ),
            signal_session_id=signal_session_id,
            caller_session_id=caller_identity.session_id,
        )

    # Case 1: Exact session_id match → accept
    if signal_session_id == caller_identity.session_id:
        return SelectionResult(
            verdict="ACCEPT",
            signal_path=signal_path,
            reason="Session ID matches",
            signal_session_id=signal_session_id,
            caller_session_id=caller_identity.session_id,
        )

    # Case 2: Mission_id + branch match (cross-window recovery)
    if caller_identity.mission_id:
        signal_sprint = signal.get("source_sprint_id", "")
        if (caller_identity.mission_id in str(signal_sprint) or
                str(signal_sprint) in str(caller_identity.mission_id)):
            return SelectionResult(
                verdict="ACCEPT",
                signal_path=signal_path,
                reason=f"Mission/sprint match: {signal_sprint}",
                signal_session_id=signal_session_id,
                caller_session_id=caller_identity.session_id,
            )

    # Case 4: Session_id present but different → reject (fail-closed)
    return SelectionResult(
        verdict="REJECT",
        signal_path=signal_path,
        reason=(
            f"Session mismatch: signal has session_id={signal_session_id!r}, "
            f"caller has session_id={caller_identity.session_id!r}. "
            f"This continuation belongs to another chat."
        ),
        signal_session_id=signal_session_id,
        caller_session_id=caller_identity.session_id,
    )
