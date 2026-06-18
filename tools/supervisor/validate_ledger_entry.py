"""
validate_ledger_entry.py — Track P ledger entry validation (TC-P2-008).

Validates that a Track P sprint has written at least one ledger entry to
reports/r90/product-code-change-ledger.json for each G3/G4/G5 work item
in the declaration.

Used by autonomous_cycle.py --track product to enforce REQ-LED-001 through REQ-LED-003.

Exit codes (when run as __main__):
    0 — validation passed
    7 — LEDGER_ENTRY_MISSING (Track P sprint must write ledger entry before closing)

Usage:
    python tools/supervisor/validate_ledger_entry.py \
        --sprint-id <id> \
        --declaration <path-to-yaml>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent
_default_ledger = _default_repo / "reports" / "r90" / "product-code-change-ledger.json"

# Work groups that require ledger entries (Track P product groups)
PRODUCT_WORK_GROUPS = frozenset({"G3", "G4", "G5"})

# Required fields per ledger entry (REQ-LED-002)
REQUIRED_FIELDS = ("capability", "format", "test_delta", "git_head", "sprint_id")


def _load_ledger(ledger_path: Path) -> list:
    """Load ledger JSON. Returns list of entries or empty list on error."""
    if not ledger_path.exists():
        return []
    try:
        raw = json.loads(ledger_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        # Some ledgers are wrapped: {"entries": [...]}
        if isinstance(raw, dict):
            return raw.get("entries", raw.get("ledger", []))
    except Exception:
        pass
    return []


def _entry_has_required_fields(entry: dict) -> tuple[bool, list[str]]:
    """Return (all_present, missing_fields) for required fields check."""
    missing = [f for f in REQUIRED_FIELDS if not entry.get(f)]
    return len(missing) == 0, missing


def validate_ledger_entry_exists(
    sprint_id: str,
    work_items: list[dict],
    ledger_path: Path | None = None,
) -> tuple[bool, list[str], str | None]:
    """Validate that the ledger contains at least one entry for this sprint.

    Parameters
    ----------
    sprint_id : str
        The sprint run_id to match against ledger entries.
    work_items : list[dict]
        Declared work items (planned_work_items from declaration).
        Only G3/G4/G5 items require ledger entries (REQ-LED-001).
    ledger_path : Path | None
        Path to product-code-change-ledger.json.
        Defaults to reports/r90/product-code-change-ledger.json.

    Returns
    -------
    (is_valid, missing_items, error_msg)
        is_valid: True if validation passes
        missing_items: list of work item IDs that lack ledger entries
        error_msg: human-readable error string or None
    """
    _ledger_path = ledger_path or _default_ledger

    # Filter to product work items only
    product_items = [
        item for item in work_items
        if item.get("work_group", item.get("group", "")) in PRODUCT_WORK_GROUPS
    ]

    if not product_items:
        # No G3/G4/G5 items — ledger check not required
        return True, [], None

    ledger = _load_ledger(_ledger_path)

    # Find entries matching this sprint_id
    sprint_entries = [e for e in ledger if e.get("sprint_id") == sprint_id]

    if not sprint_entries:
        missing = [item.get("item_id", item.get("title", "?")) for item in product_items]
        return False, missing, (
            f"No ledger entries found for sprint_id={sprint_id!r} in {_ledger_path}. "
            f"Track P work items ({len(product_items)} items) require a ledger entry. "
            f"Write to {_ledger_path} with fields: {', '.join(REQUIRED_FIELDS)}."
        )

    # Validate required fields on found entries (REQ-LED-002)
    field_violations: list[str] = []
    for entry in sprint_entries:
        ok, missing_fields = _entry_has_required_fields(entry)
        if not ok:
            entry_id = entry.get("capability", entry.get("item_id", "?"))
            field_violations.append(
                f"Entry {entry_id!r} missing fields: {missing_fields}"
            )

    if field_violations:
        return False, field_violations, (
            f"Ledger entries for sprint_id={sprint_id!r} have missing required fields. "
            f"Violations: {'; '.join(field_violations)}"
        )

    return True, [], None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Track P ledger entry exists for sprint"
    )
    parser.add_argument("--sprint-id", required=True, help="Sprint run_id to validate")
    parser.add_argument("--ledger-path", type=Path, default=None,
                        help=f"Path to ledger JSON (default: {_default_ledger})")
    parser.add_argument("--declaration", type=Path, default=None,
                        help="Path to evidence-declaration.yaml (for work item extraction)")
    parser.add_argument("--repo-root", type=Path, default=_default_repo)
    args = parser.parse_args(argv)

    work_items: list[dict] = []
    if args.declaration and args.declaration.exists():
        try:
            import yaml
            decl = yaml.safe_load(args.declaration.read_text(encoding="utf-8"))
            work_items = decl.get("planned_work_items", [])
        except Exception as e:
            print(f"WARNING: Could not load declaration: {e}", file=sys.stderr)

    ledger_path = args.ledger_path
    if ledger_path is None:
        ledger_path = args.repo_root / "reports" / "r90" / "product-code-change-ledger.json"

    is_valid, missing, error_msg = validate_ledger_entry_exists(
        sprint_id=args.sprint_id,
        work_items=work_items,
        ledger_path=ledger_path,
    )

    if is_valid:
        print(f"LEDGER_VALID: sprint_id={args.sprint_id!r} has valid ledger entry.")
        return 0
    else:
        print(f"LEDGER_ENTRY_MISSING: {error_msg}", file=sys.stderr)
        return 7


if __name__ == "__main__":
    sys.exit(main())
