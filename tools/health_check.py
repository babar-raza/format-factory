"""health_check.py — Project health check for format-factory.

Validates environment, dependencies, and test suite status.
Produces JSON output for observability.

Usage:
    python tools/health_check.py          # full check (runs all tests)
    python tools/health_check.py --quick  # smoke check (first failure only, 30s timeout)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_cmd(args: list[str], timeout: int = 300) -> tuple[int, str]:
    """Run a command and return (returncode, stdout)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except FileNotFoundError:
        return -1, "NOT_FOUND"


def check_health(quick: bool = False) -> dict:
    """Run health checks and return results as a dict."""
    results: dict = {}

    # Python version
    results["python_version"] = sys.version.split()[0]

    # Check pytest
    rc, out = _run_cmd([sys.executable, "-m", "pytest", "--version"])
    results["pytest"] = "available" if rc == 0 else "missing"

    # Check ruff
    rc, out = _run_cmd([sys.executable, "-m", "ruff", "version"])
    results["ruff"] = out if rc == 0 else "missing"

    # Run tests
    test_args = [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header"]
    if quick:
        test_args.extend(["-x", "--timeout=30"])
    else:
        test_args.extend(["--timeout=120"])

    rc, out = _run_cmd(test_args, timeout=600)
    results["tests_pass"] = rc == 0
    # Extract last line as summary
    lines = out.split("\n") if out else []
    results["test_summary"] = lines[-1] if lines else "no output"
    results["test_exit_code"] = rc

    # Overall health
    results["healthy"] = results["tests_pass"] and results["pytest"] == "available"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="format-factory health check")
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick smoke check (first failure, 30s timeout)",
    )
    parser.add_argument(
        "--json", action="store_true", default=True,
        help="Output as JSON (default)",
    )
    args = parser.parse_args()

    results = check_health(quick=args.quick)
    print(json.dumps(results, indent=2))

    return 0 if results["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
