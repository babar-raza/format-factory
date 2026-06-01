"""
inspect_declared_evidence.py — Declared Evidence Inspector
Inspects a worker-declared evidence directory by walking declared paths,
extracting facts, and assessing per-item evidence presence.

Exit codes:
  0 — inspection complete
  1 — declaration invalid
  9 — unexpected error
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def inspect_item(item: dict, repo_root: Path) -> dict:
    """Inspect a single planned work item for evidence presence."""
    item_id = item.get("item_id", "unknown")
    status = item.get("status", "not_started")
    evidence_paths = item.get("evidence_paths", [])
    tests = item.get("tests_supporting", [])

    found_paths = []
    missing_paths = []
    for p in evidence_paths:
        full = repo_root / p
        if full.exists():
            found_paths.append(p)
        else:
            missing_paths.append(p)

    has_evidence = len(found_paths) > 0
    has_tests = len(tests) > 0

    return {
        "item_id": item_id,
        "declared_status": status,
        "evidence_paths_declared": evidence_paths,
        "evidence_paths_found": found_paths,
        "evidence_paths_missing": missing_paths,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "tests_declared": tests,
    }


def inspect_declaration(decl: dict, repo_root: Path) -> dict:
    """Full inspection of a declaration."""
    evidence_root = decl.get("evidence_root", "")
    root_path = repo_root / evidence_root if evidence_root else None

    inspection = {
        "run_id": decl.get("run_id", "unknown"),
        "sprint_id": decl.get("sprint_id", "unknown"),
        "evidence_root": evidence_root,
        "evidence_root_exists": root_path.is_dir() if root_path else False,
        "timestamp": datetime.now().isoformat(),
        "item_inspections": [],
        "artifact_inspections": [],
        "test_results": decl.get("test_results", {}),
        "tests_run": decl.get("tests_run", 0),
        "zip_declared": bool(decl.get("zip_export_path")),
        "zip_path": decl.get("zip_export_path"),
    }

    # Inspect each work item
    for item in decl.get("planned_work_items", []):
        inspection["item_inspections"].append(inspect_item(item, repo_root))

    # Inspect declared artifacts
    for artifact in decl.get("evidence_artifacts", []):
        apath = artifact.get("path", "")
        full = repo_root / apath if apath else None
        inspection["artifact_inspections"].append({
            "path": apath,
            "exists": full.exists() if full else False,
            "type": artifact.get("type", "unknown"),
            "related_work_items": artifact.get("related_work_items", []),
        })

    return inspection


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect declared evidence directory")
    parser.add_argument("--declaration", type=Path, required=True, help="Path to evidence-declaration.yaml")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, help="Write inspection JSON to file")
    args = parser.parse_args()

    if not args.declaration.exists():
        print(f"ERROR: Declaration not found: {args.declaration}", file=sys.stderr)
        return 1

    decl = load_yaml(args.declaration)
    inspection = inspect_declaration(decl, args.repo_root)

    output_json = json.dumps(inspection, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json, encoding="utf-8")
        print(f"INSPECTION_COMPLETE: {args.output}")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
