"""
sprint_number_allocator.py — Atomic sprint number allocator for Format Factory.

Ensures strictly monotonic sprint numbering across all sessions and tracks.
Uses os.replace() atomic writes (Windows-compatible; no fcntl/filelock needed).

Ledger: .local/supervisor/sprint-ledger.json
Receipts: .local/supervisor/sprint-receipts/{sprint_id}.json

TC-SRB-020 (splendid-roaming-beaver, 2026-07-12)
Mission: SRB-SPRINT-ENGINE-PRODUCTIONIZATION-001

CLI:
    python tools/supervisor/sprint_number_allocator.py allocate \\
        --semantic-alias "glistening-leaping-chipmunk" \\
        --mission-id "MACH-001" \\
        [--plan-id "plans/.claude/my-plan.md"]

    python tools/supervisor/sprint_number_allocator.py status
    python tools/supervisor/sprint_number_allocator.py list [--n 10]
    python tools/supervisor/sprint_number_allocator.py recover --sprint-id SPRINT-00842

Exit codes:
    0 — success
    1 — error
    2 — already allocated (idempotent — not an error)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LEDGER_PATH_REL = ".local/supervisor/sprint-ledger.json"
_RECEIPTS_DIR_REL = ".local/supervisor/sprint-receipts"
_LEDGER_PATH = _REPO_ROOT / _LEDGER_PATH_REL
_RECEIPTS_DIR = _REPO_ROOT / _RECEIPTS_DIR_REL

# Module-level lock: makes allocate_sprint_number() thread-safe within one process.
# os.replace() is crash-safe (atomic at the OS level) but not safe when two threads
# write to the same .tmp file concurrently on Windows.
_ALLOC_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# Core ledger functions (TC-SRB-020-02)
# ---------------------------------------------------------------------------


def load_ledger(ledger_path: Path | None = None) -> dict:
    """Load the sprint ledger JSON. Returns a default dict if the file is missing.

    Args:
        ledger_path: Path to the ledger file. Defaults to the canonical path.

    Returns:
        Ledger dict with at least schema_version, highest_allocated_number, entries.
    """
    path = ledger_path or _LEDGER_PATH
    if not path.exists():
        return {
            "schema_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "bootstrap_note": "Ledger created on first use (no historical sprints).",
            "highest_allocated_number": 0,
            "entries": [],
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to read sprint ledger at {path}: {exc}") from exc


def find_highest_number(ledger: dict) -> int:
    """Return the highest allocated sprint number from the ledger.

    Excludes entries with status='abandoned'. Falls back to
    ledger['highest_allocated_number'] when no entries exist.

    Args:
        ledger: Ledger dict as returned by load_ledger().

    Returns:
        The current highest sprint number (0 if ledger is empty).
    """
    entries = ledger.get("entries", [])
    active_numbers = [
        e["sprint_number"]
        for e in entries
        if isinstance(e.get("sprint_number"), int) and e.get("status") != "abandoned"
    ]
    if active_numbers:
        return max(active_numbers)
    return int(ledger.get("highest_allocated_number", 0))


def find_existing_allocation(ledger: dict, semantic_alias: str) -> dict | None:
    """Return an existing ledger entry for the given semantic_alias, or None.

    This is the idempotency check: calling allocate twice with the same alias
    returns the original allocation, not a new number.

    Args:
        ledger: Ledger dict.
        semantic_alias: The human-readable sprint alias (e.g. "glistening-leaping-chipmunk").

    Returns:
        Existing entry dict if found, else None.
    """
    for entry in ledger.get("entries", []):
        if entry.get("semantic_alias") == semantic_alias:
            return entry
    return None


# ---------------------------------------------------------------------------
# Allocation function (TC-SRB-020-03)
# ---------------------------------------------------------------------------


def allocate_sprint_number(
    semantic_alias: str,
    mission_id: str | None = None,
    plan_id: str | None = None,
    ledger_path: Path | None = None,
    receipts_dir: Path | None = None,
) -> dict:
    """Allocate (or retrieve existing) sprint number for the given semantic alias.

    Uses os.replace() atomic write for Windows-safe crash-resistant allocation.

    Args:
        semantic_alias: The sprint's semantic name (e.g. "glistening-leaping-chipmunk").
        mission_id: Optional mission ID to record in the allocation.
        plan_id: Optional plan file path to record.
        ledger_path: Override ledger path (default: canonical).
        receipts_dir: Override receipts directory (default: canonical).

    Returns:
        Receipt dict with sprint_id, sprint_number, verdict, allocated_at.
    """
    lp = ledger_path or _LEDGER_PATH
    rd = receipts_dir or _RECEIPTS_DIR

    with _ALLOC_LOCK:
        return _allocate_sprint_number_locked(semantic_alias, mission_id, plan_id, lp, rd)


def _allocate_sprint_number_locked(
    semantic_alias: str,
    mission_id: str | None,
    plan_id: str | None,
    lp: Path,
    rd: Path,
) -> dict:
    """Inner (lock-held) implementation of allocate_sprint_number."""
    lp.parent.mkdir(parents=True, exist_ok=True)
    rd.mkdir(parents=True, exist_ok=True)

    ledger = load_ledger(lp)

    # Idempotency check: return existing allocation if alias already registered
    existing = find_existing_allocation(ledger, semantic_alias)
    if existing:
        return {
            "verdict": "ALREADY_ALLOCATED",
            "sprint_id": existing["sprint_id"],
            "sprint_number": existing["sprint_number"],
            "semantic_alias": semantic_alias,
            "allocated_at": existing.get("allocated_at", ""),
            "mission_id": existing.get("mission_id"),
            "plan_id": existing.get("plan_id"),
            "receipt_path": str(rd / f"{existing['sprint_id']}.json"),
        }

    # Allocate next number
    highest = find_highest_number(ledger)
    new_number = highest + 1
    new_sprint_id = f"SPRINT-{new_number:05d}"
    now = datetime.now(timezone.utc).isoformat()
    supervisor_id = str(uuid.uuid4())[:8]

    new_entry = {
        "sprint_number": new_number,
        "sprint_id": new_sprint_id,
        "semantic_alias": semantic_alias,
        "mission_id": mission_id,
        "plan_id": plan_id,
        "status": "ALLOCATED",
        "allocated_at": now,
        "supervisor_id": supervisor_id,
    }

    # Atomic write: write to .tmp then os.replace()
    ledger_entries = list(ledger.get("entries", []))
    ledger_entries.append(new_entry)
    new_ledger = {
        **ledger,
        "highest_allocated_number": new_number,
        "updated_at": now,
        "entries": ledger_entries,
    }
    tmp_path = Path(str(lp) + ".tmp")
    tmp_path.write_text(json.dumps(new_ledger, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp_path), str(lp))

    # Write receipt
    receipt = {
        "schema_version": "1.0",
        "verdict": "ALLOCATED",
        "sprint_id": new_sprint_id,
        "sprint_number": new_number,
        "semantic_alias": semantic_alias,
        "mission_id": mission_id,
        "plan_id": plan_id,
        "allocated_at": now,
        "supervisor_id": supervisor_id,
    }
    receipt_path = rd / f"{new_sprint_id}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path)

    return receipt


# ---------------------------------------------------------------------------
# Recover function (TC-SRB-020-04)
# ---------------------------------------------------------------------------


def recover_sprint(
    sprint_id: str,
    ledger_path: Path | None = None,
    receipts_dir: Path | None = None,
) -> dict:
    """Recover a sprint whose allocation was interrupted (in-flight tmp exists).

    Checks for an orphaned .tmp file and replaces the ledger if the tmp is newer.
    If no recovery is needed, returns status=CLEAN.

    Args:
        sprint_id: The sprint ID to check for recovery.
        ledger_path: Override ledger path.
        receipts_dir: Override receipts directory.

    Returns:
        Dict with verdict: RECOVERED | CLEAN | NOT_FOUND.
    """
    lp = ledger_path or _LEDGER_PATH
    rd = receipts_dir or _RECEIPTS_DIR

    tmp_path = Path(str(lp) + ".tmp")
    if not tmp_path.exists():
        return {"verdict": "CLEAN", "sprint_id": sprint_id, "note": "No orphaned .tmp file found"}

    # .tmp exists — atomically apply it
    try:
        tmp_ledger = json.loads(tmp_path.read_text(encoding="utf-8"))
        # Verify the tmp contains the sprint we're looking for
        entries = tmp_ledger.get("entries", [])
        found = any(e.get("sprint_id") == sprint_id for e in entries)
        if found:
            os.replace(str(tmp_path), str(lp))
            return {
                "verdict": "RECOVERED",
                "sprint_id": sprint_id,
                "note": f"Recovered from {tmp_path} — orphaned .tmp applied",
            }
        return {
            "verdict": "CLEAN",
            "sprint_id": sprint_id,
            "note": f".tmp exists but does not contain {sprint_id} — no action taken",
        }
    except Exception as exc:
        return {"verdict": "ERROR", "sprint_id": sprint_id, "error": str(exc)}


# ---------------------------------------------------------------------------
# Status and list functions (TC-SRB-020-05)
# ---------------------------------------------------------------------------


def get_status(ledger_path: Path | None = None) -> dict:
    """Return a status summary of the sprint ledger.

    Args:
        ledger_path: Override ledger path.

    Returns:
        Dict with total_allocated, highest_number, most_recent entry, etc.
    """
    lp = ledger_path or _LEDGER_PATH
    if not lp.exists():
        return {
            "ledger_exists": False,
            "total_allocated": 0,
            "highest_number": 0,
            "most_recent": None,
        }
    ledger = load_ledger(lp)
    entries = ledger.get("entries", [])
    return {
        "ledger_exists": True,
        "total_allocated": len(entries),
        "highest_number": find_highest_number(ledger),
        "bootstrap_highest": ledger.get("highest_allocated_number", 0),
        "most_recent": entries[-1] if entries else None,
        "updated_at": ledger.get("updated_at"),
    }


def list_sprints(n: int = 10, ledger_path: Path | None = None) -> list[dict]:
    """Return the last N sprint entries (most recent first).

    Args:
        n: Number of entries to return (default 10).
        ledger_path: Override ledger path.

    Returns:
        List of entry dicts.
    """
    ledger = load_ledger(ledger_path)
    entries = ledger.get("entries", [])
    return list(reversed(entries[-n:])) if entries else []


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sprint_number_allocator",
        description="Atomic sprint number allocator — Format Factory (TC-SRB-020)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # allocate
    alloc = sub.add_parser("allocate", help="Allocate a new sprint number")
    alloc.add_argument("--semantic-alias", required=True, help="Sprint semantic alias")
    alloc.add_argument("--mission-id", default=None)
    alloc.add_argument("--plan-id", default=None)
    alloc.add_argument("--ledger", default=None, type=Path, help="Override ledger path")

    # recover
    rec = sub.add_parser("recover", help="Recover from interrupted allocation")
    rec.add_argument("--sprint-id", required=True)
    rec.add_argument("--ledger", default=None, type=Path)

    # status
    stat = sub.add_parser("status", help="Show ledger status")
    stat.add_argument("--ledger", default=None, type=Path)

    # list
    lst = sub.add_parser("list", help="List recent sprint allocations")
    lst.add_argument("--n", type=int, default=10, help="Number to show (default 10)")
    lst.add_argument("--ledger", default=None, type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    ledger_override = getattr(args, "ledger", None)

    try:
        if args.command == "allocate":
            result = allocate_sprint_number(
                semantic_alias=args.semantic_alias,
                mission_id=args.mission_id,
                plan_id=args.plan_id,
                ledger_path=ledger_override,
            )
            print(json.dumps(result, indent=2))
            return 2 if result.get("verdict") == "ALREADY_ALLOCATED" else 0

        elif args.command == "recover":
            result = recover_sprint(
                sprint_id=args.sprint_id,
                ledger_path=ledger_override,
            )
            print(json.dumps(result, indent=2))
            return 1 if result.get("verdict") == "ERROR" else 0

        elif args.command == "status":
            result = get_status(ledger_path=ledger_override)
            print(json.dumps(result, indent=2))
            return 0

        elif args.command == "list":
            result = list_sprints(n=args.n, ledger_path=ledger_override)
            print(json.dumps(result, indent=2))
            return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
