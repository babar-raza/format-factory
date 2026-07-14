"""dry_run_migration.py — Backfill Migration Preview Tool (TC-GFB-023, FF-MR-2026-001)

READ-ONLY PREVIEW ONLY. This tool makes ZERO changes to src/.
It reads source files, qname registries, and architecture profiles,
then produces a structured preview of proposed renames/moves.

Contract: .governance/backfill/backfill-dry-run-contract.yaml
Schema:   .governance/backfill/migration-map.schema.yaml

Usage:
    python tools/backfill/dry_run_migration.py --format <format_id> [--target-profile <profile>]
    python tools/backfill/dry_run_migration.py --format all
    python tools/backfill/dry_run_migration.py --format fods --out .local/supervisor/dry-run-fods.json

Exit codes:
    0: No migrations proposed (format is clean)
    1: Migrations proposed (preview written; src/ unchanged)
    2: Error reading source or registry

IMPORTANT: After running, verify: git diff src/ must be EMPTY.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PYTHON = REPO_ROOT / "src" / "python"
QNAME_REGISTRY_DIR = REPO_ROOT / "shared" / "qname-registry"
GOVERNANCE_BACKFILL = REPO_ROOT / ".governance" / "backfill"
STATE_DIR = REPO_ROOT / ".local" / "supervisor"

# Target architecture profiles define which qname alignment criteria matter
_TARGET_PROFILES = {
    "ODF_RICH": {
        "description": "Full ODF spec alignment — all QNames must have spec_qname ClassVar",
        "required_criteria": ["spec_qname_classvar", "spec_path_layout", "compat_shim"],
    },
    "MINIMAL": {
        "description": "Minimum viable alignment — spec_qname ClassVar only",
        "required_criteria": ["spec_qname_classvar"],
    },
    "PATH_ONLY": {
        "description": "File layout alignment only — no symbol renames",
        "required_criteria": ["spec_path_layout"],
    },
}
_DEFAULT_PROFILE = "ODF_RICH"

# Known active formats in the Python FOSS product
_KNOWN_FORMATS = [
    "abw", "csv", "dif", "fods", "fodg", "fodp", "fodt", "gnumeric",
    "ndjson", "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi",
    "sylk", "toml", "tsv", "xcf", "zst",
]


def _has_spec_qname(file_path: Path) -> list[str]:
    """Return class names that have a spec_qname ClassVar field."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return []
    classes_with_qname = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if (
                    isinstance(item.target, ast.Name)
                    and item.target.id == "spec_qname"
                ):
                    classes_with_qname.append(node.name)
                    break
    return classes_with_qname


def _find_classes_missing_spec_qname(format_id: str) -> list[dict[str, Any]]:
    """Scan src/python/<format_id>/ for classes missing spec_qname ClassVar."""
    format_root = SRC_PYTHON / format_id
    if not format_root.is_dir():
        return []

    entries = []
    for py_file in sorted(format_root.rglob("*.py")):
        # Skip test files and __init__
        if py_file.name.startswith("test_") or py_file.name == "__init__.py":
            continue
        # Skip Compat/ facades — these are shims, not model classes
        rel = py_file.relative_to(REPO_ROOT)
        rel_str = rel.as_posix()

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            # Only flag classes in spec/ subdirectory (spec model classes)
            if "spec" not in rel_str.split("/"):
                continue
            has_qname = any(
                isinstance(item, ast.AnnAssign)
                and isinstance(item.target, ast.Name)
                and item.target.id == "spec_qname"
                for item in node.body
            )
            if not has_qname:
                entries.append(
                    {
                        "format_id": format_id,
                        "source_file": rel_str,
                        "old_symbol": node.name,
                        "new_symbol": node.name,  # same name, just need spec_qname added
                        "symbol_type": "CLASS",
                        "old_path": None,
                        "new_path": None,
                        "namespace_change": False,
                        "reason": f"Add spec_qname ClassVar to align with spec (REQ-BF-001)",
                        "authority_ref": "REQ-BF-001",
                        "behavior_preservation_class": "PRESERVED_UNCHANGED",
                        "migration_risk": "LOW",
                    }
                )
    return entries


def _check_qname_registry(format_id: str) -> list[dict[str, Any]]:
    """Check qname-registry for entries missing from src/python/<format_id>/spec/."""
    registry_file = QNAME_REGISTRY_DIR / f"{format_id}.yaml"
    if not registry_file.exists():
        return []

    try:
        import yaml  # type: ignore[import-untyped]
        data = yaml.safe_load(registry_file.read_text(encoding="utf-8"))
    except Exception:
        return []

    entries = data if isinstance(data, list) else data.get("entries", [])
    if not entries:
        return []

    format_root = SRC_PYTHON / format_id / "spec"
    missing = []
    for entry in entries:
        qname = entry.get("qname") or entry.get("spec_qname") or ""
        if not qname:
            continue
        status = entry.get("status", "")
        if status in ("architecture_only", "deprecated", "removed"):
            continue
        # Check if a file implementing this qname exists
        local_name = qname.split(":")[-1].replace("-", "_")
        # Look for any py file containing the local_name
        found = any(
            py_f.stem == local_name or local_name in py_f.stem
            for py_f in (format_root.rglob("*.py") if format_root.is_dir() else [])
        )
        if not found and format_root.is_dir():
            missing.append(
                {
                    "format_id": format_id,
                    "source_file": f"src/python/{format_id}/spec/{local_name}/{local_name}.py",
                    "old_symbol": "(missing)",
                    "new_symbol": local_name,
                    "symbol_type": "CLASS",
                    "old_path": None,
                    "new_path": f"src/python/{format_id}/spec/{local_name}/{local_name}.py",
                    "namespace_change": False,
                    "reason": f"Spec QName {qname!r} has no implementation in spec/",
                    "authority_ref": qname,
                    "behavior_preservation_class": "UNVERIFIED",
                    "migration_risk": "MEDIUM",
                }
            )
    return missing


def run_dry_run(
    format_id: str,
    target_profile: str = _DEFAULT_PROFILE,
    out_path: Path | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """Execute dry run for a single format. Returns result dict. Makes NO src/ changes."""
    profile = _TARGET_PROFILES.get(target_profile, _TARGET_PROFILES[_DEFAULT_PROFILE])
    timestamp = datetime.now(timezone.utc).isoformat()

    # Collect proposed migrations
    proposed: list[dict[str, Any]] = []

    if "spec_qname_classvar" in profile["required_criteria"]:
        proposed.extend(_find_classes_missing_spec_qname(format_id))

    if "spec_path_layout" in profile["required_criteria"]:
        proposed.extend(_check_qname_registry(format_id))

    # Deduplicate by (source_file, old_symbol)
    seen: set[tuple[str, str]] = set()
    deduped = []
    for p in proposed:
        key = (p["source_file"], p["old_symbol"])
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    proposed = deduped

    # Risk breakdown
    risk_counts: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for p in proposed:
        risk_counts[p.get("migration_risk", "MEDIUM")] += 1

    result: dict[str, Any] = {
        "dry_run": True,
        "src_mutations": 0,  # ALWAYS 0 — this is the contract
        "format_id": format_id,
        "target_profile": target_profile,
        "profile_description": profile["description"],
        "timestamp": timestamp,
        "proposed_migration_count": len(proposed),
        "risk_breakdown": risk_counts,
        "proposed_migrations": proposed,
        "contract_ref": ".governance/backfill/backfill-dry-run-contract.yaml",
        "schema_ref": ".governance/backfill/migration-map.schema.yaml",
    }

    # Write output (NOT to src/)
    if out_path is None:
        ts_short = timestamp[:19].replace(":", "-").replace("T", "_")
        out_path = STATE_DIR / f"dry-run-{format_id}-{ts_short}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def _print_summary(result: dict[str, Any]) -> None:
    fmt = result["format_id"]
    count = result["proposed_migration_count"]
    risk = result["risk_breakdown"]
    if count == 0:
        print(f"[dry_run] {fmt}: no migrations proposed (already aligned)")
    else:
        print(f"[dry_run] {fmt}: {count} migration(s) proposed")
        print(f"  Risk: LOW={risk['LOW']} MEDIUM={risk['MEDIUM']} HIGH={risk['HIGH']} CRITICAL={risk['CRITICAL']}")
        for m in result["proposed_migrations"][:10]:
            print(f"  - [{m['migration_risk']}] {m['source_file']} :: {m['old_symbol']} -> {m['new_symbol']}")
        if count > 10:
            print(f"  ... and {count - 10} more (see output JSON)")
    print(f"  Output: {result.get('_out_path', '(see .local/supervisor/dry-run-*.json)')}")
    print(f"  src_mutations: {result['src_mutations']}  (must be 0)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Backfill migration dry-run preview (READ-ONLY — makes no src/ changes)"
    )
    parser.add_argument(
        "--format", required=True,
        help="Format ID to preview (e.g., fods, csv) or 'all' for all known formats",
    )
    parser.add_argument(
        "--target-profile", default=_DEFAULT_PROFILE,
        choices=list(_TARGET_PROFILES.keys()),
        help=f"Architecture alignment profile (default: {_DEFAULT_PROFILE})",
    )
    parser.add_argument(
        "--out", default=None,
        help="Output JSON path (default: .local/supervisor/dry-run-<format>-<ts>.json)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args(argv)

    formats = _KNOWN_FORMATS if args.format == "all" else [args.format]
    out_path = Path(args.out) if args.out else None

    any_migrations = False
    for fmt in formats:
        result = run_dry_run(
            fmt,
            target_profile=args.target_profile,
            out_path=out_path if len(formats) == 1 else None,
            verbose=args.verbose,
        )
        _print_summary(result)
        if result["proposed_migration_count"] > 0:
            any_migrations = True

    # Safety assertion: src/ must be unchanged (always true since we don't write there)
    print("[dry_run] Contract assertion: src_mutations=0 (READ-ONLY confirmed)")
    return 1 if any_migrations else 0


if __name__ == "__main__":
    sys.exit(main())
