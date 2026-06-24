"""
write_chat_plan_binding.py — Create/update/clear per-mission chat plan bindings.

A chat plan binding records which plan a specific session is executing.
check_continuation.py Check 0c reads these bindings and blocks global ledger
fallback when a session has an active (IN_PROGRESS) binding with
global_ledger_fallback_allowed=false.

Bindings are session-scoped: only the session that created a binding is
blocked by it. Other sessions are unaffected. A 48-hour TTL prevents stale
bindings from permanently blocking a crashed session.

Usage:
  python tools/supervisor/write_chat_plan_binding.py --mission-id X --plan-path Y
  python tools/supervisor/write_chat_plan_binding.py --mission-id X --plan-path Y --complete
  python tools/supervisor/write_chat_plan_binding.py --mission-id X --plan-path Y --last-taskcard Z
  python tools/supervisor/write_chat_plan_binding.py --clear-mission X
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_MISSIONS_DIR = _REPO_ROOT / ".local" / "missions"


def _get_session_id() -> str:
    """Get current session ID using the same logic as check_continuation.py."""
    import os
    env_id = os.environ.get("CLAUDE_SESSION_ID")
    if env_id:
        return env_id
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from continuation_identity import _derive_stable_session_id
        return _derive_stable_session_id("product")
    except Exception:
        import uuid
        return str(uuid.uuid4()).replace("-", "")[:12]


def write_binding(
    mission_id: str,
    plan_path: str,
    *,
    complete: bool = False,
    last_taskcard: str | None = None,
    session_id: str | None = None,
    ttl_hours: int = 48,
) -> Path:
    """Write or update a plan binding for the given mission."""
    mission_dir = _MISSIONS_DIR / mission_id
    mission_dir.mkdir(parents=True, exist_ok=True)
    binding_path = mission_dir / "plan-binding.yaml"

    now = datetime.now(timezone.utc).isoformat()
    sid = session_id or _get_session_id()

    # Read existing binding for created_at preservation
    created_at = now
    if binding_path.exists():
        try:
            import yaml
            existing = yaml.safe_load(binding_path.read_text(encoding="utf-8"))
            b = existing.get("chat_plan_binding", {})
            if b.get("created_at"):
                created_at = b["created_at"]
        except Exception:
            pass

    binding = {
        "chat_plan_binding": {
            "mission_id": mission_id,
            "plan_path": plan_path,
            "session_id": sid,
            "status": "COMPLETE" if complete else "IN_PROGRESS",
            "global_ledger_fallback_allowed": True if complete else False,
            "created_at": created_at,
            "updated_at": now,
            "last_taskcard": last_taskcard,
            "ttl_hours": ttl_hours,
        }
    }

    try:
        import yaml
        binding_path.write_text(
            yaml.dump(binding, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    except ImportError:
        # Fallback: write as JSON if yaml unavailable
        binding_path.with_suffix(".json").write_text(
            json.dumps(binding, indent=2), encoding="utf-8"
        )
        binding_path = binding_path.with_suffix(".json")

    return binding_path


def clear_mission(mission_id: str) -> bool:
    """Remove the binding directory for a mission (crash recovery)."""
    mission_dir = _MISSIONS_DIR / mission_id
    if mission_dir.exists():
        shutil.rmtree(mission_dir)
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write or clear a chat plan binding")
    parser.add_argument("--mission-id", type=str, help="Mission identifier")
    parser.add_argument("--plan-path", type=str, help="Path to the plan file")
    parser.add_argument("--complete", action="store_true",
                        help="Mark binding as COMPLETE (unblocks global ledger)")
    parser.add_argument("--last-taskcard", type=str, default=None,
                        help="Last completed taskcard ID")
    parser.add_argument("--clear-mission", type=str, default=None, metavar="MISSION_ID",
                        help="Remove binding directory for given mission (crash recovery)")
    parser.add_argument("--ttl-hours", type=int, default=48,
                        help="TTL in hours before binding auto-expires (default: 48)")
    args = parser.parse_args(argv)

    if args.clear_mission:
        removed = clear_mission(args.clear_mission)
        if removed:
            print(f"Cleared mission binding: {args.clear_mission}")
        else:
            print(f"No binding found for mission: {args.clear_mission}")
        return 0

    if not args.mission_id or not args.plan_path:
        parser.error("--mission-id and --plan-path are required (unless using --clear-mission)")

    path = write_binding(
        args.mission_id, args.plan_path,
        complete=args.complete,
        last_taskcard=args.last_taskcard,
        ttl_hours=args.ttl_hours,
    )
    status = "COMPLETE" if args.complete else "IN_PROGRESS"
    print(f"Binding written: {path} (status={status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
