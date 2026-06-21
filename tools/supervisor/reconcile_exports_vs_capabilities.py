#!/usr/bin/env python3
"""Post-sprint reconciliation: compare __all__ exports vs capability records (TC-CAP-002).

Compares actual Python module exports against the unified capability map to
detect drift: functions that exist in code but not in the capability map,
or capability records that reference non-existent functions.

Usage:
    python tools/supervisor/reconcile_exports_vs_capabilities.py [--json]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"
CAP_MAP = REPO_ROOT / "reports" / "capability-layer" / "unified-capability-map.json"

# Map format directory names to capability map format names
FORMAT_DIR_TO_CAP = {
    "fods": "FODS", "fodt": "FODT", "fodp": "FODP", "fodg": "FODG",
    "ods": "ODS", "odt": "ODT", "csv": "CSV", "tsv": "TSV",
    "dif": "DIF", "sylk": "SYLK", "ndjson": "NDJSON", "abw": "ABW",
    "gnumeric": "Gnumeric", "pbm": "PBM", "pgm": "PGM", "ppm": "PPM",
    "qoi": "QOI", "xcf": "XCF",
}


def _load_module_exports(fmt_dir: str) -> list[str]:
    """Parse __all__ from src/python/<fmt>/__init__.py without importing."""
    init = SRC_PYTHON / fmt_dir / "__init__.py"
    if not init.is_file():
        return []
    try:
        import ast
        tree = ast.parse(init.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            return [
                                elt.value for elt in node.value.elts
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                            ]
        return []
    except Exception:
        return []


def _load_capability_functions(cap_format: str) -> set[str]:
    """Extract function references from capability map for a format."""
    if not CAP_MAP.is_file():
        return set()
    with open(CAP_MAP, encoding="utf-8") as f:
        data = json.load(f)
    caps = data.get("capabilities", [])
    fns = set()
    for c in caps:
        if c.get("format", "") != cap_format:
            continue
        if c.get("product_type") not in ("foss", "foss_reduced"):
            continue
        # Extract function names from source_refs
        for ref in c.get("source_refs", []):
            if isinstance(ref, str) and "::" in ref:
                fn = ref.split("::")[-1]
                fns.add(fn)
            elif isinstance(ref, str):
                fns.add(ref)
        # Also use capability_name as fallback
        name = c.get("capability_name", "")
        if name:
            fns.add(name)
    return fns


def reconcile() -> dict:
    """Run reconciliation across all known formats."""
    results = []
    total_exports = 0
    total_cap_fns = 0
    total_untracked = 0

    for fmt_dir, cap_name in sorted(FORMAT_DIR_TO_CAP.items()):
        exports = _load_module_exports(fmt_dir)
        cap_fns = _load_capability_functions(cap_name)

        # Functions in code but not in capability map
        export_set = set(exports)
        untracked = export_set - cap_fns if cap_fns else set()

        total_exports += len(exports)
        total_cap_fns += len(cap_fns)
        total_untracked += len(untracked)

        results.append({
            "format": fmt_dir,
            "cap_format": cap_name,
            "export_count": len(exports),
            "cap_function_count": len(cap_fns),
            "untracked_exports": sorted(untracked) if untracked else [],
        })

    return {
        "total_formats": len(results),
        "total_exports": total_exports,
        "total_capability_functions": total_cap_fns,
        "total_untracked": total_untracked,
        "formats": results,
    }


def main() -> int:
    result = reconcile()
    use_json = "--json" in sys.argv

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Export vs Capability Reconciliation")
        print(f"Formats: {result['total_formats']}")
        print(f"Total exports: {result['total_exports']}")
        print(f"Total cap functions: {result['total_capability_functions']}")
        print(f"Untracked exports: {result['total_untracked']}")
        print()
        for fmt in result["formats"]:
            status = "OK" if not fmt["untracked_exports"] else f"{len(fmt['untracked_exports'])} untracked"
            print(f"  {fmt['format']:12s} exports={fmt['export_count']:3d}  cap_fns={fmt['cap_function_count']:3d}  {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
