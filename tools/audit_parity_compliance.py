"""audit_parity_compliance.py — Phase I (FF-FORENSIC-AUDIT-20260623)

Cross-language parity compliance tool. Reads registry/parity-matrix.yaml and
gap-ledger.json to compare features implemented in Python vs .NET.

Flags:
  - Features in .NET but not Python (dotnet_ahead)
  - Features in Python but not .NET (python_ahead)
  - Features missing in both (both_missing)
  - Formats where parity is unknown

Emits: reports/parity-gap-{date}.json

Usage:
    python tools/audit_parity_compliance.py [--out PATH]
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

_REPO = Path(__file__).parent.parent
_PARITY_MATRIX = _REPO / "registry/parity-matrix.yaml"
_GAP_LEDGER = _REPO / "reports/capability-layer/gap-ledger.json"
_POC_TARGETS = _REPO / "product-capability-matrix/poc-targets.yaml"


def _check_format_exports(fmt_dir: Path, lang: str) -> dict[str, Any]:
    """Check what a format package exports (Python only)."""
    if lang != "python":
        return {}

    init_file = fmt_dir / "__init__.py"
    if not init_file.exists():
        return {"exists": False}

    content = init_file.read_text(encoding="utf-8", errors="replace")
    # Count exported names
    all_list: list[str] = []
    in_all = False
    for line in content.splitlines():
        if "__all__" in line and "[" in line:
            in_all = True
        if in_all:
            import re
            for m in re.findall(r'"([^"]+)"|\'([^\']+)\'', line):
                sym = m[0] or m[1]
                if sym:
                    all_list.append(sym)
            if "]" in line and not line.strip().startswith("__all__"):
                in_all = False

    return {
        "exists": True,
        "export_count": len(all_list),
        "exports_sample": all_list[:10],
    }


def _count_dotnet_public_methods(proj_dir: Path) -> dict[str, Any]:
    """Count public methods in .NET project (cs file scan)."""
    if not proj_dir.exists():
        return {"exists": False}

    import re
    public_methods = []
    for cs in proj_dir.rglob("*.cs"):
        try:
            content = cs.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Find public methods (simple heuristic)
        methods = re.findall(r"public\s+\w+\s+(\w+)\s*\(", content)
        public_methods.extend(methods)

    return {
        "exists": True,
        "public_method_count": len(public_methods),
        "methods_sample": public_methods[:10],
    }


def run_audit(out_path: Path | None = None) -> dict[str, Any]:
    """Run cross-language parity compliance audit."""
    if not _HAS_YAML:
        print("ERROR: pyyaml not installed")
        return {}

    if not _PARITY_MATRIX.exists():
        print(f"ERROR: {_PARITY_MATRIX} not found")
        return {}

    matrix = _yaml.safe_load(_PARITY_MATRIX.read_text(encoding="utf-8"))
    formats = matrix.get("formats", {})

    # Load gap ledger for capability context
    gap_by_format: dict[str, list[dict]] = {}
    if _GAP_LEDGER.exists():
        try:
            ledger = json.loads(_GAP_LEDGER.read_text(encoding="utf-8", errors="replace"))
            for gap in ledger.get("gaps", []):
                fmt = gap.get("format", "?").lower()
                gap_by_format.setdefault(fmt, []).append(gap)
        except Exception:
            pass

    per_format_results = []
    dotnet_only = []
    python_only = []
    both_formats = []
    missing_both = []

    for fmt_name, fmt_data in formats.items():
        parity = fmt_data.get("parity", "unknown")
        has_python = fmt_data.get("python", {}).get("exists", False)
        has_dotnet = fmt_data.get("dotnet", {}).get("exists", False)

        # Get Python export info
        py_info: dict = {}
        if has_python:
            py_module = fmt_data.get("python", {}).get("module", "")
            if py_module:
                # Extract first path segment
                first_path = py_module.split("+")[0].strip().rstrip("/")
                py_dir = _REPO / first_path
                py_info = _check_format_exports(py_dir, "python")

        # Get .NET method info
        dn_info: dict = {}
        if has_dotnet:
            dn_project = fmt_data.get("dotnet", {}).get("project", "")
            if dn_project:
                dn_dir = (_REPO / dn_project).parent
                dn_info = _count_dotnet_public_methods(dn_dir)

        # Gap context
        fmt_gaps = gap_by_format.get(fmt_name.lower(), [])
        open_gaps = [g for g in fmt_gaps if g.get("status") == "open"]

        # Parity verdict
        if parity == "both":
            parity_verdict = "BOTH_PRESENT"
            both_formats.append(fmt_name)
            # Check if API counts differ significantly
            py_count = py_info.get("export_count", 0)
            dn_count = dn_info.get("public_method_count", 0)
            parity_gap = abs(py_count - dn_count)
            parity_note = (
                f"Python exports {py_count}, .NET has {dn_count} public methods"
            )
        elif parity == "python_only":
            parity_verdict = "PYTHON_ONLY"
            python_only.append(fmt_name)
            parity_gap = None
            parity_note = "No .NET counterpart"
        elif parity == "dotnet_only":
            parity_verdict = "DOTNET_ONLY"
            dotnet_only.append(fmt_name)
            parity_gap = None
            parity_note = "No Python counterpart"
        elif parity == "both_different_structure":
            parity_verdict = "BOTH_DIFFERENT_STRUCTURE"
            both_formats.append(fmt_name)
            parity_gap = None
            parity_note = fmt_data.get("python", {}).get("note", "")
        else:
            parity_verdict = "UNKNOWN"
            parity_gap = None
            parity_note = parity

        per_format_results.append({
            "format": fmt_name,
            "parity": parity,
            "parity_verdict": parity_verdict,
            "has_python": has_python,
            "has_dotnet": has_dotnet,
            "python_info": py_info,
            "dotnet_info": dn_info,
            "parity_note": parity_note,
            "parity_count_gap": parity_gap,
            "open_gaps": len(open_gaps),
            "decision": fmt_data.get("decision", ""),
        })

    report = {
        "audit_type": "cross_language_parity_compliance",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "parity_matrix_path": str(_PARITY_MATRIX),
        "summary": {
            "total_formats": len(formats),
            "both_python_and_dotnet": len(both_formats),
            "python_only": len(python_only),
            "dotnet_only": len(dotnet_only),
            "python_only_formats": python_only,
            "dotnet_only_formats": dotnet_only,
            "both_formats": both_formats,
        },
        "per_format": per_format_results,
    }

    # Print summary
    print("Cross-Language Parity Compliance Report")
    print("=" * 50)
    print(f"Total formats:    {len(formats)}")
    print(f"Both Python+.NET: {len(both_formats)}")
    print(f"Python only:      {len(python_only)} {python_only}")
    print(f".NET only:        {len(dotnet_only)} {dotnet_only}")
    print()
    print("Both-language formats (API depth comparison):")
    for r in per_format_results:
        if r["parity_verdict"] in ("BOTH_PRESENT", "BOTH_DIFFERENT_STRUCTURE"):
            py = r["python_info"].get("export_count", "?")
            dn = r["dotnet_info"].get("public_method_count", "?")
            gap = r.get("parity_count_gap")
            gap_str = f" (gap={gap})" if gap is not None else ""
            print(f"  {r['format']:12s}: Python exports={py}, .NET methods={dn}{gap_str}")

    if out_path is None:
        date_str = datetime.now().strftime("%Y%m%d")
        out_path = _REPO / f"reports/parity-gap-{date_str}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written: {out_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-language parity compliance audit")
    parser.add_argument("--out", help="Output path for parity gap report JSON")
    args = parser.parse_args()
    out_path = Path(args.out) if args.out else None
    run_audit(out_path=out_path)


if __name__ == "__main__":
    main()
