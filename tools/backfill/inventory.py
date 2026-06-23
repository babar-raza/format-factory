"""Backfill inventory — scan format packages for classes needing canonical renaming.

TC-MACH-BACK-001: READ-ONLY tool. Scans src/python/{format}/ for production classes,
compares against QName registry entries, and outputs a backfill plan.

Usage:
    python tools/backfill/inventory.py --format fods
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def scan_format(format_name: str, repo_root: Path | None = None) -> dict:
    """Scan a format package for production classes and compare to QName registry."""
    root = repo_root or REPO_ROOT
    fmt_dir = root / "src" / "python" / format_name
    registry_path = root / "shared" / "qname-registry" / f"{format_name}.yaml"

    if not fmt_dir.exists():
        return {"error": f"Format directory not found: {fmt_dir}", "classes": []}

    # Load QName registry entries
    registry_entries = []
    if registry_path.exists():
        try:
            import yaml
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                registry_entries = data
            elif isinstance(data, dict):
                registry_entries = data.get("entries", [])
            else:
                registry_entries = []
        except Exception:
            pass

    # Build canonical name index from registry
    canonical_index = {}
    for entry in registry_entries:
        qname = entry.get("qname", "")
        canonical = entry.get("canonical_class", "")
        if qname and canonical:
            canonical_index[qname] = {
                "canonical_class": canonical,
                "namespace_uri": entry.get("namespace_uri", ""),
                "spec_fact_ref": entry.get("spec_fact_ref", ""),
                "status": entry.get("status", "seeded"),
            }

    # Scan Python files for class definitions
    classes = []
    for py_file in sorted(fmt_dir.rglob("*.py")):
        rel = py_file.relative_to(root).as_posix()
        parts = rel.split("/")
        if "__pycache__" in parts or "build" in parts:
            continue
        # Skip Compat/ and spec/ directories
        is_compat = "Compat" in parts
        is_spec = "spec" in parts

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                # Check if class has spec_qname attribute
                spec_qname = None
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "spec_qname":
                                if isinstance(item.value, ast.Constant):
                                    spec_qname = item.value.value

                # Match to registry
                registry_match = canonical_index.get(spec_qname) if spec_qname else None

                classes.append({
                    "current_name": node.name,
                    "current_file": rel,
                    "is_compat": is_compat,
                    "is_spec": is_spec,
                    "spec_qname": spec_qname,
                    "canonical_name": registry_match["canonical_class"] if registry_match else None,
                    "migration_required": (
                        registry_match is not None
                        and not is_compat
                        and not is_spec
                        and node.name != registry_match["canonical_class"]
                    ),
                    "registry_status": registry_match["status"] if registry_match else None,
                })

    return {
        "format": format_name,
        "format_dir": str(fmt_dir),
        "registry_path": str(registry_path) if registry_path.exists() else None,
        "registry_entries": len(registry_entries),
        "classes_found": len(classes),
        "classes": classes,
        "migration_needed": sum(1 for c in classes if c["migration_required"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill inventory scanner")
    parser.add_argument("--format", required=True, help="Format name to scan (e.g., fods)")
    parser.add_argument("--output", default=None, help="Output YAML path")
    args = parser.parse_args()

    result = scan_format(args.format)

    if result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Format: {result['format']}")
    print(f"Classes found: {result['classes_found']}")
    print(f"Migration needed: {result['migration_needed']}")

    for cls in result["classes"]:
        if cls["migration_required"]:
            print(f"  {cls['current_name']} -> {cls['canonical_name']} ({cls['current_file']})")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            import yaml
            out.write_text(yaml.dump(result, default_flow_style=False), encoding="utf-8")
        except ImportError:
            out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nPlan written to: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
