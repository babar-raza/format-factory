#!/usr/bin/env python3
"""Collect file inventory (reviewed, modified, created) for evidence bundles."""

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


def collect_file_inventory(repo_root, output_dir, base_commit=None):
    """Collect file lists relative to base_commit."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(repo_root)

    if base_commit:
        # Files modified since base_commit
        diff_output = run_git(["diff", "--name-only", base_commit, "HEAD"], repo_root)
        modified = diff_output.splitlines() if diff_output else []

        # Files added since base_commit
        diff_stat = run_git(["diff", "--name-status", base_commit, "HEAD"], repo_root)
        created = []
        for line in diff_stat.splitlines():
            if line.startswith("A\t"):
                created.append(line[2:])
    else:
        modified = []
        created = []

    # All tracked files = files-reviewed (the full repo listing)
    all_files = run_git(["ls-files"], repo_root)
    reviewed = all_files.splitlines() if all_files else []

    (output_dir / "files-reviewed.txt").write_text(
        "\n".join(sorted(reviewed)), encoding="utf-8"
    )
    (output_dir / "files-modified.txt").write_text(
        "\n".join(sorted(modified)), encoding="utf-8"
    )
    (output_dir / "files-created.txt").write_text(
        "\n".join(sorted(created)), encoding="utf-8"
    )

    return len(reviewed), len(modified), len(created)


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    base = sys.argv[3] if len(sys.argv) > 3 else None
    r, m, c = collect_file_inventory(repo, out, base)
    print(f"Inventory: {r} reviewed, {m} modified, {c} created")
