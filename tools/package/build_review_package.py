#!/usr/bin/env python3
"""
Build a review package from the repository for external review.

Modes:
  - source-only: Source files only, no build artifacts
  - evidence-replay: Source + evidence bundles + reports
  - full-local-diagnostic: Everything except secrets and large binaries

Usage:
    python tools/package/build_review_package.py --mode source-only --output review.zip
    python tools/package/build_review_package.py --mode source-only --dry-run
"""
import argparse
import fnmatch
import os
import pathlib
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

DEFAULT_EXCLUSIONS = [
    ".git/",
    ".git/**",
    ".venv/",
    ".venv/**",
    ".local/",
    ".local/**",
    "bin/",
    "bin/**",
    "obj/",
    "obj/**",
    "__pycache__/",
    "__pycache__/**",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.dll",
    "*.pdb",
    "*.nupkg",
    "*.snupkg",
    "*.exe",
    ".env",
    ".env.*",
    "*.log",
    "*.tmp",
    "*.swp",
    "htmlcov/",
    "htmlcov/**",
    ".coverage",
    ".coverage.*",
    ".pytest_cache/",
    ".pytest_cache/**",
    ".mypy_cache/",
    ".mypy_cache/**",
    ".ruff_cache/",
    ".ruff_cache/**",
]

MODE_EXCLUSIONS = {
    "source-only": DEFAULT_EXCLUSIONS + [
        "reports/",
        "reports/**",
        "memory/",
        "memory/**",
        ".claude/",
        ".claude/**",
    ],
    "evidence-replay": DEFAULT_EXCLUSIONS,
    "full-local-diagnostic": [
        ".git/",
        ".git/**",
        ".env",
        ".env.*",
    ],
}


def matches_exclusion(relpath, exclusions):
    for pattern in exclusions:
        if fnmatch.fnmatch(relpath, pattern):
            return True
        if fnmatch.fnmatch(relpath.replace("\\", "/"), pattern):
            return True
        # Check path components
        parts = relpath.replace("\\", "/").split("/")
        for part in parts:
            if fnmatch.fnmatch(part, pattern.rstrip("/")):
                return True
    return False


def get_tracked_files():
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def get_filesystem_files(root=None):
    """Fallback file discovery when .git is absent."""
    root = root or ROOT
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories in-place
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in
                       ('bin', 'obj', '__pycache__', 'node_modules', '.venv', 'venv')]
        for fn in filenames:
            full = pathlib.Path(dirpath) / fn
            rel = full.relative_to(root).as_posix()
            files.append(rel)
    return files


def build_package(mode, output_path, dry_run=False):
    exclusions = MODE_EXCLUSIONS.get(mode, DEFAULT_EXCLUSIONS)

    # Prefer git ls-files; fall back to filesystem walk
    git_dir = ROOT / ".git"
    if git_dir.exists():
        source_discovery_mode = "git_ls_files"
        all_files = get_tracked_files()
    else:
        source_discovery_mode = "filesystem_fallback"
        all_files = get_filesystem_files()

    included = []
    excluded = []
    for f in all_files:
        if matches_exclusion(f, exclusions):
            excluded.append(f)
        else:
            included.append(f)

    # Build manifest
    manifest = {
        "mode": mode,
        "source_discovery_mode": source_discovery_mode,
        "included_count": len(included),
        "excluded_count": len(excluded),
        "exclusion_patterns": exclusions,
    }

    if dry_run:
        print(f"Mode: {mode}")
        print(f"Included: {len(included)}")
        print(f"Excluded: {len(excluded)}")
        print(f"Output: {output_path}")
        print("DRY_RUN: no zip created")
        return manifest

    output = pathlib.Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in included:
            full_path = ROOT / f
            if full_path.exists():
                zf.write(full_path, f)

        # Add manifest
        import json
        zf.writestr("review-package-manifest.yaml",
                     f"mode: {mode}\nincluded_count: {len(included)}\nexcluded_count: {len(excluded)}\n")

    print(f"Package created: {output}")
    print(f"  Mode: {mode}")
    print(f"  Included: {len(included)}")
    print(f"  Excluded: {len(excluded)}")
    print("REVIEW_PACKAGE: PASS")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Build review package")
    parser.add_argument("--mode", choices=["source-only", "evidence-replay", "full-local-diagnostic"],
                        default="source-only")
    parser.add_argument("--output", default=".local/review-package.zip")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    build_package(args.mode, args.output, args.dry_run)


if __name__ == "__main__":
    main()
