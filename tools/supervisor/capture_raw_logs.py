"""
capture_raw_logs.py — Capture raw test logs for supervisor evidence packages.

Runs a test command (default: pytest) with stdout/stderr redirected to files
in the evidence root's raw-logs/ directory.

Output structure:
  <evidence_root>/raw-logs/raw-test-log.txt  (combined stdout+stderr)
  <evidence_root>/raw-logs/stdout.txt        (stdout only)
  <evidence_root>/raw-logs/stderr.txt        (stderr only)
  <evidence_root>/raw-logs/capture-meta.json  (metadata: command, exit code, duration, timestamps)

Usage:
  python capture_raw_logs.py --evidence-root .local/evidences/supervisor-r107 \
    --test-dir tests/supervisor/ --marker "supervisor"

  python capture_raw_logs.py --evidence-root .local/evidences/supervisor-r107 \
    --command "pytest tests/supervisor/ -v"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def capture_test_logs(
    evidence_root: Path,
    command: list[str] | None = None,
    test_dir: str | None = None,
    marker: str | None = None,
    timeout: int = 600,
) -> dict:
    """Run a test command and capture stdout/stderr to evidence root.

    Args:
        evidence_root: Path to evidence root directory
        command: Explicit command list (overrides test_dir/marker)
        test_dir: Directory to pass to pytest
        marker: Pytest marker to filter tests
        timeout: Maximum seconds to wait for command

    Returns:
        dict with keys: exit_code, stdout_path, stderr_path, combined_path,
        meta_path, duration, timestamp, command
    """
    raw_logs_dir = evidence_root / "raw-logs"
    raw_logs_dir.mkdir(parents=True, exist_ok=True)

    # Build command
    if command is None:
        cmd = [sys.executable, "-m", "pytest"]
        if test_dir:
            cmd.append(test_dir)
        if marker:
            cmd.extend(["-m", marker])
        cmd.extend(["-v", "--tb=short"])
    else:
        cmd = command

    stdout_path = raw_logs_dir / "stdout.txt"
    stderr_path = raw_logs_dir / "stderr.txt"
    combined_path = raw_logs_dir / "raw-test-log.txt"

    start_time = time.monotonic()
    timestamp = datetime.now().isoformat()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path(__file__).resolve().parent.parent.parent),
        )
        exit_code = result.returncode
        stdout_text = result.stdout or ""
        stderr_text = result.stderr or ""
    except subprocess.TimeoutExpired as e:
        exit_code = -1
        stdout_text = (e.stdout or b"").decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr_text = (e.stderr or b"").decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
    except Exception as e:
        exit_code = -2
        stdout_text = ""
        stderr_text = str(e)

    duration = time.monotonic() - start_time

    # Write output files
    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")
    combined_path.write_text(
        f"=== STDOUT ===\n{stdout_text}\n=== STDERR ===\n{stderr_text}\n",
        encoding="utf-8",
    )

    # Write metadata
    meta = {
        "command": cmd if isinstance(cmd, list) else [cmd],
        "exit_code": exit_code,
        "duration_seconds": round(duration, 2),
        "timestamp": timestamp,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "combined_path": str(combined_path),
        "stdout_lines": stdout_text.count("\n"),
        "stderr_lines": stderr_text.count("\n"),
    }
    meta_path = raw_logs_dir / "capture-meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return {
        "exit_code": exit_code,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "combined_path": str(combined_path),
        "meta_path": str(meta_path),
        "duration": round(duration, 2),
        "timestamp": timestamp,
        "command": cmd,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True,
                        help="Path to evidence root directory")
    parser.add_argument("--command", type=str, default=None,
                        help="Full test command (overrides --test-dir/--marker)")
    parser.add_argument("--test-dir", type=str, default=None,
                        help="Directory to pass to pytest")
    parser.add_argument("--marker", type=str, default=None,
                        help="Pytest marker filter")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Timeout in seconds (default: 600)")
    args = parser.parse_args()

    command = args.command.split() if args.command else None
    result = capture_test_logs(
        evidence_root=args.evidence_root,
        command=command,
        test_dir=args.test_dir,
        marker=args.marker,
        timeout=args.timeout,
    )

    print(json.dumps(result, indent=2))
    return 0 if result["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
