"""
reset_track_signal.py — Reset a track's continuation signal to the current session.

Use when:
  - SESSION_MISMATCH blocks legitimate continuation (same chat, HEAD changed after commit)
  - Starting fresh after a failed sprint (clears hard_stops, sets autonomous_continue=True)
  - Explicitly adopting a prior session's signal (with --adopt-session)

Usage:
  python tools/supervisor/reset_track_signal.py --track product
  python tools/supervisor/reset_track_signal.py --track machinery
  python tools/supervisor/reset_track_signal.py --track product --dry-run
  python tools/supervisor/reset_track_signal.py --track product --adopt-session <old-session-id>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
sys.path.insert(0, str(_here))

from atomic_io import atomic_write_json
from continuation_identity import get_or_create_session_identity


_SIGNAL_PATHS = {
    "product": _repo_root / ".local" / "supervisor" / "product" / "continuation-signal.json",
    "machinery": _repo_root / ".local" / "supervisor" / "machinery" / "continuation-signal.json",
    "legacy": _repo_root / ".local" / "supervisor" / "continuation-signal.json",
}


def reset_signal(
    track: str,
    *,
    adopt_session: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Reset the track's continuation signal to the current session.

    Args:
        track: "product" | "machinery" | "legacy"
        adopt_session: if set, re-stamp this old session_id with the current one
                       (explicit cross-session adoption — use with care)
        dry_run: if True, compute and print what would happen without writing

    Returns:
        The signal dict that would be (or was) written.
    """
    signal_path = _SIGNAL_PATHS.get(track)
    if signal_path is None:
        raise ValueError(f"Unknown track {track!r}. Use: product | machinery | legacy")

    # Resolve current session identity
    track_type = track if track in ("product", "machinery") else "product"
    identity = get_or_create_session_identity(track_type=track_type)
    new_session_id = identity.session_id

    # Load existing signal to preserve iteration and rework context (but clear hard stops)
    existing: dict = {}
    if signal_path.exists():
        try:
            existing = json.loads(signal_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Validate adopt-session: warn if it's not in the existing signal
    if adopt_session:
        old_session = existing.get("session_id", "")
        if old_session != adopt_session:
            print(
                f"WARNING: --adopt-session={adopt_session!r} does not match "
                f"existing signal session_id={old_session!r}. "
                "Adopting anyway — this is your explicit choice.",
                file=sys.stderr,
            )

    # Build the fresh signal
    new_signal: dict = {
        "autonomous_continue": True,
        "session_id": new_session_id,
        "track": track,
        "owner": "reset_track_signal",
        "iteration": existing.get("iteration", 0),
        "max_iterations": existing.get("max_iterations", 5),
        "continuation_state": "YES_RESET_CLEAN",
        "hard_stops_detected": [],  # Clear all hard stops
        "rework_items": [],          # Clear rework items
        "reset_at": datetime.now(timezone.utc).isoformat(),
        "reset_source": (
            f"adopted_from:{adopt_session}" if adopt_session else "reset_to_current_session"
        ),
    }

    # Preserve govblock_resolved_by if present (don't erase architectural resolution evidence)
    if existing.get("govblock_resolved_by"):
        new_signal["govblock_resolved_by"] = existing["govblock_resolved_by"]

    if dry_run:
        print(f"[dry-run] Would write to {signal_path}:")
        print(json.dumps(new_signal, indent=2))
        return new_signal

    # Write atomically
    atomic_write_json(signal_path, new_signal)
    print(f"[reset_track_signal] {track} signal reset → session_id={new_session_id!r}")
    print(f"[reset_track_signal] Written to: {signal_path}")
    if adopt_session:
        print(f"[reset_track_signal] Adopted from prior session: {adopt_session!r}")

    return new_signal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reset a track's continuation signal to the current session."
    )
    parser.add_argument(
        "--track",
        required=True,
        choices=["product", "machinery", "legacy"],
        help="Which track's signal to reset",
    )
    parser.add_argument(
        "--adopt-session",
        default=None,
        metavar="SESSION_ID",
        help=(
            "Explicitly adopt a prior session's signal by re-stamping it with "
            "the current session_id. Use when intentionally continuing another "
            "chat's work."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without modifying any files",
    )
    args = parser.parse_args(argv)

    try:
        result = reset_signal(
            args.track,
            adopt_session=args.adopt_session,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
