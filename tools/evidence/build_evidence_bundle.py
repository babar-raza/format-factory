#!/usr/bin/env python3
"""
Build a deterministic evidence bundle from a contract YAML.

Usage:
    python build_evidence_bundle.py --repo-root . --contract contracts/run031.yaml --output bundle.zip
    python build_evidence_bundle.py --repo-root . --contract contracts/run031.yaml --dry-run

The bundle contains exactly two top-level folders:
  - repo/        (selected repository files)
  - bundle-metadata/  (analytical and audit metadata files)

Produces bundle-manifest.yaml in the metadata directory listing all included,
missing, and skipped files.
"""

import argparse
import fnmatch
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_yaml_minimal(text):
    """Minimal YAML parser for contract files (handles simple key-value and lists)."""
    result = {}
    current_key = None
    current_list = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Nested list item with key (e.g., "- path: foo/bar")
        if stripped.startswith("- ") and ":" in stripped[2:]:
            if current_list is not None:
                kv = stripped[2:].strip()
                colon_idx = kv.index(":")
                val = kv[colon_idx + 1:].strip().strip('"').strip("'")
                current_list.append(val)
            continue

        # Simple list item
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
                current_key = key
                if value == "[]":
                    result[key] = []
                    current_list = None
                else:
                    result[key] = []
                    current_list = result[key]
            else:
                try:
                    result[key] = int(value)
                except ValueError:
                    if value.lower() == "true":
                        result[key] = True
                    elif value.lower() == "false":
                        result[key] = False
                    else:
                        result[key] = value
                current_list = None
                current_key = key

    return result


def load_contract(contract_path):
    """Load a contract YAML file."""
    text = Path(contract_path).read_text(encoding="utf-8")
    if yaml:
        data = yaml.safe_load(text)
        # Normalize required_files list-of-dicts to flat list of paths
        if "required_files" in data and isinstance(data["required_files"], list):
            paths = []
            for item in data["required_files"]:
                if isinstance(item, dict) and "path" in item:
                    paths.append(item["path"])
                elif isinstance(item, str):
                    paths.append(item)
            data["required_repo_files"] = paths
        return data
    else:
        return parse_yaml_minimal(text)


def matches_forbidden(path, forbidden_patterns):
    """Check if a path matches any forbidden pattern."""
    path_normalized = path.replace("\\", "/")
    for pattern in forbidden_patterns:
        pattern_clean = pattern.rstrip("/")
        if fnmatch.fnmatch(path_normalized, pattern_clean + "*"):
            return True
        if fnmatch.fnmatch(path_normalized, pattern_clean):
            return True
        if path_normalized.startswith(pattern_clean + "/"):
            return True
        if path_normalized.startswith(pattern_clean):
            return True
        parts = path_normalized.split("/")
        for i in range(len(parts)):
            subpath = "/".join(parts[i:])
            if fnmatch.fnmatch(subpath, pattern_clean + "*"):
                return True
            if fnmatch.fnmatch(subpath, pattern_clean):
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


def check_git_clean(repo_root):
    """Check if git working tree is clean. Returns (is_clean, status_text)."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    status_text = result.stdout.strip()
    is_clean = len(status_text) == 0
    return is_clean, status_text


def write_manifest(manifest_path, included_repo, included_meta, missing_repo, missing_meta,
                   forbidden_skipped, contract_path, bundle_path):
    """Write bundle-manifest.yaml to the metadata directory."""
    lines = [
        "# Evidence Bundle Manifest",
        f"# Generated: {datetime.now().astimezone().isoformat()}",
        f"contract: {contract_path}",
        f"bundle: {bundle_path}",
        "",
        f"repo_files_included: {len(included_repo)}",
        f"metadata_files_included: {len(included_meta)}",
        f"repo_files_missing: {len(missing_repo)}",
        f"metadata_files_missing: {len(missing_meta)}",
        f"forbidden_files_skipped: {len(forbidden_skipped)}",
        "",
    ]

    if missing_repo:
        lines.append("missing_repo_files:")
        for f in sorted(missing_repo):
            lines.append(f"  - {f}")
        lines.append("")

    if missing_meta:
        lines.append("missing_metadata_files:")
        for f in sorted(missing_meta):
            lines.append(f"  - {f}")
        lines.append("")

    if forbidden_skipped:
        lines.append("forbidden_files_skipped_list:")
        for f in sorted(forbidden_skipped)[:20]:
            lines.append(f"  - {f}")
        lines.append("")

    Path(manifest_path).write_text("\n".join(lines), encoding="utf-8")


def build_bundle(repo_root, contract_path, output_path, metadata_dir, dry_run=False,
                 require_clean_git=True):
    """Build the evidence bundle zip."""
    contract = load_contract(contract_path)
    repo_root = Path(repo_root).resolve()

    required_top_level = contract.get("required_top_level_folders", ["repo", "bundle-metadata"])
    forbidden_patterns = contract.get("forbidden_paths", contract.get("forbidden_patterns", []))
    required_repo_files = contract.get("required_repo_files", [])
    required_metadata_files = contract.get("required_metadata_files", [])
    min_metadata_count = contract.get("min_metadata_count", 5)
    require_contract = contract.get("require_contract_in_bundle", False)
    contract_repo_path = contract.get("contract_repo_path", "")
    require_manifest_flag = contract.get("require_manifest", False)
    git_clean_required = contract.get("require_clean_git", require_clean_git)

    # Check git cleanliness FIRST (before any file collection)
    if git_clean_required:
        is_clean, git_porcelain = check_git_clean(repo_root)
        if not is_clean:
            print("BUILD ERROR: Git working tree is not clean.")
            print("Uncommitted changes:")
            for line in git_porcelain.splitlines()[:20]:
                print(f"  {line}")
            print()
            print("Commit or stash all changes before building the evidence bundle.")
            print("BUNDLE_BUILD: FAIL")
            return False

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
            if (repo_root / rf).exists():
                repo_files_to_include.append(rf)
            else:
                missing_repo.append(rf)

    if missing_repo:
        errors.append(f"Missing required repo files ({len(missing_repo)}): {missing_repo[:10]}")

    # Check required metadata files
    missing_metadata = []
    for mf in required_metadata_files:
        if mf not in metadata_files:
            missing_metadata.append(mf)

    if missing_metadata:
        errors.append(f"Missing required metadata files ({len(missing_metadata)}): {missing_metadata[:10]}")

    # Check min metadata count
    if len(metadata_files) < min_metadata_count:
        errors.append(f"Metadata count {len(metadata_files)} < minimum {min_metadata_count}")

    # Check contract-in-bundle
    if require_contract and contract_repo_path:
        if contract_repo_path not in repo_files_to_include:
            errors.append(f"Contract file not in repo tracked files: {contract_repo_path}")

    # Check manifest requirement — manifest is generated during build, so just flag
    if require_manifest_flag and metadata_path:
        manifest_target = metadata_path / "bundle-manifest.yaml"
        # We will generate it, so this is a pre-check that manifest_dir exists
        if not metadata_path.exists():
            errors.append("Metadata directory does not exist; cannot generate manifest")

    if dry_run:
        print("=" * 60)
        print("DRY RUN — Evidence Bundle Build")
        print("=" * 60)
        print(f"Contract: {contract_path}")
        print(f"Repo root: {repo_root}")
        print(f"Output: {output_path}")
        print(f"Repo files to include: {len(repo_files_to_include)}")
        print(f"Metadata files: {len(metadata_files)}")
        print(f"Min metadata required: {min_metadata_count}")
        print(f"Forbidden hits: {len(forbidden_hits)}")
        print(f"Missing repo files: {len(missing_repo)}")
        print(f"Missing metadata: {len(missing_metadata)}")
        if require_contract:
            in_bundle = contract_repo_path in repo_files_to_include
            print(f"Contract in bundle: {'YES' if in_bundle else 'NO'}")
        if errors:
            print("\nERRORS:")
            for e in errors:
                print(f"  - {e}")
            print("\nBUNDLE_BUILD: FAIL (dry-run)")
            return False
        else:
            print("\nBUNDLE_BUILD: PASS (dry-run)")
            return True

    if errors:
        print("BUILD ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print("\nBUNDLE_BUILD: FAIL")
        return False

    # Generate manifest before building zip
    if metadata_path:
        manifest_path = metadata_path / "bundle-manifest.yaml"
        write_manifest(
            manifest_path,
            included_repo=repo_files_to_include,
            included_meta=metadata_files,
            missing_repo=missing_repo,
            missing_meta=missing_metadata,
            forbidden_skipped=forbidden_hits,
            contract_path=str(contract_path),
            bundle_path=str(output_path),
        )
        if "bundle-manifest.yaml" not in metadata_files:
            metadata_files.append("bundle-manifest.yaml")

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
            for mf in sorted(set(metadata_files)):
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
            print("BUNDLE_BUILD: FAIL")
            return False

    with zipfile.ZipFile(output_path, "r") as zf:
        entries = zf.namelist()
    size = output_path.stat().st_size
    print(f"Bundle created: {output_path}")
    print(f"  Entries: {len(entries)}")
    print(f"  Size: {size:,} bytes")
    print(f"  Top-level folders: {sorted(top_level)}")
    print(f"  Repo files: {len(repo_files_to_include)}")
    print(f"  Metadata files: {len(metadata_files)}")
    print(f"  Min metadata required: {min_metadata_count}")
    if require_contract:
        print(f"  Contract in bundle: YES")
    print(f"  Manifest generated: YES")
    print("BUNDLE_BUILD: PASS")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build evidence bundle from contract")
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--contract", required=True, help="Contract YAML path")
    parser.add_argument("--output", required=True, help="Output zip path")
    parser.add_argument("--metadata-dir", default=None, help="Directory containing metadata files")
    parser.add_argument("--dry-run", action="store_true", help="Validate without creating zip")
    parser.add_argument("--no-git-check", action="store_true",
                        help="Skip git cleanliness check")
    args = parser.parse_args()

    success = build_bundle(
        args.repo_root,
        args.contract,
        args.output,
        args.metadata_dir,
        args.dry_run,
        require_clean_git=not args.no_git_check,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
