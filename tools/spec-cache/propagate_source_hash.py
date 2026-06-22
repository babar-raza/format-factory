"""propagate_source_hash.py — Propagate content_hash from spec-index.yaml to acquisition-packs.

For each format, reads .local/spec-cache/{format}/{version}/spec-index.yaml and
updates acquisition-packs/{format}/pack.yaml with the source_hash field.

Usage:
    python propagate_source_hash.py [--format fods] [--format zst] [--all]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"
_PACKS = _REPO_ROOT / "acquisition-packs"

_HASH_PATTERN = re.compile(r"content_hash:\s*(sha256:[a-f0-9]+)")


def _find_content_hash(format_id: str) -> str | None:
    """Return the first content_hash found in any spec-index.yaml for the format."""
    for si in sorted((_SPEC_CACHE / format_id.lower()).rglob("spec-index.yaml")):
        m = _HASH_PATTERN.search(si.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return None


def _update_pack_yaml(pack_path: Path, source_hash: str) -> bool:
    """Set or update source_hash field in pack.yaml. Returns True if changed."""
    text = pack_path.read_text(encoding="utf-8")
    null_pattern = re.compile(r"^(source_hash:\s*)null\s*$", re.MULTILINE)
    existing_pattern = re.compile(r"^(source_hash:\s*)(sha256:[a-f0-9]+)\s*$", re.MULTILINE)

    if null_pattern.search(text):
        new_text = null_pattern.sub(rf"\g<1>{source_hash}", text)
    elif existing_pattern.search(text):
        m = existing_pattern.search(text)
        if m and m.group(2) == source_hash:
            return False  # already correct
        new_text = existing_pattern.sub(rf"\g<1>{source_hash}", text)
    else:
        # Field missing — insert after 'generated_by:' or at end of header block
        insert_after = re.compile(r"^(generated_at:.*)", re.MULTILINE)
        if insert_after.search(text):
            new_text = insert_after.sub(rf"\1\nsource_hash: {source_hash}", text, count=1)
        else:
            new_text = text.rstrip("\n") + f"\nsource_hash: {source_hash}\n"

    pack_path.write_text(new_text, encoding="utf-8")
    return True


def propagate(format_id: str) -> dict:
    pack_path = _PACKS / format_id.lower() / "pack.yaml"
    if not pack_path.exists():
        return {"format_id": format_id, "status": "no_pack_yaml"}

    content_hash = _find_content_hash(format_id)
    if not content_hash:
        return {"format_id": format_id, "status": "no_spec_index_hash"}

    changed = _update_pack_yaml(pack_path, content_hash)
    return {
        "format_id": format_id,
        "status": "updated" if changed else "already_correct",
        "source_hash": content_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Propagate spec content_hash to acquisition packs")
    parser.add_argument("--format", action="append", dest="formats", metavar="FORMAT_ID")
    parser.add_argument("--all", action="store_true", help="Process all formats with acquisition packs")
    args = parser.parse_args()

    if args.all:
        formats = [d.name for d in _PACKS.iterdir() if d.is_dir() and not d.name.startswith("_")]
    else:
        formats = args.formats or []

    if not formats:
        print("Specify --format <id> or --all", file=sys.stderr)
        return 1

    for fmt in sorted(formats):
        result = propagate(fmt)
        print(f"[{result['format_id']}] {result['status']}" +
              (f": {result.get('source_hash','')}" if result.get('source_hash') else ""),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
