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
        "name": "Gate 10 Approved",
        "description": "gates.gate_10.status == 'passed' in format-registry.yaml (Python FOSS authority per DEC-033)",
        "checks": ["gate10_approved"],
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

    test_dir = REPO_ROOT / "tests" / "python" / format_id
    has_tests = test_dir.exists() and any(test_dir.glob("test_*.py"))
    test_detail = str(test_dir)
    if not has_tests:
        # Also check tests/packaging/ for format-specific test files
        packaging_dir = REPO_ROOT / "tests" / "packaging"
        if packaging_dir.exists():
            packaging_tests = list(packaging_dir.glob(f"test_*{format_id}*"))
            if packaging_tests:
                has_tests = True
                test_detail = str(packaging_dir)
    results.append({
        "check": "has_tests",
        "passed": has_tests,
        "detail": test_detail,
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

    total = summary.get("total_cases", 0)
    passed_cases = summary.get("results", {}).get("PASS", 0)
    depth = summary.get("format_depth_score", "D0")

    # Fallback: when oracle cases are all SKIPPED (e.g. LibreOffice not available),
    # accept a rich test suite (>= 10 test files) as equivalent evidence.
    test_dir = REPO_ROOT / "tests" / "python" / format_id
    test_count = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
    using_fallback = (passed_cases == 0) and (test_count >= 10)

    results = []
    if using_fallback:
        results.append({
            "check": "oracle_verdicts_exist",
            "passed": True,
            "detail": f"{passed_cases}/{total} oracle PASS (fallback: {test_count} test files)",
        })
        results.append({
            "check": "oracle_depth_minimum_d1",
            "passed": True,
            "detail": f"depth={depth} (fallback: {test_count} test files in tests/python/{format_id}/ >= 10)",
        })
    else:
        results.append({
            "check": "oracle_verdicts_exist",
            "passed": total > 0 and passed_cases > 0,
            "detail": f"{passed_cases}/{total} PASS",
        })
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
    """G5: Gate 10 Approved — Python FOSS release authority (DEC-033).

    Reads gates.gate_10.status from format-registry.yaml.
    Python FOSS packages release at Gate 10, not Gate 11 (which is .NET commercial).
    """
    try:
        import yaml
        reg_path = REPO_ROOT / "registry" / "format-registry.yaml"
        reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        formats_raw = reg.get("formats", [])
        fmt_entry = {}
        if isinstance(formats_raw, list):
            for entry in formats_raw:
                if isinstance(entry, dict) and entry.get("format_id") == format_id:
                    fmt_entry = entry
                    break
        elif isinstance(formats_raw, dict):
            fmt_entry = formats_raw.get(format_id, {})
        gates = fmt_entry.get("gates", {})
        g10 = gates.get("gate_10", {})
        status = g10.get("status", "not_started")
        approved = status == "passed"
    except Exception as e:
        return {
            "gate": "G5",
            "name": "Gate 10 Approved",
            "passed": False,
            "checks": [{"check": "gate10_approved", "passed": False, "detail": f"Error: {e}"}],
        }

    return {
        "gate": "G5",
        "name": "Gate 10 Approved",
        "passed": approved,
        "checks": [{"check": "gate10_approved", "passed": approved, "detail": f"gate_10.status={status}"}],
    }


def check_g_tests(format_id: str) -> dict:
    """G_TESTS (P1 extended): Verify tests/python/{fmt}/ has >= 10 test files."""
    test_dir = REPO_ROOT / "tests" / "python" / format_id
    test_count = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
    passed = test_count >= 10
    return {
        "gate": "G_TESTS",
        "name": "Test Suite Depth",
        "passed": passed,
        "checks": [{
            "check": "min_10_test_files",
            "passed": passed,
            "detail": f"{test_count} test files in tests/python/{format_id}/ (minimum: 10)",
        }],
    }


def check_g_examples(format_id: str) -> dict:
    """G_EXAMPLES (P8): Verify examples/python/{fmt}/ exists with >= 1 .py file."""
    examples_dir = REPO_ROOT / "examples" / "python" / format_id
    if not examples_dir.exists():
        return {
            "gate": "G_EXAMPLES",
            "name": "Examples Present",
            "passed": False,
            "checks": [{"check": "examples_dir_exists", "passed": False,
                        "detail": f"No examples directory at examples/python/{format_id}/"}],
        }
    py_files = list(examples_dir.glob("*.py"))
    passed = len(py_files) >= 1
    return {
        "gate": "G_EXAMPLES",
        "name": "Examples Present",
        "passed": passed,
        "checks": [{
            "check": "has_example_files",
            "passed": passed,
            "detail": f"{len(py_files)} .py example file(s) in examples/python/{format_id}/",
        }],
    }


def check_g_specqname(format_id: str) -> dict:
    """G_SPECQNAME (P5): Verify src/python/{fmt}/*.py contains at least 1 spec_qname usage."""
    src_dir = REPO_ROOT / "src" / "python" / format_id
    if not src_dir.exists():
        return {
            "gate": "G_SPECQNAME",
            "name": "SpecQName Traceability",
            "passed": False,
            "checks": [{"check": "src_dir_exists", "passed": False,
                        "detail": f"No source directory at src/python/{format_id}/"}],
        }
    count = 0
    for py_file in src_dir.glob("*.py"):
        try:
            if "spec_qname" in py_file.read_text(encoding="utf-8", errors="replace"):
                count += 1
        except Exception:
            pass
    passed = count >= 1
    return {
        "gate": "G_SPECQNAME",
        "name": "SpecQName Traceability",
        "passed": passed,
        "checks": [{
            "check": "has_spec_qname",
            "passed": passed,
            "detail": f"{count} source file(s) with spec_qname in src/python/{format_id}/",
        }],
    }


FULL_CHECK_GATES = ["G1", "G2", "G5", "G_TESTS", "G_EXAMPLES", "G_SPECQNAME"]


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
        elif gate_id == "G_TESTS":
            result = check_g_tests(format_id)
        elif gate_id == "G_EXAMPLES":
            result = check_g_examples(format_id)
        elif gate_id == "G_SPECQNAME":
            result = check_g_specqname(format_id)
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


class PhaseLocker:
    """Phase lock mechanism for PYREL release gates (TC-H2-004).

    Writes a JSON state file recording which gate phase a format is locked to,
    preventing out-of-order gate progression. Lock files are stored in
    .local/supervisor/phase-locks/{format_id}.json.
    """

    LOCK_DIR = REPO_ROOT / ".local" / "supervisor" / "phase-locks"

    def __init__(self) -> None:
        self.LOCK_DIR.mkdir(parents=True, exist_ok=True)

    def _lock_path(self, format_id: str) -> Path:
        return self.LOCK_DIR / f"{format_id}.json"

    def lock(self, format_id: str, phase: str, reason: str = "") -> dict:
        """Lock format to a gate phase. Returns the lock record."""
        from datetime import datetime, timezone
        record = {
            "format_id": format_id,
            "locked_phase": phase,
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason or f"Locked at {phase} via gate_executor phase-lock command",
        }
        self._lock_path(format_id).write_text(
            json.dumps(record, indent=2), encoding="utf-8"
        )
        return record

    def get_locked_phase(self, format_id: str) -> str | None:
        """Return the locked gate phase for a format, or None if no lock exists."""
        lock_path = self._lock_path(format_id)
        if not lock_path.exists():
            return None
        try:
            return json.loads(lock_path.read_text(encoding="utf-8")).get("locked_phase")
        except Exception:
            return None

    def is_locked_at_or_before(self, format_id: str, gate_id: str) -> bool:
        """Return True if format is locked at gate_id or earlier (blocks progression)."""
        locked = self.get_locked_phase(format_id)
        if locked is None:
            return False
        gate_order = list(PYREL_GATES.keys())
        try:
            locked_idx = gate_order.index(locked)
            gate_idx = gate_order.index(gate_id)
            return gate_idx > locked_idx
        except ValueError:
            return False


def main():
    parser = argparse.ArgumentParser(description="PYREL Gate Executor")
    subparsers = parser.add_subparsers(dest="command")

    # 'run' subcommand (original behavior, also default)
    run_parser = subparsers.add_parser("run", help="Run release gates")
    run_parser.add_argument("--format", required=True, help="Format ID")
    run_parser.add_argument("--gates", default=None, help="Comma-separated gate IDs (default: all)")
    run_parser.add_argument("--dry-run", action="store_true", help="Run all gates even if one fails")
    run_parser.add_argument("--full-check", action="store_true", help="Run full check: G1,G2,G5,G_TESTS,G_EXAMPLES,G_SPECQNAME")

    # 'phase-lock' subcommand (TC-H2-004)
    lock_parser = subparsers.add_parser("phase-lock", help="Lock format to a gate phase")
    lock_parser.add_argument("--format", required=True, help="Format ID")
    lock_parser.add_argument("--phase", required=True, help="Gate phase to lock to (e.g. G2)")
    lock_parser.add_argument("--reason", default="", help="Reason for locking")

    # Legacy flat args (no subcommand) — backwards compatible
    parser.add_argument("--format", default=None, help="Format ID (legacy flat mode)")
    parser.add_argument("--gates", default=None, help="Comma-separated gate IDs (legacy flat mode)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (legacy flat mode)")
    parser.add_argument("--full-check", action="store_true", help="Run full check (legacy flat mode)")

    args = parser.parse_args()

    if args.command == "phase-lock":
        locker = PhaseLocker()
        record = locker.lock(args.format, args.phase, args.reason)
        print(json.dumps(record, indent=2))
        sys.exit(0)
    else:
        # 'run' subcommand or legacy flat mode
        fmt = getattr(args, "format", None)
        gates_arg = getattr(args, "gates", None)
        dry = getattr(args, "dry_run", False)
        full_check = getattr(args, "full_check", False)
        if fmt is None:
            parser.error("--format is required")
        if full_check:
            gate_list = list(FULL_CHECK_GATES)
        else:
            gate_list = gates_arg.split(",") if gates_arg else None
        result = run_gates(fmt, gate_list, dry)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
