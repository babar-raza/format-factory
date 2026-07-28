"""fact_id_allocator.py — Stable fact ID allocator for SAL facts (TC-SAL-ID-001).

Assigns deterministic, stable IDs in the format SAL-{FORMAT}-{NNNNN} to SAL facts.
Uses os.replace() atomic writes for crash safety. Thread-safe via threading.Lock().

Ledger: .local/sal-id/fact-id-ledger.json
The ledger is the single source of truth for all fact ID assignments.

Idempotency: if a fact (identified by its old qname) has already been assigned an ID,
the same ID is returned. Re-running the allocator on the same input produces identical
output.

Determinism: facts are processed in a stable order (workbench facts first by number,
then EX-extraction facts by number, then any remaining by qname lexicographic order).
Same input order always produces the same ID assignments.

CLI:
    python fact_id_allocator.py bulk --input .local/spec-cache/sal-facts-latest.json
    python fact_id_allocator.py allocate --format fods --old-id FACT-FODS-001
    python fact_id_allocator.py status
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LEDGER_PATH = _REPO_ROOT / ".local" / "sal-id" / "fact-id-ledger.json"
_ALLOC_LOCK = threading.Lock()

_RE_STANDARD = re.compile(r"^FACT-([A-Z0-9-]+)-(\d+)$")
_RE_EX = re.compile(r"^FACT-([A-Z0-9-]+)-EX-(\d+)$")


def _sort_key(old_id: str) -> tuple[int, int, str]:
    """Sort key: workbench facts (priority 0) before EX facts (priority 1), then by number."""
    m_ex = _RE_EX.match(old_id)
    if m_ex:
        return (1, int(m_ex.group(2)), old_id)
    m_std = _RE_STANDARD.match(old_id)
    if m_std:
        return (0, int(m_std.group(2)), old_id)
    return (2, 0, old_id)


def load_ledger(ledger_path: Path | None = None) -> dict:
    path = ledger_path or _LEDGER_PATH
    if not path.exists():
        return {
            "schema_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "formats": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _save_ledger(ledger: dict, ledger_path: Path | None = None) -> None:
    path = ledger_path or _LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def allocate(
    format_id: str,
    old_id: str,
    ledger_path: Path | None = None,
) -> dict:
    """Allocate or retrieve a stable fact ID for one fact.

    Returns dict with old_id, new_id, verdict ('NEW' or 'EXISTING').
    """
    with _ALLOC_LOCK:
        return _allocate_locked(format_id, old_id, ledger_path)


def _allocate_locked(format_id: str, old_id: str, ledger_path: Path | None) -> dict:
    ledger = load_ledger(ledger_path)
    fmt_upper = format_id.upper()
    fmt_key = format_id.lower()

    if fmt_key not in ledger["formats"]:
        ledger["formats"][fmt_key] = {"highest": 0, "mappings": {}}

    fmt_data = ledger["formats"][fmt_key]
    if old_id in fmt_data["mappings"]:
        return {
            "old_id": old_id,
            "new_id": fmt_data["mappings"][old_id],
            "verdict": "EXISTING",
        }

    fmt_data["highest"] += 1
    new_id = f"SAL-{fmt_upper}-{fmt_data['highest']:05d}"
    fmt_data["mappings"][old_id] = new_id
    _save_ledger(ledger, ledger_path)

    return {"old_id": old_id, "new_id": new_id, "verdict": "NEW"}


def allocate_bulk(
    sal_facts_path: Path,
    ledger_path: Path | None = None,
) -> dict:
    """Allocate stable IDs for all facts in a sal-facts-latest.json file.

    Returns summary dict with total_mapped, new_count, existing_count, and
    the full mapping {old_id: new_id}.
    """
    data = json.loads(sal_facts_path.read_text(encoding="utf-8"))
    results = data.get("results", [])

    total_new = 0
    total_existing = 0
    full_mapping: dict[str, str] = {}

    with _ALLOC_LOCK:
        ledger = load_ledger(ledger_path)

        for fmt_result in results:
            fmt_id = fmt_result["format_id"]
            fmt_upper = fmt_id.upper()
            fmt_key = fmt_id.lower()

            if fmt_key not in ledger["formats"]:
                ledger["formats"][fmt_key] = {"highest": 0, "mappings": {}}
            fmt_data = ledger["formats"][fmt_key]

            facts = fmt_result.get("spec_facts", [])
            old_ids = [f["qname"] for f in facts if "qname" in f]
            old_ids.sort(key=_sort_key)

            for old_id in old_ids:
                if old_id in fmt_data["mappings"]:
                    full_mapping[old_id] = fmt_data["mappings"][old_id]
                    total_existing += 1
                else:
                    fmt_data["highest"] += 1
                    new_id = f"SAL-{fmt_upper}-{fmt_data['highest']:05d}"
                    fmt_data["mappings"][old_id] = new_id
                    full_mapping[old_id] = new_id
                    total_new += 1

        _save_ledger(ledger, ledger_path)

    return {
        "total_mapped": total_new + total_existing,
        "new_count": total_new,
        "existing_count": total_existing,
        "mapping": full_mapping,
    }


def get_status(ledger_path: Path | None = None) -> dict:
    ledger = load_ledger(ledger_path)
    per_format = {}
    total = 0
    for fmt_key, fmt_data in ledger.get("formats", {}).items():
        count = len(fmt_data.get("mappings", {}))
        per_format[fmt_key] = {
            "highest": fmt_data.get("highest", 0),
            "mapped_count": count,
        }
        total += count
    return {"total_mapped": total, "formats": per_format}


def main() -> None:
    parser = argparse.ArgumentParser(description="SAL Fact ID Allocator (TC-SAL-ID-001)")
    sub = parser.add_subparsers(dest="command")

    alloc = sub.add_parser("allocate", help="Allocate one fact ID")
    alloc.add_argument("--format", required=True)
    alloc.add_argument("--old-id", required=True)
    alloc.add_argument("--ledger", type=Path, default=None)

    bulk = sub.add_parser("bulk", help="Allocate IDs for all facts in a SAL database")
    bulk.add_argument("--input", required=True, type=Path)
    bulk.add_argument("--ledger", type=Path, default=None)

    sub.add_parser("status", help="Show allocation status")

    args = parser.parse_args()

    if args.command == "allocate":
        result = allocate(args.format, args.old_id, args.ledger)
        print(json.dumps(result, indent=2))
    elif args.command == "bulk":
        result = allocate_bulk(args.input, args.ledger)
        print(json.dumps({
            "total_mapped": result["total_mapped"],
            "new_count": result["new_count"],
            "existing_count": result["existing_count"],
        }, indent=2))
    elif args.command == "status":
        print(json.dumps(get_status(), indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
