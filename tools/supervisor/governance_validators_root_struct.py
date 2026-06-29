"""V91 (TC-ROOT-005): Root structure architecture governance validator.

Validates repository top-level directories against registry/repository-root-folders.yaml.

Checks:
  1. Registry completeness — every top-level directory on disk is registered
  2. README presence — every RETAIN folder with readme_required has its README
  3. Resurrection detection — DELETED folders must not exist on disk
  4. Format coverage contract — format-scoped folders match coverage baseline

FAIL + blocks_sprint=True for unregistered directories.
WARN for missing READMEs, resurrected deleted dirs, coverage gaps.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def validate_root_structure(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V91: Root structure architecture governance."""
    from governance_validator_utils import _make_result  # noqa: PLC0415

    _r = repo_root or _REPO_ROOT
    registry_path = _r / "registry" / "repository-root-folders.yaml"

    if not registry_path.exists():
        return _make_result(
            "root_structure_validator", "WARN", [],
            "registry/repository-root-folders.yaml not found — skipping",
            blocks_sprint=False,
        )

    import yaml  # noqa: PLC0415
    with open(registry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    folders = data.get("folders", [])
    if not folders:
        return _make_result(
            "root_structure_validator", "WARN", [],
            "Registry has no folder entries", blocks_sprint=False,
        )

    # Build lookup
    by_path: dict[str, dict] = {}
    for entry in folders:
        fp = entry.get("folder_path", "").rstrip("/")
        by_path[fp] = entry

    items: list[dict] = []
    has_fail = False

    # --- Check 1: Every top-level directory on disk is registered ---
    skip_names = {"__pycache__", "node_modules", "dist"}
    for child in sorted(_r.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name in skip_names:
            continue
        key = name
        if key not in by_path:
            items.append({
                "check": "unregistered_directory",
                "path": name,
                "severity": "FAIL",
                "message": f"Top-level directory '{name}' is not in repository-root-folders.yaml",
            })
            has_fail = True

    # --- Check 2: README presence for RETAIN folders ---
    for entry in folders:
        if entry.get("retention") != "RETAIN":
            continue
        if not entry.get("readme_required"):
            continue
        fp = entry["folder_path"].rstrip("/")
        folder = _r / fp
        if not folder.exists():
            continue
        convention = entry.get("readme_convention", "README.md")
        readme = folder / convention
        if not readme.exists():
            items.append({
                "check": "missing_readme",
                "path": f"{fp}/{convention}",
                "severity": "WARN",
                "message": f"RETAIN folder '{fp}' is missing {convention}",
            })

    # --- Check 3: Resurrection detection ---
    for entry in folders:
        if entry.get("retention") != "DELETED":
            continue
        fp = entry["folder_path"].rstrip("/")
        folder = _r / fp
        if folder.exists():
            items.append({
                "check": "resurrected_deleted",
                "path": fp,
                "severity": "WARN",
                "message": f"Deleted folder '{fp}' has reappeared on disk",
            })

    # --- Check 4: Format coverage contract ---
    coverage_path = _r / "reports" / "repository-structure" / "format-folder-coverage.yaml"
    if coverage_path.exists():
        with open(coverage_path, encoding="utf-8") as f:
            coverage = yaml.safe_load(f)
        for folder_entry in coverage.get("folders", []):
            verdict = folder_entry.get("verdict", "")
            if "MAJOR_GAP" in verdict.upper():
                items.append({
                    "check": "format_coverage_gap",
                    "path": folder_entry.get("path", "?"),
                    "severity": "WARN",
                    "message": f"Format coverage gap: {folder_entry.get('path')} verdict={verdict}",
                })

    # Determine result
    if has_fail:
        result = "FAIL"
    elif items:
        result = "WARN"
    else:
        result = "PASS"

    fail_count = sum(1 for i in items if i.get("severity") == "FAIL")
    warn_count = sum(1 for i in items if i.get("severity") == "WARN")
    summary = f"Root structure: {fail_count} FAIL, {warn_count} WARN, {len(by_path)} registered folders"

    return _make_result(
        "root_structure_validator", result, items, summary,
        blocks_sprint=has_fail,
    )


def main() -> int:
    """CLI entry point."""
    import argparse  # noqa: PLC0415
    parser = argparse.ArgumentParser(description="Validate repository root structure")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = validate_root_structure({}, args.repo_root)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Result: {result['result']}")
        print(f"Summary: {result['summary']}")
        if result.get("items"):
            for item in result["items"]:
                print(f"  [{item['severity']}] {item['message']}")

    return 0 if result["result"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
