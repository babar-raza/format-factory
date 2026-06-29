"""Generate per-format product inventory from repository evidence.

Reads format registry, oracle results, certification matrix, and source
directories to produce a comprehensive product table.

Usage:
    python tools/docs/generate_product_inventory.py
    python tools/docs/generate_product_inventory.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FAMILY_DISPLAY = {
    "cells": "Spreadsheets",
    "words": "Documents",
    "presentation": "Presentations",
    "drawing": "Drawings",
    "imaging": "Images",
    "data": "Data Formats",
    "archive": "Archive/Compression",
    "odf": "Shared Infrastructure",
}

FAMILY_ORDER = ["cells", "words", "presentation", "drawing", "imaging", "data", "archive", "odf"]


def _read_yaml(path: Path):
    if not path.exists():
        return None
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _count_dir(directory: Path, pattern: str, exclude: tuple[str, ...] = ()) -> int:
    if not directory.is_dir():
        return 0
    count = 0
    for f in directory.rglob(pattern):
        if any(ex in f.parts for ex in exclude):
            continue
        count += 1
    return count


def _gate_summary(gates: dict) -> str:
    """Summarize gate progress as 'G1-G9 PASS' style string."""
    if not gates:
        return "N/A"
    passed = []
    for i in range(1, 12):
        gkey = f"gate_{i}"
        g = gates.get(gkey)
        if isinstance(g, dict) and g.get("status") in ("passed", "approved", "commercial_readiness_in_progress"):
            passed.append(i)
        elif isinstance(g, str) and g in ("passed", "approved"):
            passed.append(i)
    if not passed:
        return "N/A"
    return f"G1-G{max(passed)}"


def collect_product_inventory(repo_root: Path = REPO_ROOT) -> list[dict]:
    """Collect per-format product inventory."""
    reg = _read_yaml(repo_root / "registry" / "format-registry.yaml")
    if not reg or not isinstance(reg, dict):
        return []

    cert_matrix = _read_json(
        repo_root / "reports" / "certification" / "portfolio-certification-matrix.json"
    )
    cert_by_fmt: dict[str, dict] = {}
    if cert_matrix and isinstance(cert_matrix, dict):
        for entry in cert_matrix.get("formats", []):
            cert_by_fmt[entry["format_id"]] = entry

    inventory = []
    for fmt in reg.get("formats", []):
        fid = fmt.get("format_id", "")
        if fid == "odf-shared":
            continue
        family = fmt.get("family", "unknown")

        # Oracle
        oracle = _read_json(
            repo_root / "oracle" / "formats" / fid / "reports" / "oracle-run-summary.json"
        )
        oracle_str = oracle.get("pass_rate", "N/A") if oracle else "N/A"
        oracle_verdict = oracle.get("verdict", "N/A") if oracle else "N/A"

        # Source counts
        py_count = _count_dir(
            repo_root / "src" / "python" / fid, "*.py",
            exclude=("__pycache__", "build", "egg-info"),
        )
        net_count = _count_dir(
            repo_root / "src" / "net" / fid, "*.cs",
            exclude=("obj", "bin"),
        )

        # Test counts
        py_tests = _count_dir(
            repo_root / "tests" / "python" / fid, "*.py",
            exclude=("__pycache__",),
        )
        net_tests = _count_dir(
            repo_root / "tests" / "net" / fid, "*.cs",
            exclude=("obj", "bin"),
        )

        # Certification
        cert_entry = cert_by_fmt.get(fid, {})
        cert_verdict = cert_entry.get("overall_verdict", "N/A")
        cert_dims = cert_entry.get("dimensions", {})
        api_count = cert_dims.get("api_contract", {}).get("python_apis", 0)
        dotnet_apis = cert_dims.get("api_contract", {}).get("dotnet_apis", 0)

        # Gates
        gates = fmt.get("gates", {}) or {}
        gate_str = _gate_summary(gates)
        g11_status = (gates.get("gate_11") or {}).get("status", "N/A")

        inventory.append({
            "format_id": fid,
            "display_name": fmt.get("display_name", fid.upper()),
            "family": family,
            "family_display": FAMILY_DISPLAY.get(family, family.title()),
            "extensions": fmt.get("extensions", []),
            "has_python": py_count > 0,
            "has_dotnet": net_count > 0,
            "python_source_files": py_count,
            "dotnet_source_files": net_count,
            "python_tests": py_tests,
            "dotnet_tests": net_tests,
            "python_apis": api_count,
            "dotnet_apis": dotnet_apis,
            "oracle": oracle_str,
            "oracle_verdict": oracle_verdict,
            "certification": cert_verdict,
            "gates": gate_str,
            "gate_11": g11_status,
        })

    # Sort by family order, then alphabetically within family
    def sort_key(item: dict) -> tuple:
        fam = item["family"]
        idx = FAMILY_ORDER.index(fam) if fam in FAMILY_ORDER else 99
        return (idx, item["format_id"])

    inventory.sort(key=sort_key)
    return inventory


def render_product_inventory_markdown(inventory: list[dict]) -> str:
    """Render product inventory as markdown."""
    lines = [
        "## Product Inventory",
        "",
        f"**{sum(1 for i in inventory if i['has_python'])} Python packages** | "
        f"**{sum(1 for i in inventory if i['has_dotnet'])} .NET projects** | "
        f"**{len(inventory)} formats tracked**",
        "",
        "| Format | Family | Python | .NET | Oracle | Certified | Gates |",
        "|---|---|---|---|---|---|---|",
    ]

    current_family = None
    for item in inventory:
        if item["family"] != current_family:
            current_family = item["family"]

        py_str = f"{item['python_source_files']} files" if item["has_python"] else "-"
        net_str = f"{item['dotnet_source_files']} files" if item["has_dotnet"] else "-"

        lines.append(
            f"| {item['display_name']} | {item['family_display']} "
            f"| {py_str} | {net_str} "
            f"| {item['oracle']} | {item['certification']} | {item['gates']} |"
        )

    # Per-family summary
    lines.extend(["", "### Product Families", ""])
    families: dict[str, list] = {}
    for item in inventory:
        families.setdefault(item["family"], []).append(item)

    for fam in FAMILY_ORDER:
        if fam not in families or fam == "odf":
            continue
        items = families[fam]
        display = FAMILY_DISPLAY.get(fam, fam.title())
        active = [i for i in items if i["has_python"]]
        lines.append(
            f"- **{display}** ({len(items)} formats, "
            f"{len(active)} with Python source): "
            f"{', '.join(i['format_id'].upper() for i in items)}"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate product inventory")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    inventory = collect_product_inventory(args.repo_root)
    if args.json:
        print(json.dumps(inventory, indent=2))
    else:
        print(render_product_inventory_markdown(inventory))
    return 0


if __name__ == "__main__":
    sys.exit(main())
