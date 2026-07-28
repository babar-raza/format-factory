"""qname_structure_validator.py — Standalone QName structure compliance validator.

Scans src/python/ for classes missing spec_qname attributes and checks namespace
directory alignment. Produces an honest YAML baseline report.

CLI:
  python tools/validators/qname_structure_validator.py src/python/ --format fods
  python tools/validators/qname_structure_validator.py src/python/
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def scan_src_for_classes(src_root: Path, format_filter: str | None = None) -> list[dict]:
    """AST-parse all .py files; extract class names and spec_qname attributes."""
    results = []
    for py_file in sorted(src_root.rglob("*.py")):
        rel = py_file.relative_to(src_root)
        parts = rel.parts
        # Skip build artifacts and duplicate nested packages
        if "build" in parts or "__pycache__" in parts:
            continue
        # Apply format filter
        if format_filter and parts[0].lower() != format_filter.lower():
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            spec_qname = _extract_spec_qname(node)
            results.append({
                "file": str(rel),
                "class_name": node.name,
                "spec_qname": spec_qname,
                "has_spec_qname": spec_qname is not None,
                "in_spec_dir": "spec" in parts,
            })
    return results


def _extract_spec_qname(cls_node: ast.ClassDef) -> str | None:
    """Return spec_qname class attribute value, or None if absent."""
    for stmt in cls_node.body:
        if isinstance(stmt, ast.Assign):
            targets = stmt.targets
            value = stmt.value
        elif isinstance(stmt, ast.AnnAssign):
            targets = [stmt.target]
            value = stmt.value
        else:
            continue
        for target in targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "spec_qname"
                and isinstance(value, ast.Constant)
            ):
                return str(value.value)
    return None


def check_spec_qname(cls: dict) -> bool:
    """Return True if class has spec_qname attribute."""
    return cls["has_spec_qname"]


def check_namespace_dir(cls: dict) -> bool:
    """Return True if class is in a spec/namespace/ subdir (approximate check)."""
    return cls["in_spec_dir"]


def report(src_root: Path, format_filter: str | None = None) -> dict:
    """Aggregate compliance report as a dict (can be serialized to YAML)."""
    classes = scan_src_for_classes(src_root, format_filter)
    spec_only = [c for c in classes if c["in_spec_dir"]]
    compliant = [c for c in spec_only if c["has_spec_qname"]]
    missing = [c for c in spec_only if not c["has_spec_qname"]]
    non_spec = [c for c in classes if not c["in_spec_dir"] and c["has_spec_qname"]]

    if not spec_only:
        status = "NO_SPEC_CLASSES"
    elif missing:
        status = "PARTIALLY_COMPLIANT" if compliant else "NON_COMPLIANT"
    else:
        status = "COMPLIANT"

    return {
        "status": status,
        "total_classes": len(classes),
        "spec_classes": len(spec_only),
        "compliant_spec_classes": len(compliant),
        "missing_spec_qname": len(missing),
        "non_spec_with_spec_qname": len(non_spec),
        "violations": [
            {"file": c["file"], "class": c["class_name"]}
            for c in missing
        ],
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="QName structure compliance validator")
    parser.add_argument("src_root", nargs="?", default="src/python",
                        help="Source root to scan (default: src/python)")
    parser.add_argument("--format", help="Filter to a single format (e.g. fods)")
    args = parser.parse_args()

    src_root = Path(args.src_root)
    if not src_root.is_absolute():
        src_root = _REPO_ROOT / src_root

    result = report(src_root, args.format)

    try:
        import yaml  # type: ignore
        print(yaml.dump(result, default_flow_style=False, sort_keys=True))
    except ImportError:
        import json
        print(json.dumps(result, indent=2))

    return 0 if result["status"] == "COMPLIANT" else 1


if __name__ == "__main__":
    sys.exit(_cli())
