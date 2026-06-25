#!/usr/bin/env python3
"""
install_hooks.py — Format Factory governance hook installer (TC-SGF-001)

Symlinks .hooks/pre-commit-skill-guard into .git/hooks/pre-commit.
Idempotent: running twice produces identical output.

Usage:
    python tools/governance/install_hooks.py
    python tools/governance/install_hooks.py --uninstall
    python tools/governance/install_hooks.py --status
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK_SRC = REPO_ROOT / ".hooks" / "pre-commit-skill-guard"
HOOK_DEST = REPO_ROOT / ".git" / "hooks" / "pre-commit"
HOOK_DEST_DIR = REPO_ROOT / ".git" / "hooks"


def status() -> dict:
    """Return current hook installation status."""
    return {
        "hook_src_exists": HOOK_SRC.exists(),
        "hook_dest_exists": HOOK_DEST.exists(),
        "hook_dest_is_symlink": HOOK_DEST.is_symlink(),
        "hook_dest_points_to_src": (
            HOOK_DEST.is_symlink() and
            Path(os.path.join(HOOK_DEST_DIR, os.readlink(HOOK_DEST))).resolve() == HOOK_SRC
        ),
        "hook_dest_path": str(HOOK_DEST),
        "hook_src_path": str(HOOK_SRC),
    }


def install(verbose: bool = True) -> int:
    """
    Install the pre-commit hook symlink.
    Returns 0 on success (including already-installed), 1 on error.
    """
    if not HOOK_SRC.exists():
        print(f"ERROR: hook source not found: {HOOK_SRC}", file=sys.stderr)
        return 1

    if not HOOK_DEST_DIR.exists():
        print(f"ERROR: .git/hooks/ directory not found — is this a git repo?", file=sys.stderr)
        return 1

    st = status()

    # Already correctly installed (idempotency)
    if st["hook_dest_is_symlink"] and st["hook_dest_points_to_src"]:
        if verbose:
            print(f"[install-hooks] Already installed (idempotent): {HOOK_DEST}")
        return 0

    # Destination exists but is not our symlink — back it up
    if HOOK_DEST.exists() or HOOK_DEST.is_symlink():
        backup = HOOK_DEST.with_suffix(".pre-skill-guard.bak")
        if verbose:
            print(f"[install-hooks] Backing up existing hook to {backup}")
        HOOK_DEST.rename(backup)

    # Create relative symlink for portability
    try:
        rel_target = os.path.relpath(HOOK_SRC, HOOK_DEST_DIR)
        os.symlink(rel_target, HOOK_DEST)
        if verbose:
            print(f"[install-hooks] Installed: {HOOK_DEST} -> {rel_target}")
        return 0
    except Exception as e:
        # On Windows, symlinks may require elevated permissions — fall back to copy
        try:
            import shutil
            shutil.copy2(HOOK_SRC, HOOK_DEST)
            if verbose:
                print(f"[install-hooks] Copied (symlink unavailable): {HOOK_DEST}")
            return 0
        except Exception as e2:
            print(f"ERROR: could not install hook: {e2}", file=sys.stderr)
            return 1


def uninstall(verbose: bool = True) -> int:
    """Remove the installed hook (if it is our symlink)."""
    st = status()
    if not st["hook_dest_exists"] and not st["hook_dest_is_symlink"]:
        if verbose:
            print("[install-hooks] Hook not installed — nothing to remove")
        return 0

    if st["hook_dest_is_symlink"] and st["hook_dest_points_to_src"]:
        HOOK_DEST.unlink()
        if verbose:
            print(f"[install-hooks] Removed: {HOOK_DEST}")
        return 0

    if verbose:
        print(f"[install-hooks] WARNING: {HOOK_DEST} exists but is not our hook — not removing")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Format Factory governance hooks")
    parser.add_argument("--uninstall", action="store_true", help="Remove the installed hook")
    parser.add_argument("--status", action="store_true", help="Show current installation status")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    verbose = not args.quiet

    if args.status:
        st = status()
        for k, v in st.items():
            print(f"  {k}: {v}")
        installed = st["hook_dest_is_symlink"] and st["hook_dest_points_to_src"]
        print(f"\nstatus: {'INSTALLED' if installed else 'NOT_INSTALLED'}")
        return 0

    if args.uninstall:
        return uninstall(verbose=verbose)

    return install(verbose=verbose)


if __name__ == "__main__":
    sys.exit(main())
