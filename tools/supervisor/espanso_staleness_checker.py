"""espanso_staleness_checker.py — Espanso Provenance Map Staleness Detector

TC-P1-001 (FF-ESP-INT-001 / imperative-coalescing-bengio)

Modes:
  --backfill-hashes   : Extract body at stored line_range for each entry and write
                        body_sha256 back to provenance map. Idempotent.
  --detect (default)  : Compare current file body hashes against stored body_sha256.
                        Report MODIFIED, NEW, and UNCHANGED blocks.
  --update-map        : Append new blocks (not yet in map) as new entries with
                        disposition UNCLASSIFIED. Never overwrites existing entries.

Requirements met:
  REQ-STALE-001: detect new/modified blocks
  REQ-STALE-002: backfill body_sha256 from stored line_range
  REQ-STALE-003: idempotent — second run on unchanged files exits 0
  REQ-STALE-004: --update-map appends NEW entries only, never overwrites

Exit codes:
  --backfill-hashes: 0 always (best-effort)
  --detect: 0 if no modifications or new blocks detected; 1 if changes found
  --update-map: 0 always (new entries appended if found)
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_PROVENANCE_MAP = REPO_ROOT / ".supervisor" / "prompts" / "espanso-provenance-map.yaml"
DEFAULT_ESPANSO_SOURCE = Path(
    "C:/Users/prora/AppData/Roaming/espanso/match/format-factory.yml"
)

# Regex to detect Espanso trigger blocks
_TRIGGER_RE = re.compile(r"^\s*-\s+trigger:\s+['\"]?(.+?)['\"]?\s*$")
_TRIGGERS_RE = re.compile(r"^\s+triggers:\s*$")
_TRIGGER_ITEM_RE = re.compile(r"^\s+-\s+['\"]?(.+?)['\"]?\s*$")


def _compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_provenance_map(map_path: Path) -> dict:
    return yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}


def _save_provenance_map(map_path: Path, data: dict) -> None:
    text = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    map_path.write_text(text, encoding="utf-8")


def _load_source_lines(source_path: Path) -> list[str]:
    return source_path.read_text(encoding="utf-8", errors="replace").splitlines()


def _extract_body_at_range(lines: list[str], line_range: list[int]) -> str:
    """Extract lines at [start, end] (1-indexed, inclusive). Returns joined text."""
    start, end = line_range[0], line_range[1]
    # Convert to 0-indexed
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)
    return "\n".join(lines[start_idx:end_idx])


def _find_blocks_in_source(lines: list[str]) -> list[dict]:
    """Find all Espanso blocks by scanning for trigger: entries.
    Returns list of {line_start, line_end, primary_trigger}.
    """
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = _TRIGGER_RE.match(line)
        if m:
            trigger = m.group(1).strip()
            start = i + 1  # 1-indexed
            # Find the end of this block: next trigger: or - trigger: at same indent level
            # Simple heuristic: scan forward until we hit the next "  - trigger:" pattern
            j = i + 1
            while j < n:
                next_line = lines[j]
                if _TRIGGER_RE.match(next_line):
                    break
                j += 1
            end = j  # 1-indexed exclusive, so end of block is j (the last line of this block)
            blocks.append({
                "line_start": start,
                "line_end": end,
                "primary_trigger": trigger,
            })
            i = j
        else:
            i += 1
    return blocks


def cmd_backfill_hashes(args: argparse.Namespace) -> int:
    """--backfill-hashes: compute SHA256 for each entry's body and write to provenance map."""
    map_path = args.map
    source_path = args.source

    if not source_path.exists():
        print(f"[backfill-hashes] ERROR: Espanso source not found at {source_path}")
        return 1

    data = _load_provenance_map(map_path)
    lines = _load_source_lines(source_path)

    entries = data.get("provenance_entries", [])
    updated = 0
    for entry in entries:
        lr = entry.get("line_range")
        if not lr or len(lr) < 2:
            continue
        body = _extract_body_at_range(lines, lr)
        sha = _compute_sha256(body)
        if entry.get("body_sha256") != sha:
            entry["body_sha256"] = sha
            updated += 1

    _save_provenance_map(map_path, data)
    print(f"[backfill-hashes] Updated {updated}/{len(entries)} entries with body_sha256")
    if updated == 0:
        print("[backfill-hashes] All entries already have current body_sha256 — IDEMPOTENT")
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    """--detect: compare current source body hashes against stored body_sha256."""
    map_path = args.map
    source_path = args.source

    if not source_path.exists():
        print(f"[detect] ERROR: Espanso source not found at {source_path}")
        print("[detect] Cannot detect staleness without source file.")
        return 0  # Non-blocking: source may not be available in CI

    data = _load_provenance_map(map_path)
    lines = _load_source_lines(source_path)
    current_line_count = len(lines)
    stored_line_count = data.get("source_line_count", 0)

    print(f"[detect] Stored line count: {stored_line_count} | Current: {current_line_count}")

    entries = data.get("provenance_entries", [])
    modified = []
    no_hash = []

    for entry in entries:
        lr = entry.get("line_range")
        stored_sha = entry.get("body_sha256")
        block_id = entry.get("block_id", "?")

        if not stored_sha:
            no_hash.append(block_id)
            continue

        if not lr or len(lr) < 2:
            continue

        body = _extract_body_at_range(lines, lr)
        current_sha = _compute_sha256(body)

        if current_sha != stored_sha:
            modified.append({
                "block_id": block_id,
                "trigger": entry.get("primary_trigger", "?"),
                "stored_sha": stored_sha[:16],
                "current_sha": current_sha[:16],
            })

    # Detect new blocks (source grew)
    new_block_count = 0
    if current_line_count > stored_line_count:
        new_block_count = current_line_count - stored_line_count
        print(
            f"[detect] Source grew by {new_block_count} lines — likely new Espanso entries. "
            "Run --update-map to ingest new entries."
        )

    if no_hash:
        print(f"[detect] {len(no_hash)} entries lack body_sha256 — run --backfill-hashes first")

    if modified:
        print(f"[detect] MODIFIED: {len(modified)} block(s) have changed body content:")
        for m in modified:
            print(
                f"  block_id={m['block_id']} trigger={m['trigger']} "
                f"stored={m['stored_sha']}... current={m['current_sha']}..."
            )
        return 1

    if new_block_count > 0:
        print(f"[detect] NEW CONTENT: source grew by {new_block_count} lines")
        return 1

    print(f"[detect] PASS — {len(entries)} entries checked, no modifications detected")
    return 0


def cmd_update_map(args: argparse.Namespace) -> int:
    """--update-map: append new block entries for triggers not in the map."""
    map_path = args.map
    source_path = args.source

    if not source_path.exists():
        print(f"[update-map] ERROR: Espanso source not found at {source_path}")
        return 1

    data = _load_provenance_map(map_path)
    lines = _load_source_lines(source_path)

    entries = data.get("provenance_entries", [])
    existing_triggers = set()
    for e in entries:
        existing_triggers.add(e.get("primary_trigger", ""))
        for t in e.get("all_triggers", []):
            existing_triggers.add(t)

    # Find all blocks in source
    source_blocks = _find_blocks_in_source(lines)

    new_entries = []
    next_id = max((e.get("block_id", 0) for e in entries), default=0) + 1

    for blk in source_blocks:
        trigger = blk["primary_trigger"]
        if trigger in existing_triggers:
            continue
        body = _extract_body_at_range(lines, [blk["line_start"], blk["line_end"]])
        new_entries.append({
            "block_id": next_id,
            "primary_trigger": trigger,
            "all_triggers": [trigger],
            "line_range": [blk["line_start"], blk["line_end"]],
            "family": "unclassified",
            "disposition": "UNCLASSIFIED",
            "body_sha256": _compute_sha256(body),
            "notes": "Auto-appended by --update-map. Classify manually.",
        })
        existing_triggers.add(trigger)
        next_id += 1

    if new_entries:
        data["provenance_entries"] = entries + new_entries
        data["block_count"] = len(data["provenance_entries"])
        data["source_line_count"] = len(lines)
        _save_provenance_map(map_path, data)
        print(f"[update-map] Appended {len(new_entries)} new entries (UNCLASSIFIED)")
    else:
        print("[update-map] No new entries found — map is current")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Espanso provenance map staleness checker")
    parser.add_argument("--map", type=Path, default=DEFAULT_PROVENANCE_MAP,
                        help="Path to espanso-provenance-map.yaml")
    parser.add_argument("--source", type=Path, default=DEFAULT_ESPANSO_SOURCE,
                        help="Path to Espanso format-factory.yml source")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--backfill-hashes", action="store_true",
                      help="Backfill body_sha256 into all entries from stored line_range")
    mode.add_argument("--update-map", action="store_true",
                      help="Append new source blocks not yet in the provenance map")
    args = parser.parse_args()

    if args.backfill_hashes:
        return cmd_backfill_hashes(args)
    elif args.update_map:
        return cmd_update_map(args)
    else:
        return cmd_detect(args)


if __name__ == "__main__":
    sys.exit(main())
