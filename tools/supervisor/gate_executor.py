"""Python Release Gate Executor (FF-XPLAN-001 W2B-004, PYREL-001).

Evaluates PYREL-G1 through G5 release readiness gates for a format.
Gates are sequential — each gate requires prior gates to pass.

Usage:
    python tools/supervisor/gate_executor.py --format fods --dry-run
    python tools/supervisor/gate_executor.py --format fods --gates G1,G2,G3,G4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# PYREL gate definitions (FF-XPLAN-001 W2B-001)
PYREL_GATES = {
    "G1": {
        "name": "Source Readiness",
        "description": "Format has pyproject.toml, __init__.py, and tests",
        "checks": ["has_pyproject_toml", "has_init_py", "has_tests"],
    },
    "G2": {
        "name": "Oracle Evidence",
        "description": "Oracle verdicts exist with depth >= D1",
        "checks": ["oracle_verdicts_exist", "oracle_depth_minimum_d1"],
    },
    "G3": {
        "name": "Package Build",
        "description": "Clean build produces wheel and sdist",
        "checks": ["build_succeeds"],
    },
    "G4": {
        "name": "Install Verification",
        "description": "Clean install + import succeeds",
        "checks": ["install_succeeds", "import_succeeds"],
    },
    "G5": {
        "name": "Publication Authorization",
        "description": "Gate 11 G11-G approved in format-registry.yaml",
        "checks": ["gate11_approved"],
    },
}


def check_g1(format_id: str) -> dict:
    """G1: Source Readiness — verify source structure exists."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    results = []

    pyproject = src_dir / "pyproject.toml"
    results.append({
        "check": "has_pyproject_toml",
        "passed": pyproject.exists(),
        "detail": str(pyproject),
    })

    init_py = src_dir / "__init__.py"
    results.append({
        "check": "has_init_py",
        "passed": init_py.exists(),
        "detail": str(init_py),
    })

    test_dir = REPO_ROOT / "tests" / format_id
    has_tests = test_dir.exists() and any(test_dir.glob("test_*.py"))
    results.append({
        "check": "has_tests",
        "passed": has_tests,
        "detail": str(test_dir),
    })

    return {
        "gate": "G1",
        "name": "Source Readiness",
        "passed": all(r["passed"] for r in results),
        "checks": results,
    }


def check_g2(format_id: str) -> dict:
    """G2: Oracle Evidence — verify oracle verdicts exist with depth >= D1."""
    summary_path = REPO_ROOT / "oracle" / "formats" / format_id / "reports" / "oracle-run-summary.json"

    if not summary_path.exists():
        return {
            "gate": "G2",
            "name": "Oracle Evidence",
            "passed": False,
            "checks": [{"check": "oracle_verdicts_exist", "passed": False, "detail": f"No summary at {summary_path}"}],
        }

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "gate": "G2",
            "name": "Oracle Evidence",
            "passed": False,
            "checks": [{"check": "oracle_verdicts_exist", "passed": False, "detail": f"Parse error: {e}"}],
        }

    results = []
    total = summary.get("total_cases", 0)
    passed = summary.get("results", {}).get("PASS", 0)
    results.append({
        "check": "oracle_verdicts_exist",
        "passed": total > 0 and passed > 0,
        "detail": f"{passed}/{total} PASS",
    })

    depth = summary.get("format_depth_score", "D0")
    depth_ok = depth in ("D1", "D2", "D3")
    results.append({
        "check": "oracle_depth_minimum_d1",
        "passed": depth_ok,
        "detail": f"depth={depth}, required=D1+",
    })

    return {
        "gate": "G2",
        "name": "Oracle Evidence",
        "passed": all(r["passed"] for r in results),
        "checks": results,
    }


def check_g5(format_id: str) -> dict:
    """G5: Publication Authorization — Gate 11 G11-G approved."""
    try:
        import yaml
        reg_path = REPO_ROOT / "registry" / "format-registry.yaml"
        reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        fmt_entry = reg.get("formats", {}).get(format_id, {})
        gates = fmt_entry.get("gates", {})
        g11 = gates.get("gate_11", {})
        g11g = g11.get("G11-G", {})
        status = g11g.get("status", "not_approved")
        approved = status == "approved"
    except Exception as e:
        return {
            "gate": "G5",
            "name": "Publication Authorization",
            "passed": False,
            "checks": [{"check": "gate11_approved", "passed": False, "detail": f"Error: {e}"}],
        }

    return {
        "gate": "G5",
        "name": "Publication Authorization",
        "passed": approved,
        "checks": [{"check": "gate11_approved", "passed": approved, "detail": f"G11-G status={status}"}],
    }


def run_gates(format_id: str, gates: list[str] | None = None, dry_run: bool = False) -> dict:
    """Run PYREL gates for a format. Gates are sequential."""
    if gates is None:
        gates = ["G1", "G2", "G3", "G4", "G5"]

    results = []
    all_passed = True

    for gate_id in gates:
        if gate_id == "G1":
            result = check_g1(format_id)
        elif gate_id == "G2":
            result = check_g2(format_id)
        elif gate_id in ("G3", "G4"):
            # G3/G4 require actual build/install — skip in scaffold, mark as NOT_IMPLEMENTED
            result = {
                "gate": gate_id,
                "name": PYREL_GATES[gate_id]["name"],
                "passed": False,
                "checks": [{"check": "not_implemented", "passed": False, "detail": "Build/install verification requires execution environment"}],
            }
        elif gate_id == "G5":
            result = check_g5(format_id)
        else:
            result = {"gate": gate_id, "passed": False, "checks": [{"check": "unknown_gate", "passed": False}]}

        results.append(result)
        if not result["passed"]:
            all_passed = False
            if not dry_run:
                break  # Sequential — stop at first failure

    return {
        "format_id": format_id,
        "gates_evaluated": [r["gate"] for r in results],
        "all_passed": all_passed,
        "results": results,
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description="PYREL Gate Executor")
    parser.add_argument("--format", required=True, help="Format ID")
    parser.add_argument("--gates", default=None, help="Comma-separated gate IDs (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Run all gates even if one fails")
    args = parser.parse_args()

    gate_list = args.gates.split(",") if args.gates else None
    result = run_gates(args.format, gate_list, args.dry_run)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
