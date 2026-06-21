"""
qname_src_compliance_reporter.py — TC-QNAME-VALIDATOR-001

Checks whether expected canonical class files exist in src/ per
reports/specification-authority-layer-mwp/qname-ontology/canonical-class-inventory.yaml.

Emits a JSON compliance report with per-class status:
  - implemented: a real (non-stub) canonical class file exists
  - stub_only: a Spec/ file exists but is architecture_only
  - facade_only: only the legacy format-prefixed facade exists
  - missing: no src representation found

Usage:
  python tools/specification-authority-layer/qname_src_compliance_reporter.py [--output PATH]
"""

import json
import sys
from pathlib import Path

_REPO = Path(__file__).parents[2]

INVENTORY_PATH = (
    _REPO
    / "reports"
    / "specification-authority-layer-mwp"
    / "qname-ontology"
    / "canonical-class-inventory.yaml"
)

_ARCHITECTURE_ONLY_MARKERS = [
    "architecture_only",
    "// architecture_only",
    "// Architecture only",
    "ArchitectureOnly",
]


def _load_inventory():
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        # Fallback: minimal YAML parser for our known structure
        return _load_inventory_fallback()
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_inventory_fallback():
    """Parse canonical-class-inventory.yaml without PyYAML."""
    classes = []
    current = {}
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip()
            if stripped.startswith("  - canonical:"):
                if current:
                    classes.append(current)
                current = {"canonical": stripped.split(":", 1)[1].strip().strip('"')}
            elif stripped.startswith("    qname:"):
                current["qname"] = stripped.split(":", 1)[1].strip().strip('"')
            elif stripped.startswith("    status:"):
                current["status"] = stripped.split(":", 1)[1].strip().strip('"')
            elif stripped.startswith("    facade_path:"):
                current["facade_path"] = stripped.split(":", 1)[1].strip().strip('"')
    if current:
        classes.append(current)
    return {"classes": classes}


def _canonical_to_dotnet_paths(canonical: str):
    """
    Derive candidate .NET Spec/ file paths for a canonical name like 'Table.TableCell'.
    Checks all format-specific Spec/ directories.
    """
    namespace, class_name = canonical.rsplit(".", 1)
    # Check all Spec/ trees under src/net/*/
    paths = []
    net_root = _REPO / "src" / "net"
    if net_root.exists():
        for fmt_dir in net_root.iterdir():
            if fmt_dir.is_dir():
                candidate = fmt_dir / "Spec" / namespace / f"{class_name}.cs"
                paths.append(candidate)
    return paths


def _is_architecture_only(path: Path) -> bool:
    """Return True if the file is a stub/architecture-only class."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        for marker in _ARCHITECTURE_ONLY_MARKERS:
            if marker in content:
                return True
        # Heuristic: if file has no method body (only static string constants)
        non_comment_lines = [
            ln.strip()
            for ln in content.splitlines()
            if ln.strip() and not ln.strip().startswith("//")
        ]
        # Files with < 15 non-comment lines are almost certainly stubs
        if len(non_comment_lines) < 15:
            return True
    except Exception:
        pass
    return False


def _classify_class(entry: dict) -> dict:
    """Classify a single canonical class entry."""
    canonical = entry.get("canonical", "")
    inventory_status = entry.get("status", "not_implemented")
    facade_path_str = entry.get("facade_path")

    dotnet_paths = _canonical_to_dotnet_paths(canonical)
    found_dotnet = [p for p in dotnet_paths if p.exists()]

    facade_exists = False
    if facade_path_str:
        facade_full = _REPO / facade_path_str
        facade_exists = facade_full.exists()

    # Classify
    if found_dotnet:
        if any(not _is_architecture_only(p) for p in found_dotnet):
            status = "implemented"
        else:
            status = "stub_only"
    elif facade_exists:
        status = "facade_only"
    else:
        status = "missing"

    result = {
        "canonical": canonical,
        "qname": entry.get("qname", ""),
        "inventory_status": inventory_status,
        "compliance_status": status,
        "dotnet_spec_files_found": [str(p.relative_to(_REPO).as_posix()) for p in found_dotnet],
        "facade_path": facade_path_str,
        "facade_exists": facade_exists,
    }
    return result


def run_compliance_check() -> dict:
    """Run compliance check and return report dict."""
    data = _load_inventory()
    classes = data.get("classes", [])

    results = []
    counts = {"implemented": 0, "stub_only": 0, "facade_only": 0, "missing": 0}

    for entry in classes:
        classification = _classify_class(entry)
        results.append(classification)
        counts[classification["compliance_status"]] += 1

    report = {
        "schema_version": "1.0",
        "inventory_path": str(INVENTORY_PATH.relative_to(_REPO).as_posix()),
        "total_classes": len(results),
        "summary": counts,
        "classes": results,
    }
    return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="QName src compliance reporter")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    report = run_compliance_check()

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report written to: {out_path}")
    else:
        print(json.dumps(report, indent=2))

    total = report["total_classes"]
    s = report["summary"]
    print(
        f"\nSummary: {total} classes — "
        f"implemented={s['implemented']}, stub_only={s['stub_only']}, "
        f"facade_only={s['facade_only']}, missing={s['missing']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
