"""
migrate_sources_jsonl.py — One-time migration of sources.jsonl to SpecSource schema.

TC-SAL-IMPL-004: Migrate .local/spec-source-registry/sources.jsonl from the
legacy schema (spec_id, spec_name, source_sha256, local_path) to SpecSource
schema (source_id, title, sha256_snapshot, url_or_path, source_type, etc.).

Usage:
  python migrate_sources_jsonl.py              # dry-run (print migrated records)
  python migrate_sources_jsonl.py --execute    # overwrite sources.jsonl in place
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_REPO = Path(__file__).resolve().parents[2]
_SOURCES_PATH = _REPO / ".local" / "spec-source-registry" / "sources.jsonl"

# Map retrieval_status to source_type
_STATUS_TO_TYPE = {
    "cached": "acquired_verified",
    "PUBLIC_STANDARD": "public_standard",
    "PUBLIC_OPEN_FORMAT": "public_standard",
    "HISTORICAL_REFERENCE": "historical_reference",
    "RETRIEVED_VIA_WEBFETCH": "web_fetched",
    "BLOCKED_SERVER_DOWN": "unavailable",
}


def _infer_source_type(record: Dict[str, Any]) -> str:
    status = record.get("retrieval_status", "")
    return _STATUS_TO_TYPE.get(status, "unknown")


def migrate_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert one legacy record to SpecSource schema."""
    return {
        "source_id": record.get("spec_id", ""),
        "format_id": record.get("format_id", ""),
        "title": record.get("spec_name", ""),
        "source_type": _infer_source_type(record),
        "url_or_path": record.get("local_path", ""),
        "registered_at": record.get("cached_at", ""),
        "status": "registered" if record.get("retrieval_status") != "BLOCKED_SERVER_DOWN" else "unavailable",
        "sha256_snapshot": record.get("source_sha256"),
        "snapshot_path": record.get("local_path", ""),
        "fetch_policy": "deferred_local_fixture",
        "local_fixture_path": record.get("local_path"),
        "sections_indexed": 0,
        "requirements_extracted": 0,
        "extra": {
            "legacy_version": record.get("version", ""),
            "legacy_retrieval_status": record.get("retrieval_status", ""),
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "migration_tool": "migrate_sources_jsonl.py v1.0",
        },
    }


def load_legacy() -> List[Dict[str, Any]]:
    if not _SOURCES_PATH.exists():
        print(f"[migrate] sources.jsonl not found at {_SOURCES_PATH}", file=sys.stderr)
        return []
    records = []
    for line in _SOURCES_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate sources.jsonl to SpecSource schema")
    parser.add_argument("--execute", action="store_true", help="Overwrite sources.jsonl (default: dry-run)")
    args = parser.parse_args()

    legacy = load_legacy()
    if not legacy:
        print("[migrate] No records to migrate.", file=sys.stderr)
        return

    migrated = [migrate_record(r) for r in legacy]

    for m in migrated:
        print(f"[migrate] {m['format_id']}: {m['source_id']} -> source_type={m['source_type']}", file=sys.stderr)

    if args.execute:
        # Backup
        backup = _SOURCES_PATH.with_suffix(".jsonl.bak")
        backup.write_text(_SOURCES_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[migrate] Backup written to {backup}", file=sys.stderr)

        # Write migrated
        lines = [json.dumps(m, ensure_ascii=False) for m in migrated]
        _SOURCES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[migrate] Migrated {len(migrated)} records to {_SOURCES_PATH}", file=sys.stderr)
    else:
        print(json.dumps(migrated, indent=2))
        print(f"\n[migrate] DRY RUN — {len(migrated)} records would be migrated", file=sys.stderr)
        print("[migrate] Run with --execute to apply.", file=sys.stderr)


if __name__ == "__main__":
    main()
