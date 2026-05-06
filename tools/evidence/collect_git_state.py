#!/usr/bin/env python3
"""Collect git state into metadata files for evidence bundles."""

import subprocess
import sys
from pathlib import Path


def run_git(args, cwd):
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def collect_git_state(repo_root, output_dir):
    """Collect git status, log, and diff into output_dir."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(repo_root)

    # git status
    status = run_git(["status"], repo_root)
    (output_dir / "git-status.txt").write_text(status, encoding="utf-8")

    # git log (last 15 commits, oneline)
    log = run_git(["log", "--oneline", "-15"], repo_root)
    (output_dir / "git-log.txt").write_text(log, encoding="utf-8")

    return True


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    collect_git_state(repo, out)
    print(f"Git state collected to {out}")
