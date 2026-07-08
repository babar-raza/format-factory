"""maintenance_obligation_register.py — Maintenance Obligation Register (MOR)

Extracts, registers, surfaces, and completes maintenance obligations declared in plan
files. Obligations are items deferred beyond a plan's scope with a concrete future
action — observation windows, scheduled maintenance, follow-up tasks.

Why not the gap ledger:
  capability_map_generator.py regenerates gap-ledger.json on every autonomous cycle.
  Open entries not derived from POC targets are silently discarded. The MOR is a
  separate JSON file that capability_map_generator.py never touches.

Canonical plan declaration format (## Deferred Work Register section):

  ```yaml
  deferred_item:
    obligation_id: MO-BGG-001
    source_taskcard: TC-BF-004
    type: observation_window
    action: "run check_tombstone_records.py; classify files as FIRED or CONFIRMED_DEAD"
    scheduled_date: "2026-08-05"
    owner: governance
    reason: "30-day observation window from tombstone_date 2026-07-06"
  ```

Lifecycle: open → completed | missed
MOR path: reports/supervisor/maintenance-obligations.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_MOR_REL = Path("reports") / "supervisor" / "maintenance-obligations.json"
_SCHEMA_VERSION = "1.0"

# Required fields for a valid deferred_item block
_REQUIRED_FIELDS = {"obligation_id", "type", "action"}
# Valid obligation types
_VALID_TYPES = {
    "observation_window",
    "scheduled_maintenance",
    "follow_up",
    "valid_deferred",
}

# Regex to find fenced YAML blocks inside ## Deferred Work Register sections
_SECTION_RE = re.compile(
    r"##\s+Deferred\s+Work\s+Register.*?(?=\n##\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)
_FENCED_YAML_RE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL)


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------


def extract_from_plan(plan_path: Path) -> list[dict[str, Any]]:
    """Parse ## Deferred Work Register sections for deferred_item: YAML blocks.

    Returns a list of raw obligation dicts. Returns an empty list when the
    section is absent or no valid blocks are found.

    Raises ValueError on malformed YAML (fail loudly — do not silently skip).
    Raises FileNotFoundError if plan_path does not exist.
    """
    try:
        import yaml as _yaml
    except ImportError:
        # yaml not available — fall back to minimal key-value parser
        _yaml = None  # type: ignore[assignment]

    text = plan_path.read_text(encoding="utf-8", errors="replace")
    sections = _SECTION_RE.findall(text)
    if not sections:
        return []

    obligations: list[dict[str, Any]] = []
    for section in sections:
        for fenced in _FENCED_YAML_RE.findall(section):
            block = fenced.strip()
            if not block.startswith("deferred_item:"):
                continue
            if _yaml is not None:
                try:
                    parsed = _yaml.safe_load(block)
                except Exception as exc:
                    raise ValueError(
                        f"Malformed YAML in Deferred Work Register of {plan_path}: {exc}"
                    ) from exc
                item = parsed.get("deferred_item", parsed) if isinstance(parsed, dict) else {}
            else:
                item = _parse_kv_block(block)

            missing = _REQUIRED_FIELDS - set(item.keys())
            if missing:
                raise ValueError(
                    f"deferred_item in {plan_path} missing required fields: {missing}. "
                    f"Block content: {block[:120]}"
                )
            if item.get("type") not in _VALID_TYPES:
                raise ValueError(
                    f"deferred_item obligation_id={item.get('obligation_id')!r} has "
                    f"invalid type={item.get('type')!r}. "
                    f"Valid types: {sorted(_VALID_TYPES)}"
                )
            obligations.append(dict(item))

    return obligations


def register_obligations(
    obligations: list[dict[str, Any]],
    source_plan: str,
    source_plan_hash: str,
    register_path: Path,
) -> tuple[int, int]:
    """Idempotent write to MOR. Deduplicates by obligation_id.

    Returns (newly_added, already_existed).
    Completed obligations are never overwritten.
    Creates the register file if absent.
    """
    mor = _load_mor(register_path)
    existing_ids = {o["obligation_id"]: i for i, o in enumerate(mor["obligations"])}
    now = datetime.now(timezone.utc).isoformat()

    added = 0
    existed = 0
    for raw in obligations:
        oid = raw["obligation_id"]
        if oid in existing_ids:
            # Never overwrite a completed obligation
            idx = existing_ids[oid]
            if mor["obligations"][idx].get("status") != "completed":
                # Update mutable metadata (action/reason may be refined) but
                # preserve status and completion fields
                mor["obligations"][idx].update(
                    {k: v for k, v in raw.items() if k not in ("status", "completed_at", "completion_evidence")}
                )
                mor["obligations"][idx]["source_plan"] = source_plan
                mor["obligations"][idx]["source_plan_hash"] = source_plan_hash
            existed += 1
        else:
            entry = {
                "obligation_id": oid,
                "type": raw.get("type"),
                "action": raw.get("action"),
                "scheduled_date": str(raw["scheduled_date"]) if "scheduled_date" in raw else None,
                "owner": raw.get("owner", "maintenance"),
                "reason": raw.get("reason", ""),
                "source_plan": source_plan,
                "source_plan_hash": source_plan_hash,
                "source_taskcard": raw.get("source_taskcard"),
                "status": "open",
                "created_at": now,
                "completed_at": None,
                "completion_evidence": None,
            }
            mor["obligations"].append(entry)
            added += 1

    mor["last_updated"] = now
    _save_mor(register_path, mor)
    return added, existed


def surface_due_obligations(
    register_path: Path,
    lookahead_days: int = 14,
) -> list[dict[str, Any]]:
    """Return open obligations due within lookahead_days, plus undated open ones.

    Returns an empty list if the register is absent.
    """
    if not register_path.exists():
        return []

    mor = _load_mor(register_path)
    today = date.today()
    due: list[dict[str, Any]] = []

    for o in mor["obligations"]:
        if o.get("status") != "open":
            continue
        sched = o.get("scheduled_date")
        if sched is None:
            due.append(o)
        else:
            try:
                d = date.fromisoformat(str(sched))
                if (d - today).days <= lookahead_days:
                    due.append(o)
            except ValueError:
                due.append(o)  # unparseable date — always surface

    return sorted(due, key=lambda x: (x.get("scheduled_date") or "9999-99-99"))


def mark_completed(
    obligation_id: str,
    evidence: str,
    register_path: Path,
) -> bool:
    """Transition obligation from open to completed. Idempotent.

    Returns False if obligation not found (not an error — safe to call without
    verifying existence first).
    """
    if not register_path.exists():
        return False

    mor = _load_mor(register_path)
    now = datetime.now(timezone.utc).isoformat()
    for o in mor["obligations"]:
        if o["obligation_id"] == obligation_id:
            if o.get("status") == "completed":
                return True  # idempotent
            o["status"] = "completed"
            o["completed_at"] = now
            o["completion_evidence"] = evidence
            mor["last_updated"] = now
            _save_mor(register_path, mor)
            return True
    return False


# ---------------------------------------------------------------------------
# Convenience wrapper used by write_plan_lock.py
# ---------------------------------------------------------------------------


def extract_and_pin_deferred_items(
    plan_path: str,
    plan_hash: str,
    locked_at: str,
    repo_root: Path | None = None,
) -> int:
    """Extract deferred items from plan and write to MOR. Returns count added.

    Designed to be called from write_plan_lock.py at TERMINAL_CLOSED.
    Non-blocking callers should wrap this in try/except.
    """
    root = repo_root or _REPO_ROOT
    p = Path(plan_path) if Path(plan_path).is_absolute() else root / plan_path
    if not p.exists():
        return 0

    obligations = extract_from_plan(p)
    if not obligations:
        return 0

    mor_path = root / _MOR_REL
    mor_path.parent.mkdir(parents=True, exist_ok=True)
    added, _ = register_obligations(obligations, plan_path, plan_hash, mor_path)
    return added


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_mor(path: Path) -> dict[str, Any]:
    """Load MOR JSON or return a fresh skeleton."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema_version": _SCHEMA_VERSION,
        "generated_by": "maintenance_obligation_register",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "obligations": [],
    }


def _save_mor(path: Path, mor: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mor, indent=2) + "\n", encoding="utf-8")


def _parse_kv_block(block: str) -> dict[str, Any]:
    """Minimal key-value parser used when PyYAML is not available.

    Handles simple flat YAML (no nesting, no lists).
    """
    result: dict[str, Any] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and val and key != "deferred_item":
            result[key] = val
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Maintenance Obligation Register — extract, surface, complete obligations"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # extract
    ext = sub.add_parser("extract", help="Extract deferred items from a plan file")
    ext.add_argument("--plan-path", required=True, help="Path to plan file")
    ext.add_argument(
        "--register",
        default=str(_REPO_ROOT / _MOR_REL),
        help="Path to MOR JSON (default: reports/supervisor/maintenance-obligations.json)",
    )
    ext.add_argument("--dry-run", action="store_true", help="Print items but do not write")

    # surface
    surf = sub.add_parser("surface", help="Show obligations due within N days")
    surf.add_argument("--lookahead-days", type=int, default=14)
    surf.add_argument(
        "--register",
        default=str(_REPO_ROOT / _MOR_REL),
    )

    # complete
    comp = sub.add_parser("complete", help="Mark an obligation as completed")
    comp.add_argument("--obligation-id", required=True)
    comp.add_argument("--evidence", required=True)
    comp.add_argument(
        "--register",
        default=str(_REPO_ROOT / _MOR_REL),
    )

    # list
    lst = sub.add_parser("list", help="List all obligations")
    lst.add_argument("--status", default=None, help="Filter by status (open/completed)")
    lst.add_argument(
        "--register",
        default=str(_REPO_ROOT / _MOR_REL),
    )

    args = parser.parse_args()

    if args.cmd == "extract":
        plan = Path(args.plan_path)
        if not plan.is_absolute():
            plan = _REPO_ROOT / plan
        try:
            items = extract_from_plan(plan)
        except (ValueError, FileNotFoundError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        if not items:
            print("No deferred_item blocks found in ## Deferred Work Register section.")
            return
        for item in items:
            print(json.dumps(item, indent=2))
        if not args.dry_run:
            register_path = Path(args.register)
            ph = hashlib.sha256(plan.read_bytes()).hexdigest()[:16]
            added, existed = register_obligations(items, str(plan), ph, register_path)
            print(f"\n{added} added, {existed} already existed -> {register_path}")

    elif args.cmd == "surface":
        due = surface_due_obligations(Path(args.register), args.lookahead_days)
        if not due:
            print("No obligations due within the lookahead window.")
            return
        print(f"{len(due)} obligation(s) due:")
        for o in due:
            sched = o.get("scheduled_date") or "(no date)"
            print(f"  [{o['obligation_id']}] {sched}  {o['type']}  owner={o['owner']}")
            print(f"    action: {o['action'][:80]}")

    elif args.cmd == "complete":
        ok = mark_completed(args.obligation_id, args.evidence, Path(args.register))
        if ok:
            print(f"Obligation {args.obligation_id!r} marked completed.")
        else:
            print(f"Obligation {args.obligation_id!r} not found in register.", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "list":
        if not Path(args.register).exists():
            print("MOR not found.")
            return
        mor = _load_mor(Path(args.register))
        items = mor["obligations"]
        if args.status:
            items = [o for o in items if o.get("status") == args.status]
        if not items:
            print("No obligations match.")
            return
        for o in items:
            sched = o.get("scheduled_date") or "(no date)"
            print(f"  [{o['status']:9}] {o['obligation_id']}  {sched}  {o['type']}")
            print(f"    action: {o['action'][:80]}")


if __name__ == "__main__":
    _cli()
