#!/usr/bin/env python3
"""
Validate an evidence bundle zip against a contract YAML.

Usage:
    python validate_evidence_bundle.py --contract contracts/run031.yaml --bundle path/to/bundle.zip

Prints BUNDLE_VALIDATION: PASS or BUNDLE_VALIDATION: FAIL.
Exits non-zero on failure.
"""

import argparse
import fnmatch
import re
import sys
import zipfile
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_yaml_minimal(text):
    """Minimal YAML parser for contract files."""
    result = {}
    current_key = None
    current_list = None
    in_nested_list = False  # handles "- path: ..." style

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Nested list item with key (e.g., "- path: foo/bar")
        if stripped.startswith("- ") and ":" in stripped[2:]:
            if current_list is not None:
                # Extract value after first colon
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
        # Normalize required_repo_files list-of-dicts to flat list of paths
        if "required_repo_files" in data and isinstance(data["required_repo_files"], list):
            paths = []
            for item in data["required_repo_files"]:
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


GIT_STATUS_CANDIDATE_FILES = ["git-status-final.txt", "git-status.txt"]

# Patterns that indicate a metadata report was written as a placeholder before bundle
# build and was never updated. When --check-no-pending is passed, any metadata file
# containing one of these strings causes a FAIL.
PENDING_MARKER_PATTERNS = [
    "PENDING (bundle not yet built)",
    "validation_status: PENDING",
]


def check_git_status_clean(metadata_files_content):
    """Check if a git status file in bundle metadata shows a clean working tree.

    Accepts git-status-final.txt (preferred) or git-status.txt as fallback.
    Returns (None, msg) if neither is present — caller must treat this as FAIL
    when require_clean_git is True.
    """
    git_status_text = None
    source_file = None
    for candidate in GIT_STATUS_CANDIDATE_FILES:
        text = metadata_files_content.get(candidate, "")
        if text:
            git_status_text = text
            source_file = candidate
            break

    if not git_status_text:
        candidates_str = " or ".join(GIT_STATUS_CANDIDATE_FILES)
        return None, f"No git status file found in bundle metadata (checked: {candidates_str})"

    lines = git_status_text.strip().splitlines()
    dirty_indicators = [
        "Changes not staged",
        "Changes to be committed",
        "Untracked files",
        "modified:",
        "new file:",
        "deleted:",
    ]
    for line in lines:
        for indicator in dirty_indicators:
            if indicator in line:
                return False, f"{source_file} shows uncommitted changes: '{line.strip()}'"
    return True, f"{source_file} shows clean working tree"


def check_no_pending_reports(metadata_files_content):
    """Scan all metadata files for PENDING marker patterns.

    Returns a list of (filename, matched_pattern) tuples for any file that
    contains a PENDING marker. An empty list means no PENDING markers found.
    """
    hits = []
    for fname, content in metadata_files_content.items():
        for pattern in PENDING_MARKER_PATTERNS:
            if pattern in content:
                hits.append((fname, pattern))
                break  # one hit per file is enough
    return hits


def validate_bundle(contract_path, bundle_path, strict_git=True, no_pending=False):
    """Validate a bundle zip against a contract."""
    contract = load_contract(contract_path)
    bundle_path = Path(bundle_path)

    if not bundle_path.exists():
        print(f"ERROR: Bundle not found: {bundle_path}")
        print("BUNDLE_VALIDATION: FAIL")
        return False

    required_top_level = contract.get("required_top_level_folders", ["repo", "bundle-metadata"])
    forbidden_patterns = contract.get("forbidden_paths", contract.get("forbidden_patterns", []))
    required_repo_files = contract.get("required_repo_files", [])
    required_metadata_files = contract.get("required_metadata_files", [])
    min_metadata_count = contract.get("min_metadata_count", 5)
    require_contract_in_bundle = contract.get("require_contract_in_bundle", False)
    contract_repo_path = contract.get("contract_repo_path", "")
    require_manifest = contract.get("require_manifest", False)
    require_clean_git = contract.get("require_clean_git", strict_git)

    errors = []
    warnings = []

    with zipfile.ZipFile(bundle_path, "r") as zf:
        entries = zf.namelist()

        # Check top-level folders
        top_level = set()
        for name in entries:
            parts = name.split("/")
            if parts[0]:
                top_level.add(parts[0])

        unexpected = top_level - set(required_top_level)
        if unexpected:
            errors.append(f"Unexpected top-level folders: {sorted(unexpected)}")

        missing_top = set(required_top_level) - top_level
        if missing_top:
            errors.append(f"Missing required top-level folders: {sorted(missing_top)}")

        # Collect repo and metadata file lists
        repo_files = set()
        metadata_files = set()
        metadata_files_content = {}
        for name in entries:
            if name.startswith("repo/") and not name.endswith("/"):
                repo_files.add(name[5:])  # strip "repo/" prefix
            elif name.startswith("bundle-metadata/") and not name.endswith("/"):
                fname = name[16:]  # strip "bundle-metadata/" prefix
                metadata_files.add(fname)
                # Read git status files, manifest, and (when --check-no-pending)
                # all metadata files for PENDING marker scanning.
                if (fname in GIT_STATUS_CANDIDATE_FILES
                        or fname == "bundle-manifest.yaml"
                        or no_pending):
                    try:
                        metadata_files_content[fname] = zf.read(name).decode("utf-8", errors="replace")
                    except Exception:
                        pass

        # Check forbidden patterns in repo entries
        forbidden_hits = []
        for name in entries:
            inner_path = name
            if name.startswith("repo/"):
                inner_path = name[5:]
            elif name.startswith("bundle-metadata/"):
                continue  # metadata is never forbidden

            if inner_path and matches_forbidden(inner_path, forbidden_patterns):
                forbidden_hits.append(name)

        if forbidden_hits:
            errors.append(f"Forbidden files found: {forbidden_hits[:10]}")

        # Check required repo files
        missing_repo = []
        for rf in required_repo_files:
            if rf not in repo_files:
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
        if require_contract_in_bundle and contract_repo_path:
            if contract_repo_path not in repo_files:
                errors.append(f"Contract file not found in bundle repo/: {contract_repo_path}")

        # Check manifest presence
        if require_manifest:
            if "bundle-manifest.yaml" not in metadata_files:
                errors.append("Required bundle-manifest.yaml not found in metadata")

        # Check git status cleanliness
        if require_clean_git:
            clean, msg = check_git_status_clean(metadata_files_content)
            if clean is None:
                # Missing git status file is a hard failure when require_clean_git is true
                errors.append(f"Git cleanliness check FAILED: {msg}")
            elif not clean:
                errors.append(f"Git cleanliness check FAILED: {msg}")

        # Check for PENDING markers in metadata files
        pending_hits = []
        if no_pending:
            pending_hits = check_no_pending_reports(metadata_files_content)
            for fname, pattern in pending_hits:
                errors.append(f"PENDING marker in metadata file '{fname}': {pattern!r}")

    # Print validation report
    print("=" * 60)
    print("EVIDENCE BUNDLE VALIDATION REPORT")
    print("=" * 60)
    print(f"Contract: {contract_path}")
    print(f"Bundle: {bundle_path}")
    print(f"Bundle size: {bundle_path.stat().st_size:,} bytes")
    print(f"Total entries: {len(entries)}")
    print(f"Top-level folders: {sorted(top_level)}")
    print(f"Repo files: {len(repo_files)}")
    print(f"Metadata files: {len(metadata_files)}")
    print(f"Required repo files: {len(required_repo_files)} (missing: {len(missing_repo)})")
    print(f"Required metadata files: {len(required_metadata_files)} (missing: {len(missing_metadata)})")
    print(f"Min metadata required: {min_metadata_count}")
    print(f"Forbidden hits: {len(forbidden_hits)}")
    if require_contract_in_bundle:
        print(f"Contract in bundle: {'YES' if contract_repo_path in repo_files else 'NO'}")
    if require_manifest:
        print(f"Manifest present: {'YES' if 'bundle-manifest.yaml' in metadata_files else 'NO'}")
    if require_clean_git:
        clean, msg = check_git_status_clean(metadata_files_content)
        status_label = "PASS" if clean else ("FAIL" if clean is False else "MISSING")
        print(f"Git clean ({status_label}): {msg}")
    if no_pending:
        pending_status = "PASS" if not pending_hits else "FAIL"
        print(f"No-PENDING check ({pending_status}): {len(pending_hits)} PENDING marker(s) found in metadata files")
    print()

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print()
        print("BUNDLE_VALIDATION: FAIL")
        return False
    else:
        print("All checks passed.")
        print()
        print("BUNDLE_VALIDATION: PASS")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate evidence bundle against contract")
    parser.add_argument("--contract", required=True, help="Contract YAML path")
    parser.add_argument("--bundle", required=True, help="Bundle zip path")
    parser.add_argument("--no-strict-git", action="store_true",
                        help="Skip git cleanliness check even if contract requires it")
    parser.add_argument("--check-no-pending", action="store_true",
                        help="Fail if any metadata file contains PENDING marker patterns "
                             "(use as final validation after report files are updated)")
    args = parser.parse_args()

    success = validate_bundle(
        args.contract,
        args.bundle,
        strict_git=not args.no_strict_git,
        no_pending=args.check_no_pending,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
