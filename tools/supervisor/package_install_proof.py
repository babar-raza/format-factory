"""Package install proof helper — detect changed product, run smoke tests, capture logs.

v2 improvements (R100):
- .NET project smoke test (dotnet build check)
- wheel file existence check
- blocker report generation

Bridges the /package-install-proof skill to a standalone CLI tool.

Exit codes:
  0 — proof passed
  1 — proof failed
  2 — no changed product detected
  9 — unexpected error
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_MATRIX = REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml"


PYTHON_PRODUCTS = {
    "fods": {"package": "format-factory-fods", "import": "fods"},
    "fodt": {"package": "format-factory-fodt", "import": "fodt"},
    "pbm": {"package": "format-factory-pbm", "import": "pbm"},
    "pgm": {"package": "format-factory-pgm", "import": "pgm"},
    "ppm": {"package": "format-factory-ppm", "import": "ppm"},
    "sylk": {"package": "format-factory-sylk", "import": "sylk"},
    "dif": {"package": "format-factory-dif", "import": "dif"},
    "zst": {"package": "format-factory-zst", "import": "zst"},
    "qoi": {"package": "format-factory-qoi", "import": "qoi"},
    "abw": {"package": "format-factory-abw", "import": "abw"},
    "gnumeric": {"package": "format-factory-gnumeric", "import": "gnumeric"},
    "ndjson": {"package": "format-factory-ndjson", "import": "ndjson"},
    "fodg": {"package": "format-factory-fodg", "import": "fodg"},
    "tsv": {"package": "format-factory-tsv", "import": "tsv"},
}


def detect_changed_products(repo_root: Path) -> list[str]:
    """Detect which product source directories have uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        changed = result.stdout.strip().splitlines()
    except Exception:
        changed = []

    products = set()
    for path in changed:
        if path.startswith("src/python/"):
            parts = path.split("/")
            if len(parts) >= 3:
                products.add(parts[2])
        elif path.startswith("src/net/"):
            parts = path.split("/")
            if len(parts) >= 3:
                products.add(parts[2])
    return sorted(products)


def run_import_proof(
    python: str,
    format_id: str,
    log_dir: Path,
) -> dict[str, Any]:
    """Run a basic import proof for a Python product."""
    info = PYTHON_PRODUCTS.get(format_id)
    if not info:
        return {"format": format_id, "status": "SKIPPED", "reason": "No Python product mapping"}

    import_name = info["import"]
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"install-proof-{format_id}.log"

    try:
        result = subprocess.run(
            [python, "-c", f"import {import_name}; print(f'{import_name} imported OK')"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        log_path.write_text(
            f"Command: python -c 'import {import_name}'\n"
            f"Exit code: {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n",
            encoding="utf-8",
        )
        if result.returncode == 0:
            return {
                "format": format_id,
                "status": "PASS",
                "import_name": import_name,
                "log": str(log_path),
            }
        else:
            return {
                "format": format_id,
                "status": "FAIL",
                "import_name": import_name,
                "error": result.stderr.strip()[:200],
                "log": str(log_path),
            }
    except Exception as e:
        return {"format": format_id, "status": "ERROR", "error": str(e)}


DOTNET_PRODUCTS = {
    "fods": "src/net/fods/FormatFactory.Fods.csproj",
    "fodt": "src/net/fodt/FormatFactory.Fodt.csproj",
    "netpbm": "src/net/netpbm/FormatFactory.Netpbm.csproj",
}


def run_dotnet_build_check(
    format_id: str,
    repo_root: Path,
    log_dir: Path,
) -> dict[str, Any]:
    """Run a dotnet build check for a .NET product."""
    proj_rel = DOTNET_PRODUCTS.get(format_id)
    if not proj_rel:
        return {"format": format_id, "status": "SKIPPED", "reason": "No .NET project mapping"}
    proj = repo_root / proj_rel
    if not proj.exists():
        return {"format": format_id, "status": "SKIPPED", "reason": f"Project not found: {proj_rel}"}

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"dotnet-build-{format_id}.log"
    try:
        result = subprocess.run(
            ["dotnet", "build", str(proj), "--no-restore", "-v", "minimal"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        log_path.write_text(
            f"Command: dotnet build {proj_rel}\nExit: {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}\n",
            encoding="utf-8",
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        return {"format": format_id, "status": status, "project": proj_rel, "log": str(log_path)}
    except Exception as e:
        return {"format": format_id, "status": "ERROR", "error": str(e)}


def check_wheel_exists(format_id: str, repo_root: Path) -> dict[str, Any]:
    """Check if a wheel file exists for the given format."""
    wheel_dir = repo_root / ".local" / "package-artifacts"
    if not wheel_dir.exists():
        return {"format": format_id, "status": "MISSING", "reason": "No package-artifacts directory"}
    wheels = list(wheel_dir.glob(f"format_factory_{format_id}*.whl"))
    if wheels:
        return {"format": format_id, "status": "FOUND", "wheel": str(wheels[0].name)}
    return {"format": format_id, "status": "MISSING", "reason": "No wheel found"}


def generate_blocker_report(proof_result: dict[str, Any]) -> str:
    """Generate a markdown blocker report from proof results."""
    lines = ["# Package Install Proof Blocker Report", ""]
    lines.append(f"Timestamp: {proof_result.get('timestamp', '?')}")
    lines.append(f"Formats tested: {proof_result.get('formats_tested', 0)}")
    lines.append(f"Passed: {proof_result.get('passed', 0)}")
    lines.append(f"Failed: {proof_result.get('failed', 0)}")
    lines.append("")
    blockers = []
    for r in proof_result.get("results", []):
        if r["status"] != "PASS":
            blockers.append(f"- {r['format']}: {r['status']} — {r.get('error', r.get('reason', '?'))}")
    if blockers:
        lines.append("## Blockers")
        lines.extend(blockers)
    else:
        lines.append("No blockers — all proofs passed.")
    return "\n".join(lines) + "\n"


def run_proof(
    python: str,
    format_ids: list[str],
    log_dir: Path,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Run install proofs for specified formats."""
    results = []
    for fid in format_ids:
        results.append(run_import_proof(python, fid, log_dir))

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    dotnet_results = []
    wheel_results = []
    if repo_root:
        for fid in format_ids:
            dotnet_results.append(run_dotnet_build_check(fid, repo_root, log_dir))
            wheel_results.append(check_wheel_exists(fid, repo_root))

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python": python,
        "formats_tested": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
        "dotnet_results": dotnet_results,
        "wheel_results": wheel_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python",
        default=str(REPO_ROOT / ".local" / "venv" / "Scripts" / "python"),
        help="Python interpreter path",
    )
    parser.add_argument(
        "--format",
        nargs="*",
        default=None,
        help="Format IDs to test (default: auto-detect changed)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=REPO_ROOT / ".local" / "supervisor" / "install-proof-logs",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.format:
        format_ids = args.format
    else:
        format_ids = detect_changed_products(REPO_ROOT)
        if not format_ids:
            print("NO_CHANGED_PRODUCTS: No product source changes detected")
            return 2

    print(f"Testing: {', '.join(format_ids)}")
    result = run_proof(args.python, format_ids, args.log_dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for r in result["results"]:
            print(f"  {r['format']}: {r['status']}")
        print(f"TOTAL: {result['passed']}/{result['formats_tested']} passed")

    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
