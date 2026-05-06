#!/usr/bin/env python3
"""
Build a deterministic evidence bundle from a contract YAML.

Usage:
    python build_evidence_bundle.py --repo-root . --contract contracts/run031.yaml --output bundle.zip
    python build_evidence_bundle.py --repo-root . --contract contracts/run031.yaml --dry-run

The bundle contains exactly two top-level folders:
  - repo/        (selected repository files)
  - bundle-metadata/  (analytical and audit metadata files)
"""

import argparse
import fnmatch
import os
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    # Inline minimal YAML parser for stdlib-only environments
    yaml = None


def parse_yaml_minimal(text):
    """Minimal YAML parser for contract files (handles simple key-value and lists)."""
    import re
    result = {}
    current_key = None
    current_list = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item
        if stripped.startswith("- "):
            if current_list is not None:
                current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        # Key-value
        match = re.match(r'^(\w[\w_-]*):\s*(.*)', stripped)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")

            if value == "" or value == "[]":
                # Start of a list or empty value
                current_key = key
                if value == "[]":
                    result[key] = []
                    current_list = None
                else:
                    result[key] = []
                    current_list = result[key]
            else:
                # Try to parse as int
                try:
                    result[key] = int(value)
                except ValueError:
                    result[key] = value
                current_list = None
                current_key = key

    return result


def load_contract(contract_path):
    """Load a contract YAML file."""
    text = Path(contract_path).read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text)
    else:
        return parse_yaml_minimal(text)


def matches_forbidden(path, forbidden_patterns):
    """Check if a path matches any forbidden pattern."""
    path_normalized = path.replace("\\", "/")
    for pattern in forbidden_patterns:
        if fnmatch.fnmatch(path_normalized, pattern):
            return True
        # Also check basename and each path component
        parts = path_normalized.split("/")
        for i in range(len(parts)):
            subpath = "/".join(parts[i:])
            if fnmatch.fnmatch(subpath, pattern):
                return True
    return False


def get_repo_tree(repo_root):
    """Get list of tracked files in repo."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [f for f in result.stdout.splitlines() if f.strip()]


def build_bundle(repo_root, contract_path, output_path, metadata_dir, dry_run=False):
    """Build the evidence bundle zip."""
    contract = load_contract(contract_path)
    repo_root = Path(repo_root).resolve()

    required_top_level = contract.get("required_top_level_folders", ["repo", "bundle-metadata"])
    forbidden_patterns = contract.get("forbidden_patterns", [])
    required_repo_files = contract.get("required_repo_files", [])
    required_metadata_files = contract.get("required_metadata_files", [])
    min_metadata_count = contract.get("min_metadata_count", 5)

    # Collect all tracked repo files
    all_repo_files = get_repo_tree(repo_root)

    # Filter out forbidden
    repo_files_to_include = []
    forbidden_hits = []
    for f in all_repo_files:
        if matches_forbidden(f, forbidden_patterns):
            forbidden_hits.append(f)
        else:
            repo_files_to_include.append(f)

    # Collect metadata files
    metadata_path = Path(metadata_dir).resolve() if metadata_dir else None
    metadata_files = []
    if metadata_path and metadata_path.exists():
        for mf in sorted(metadata_path.iterdir()):
            if mf.is_file():
                metadata_files.append(mf.name)

    # Validation
    errors = []

    # Check required repo files
    missing_repo = []
    for rf in required_repo_files:
        if rf not in repo_files_to_include:
            # Check if file exists on disk even if not tracked
            if (repo_root / rf).exists():
                repo_files_to_include.append(rf)
            else:
                missing_repo.append(rf)

    if missing_repo:
        errors.append(f"Missing required repo files: {missing_repo}")

    # Check required metadata files
    missing_metadata = []
    for mf in required_metadata_files:
        if mf not in metadata_files:
            missing_metadata.append(mf)

    if missing_metadata:
        errors.append(f"Missing required metadata files: {missing_metadata}")

    # Check min metadata count
    if len(metadata_files) < min_metadata_count:
        errors.append(f"Metadata count {len(metadata_files)} < minimum {min_metadata_count}")

    # Check forbidden hits
    if forbidden_hits:
        errors.append(f"Forbidden files in repo would be included: {forbidden_hits[:10]}")

    if dry_run:
        print("=" * 60)
        print("DRY RUN — Evidence Bundle Build")
        print("=" * 60)
        print(f"Contract: {contract_path}")
        print(f"Repo root: {repo_root}")
        print(f"Output: {output_path}")
        print(f"Repo files to include: {len(repo_files_to_include)}")
        print(f"Metadata files: {len(metadata_files)}")
        print(f"Forbidden hits: {len(forbidden_hits)}")
        print(f"Missing repo files: {len(missing_repo)}")
        print(f"Missing metadata: {len(missing_metadata)}")
        if errors:
            print("\nERRORS:")
            for e in errors:
                print(f"  - {e}")
            print("\nBUNDLE_VALIDATION: FAIL")
            return False
        else:
            print("\nBUNDLE_VALIDATION: PASS (dry-run)")
            return True

    if errors:
        print("BUILD ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print("\nBUNDLE_VALIDATION: FAIL")
        return False

    # Build the zip
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add repo files
        for f in sorted(set(repo_files_to_include)):
            full_path = repo_root / f
            if full_path.exists():
                arcname = f"repo/{f}"
                zf.write(full_path, arcname)

        # Add metadata files
        if metadata_path:
            for mf in sorted(metadata_files):
                full_path = metadata_path / mf
                if full_path.exists():
                    arcname = f"bundle-metadata/{mf}"
                    zf.write(full_path, arcname)

    # Verify top-level folders
    with zipfile.ZipFile(output_path, "r") as zf:
        top_level = set()
        for name in zf.namelist():
            parts = name.split("/")
            if parts[0]:
                top_level.add(parts[0])

        unexpected = top_level - set(required_top_level)
        if unexpected:
            print(f"ERROR: Unexpected top-level folders: {unexpected}")
            print("BUNDLE_VALIDATION: FAIL")
            return False

    entries = len(zipfile.ZipFile(output_path).namelist())
    size = output_path.stat().st_size
    print(f"Bundle created: {output_path}")
    print(f"  Entries: {entries}")
    print(f"  Size: {size:,} bytes")
    print(f"  Top-level folders: {sorted(top_level)}")
    print(f"  Repo files: {len(repo_files_to_include)}")
    print(f"  Metadata files: {len(metadata_files)}")
    print("BUNDLE_VALIDATION: PASS")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build evidence bundle from contract")
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--contract", required=True, help="Contract YAML path")
    parser.add_argument("--output", required=True, help="Output zip path")
    parser.add_argument("--metadata-dir", default=None, help="Directory containing metadata files")
    parser.add_argument("--dry-run", action="store_true", help="Validate without creating zip")
    args = parser.parse_args()

    success = build_bundle(
        args.repo_root,
        args.contract,
        args.output,
        args.metadata_dir,
        args.dry_run,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
