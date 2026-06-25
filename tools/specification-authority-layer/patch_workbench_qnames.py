#!/usr/bin/env python3
"""
patch_workbench_qnames.py — Populate qname=None workbench facts with claim_id.

For all verified-facts-review.json files in .local/spec-cache/*/workbench/:
  - If a fact has qname=None, set qname = claim_id (or fact_id as fallback)
  - Idempotent: skips facts that already have qname populated

Usage:
  python tools/specification-authority-layer/patch_workbench_qnames.py [--dry-run]
"""
import json
import sys
import argparse
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
CACHE_DIR = REPO / ".local" / "spec-cache"


def patch_workbench_qnames(dry_run: bool = False) -> dict:
    patched = 0
    skipped_already_set = 0
    skipped_no_id = 0
    files_touched = 0
    errors = 0

    for fpath in sorted(CACHE_DIR.rglob("*/workbench/verified-facts-review.json")):
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            d = json.loads(content)
            changed = False
            for fact in d.get("facts", []):
                if fact.get("qname") is not None:
                    skipped_already_set += 1
                    continue
                cid = fact.get("claim_id") or fact.get("fact_id") or fact.get("id")
                if not cid:
                    skipped_no_id += 1
                    continue
                fact["qname"] = cid
                patched += 1
                changed = True

            if changed:
                files_touched += 1
                if not dry_run:
                    fpath.write_text(
                        json.dumps(d, indent=2, ensure_ascii=False),
                        encoding="utf-8"
                    )
        except Exception as e:
            print(f"ERROR {fpath}: {e}", file=sys.stderr)
            errors += 1

    return {
        "patched": patched,
        "skipped_already_set": skipped_already_set,
        "skipped_no_id": skipped_no_id,
        "files_touched": files_touched,
        "errors": errors,
        "dry_run": dry_run,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch workbench fact qname=None fields")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    args = parser.parse_args()

    result = patch_workbench_qnames(dry_run=args.dry_run)
    prefix = "DRY-RUN: " if args.dry_run else ""
    print(f"{prefix}patched={result['patched']}, skipped_already_set={result['skipped_already_set']}, "
          f"skipped_no_id={result['skipped_no_id']}, files_touched={result['files_touched']}, "
          f"errors={result['errors']}")
    sys.exit(1 if result["errors"] > 0 else 0)
