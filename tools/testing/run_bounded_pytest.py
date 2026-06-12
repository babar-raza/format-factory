#!/usr/bin/env python3
"""
Bounded pytest runner — FORMAT-FACTORY-R46-MT4.

Runs pytest in a subprocess with a wall-clock timeout that does not require
pytest-timeout to be installed. When pytest-timeout IS installed it also passes
--timeout=<N> for per-test granularity; when it is NOT installed the whole
subprocess is wall-clock bounded instead.

This tool was created in R46 to replace the bare `timeout = 120` entry in
pytest.ini, which caused PytestConfigWarning in clean environments without
pytest-timeout. The pytest.ini entry is kept (with a filterwarnings suppression)
for CI environments that have pytest-timeout; this tool provides an alternative
for replay environments that may not.

Usage:
    python tools/testing/run_bounded_pytest.py --suite tests/evidence/ --max-seconds 180
    python tools/testing/run_bounded_pytest.py --suite tests/state/ --max-seconds 60
    python tools/testing/run_bounded_pytest.py --suite tests/evidence/test_auto_proof_bundle.py --max-seconds 120

Exit codes:
    0 — pytest completed within time limit and all tests passed
    1 — pytest reported failures (within time limit)
    2 — wall-clock timeout exceeded
    3 — pytest not found / environment error
"""

import argparse
import subprocess
import sys
import time


def pytest_timeout_available(python_exe):
    """Return True if pytest-timeout is importable in the given Python environment."""
    try:
        result = subprocess.run(
            [python_exe, "-c", "import pytest_timeout"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def run_bounded(suite, max_seconds, python_exe=None, extra_args=None, pythonpath=None):
    """Run pytest on the given suite with a wall-clock bound.

    Returns (exit_code, elapsed_seconds, timed_out).
    """
    if python_exe is None:
        python_exe = sys.executable

    cmd = [python_exe, "-m", "pytest", suite, "-q"]
    if extra_args:
        cmd.extend(extra_args)

    # Add per-test timeout if pytest-timeout is available
    if pytest_timeout_available(python_exe):
        cmd.append(f"--timeout={max_seconds}")

    env = None
    if pythonpath:
        import os
        env = dict(os.environ)
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{pythonpath}:{existing}" if existing else pythonpath

    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            timeout=max_seconds,
            env=env,
        )
        elapsed = time.monotonic() - start
        return result.returncode, elapsed, False
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return 2, elapsed, True


def main():
    parser = argparse.ArgumentParser(
        description="Run pytest with wall-clock timeout (no pytest-timeout required)"
    )
    parser.add_argument("--suite", required=True, help="pytest target (path or file)")
    parser.add_argument("--max-seconds", type=int, default=120, help="Wall-clock timeout in seconds")
    parser.add_argument("--python", default=sys.executable, help="Python executable to use")
    parser.add_argument("--pythonpath", help="PYTHONPATH prefix to inject")
    parser.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        help="Extra arguments passed directly to pytest",
    )
    args = parser.parse_args()

    suite = args.suite
    max_seconds = args.max_seconds
    python_exe = args.python
    extra_args = args.extra if args.extra else []
    pythonpath = args.pythonpath

    has_timeout_plugin = pytest_timeout_available(python_exe)
    timeout_source = "pytest-timeout per-test" if has_timeout_plugin else "wall-clock subprocess"
    print(f"run_bounded_pytest: suite={suite} max_seconds={max_seconds} timeout_source={timeout_source}")

    exit_code, elapsed, timed_out = run_bounded(
        suite,
        max_seconds,
        python_exe=python_exe,
        extra_args=extra_args,
        pythonpath=pythonpath,
    )

    if timed_out:
        print(f"BOUNDED_REPLAY: TIMEOUT after {elapsed:.1f}s (limit={max_seconds}s)")
        print("BOUNDED_REPLAY: FAIL")
        sys.exit(2)

    status = "PASS" if exit_code == 0 else "FAIL"
    print(f"BOUNDED_REPLAY: {status} in {elapsed:.1f}s (limit={max_seconds}s, exit={exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
