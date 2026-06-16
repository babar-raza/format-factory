"""
extractor_to_workbench_adapter.py — Schema adapter: requirement_extractor output → workbench YAML.

Reads:  .local/spec-artifacts/{source_id}-requirements.json
Writes: .local/spec-cache/{format_id}/{version}/workbench/verified-facts-review.yaml

Field mapping:
  req_id / custom_id → claim_id   (FACT-{FORMAT_UPPER}-EX-{NNN:04d})
  text_fragment      → claim
  section_id         → provenance.section_id
  source_id          → provenance.spec_id
  format_id          → provenance.format_id
  heading            → provenance.section_heading
  keyword            → provenance.extra.keyword
  extracted_at       → provenance.extracted_at
  (new)              → verification_status: pending_verification
  (new)              → extraction_method: automated_extraction
  (new)              → validated_by: null
  (new)              → validated_at: null

Usage:
  python extractor_to_workbench_adapter.py --format fods --source-id fods-1.3-normalized
  python extractor_to_workbench_adapter.py --format fods --source-id fods-1.3-normalized --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


_REPO = Path(__file__).resolve().parents[2]
_ARTIFACTS_DIR = _REPO / ".local" / "spec-artifacts"
_SPEC_CACHE = _REPO / ".local" / "spec-cache"


def _find_workbench_yaml(format_id: str) -> Optional[Path]:
    """Find verified-facts-review.yaml for a format under .local/spec-cache/."""
    matches = list(_SPEC_CACHE.glob(f"{format_id}/*/workbench/verified-facts-review.yaml"))
    if not matches:
        return None
    return matches[0]


def _load_workbench(path: Path) -> Dict[str, Any]:
    """Load workbench YAML. Returns {facts: [...]}."""
    if yaml is None:
        raise ImportError("PyYAML is required: pip install pyyaml")
    if not path.exists():
        return {"facts": []}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "facts" not in data:
        data["facts"] = []
    return data


def _save_workbench(path: Path, data: Dict[str, Any]) -> None:
    if yaml is None:
        raise ImportError("PyYAML is required: pip install pyyaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _existing_claim_ids(workbench_data: Dict[str, Any]) -> set:
    return {f.get("claim_id", "") for f in workbench_data.get("facts", [])}


def _next_ex_number(existing_ids: set, format_id: str) -> int:
    """Find next available EX number for claim IDs like FACT-FODS-EX-0001."""
    prefix = f"FACT-{format_id.upper()}-EX-"
    used = set()
    for cid in existing_ids:
        if cid.startswith(prefix):
            try:
                used.add(int(cid[len(prefix):]))
            except ValueError:
                pass
    n = 1
    while n in used:
        n += 1
    return n


def adapt_requirements(
    format_id: str,
    source_id: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Read extractor output for source_id and append new candidate facts to the workbench YAML.

    Returns a summary dict: {appended, skipped_duplicate, source_file, workbench_file}.
    """
    # Load extractor output
    req_file = _ARTIFACTS_DIR / f"{source_id}-requirements.json"
    if not req_file.exists():
        return {
            "status": "no_extractor_output",
            "message": f"No extractor output found at {req_file}",
            "appended": 0,
            "skipped_duplicate": 0,
        }

    with open(req_file, encoding="utf-8") as f:
        req_data = json.load(f)

    requirements = req_data.get("requirements", [])
    if not requirements:
        return {
            "status": "empty_requirements",
            "message": f"No requirements in {req_file}",
            "appended": 0,
            "skipped_duplicate": 0,
        }

    # Find workbench
    workbench_path = _find_workbench_yaml(format_id)
    if workbench_path is None:
        # Create a new one
        version_dir = _SPEC_CACHE / format_id / "unknown-version" / "workbench"
        workbench_path = version_dir / "verified-facts-review.yaml"
        print(f"  [WARN] No existing workbench found; will create at {workbench_path}")

    workbench_data = _load_workbench(workbench_path)
    existing_ids = _existing_claim_ids(workbench_data)

    appended = 0
    skipped = 0
    next_num = _next_ex_number(existing_ids, format_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    new_facts = []
    for req in requirements:
        req_id = req.get("req_id", "")
        text_fragment = req.get("text_fragment", "").strip()
        section_id = req.get("section_id", "")
        heading = req.get("heading", "")
        keyword = req.get("keyword", "")
        extracted_at = req.get("extracted_at", now_iso)

        if not text_fragment:
            skipped += 1
            continue

        # Generate workbench claim_id
        claim_id = f"FACT-{format_id.upper()}-EX-{next_num:04d}"
        if claim_id in existing_ids:
            skipped += 1
            continue

        fact = {
            "claim_id": claim_id,
            "claim": text_fragment,
            "verification_status": "pending_verification",
            "extraction_method": "automated_extraction",
            "validated_by": None,
            "validated_at": None,
            "provenance": {
                "section_id": section_id,
                "spec_id": source_id,
                "format_id": format_id,
                "section_heading": heading,
                "extraction_method": "automated_extraction",
                "extracted_at": extracted_at,
                "extra": {
                    "keyword": keyword,
                    "original_req_id": req_id,
                },
            },
        }

        if dry_run:
            print(f"  [DRY-RUN] Would append: {claim_id} — {text_fragment[:80]}...")
        else:
            new_facts.append(fact)
            existing_ids.add(claim_id)

        appended += 1
        next_num += 1

    if not dry_run and new_facts:
        workbench_data["facts"].extend(new_facts)
        _save_workbench(workbench_path, workbench_data)
        print(f"  [OK] Appended {len(new_facts)} new facts to {workbench_path}")

    return {
        "status": "ok",
        "source_file": str(req_file),
        "workbench_file": str(workbench_path),
        "appended": appended,
        "skipped_duplicate": skipped,
        "dry_run": dry_run,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adapt requirement_extractor.py output into workbench YAML format."
    )
    parser.add_argument("--format", required=True, dest="format_id", help="Format ID (e.g. fods)")
    parser.add_argument("--source-id", required=True, help="Source ID used in extractor output (e.g. fods-1.3-normalized)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    print(f"[adapter] format={args.format_id} source_id={args.source_id} dry_run={args.dry_run}")
    result = adapt_requirements(
        format_id=args.format_id,
        source_id=args.source_id,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))

    if result.get("status") not in ("ok", "empty_requirements", "no_extractor_output"):
        sys.exit(1)


if __name__ == "__main__":
    main()
