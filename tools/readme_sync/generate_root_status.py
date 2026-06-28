"""Root README drift detection and status summary generation.

Collects metrics from canonical sources and compares them against
values currently in README.md. Detects drift and generates summary
blocks for splicing between markers.

Usage:
    python tools/readme_sync/generate_root_status.py --mode drift-only
    python tools/readme_sync/generate_root_status.py --mode generate
    python tools/readme_sync/generate_root_status.py --mode full
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def collect_root_status(repo_root: Path = REPO_ROOT) -> dict:
    """Collect all README-relevant metrics from canonical sources."""
    status: dict = {"collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    # Package count from package-matrix.yaml
    pm_path = repo_root / "packaging" / "python" / "package-matrix.yaml"
    if pm_path.exists():
        try:
            import yaml
            data = yaml.safe_load(pm_path.read_text(encoding="utf-8"))
            status["package_count"] = len(data.get("packages", []))
        except Exception:
            status["package_count"] = None
    else:
        status["package_count"] = None

    # Validator count from governance_validators*.py
    validator_count = 0
    for f in sorted(repo_root.glob("tools/supervisor/governance_validators*.py")):
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("def validate_"):
                    validator_count += 1
        except Exception:
            pass
    status["validator_count"] = validator_count if validator_count > 0 else None

    # Sprint count from maturity-trend.json
    mt_path = repo_root / "reports" / "supervisor" / "maturity-trend.json"
    if mt_path.exists():
        try:
            data = json.loads(mt_path.read_text(encoding="utf-8"))
            status["sprint_count"] = data.get("sprint_count")
        except Exception:
            status["sprint_count"] = None
    else:
        status["sprint_count"] = None

    # Oracle format count
    oracle_dir = repo_root / "oracle" / "formats"
    if oracle_dir.is_dir():
        status["oracle_format_count"] = len([d for d in oracle_dir.iterdir() if d.is_dir()])
    else:
        status["oracle_format_count"] = None

    # QName registry count
    qname_dir = repo_root / "shared" / "qname-registry"
    if qname_dir.is_dir():
        status["qname_registry_count"] = len([
            f for f in qname_dir.glob("*.yaml") if f.name != "schema.yaml"
        ])
    else:
        status["qname_registry_count"] = None

    # Python source file count
    py_src = repo_root / "src" / "python"
    if py_src.is_dir():
        status["python_source_files"] = len([
            f for f in py_src.rglob("*.py")
            if "egg-info" not in str(f) and "__pycache__" not in str(f) and "build" not in f.parts
        ])
    else:
        status["python_source_files"] = None

    # .NET source file count
    net_src = repo_root / "src" / "net"
    if net_src.is_dir():
        status["dotnet_source_files"] = len([
            f for f in net_src.rglob("*.cs")
            if "obj" not in f.parts and "bin" not in f.parts
        ])
    else:
        status["dotnet_source_files"] = None

    return status


def _extract_readme_numbers(readme_text: str) -> dict:
    """Extract key numbers from README.md text for drift comparison."""
    numbers: dict = {}

    # Package count from header or products heading
    m = re.search(r"(\d+)\s+installable Python packages", readme_text)
    if m:
        numbers["package_count"] = int(m.group(1))

    # Validator count
    m = re.search(r"(\d+)\s+(?:programmatic )?governance validators", readme_text)
    if m:
        numbers["validator_count"] = int(m.group(1))

    # Sprint count
    m = re.search(r"Over\s+([\d,]+)\s+autonomous sprint cycles", readme_text)
    if m:
        numbers["sprint_count"] = int(m.group(1).replace(",", ""))

    # Oracle format count
    m = re.search(r"All\s+(\d+)\s+.*(?:Python FOSS|active).*(?:oracle|VERIFIED)", readme_text)
    if m:
        numbers["oracle_format_count"] = int(m.group(1))

    return numbers


def detect_root_readme_drift(repo_root: Path = REPO_ROOT) -> dict:
    """Compare README claims against canonical sources. Returns drift report."""
    readme_path = repo_root / "README.md"
    if not readme_path.exists():
        return {"drifted": True, "error": "README.md not found", "drifted_fields": ["file_missing"]}

    readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
    readme_numbers = _extract_readme_numbers(readme_text)
    status = collect_root_status(repo_root)

    drifted_fields: list[str] = []

    for key in ("package_count", "validator_count", "oracle_format_count"):
        readme_val = readme_numbers.get(key)
        source_val = status.get(key)
        if readme_val is not None and source_val is not None and readme_val != source_val:
            drifted_fields.append(key)

    # Sprint count uses "Over N" so check if source exceeds README's N significantly
    readme_sprint = readme_numbers.get("sprint_count")
    source_sprint = status.get("sprint_count")
    if readme_sprint is not None and source_sprint is not None:
        if source_sprint > readme_sprint * 1.2:  # >20% growth triggers drift
            drifted_fields.append("sprint_count")

    return {
        "drifted": len(drifted_fields) > 0,
        "drifted_fields": drifted_fields,
        "readme_values": readme_numbers,
        "source_values": {k: v for k, v in status.items() if k != "collected_at"},
        "checked_at": status["collected_at"],
    }


def generate_summary_block(status: dict) -> str:
    """Generate the markdown block for splicing between markers."""
    pkg = status.get("package_count", "?")
    val = status.get("validator_count", "?")
    sprint = status.get("sprint_count", "?")
    oracle = status.get("oracle_format_count", "?")

    lines = [
        f"<!-- BEGIN:SYSTEM-STATUS-SUMMARY generated={status['collected_at']} source=reports/system-status-review.md -->",
        f"**Metrics:** {pkg} Python packages | {val} governance validators | {sprint}+ autonomous sprints | {oracle} oracle-verified formats",
        "",
        "**Full review:** [reports/system-status-review.md](reports/system-status-review.md)",
        "<!-- END:SYSTEM-STATUS-SUMMARY -->",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Root README drift detection and status generation")
    parser.add_argument("--mode", choices=["drift-only", "generate", "full"], default="drift-only",
                        help="drift-only: check for drift. generate: print summary block. full: both.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.mode in ("drift-only", "full"):
        drift = detect_root_readme_drift(args.repo_root)
        if args.json:
            print(json.dumps(drift, indent=2))
        else:
            if drift["drifted"]:
                print(f"ROOT README DRIFT DETECTED: {drift['drifted_fields']}")
                for field in drift["drifted_fields"]:
                    readme_val = drift["readme_values"].get(field, "?")
                    source_val = drift["source_values"].get(field, "?")
                    print(f"  {field}: README says {readme_val}, source says {source_val}")
                print(f"\nChecked at: {drift['checked_at']}")
            else:
                print(f"NO_DRIFT — root README is current (checked {drift['checked_at']})")

    if args.mode in ("generate", "full"):
        status = collect_root_status(args.repo_root)
        block = generate_summary_block(status)
        if args.json:
            print(json.dumps({"summary_block": block, "status": status}, indent=2))
        else:
            print("\n--- Generated summary block ---")
            print(block)

    if args.mode == "drift-only":
        drift = detect_root_readme_drift(args.repo_root)
        return 1 if drift["drifted"] else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
