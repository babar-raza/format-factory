"""check_tombstone_records.py — Read tombstone invocation records; classify each file FIRED or CONFIRMED_DEAD.

After the 30-day observation window, run this script to determine whether any
tombstoned SUSPECTED_GHOST or DEPRECATED_STILL_ACTIVE file was invoked.

Exit codes:
  0 — all tombstoned files show CONFIRMED_DEAD (zero records)
  1 — one or more files FIRED (records found — operator attention needed)

Usage:
  python tools/supervisor/check_tombstone_records.py
  python tools/supervisor/check_tombstone_records.py --output .local/tombstone-classification.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify tombstone observation records")
    parser.add_argument("--output", type=Path, default=None,
                        help="Write classification report JSON to this path")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Explicit repo root (auto-detected if omitted)")
    args = parser.parse_args()

    # Locate repo root
    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve()
        while repo_root.name not in ("format-factory", "") and repo_root != repo_root.parent:
            repo_root = repo_root.parent

    register_path = repo_root / "tools" / "supervisor" / "COMPONENT-REGISTER.yaml"
    tombstones_dir = repo_root / ".local" / "supervisor" / "invocation-tombstones"

    # Load register
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        return 1

    if not register_path.exists():
        print(f"ERROR: COMPONENT-REGISTER.yaml not found at {register_path}", file=sys.stderr)
        return 1

    data = yaml.safe_load(register_path.read_text(encoding="utf-8"))
    active_tombstones = [
        c for c in data.get("components", [])
        if c.get("tombstone_status") == "ACTIVE"
    ]

    if not active_tombstones:
        print("INFO: No files with tombstone_status=ACTIVE found in register.")
        return 0

    # Scan tombstone records
    records: Dict[str, List[dict]] = {}
    if tombstones_dir.exists():
        for rec_file in sorted(tombstones_dir.glob("*.json")):
            try:
                rec = json.loads(rec_file.read_text(encoding="utf-8"))
                source_file = rec.get("file", "")
                stem = Path(source_file).stem if source_file else rec_file.stem.rsplit("_", 1)[0]
                records.setdefault(stem, []).append(rec)
            except Exception:
                pass

    # Classify each tombstoned file
    results = []
    fired_count = 0
    for comp in active_tombstones:
        file_path = comp.get("file", "")
        stem = Path(file_path).stem
        file_records = records.get(stem, [])
        if file_records:
            status = "FIRED"
            fired_count += 1
        else:
            status = "CONFIRMED_DEAD"
        results.append({
            "file": file_path,
            "component_id": comp.get("component_id", ""),
            "classification": comp.get("classification", ""),
            "tombstone_date": comp.get("tombstone_date", ""),
            "observation_window_expires": comp.get("observation_window_expires", ""),
            "status": status,
            "record_count": len(file_records),
            "records": file_records,
        })

    # Print summary table
    print(f"Tombstone observation report: {len(results)} files observed")
    print(f"  CONFIRMED_DEAD: {len(results) - fired_count}")
    print(f"  FIRED:          {fired_count}")
    print()
    for r in results:
        mark = "FIRED" if r["status"] == "FIRED" else "DEAD "
        print(f"  [{mark}] {r['file']} (records: {r['record_count']})")
        if r["status"] == "FIRED":
            for rec in r["records"][:3]:
                print(f"         caller: {rec.get('caller', '?')}")
                print(f"         timestamp: {rec.get('timestamp', '?')}")

    # Write JSON output
    report = {
        "total": len(results),
        "fired": fired_count,
        "confirmed_dead": len(results) - fired_count,
        "files": results,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nReport written to: {args.output}")

    if fired_count > 0:
        print(f"\nACTION REQUIRED: {fired_count} tombstoned file(s) fired — they are LIVE.")
        print("Update their register classification and investigate invocation paths.")
        return 1

    print(f"\nAll {len(results)} tombstoned files CONFIRMED_DEAD in observation period.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
