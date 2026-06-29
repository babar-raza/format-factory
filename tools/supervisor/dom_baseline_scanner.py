"""DOM Baseline Scanner — auto-generates DOM baseline inventories.

Scans src/python/{format}/ using AST to find spec classes, iterators,
factory methods, mutation methods, and serialization methods.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"
BASELINES_DIR = REPO_ROOT / "reports" / "dual-lane-deepening" / "dom-baselines"

FULL_FORMATS = ["fods", "fodt", "ods", "odt", "abw", "fodg", "fodp", "gnumeric"]

# Reuse the scanner from dom_contract_checker
sys.path.insert(0, str(Path(__file__).parent))
from dom_contract_checker import _scan_format_source


def scan_format(format_name: str) -> dict:
    """Scan a format and return DOM baseline data."""
    scan = _scan_format_source(format_name)
    if "error" in scan:
        return scan

    return {
        "format": format_name,
        "node_types": [c["class"] for c in scan["classes_with_spec_qname"]],
        "qname_count": len(scan["classes_with_spec_qname"]),
        "factory_methods": scan["factory_methods"],
        "child_accessors": scan["child_accessors"],
        "traversal_methods": scan["traversal_apis"],
        "navigation_methods": scan["navigation_methods"],
        "mutation_methods": scan["mutation_methods"],
        "serialization_methods": scan["serialization_methods"],
        "iterator_files": scan["iterator_files"],
        "behavioral_method_count": len(scan["behavioral_methods"]),
        "hierarchy_depth": _estimate_hierarchy_depth(scan),
        "roundtrip_capability": len(scan["mutation_methods"]) > 0 and len(scan["serialization_methods"]) > 0,
        "spec_qname_coverage": {c["class"]: c["file"] for c in scan["classes_with_spec_qname"]},
    }


def _estimate_hierarchy_depth(scan: dict) -> int:
    """Estimate DOM hierarchy depth from class count and accessor patterns."""
    qcount = len(scan["classes_with_spec_qname"])
    if qcount == 0:
        return 0
    if qcount == 1:
        return 1
    if len(scan["child_accessors"]) > 0:
        return min(qcount, 4)  # Cap at 4 for estimation
    return 1


def generate_baseline(format_name: str, output_path: Path | None = None) -> Path | None:
    """Generate a baseline YAML file for a format."""
    baseline = scan_format(format_name)
    if "error" in baseline:
        print(f"Error scanning {format_name}: {baseline['error']}", file=sys.stderr)
        return None

    if output_path is None:
        BASELINES_DIR.mkdir(parents=True, exist_ok=True)
        output_path = BASELINES_DIR / f"{format_name}.yaml"

    output_path.write_text(yaml.dump(baseline, default_flow_style=False, sort_keys=False), encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="DOM Baseline Scanner")
    parser.add_argument("--format", help="Format name (e.g., fods)")
    parser.add_argument("--output", help="Output path for YAML")
    parser.add_argument("--all-full", action="store_true", help="Generate baselines for all 8 FULL formats")
    args = parser.parse_args()

    if args.all_full:
        BASELINES_DIR.mkdir(parents=True, exist_ok=True)
        for fmt in FULL_FORMATS:
            path = generate_baseline(fmt)
            if path:
                print(f"Generated: {path}")
        return 0

    if not args.format:
        parser.error("Either --format or --all-full is required")

    output = Path(args.output) if args.output else None
    path = generate_baseline(args.format, output)
    if path:
        print(json.dumps(yaml.safe_load(path.read_text(encoding="utf-8")), indent=2, default=str))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
