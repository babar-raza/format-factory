#!/usr/bin/env python3
"""
TC-RR-006 (C5): Fast pre-commit check: detect new unregistered top-level directories.
Runs in < 2 seconds. Reads git staging area, not full disk scan.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # Fail open: if yaml unavailable, do not block commit
    sys.exit(0)

repo_root = Path(__file__).resolve().parents[2]
registry_path = repo_root / "registry" / "repository-root-folders.yaml"

if not registry_path.exists():
    # No registry yet — cannot validate
    sys.exit(0)

data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
registered = {
    e.get("folder_path", "").strip("/")
    for e in data.get("folders", [])
}

result = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    capture_output=True, text=True, cwd=str(repo_root)
)
staged_paths = result.stdout.splitlines()

new_unregistered: set[str] = set()
for path_str in staged_paths:
    parts = Path(path_str).parts
    if not parts:
        continue
    top = parts[0]
    if top in registered:
        continue
    if top.startswith("."):
        # dot-dirs: only flag if they are physical directories not in registry
        full = repo_root / top
        if full.is_dir() and top not in registered:
            new_unregistered.add(top)
        continue
    full = repo_root / top
    if full.is_dir():
        new_unregistered.add(top)

if new_unregistered:
    print(
        f"ERROR: Unregistered top-level directories staged for commit: "
        f"{sorted(new_unregistered)}"
    )
    print(
        "Add entries to registry/repository-root-folders.yaml "
        "before committing."
    )
    sys.exit(1)
