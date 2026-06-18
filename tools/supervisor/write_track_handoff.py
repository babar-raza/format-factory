"""
write_track_handoff.py — Track M machinery-to-product handoff writer.

Called by Track M (machinery) cycles after gap ledger refresh to publish
updated gap information that Track P (product) can read for sprint selection.

TC-P2-005: Track Handoff Protocol (REQ-TRK-009, REQ-TRK-012)

Usage:
    python tools/supervisor/write_track_handoff.py [--repo-root <path>]
    python tools/supervisor/write_track_handoff.py --gap-ledger-path <path>

Schema of .local/supervisor/shared/track-handoff.json:
    {
        "handoff_version": 1,
        "product_to_machinery": {  ← written by Track P (autonomous_cycle.py)
            "written_at": "<ISO>",
            "written_by_session": "<session_id>",
            "sprint_id": "<id>",
            "new_capabilities_count": <int>,
            "test_count": <int>
        },
        "machinery_to_product": {  ← written by this script (Track M)
            "written_at": "<ISO>",
            "written_by_session": "<session_id>",
            "gap_ledger_snapshot_path": ".local/supervisor/shared/gap-ledger-snapshot.json",
            "validated_gap_count": <int>,
            "high_priority_gap_count": <int>
        }
    }
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent

sys.path.insert(0, str(_here))

from atomic_io import atomic_write_json


def write_machinery_handoff(
    repo_root: Path,
    gap_ledger_path: Path | None = None,
    session_id: str | None = None,
) -> dict:
    """Write machinery_to_product section of the track handoff file.

    Reads the gap ledger, computes stats, writes a snapshot, and updates
    .local/supervisor/shared/track-handoff.json.

    Returns the written handoff entry dict.
    """
    repo_root = repo_root.resolve()
    shared_dir = repo_root / ".local" / "supervisor" / "shared"
    shared_dir.mkdir(parents=True, exist_ok=True)
    handoff_path = shared_dir / "track-handoff.json"

    # --- Resolve gap ledger path ---
    if gap_ledger_path is None:
        gap_ledger_path = repo_root / "reports" / "capability-layer" / "gap-ledger.json"

    # --- Read gap ledger ---
    gap_ledger: list = []
    if gap_ledger_path.exists():
        try:
            raw = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                gap_ledger = raw
            elif isinstance(raw, dict):
                gap_ledger = raw.get("gaps", raw.get("items", []))
        except Exception as e:
            print(f"  WARNING: Could not read gap ledger: {e}", file=sys.stderr)

    validated_gap_count = len(gap_ledger)
    high_priority_count = sum(
        1 for g in gap_ledger
        if str(g.get("priority", "")).lower() in ("high", "critical", "p1", "p0")
        or g.get("high_priority", False)
    )

    # --- Write gap ledger snapshot (read-only handoff for Track P) ---
    snapshot_path = shared_dir / "gap-ledger-snapshot.json"
    snapshot_rel = ".local/supervisor/shared/gap-ledger-snapshot.json"
    try:
        atomic_write_json(snapshot_path, {
            "snapshot_taken_at": datetime.now(timezone.utc).isoformat(),
            "source_path": str(gap_ledger_path.relative_to(repo_root)
                               if gap_ledger_path.is_relative_to(repo_root)
                               else gap_ledger_path),
            "gap_count": validated_gap_count,
            "high_priority_count": high_priority_count,
            "gaps": gap_ledger,
        })
    except Exception as e:
        print(f"  WARNING: gap ledger snapshot write failed: {e}", file=sys.stderr)

    # --- Resolve session_id ---
    if session_id is None:
        try:
            from continuation_identity import _derive_stable_session_id
            session_id = _derive_stable_session_id("machinery")
        except Exception:
            import uuid
            session_id = str(uuid.uuid4())[:12]

    # --- Build handoff entry ---
    entry = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "written_by_session": session_id,
        "gap_ledger_snapshot_path": snapshot_rel,
        "validated_gap_count": validated_gap_count,
        "high_priority_gap_count": high_priority_count,
    }

    # --- Read existing handoff file (preserve product_to_machinery section) ---
    existing: dict = {}
    if handoff_path.exists():
        try:
            existing = json.loads(handoff_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    existing["handoff_version"] = 1
    existing["machinery_to_product"] = entry
    atomic_write_json(handoff_path, existing)

    print(f"  Track M handoff written: {handoff_path}")
    print(f"    validated_gap_count: {validated_gap_count}")
    print(f"    high_priority_gap_count: {high_priority_count}")
    return entry


def read_machinery_handoff(repo_root: Path) -> dict | None:
    """Read machinery_to_product section of the handoff file.

    Returns the dict or None if not present. Called by Track P gap selection
    (TC-P2-005-04) to get freshest gap ledger stats from Track M.
    """
    handoff_path = repo_root / ".local" / "supervisor" / "shared" / "track-handoff.json"
    if not handoff_path.exists():
        return None
    try:
        data = json.loads(handoff_path.read_text(encoding="utf-8"))
        return data.get("machinery_to_product")
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write Track M machinery-to-product handoff entry"
    )
    parser.add_argument("--repo-root", type=Path, default=_default_repo)
    parser.add_argument("--gap-ledger-path", type=Path, default=None,
                        help="Path to gap-ledger.json (default: reports/capability-layer/gap-ledger.json)")
    parser.add_argument("--session-id", type=str, default=None)
    args = parser.parse_args(argv)

    entry = write_machinery_handoff(
        repo_root=args.repo_root,
        gap_ledger_path=args.gap_ledger_path,
        session_id=args.session_id,
    )
    print(json.dumps(entry, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
