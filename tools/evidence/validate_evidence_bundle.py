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
    """Check if a path matches any forbidden pattern.

    For patterns WITHOUT wildcards (* ? [): exact filename match or directory-prefix
    match only. This prevents `.env` from matching `.env.example`.

    For patterns WITH wildcards: standard fnmatch behavior on the full path and all
    trailing sub-paths (so `*.key` still matches `secrets/api.key`).
    """
    path_normalized = path.replace("\\", "/")
    for pattern in forbidden_patterns:
        pattern_clean = pattern.rstrip("/")
        has_wildcards = any(c in pattern_clean for c in ("*", "?", "["))

        if has_wildcards:
            # Wildcard pattern — fnmatch on full path and all trailing sub-paths
            if fnmatch.fnmatch(path_normalized, pattern_clean):
                return True
            parts = path_normalized.split("/")
            for i in range(len(parts)):
                subpath = "/".join(parts[i:])
                if fnmatch.fnmatch(subpath, pattern_clean):
                    return True
        else:
            # Non-wildcard pattern — exact match or directory-prefix match only.
            # `.env` matches `.env` and `.env/anything` but NOT `.env.example`.
            if path_normalized == pattern_clean:
                return True
            if path_normalized.startswith(pattern_clean + "/"):
                return True
            parts = path_normalized.split("/")
            for i in range(len(parts)):
                subpath = "/".join(parts[i:])
                if subpath == pattern_clean:
                    return True
                if subpath.startswith(pattern_clean + "/"):
                    return True
    return False


# Absolute floor for metadata count in normal PASS bundles.
# No run-specific contract may produce a BUNDLE_VALIDATION: PASS with fewer
# metadata files than this value unless emergency_blocker_bundle: true.
#
# Floor history:
#   run031: floor introduced at 5
#   run042: floor raised to 30 (normal PASS depth requirement)
#   run046: floor REGRESSED to 4 (incorrect fix — reversed by run047)
#   run047: floor RESTORED to 30 (correct project standard)
#
# A value of 30 ensures each sprint produces meaningful evidence depth.
# Emergency blocker bundles (blocked/failed runs) may bypass via emergency_blocker_bundle: true.
RUN_CONTRACT_METADATA_FLOOR = 30
# Minimum named required_metadata_files for full-sprint contracts (run048+).
# Any contract with min_metadata_count >= 80 must name at least this many
# specific required_metadata_files, or set historical_contract: true to bypass.
# Setting test_contract: true on a real sprint contract (contract_id matching run\d+) is REJECTED.
REQUIRED_METADATA_DEPTH_MINIMUM_NAMED = 10

GIT_STATUS_CANDIDATE_FILES = ["git-status-final.txt", "git-status.txt"]

# Patterns that indicate a metadata report was written as a placeholder before bundle
# build and was never updated. When --check-no-pending is passed, any metadata file
# containing one of these strings causes a FAIL.
PENDING_MARKER_PATTERNS = [
    "PENDING (bundle not yet built)",
    "validation_status: PENDING",
    # Final validation proof placeholders — must not appear in closure bundles
    "BUNDLE_VALIDATION: PENDING",
    "BUNDLE_VALIDATION: [PENDING]",
    "TO BE UPDATED AFTER BUNDLE",
    "PENDING — building evidence bundle",
]

# Current-state PENDING patterns — sprint-in-progress markers that must NOT appear
# in committed repo files (master-plan.md, memory/09) in their final state.
# See docs/current-state-and-evidence-authority.md.
REPO_STATE_PENDING_PATTERNS = [
    r"Latest commit:\s*PENDING",
    r"changes pending commit",
    r"run\d+\s+changes\s+pending",
]

# Repo files whose header sections are scanned for REPO_STATE_PENDING_PATTERNS.
# Only the first 3000 chars are scanned to avoid false positives in historical run notes.
CURRENT_STATE_REPO_FILES = [
    "plans/master-plan.md",
    "memory/09-current-state-before-phase1.md",
]

IDENTITY_METADATA_FILES = [
    "metadata-identity-report.md",
    "verdict.md",
    "final-state-summary.yaml",
    "final-bundle-validation-proof.txt",
    "evidence-contract-validation-report.md",
    "sprint-summary.md",
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


def check_repo_current_state_pending(zf):
    """Scan bundled repo current-state files for sprint-in-progress PENDING patterns.

    Checks the header sections (first 3000 chars) of CURRENT_STATE_REPO_FILES.
    Returns a list of (filename, pattern_found) tuples for any hits.
    See docs/current-state-and-evidence-authority.md.
    """
    hits = []
    all_entries = set(zf.namelist())
    for repo_rel_path in CURRENT_STATE_REPO_FILES:
        zip_path = f"repo/{repo_rel_path}"
        if zip_path not in all_entries:
            continue
        try:
            content = zf.read(zip_path).decode("utf-8", errors="replace")
        except Exception:
            continue
        header_section = content[:3000]
        for pattern in REPO_STATE_PENDING_PATTERNS:
            m = re.search(pattern, header_section, re.IGNORECASE)
            if m:
                # Skip matches that are clearly inside historical run table rows
                line_start = header_section.rfind("\n", 0, m.start()) + 1
                line_end = header_section.find("\n", m.end())
                line = header_section[line_start:line_end] if line_end > 0 else header_section[line_start:]
                if re.match(r"\|\s*run0\d+", line.strip()):
                    continue
                hits.append((repo_rel_path, m.group(0)))
                break
    return hits


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


def check_closure_contradictions(metadata_files_content):
    """Detect obvious final closure contradictions in bundle metadata.

    Triggered when --check-no-pending is active. Looks for cases where a final
    proof file claims PASS while a verdict or summary file claims FAIL — the pattern
    that occurred in run050 when stale intermediate-run metadata was not overwritten.

    Returns a list of (description) strings for each contradiction found.
    """
    hits = []
    proof_content = metadata_files_content.get("final-bundle-validation-proof.txt", "")
    verdict_content = metadata_files_content.get("verdict.md", "")
    summary_content = metadata_files_content.get("final-state-summary.yaml", "")

    proof_says_pass = "BUNDLE_VALIDATION: PASS" in proof_content
    verdict_says_fail = "SPRINT_VERDICT: FAIL" in verdict_content
    summary_says_fail = "result: FAIL" in summary_content

    if proof_says_pass and verdict_says_fail:
        hits.append(
            "CLOSURE_CONTRADICTION: final-bundle-validation-proof.txt says BUNDLE_VALIDATION: PASS "
            "but verdict.md says SPRINT_VERDICT: FAIL — stale closure metadata must be repaired "
            "before bundle is considered authoritative."
        )
    if proof_says_pass and summary_says_fail:
        hits.append(
            "CLOSURE_CONTRADICTION: final-bundle-validation-proof.txt says BUNDLE_VALIDATION: PASS "
            "but final-state-summary.yaml says result: FAIL — stale closure metadata must be repaired."
        )
    return hits


def extract_metadata_identity(text):
    """Extract likely primary sprint/contract IDs from identity-critical metadata."""
    identities = set()
    patterns = [
        r"\bsprint_id:\s*['\"]?([A-Za-z0-9_.-]+)",
        r"\bSprint:\s*([A-Za-z0-9_.-]+)",
        r"\bcontract_id:\s*['\"]?([A-Za-z0-9_.-]+)",
        r"\bContract:\s*.*?([A-Za-z0-9_.-]+\.ya?ml)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(1).strip().strip("'\"")
            if value.endswith((".yaml", ".yml")):
                value = Path(value).stem
            if value and value.lower() not in {"true", "false", "null"}:
                identities.add(value)
    return identities


def check_metadata_identity(metadata_files_content, require_identity=False):
    """Verify identity-critical metadata files agree on the primary sprint."""
    identities = set()
    inspected = []
    for fname in IDENTITY_METADATA_FILES:
        content = metadata_files_content.get(fname)
        if not content:
            continue
        inspected.append(fname)
        identities.update(extract_metadata_identity(content))

    if not inspected:
        if require_identity:
            return ["METADATA_IDENTITY: missing identity-critical metadata files"]
        return []
    if not identities:
        if require_identity:
            return ["METADATA_IDENTITY: identity files exist but no sprint identity was found"]
        return []
    if len(identities) > 1:
        return [
            "METADATA_IDENTITY: mixed primary sprint/contract identities found: "
            + ", ".join(sorted(identities))
        ]
    return []


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
    normal_pass_min = contract.get("normal_pass_min_metadata", 0)
    emergency_blocker = contract.get("emergency_blocker_bundle", False)
    require_contract_in_bundle = contract.get("require_contract_in_bundle", False)
    contract_repo_path = contract.get("contract_repo_path", "")
    require_manifest = contract.get("require_manifest", False)
    require_clean_git = contract.get("require_clean_git", strict_git)
    require_metadata_identity = contract.get("require_metadata_identity", False)

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
                        or fname in IDENTITY_METADATA_FILES
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

        # Check min metadata count (contract-level floor)
        if len(metadata_files) < min_metadata_count:
            errors.append(f"Metadata count {len(metadata_files)} < minimum {min_metadata_count}")

        # Check normal-pass metadata depth (contract-level floor from normal_pass_min_metadata)
        metadata_depth_fail = (
            normal_pass_min > 0 and len(metadata_files) < normal_pass_min
        )
        if metadata_depth_fail:
            errors.append(
                f"NORMAL_PASS_METADATA_DEPTH: FAIL — "
                f"metadata count {len(metadata_files)} < normal_pass_min_metadata {normal_pass_min}"
            )

        # Check absolute hardcoded floor (RUN_CONTRACT_METADATA_FLOOR).
        # This cannot be bypassed by setting a low min_metadata_count or normal_pass_min_metadata
        # in the run-specific contract. Only emergency_blocker_bundle: true bypasses this.
        # Prevents regression where a contract lowers the floor below the project standard.
        if not emergency_blocker and len(metadata_files) < RUN_CONTRACT_METADATA_FLOOR:
            errors.append(
                f"RUN_CONTRACT_METADATA_FLOOR: FAIL — "
                f"metadata count {len(metadata_files)} < absolute floor {RUN_CONTRACT_METADATA_FLOOR}. "
                f"Ensure sprint produces sufficient metadata files. "
                f"Only emergency_blocker_bundle: true may bypass this floor."
            )

        # New check (run047): Contract itself cannot set min_metadata_count below the base floor.
        # This prevents regression where a run-specific contract lowers the floor
        # (as run046 did with min_metadata_count: 3). Even if the bundle has 35 files,
        # a non-compliant contract must FAIL so the contract is repaired before use.
        if not emergency_blocker and min_metadata_count < RUN_CONTRACT_METADATA_FLOOR:
            errors.append(
                f"RUN_CONTRACT_MINIMUM_NOT_BELOW_BASE: FAIL — "
                f"contract min_metadata_count={min_metadata_count} is below "
                f"RUN_CONTRACT_METADATA_FLOOR={RUN_CONTRACT_METADATA_FLOOR}. "
                f"A run contract may not lower the metadata floor below the project standard. "
                f"Set min_metadata_count >= {RUN_CONTRACT_METADATA_FLOOR} or use "
                f"emergency_blocker_bundle: true only for documented blocked/failed bundles. "
                f"(This check prevents run046-style contract regression from passing in future sessions.)"
            )

        # New check (run048): Full-sprint contracts with min_metadata_count >= 80
        # must name at least REQUIRED_METADATA_DEPTH_MINIMUM_NAMED specific
        # required_metadata_files. This prevents contracts like run047 that have
        # high metadata counts but name only 4 generic files (git-log, etc.),
        # giving no meaningful evidence depth assurance.
        # Use test_contract: true for test/legacy contracts to bypass.
        # Reject test_contract: true on real sprint contracts (contract_id matching run\d+)
        import re as _re
        contract_id = contract.get("contract_id", "")
        if contract.get("test_contract", False) and _re.match(r"run\d+", contract_id):
            errors.append(
                f"TEST_CONTRACT_MISUSE: FAIL — contract_id '{contract_id}' matches run\\d+ pattern "
                f"but has test_contract: true. Real sprint contracts must not use test_contract. "
                f"Use historical_contract: true for legacy contracts that predate depth requirements."
            )

        if (not emergency_blocker
                and not contract.get("test_contract", False)
                and not contract.get("historical_contract", False)
                and min_metadata_count >= 80
                and len(required_metadata_files) < REQUIRED_METADATA_DEPTH_MINIMUM_NAMED):
            errors.append(
                f"REQUIRED_METADATA_DEPTH: FAIL — "
                f"contract min_metadata_count={min_metadata_count} "
                f"but only {len(required_metadata_files)} required_metadata_files "
                f"specified (minimum {REQUIRED_METADATA_DEPTH_MINIMUM_NAMED} required "
                f"for full-sprint contracts). "
                f"Add meaningful named required_metadata_files to this contract, or set "
                f"test_contract: true for test/validation contracts."
            )

        # Check contract-in-bundle
        if require_contract_in_bundle and contract_repo_path:
            if contract_repo_path not in repo_files:
                errors.append(f"Contract file not found in bundle repo/: {contract_repo_path}")

        # Check manifest presence
        if require_manifest:
            if "bundle-manifest.yaml" not in metadata_files:
                errors.append("Required bundle-manifest.yaml not found in metadata")

        # Check git status cleanliness
        # Rule: Dirty git-status-final.txt ALWAYS causes FAIL unless emergency_blocker_bundle: true.
        # require_clean_git: false only suppresses the "no git status file found" error.
        # It does NOT bypass the dirty-git check when the file is present and dirty.
        clean, msg = check_git_status_clean(metadata_files_content)
        if clean is None:
            # No git status file found in bundle
            if require_clean_git:
                errors.append(f"Git cleanliness check FAILED: {msg}")
            else:
                warnings.append(f"Git status file not found in bundle (require_clean_git: false): {msg}")
        elif not clean:
            if emergency_blocker:
                warnings.append(f"Git dirty (allowed — emergency_blocker_bundle: true): {msg}")
            else:
                errors.append(
                    f"Git cleanliness check FAILED: {msg} "
                    f"(dirty git fails even when require_clean_git: false; "
                    f"use emergency_blocker_bundle: true only for explicitly blocked/failed bundles)"
                )

        # Check for PENDING markers in metadata files and repo current-state files
        pending_hits = []
        repo_pending_hits = []
        closure_contradiction_hits = []
        if no_pending:
            pending_hits = check_no_pending_reports(metadata_files_content)
            for fname, pattern in pending_hits:
                errors.append(f"PENDING marker in metadata file '{fname}': {pattern!r}")
            repo_pending_hits = check_repo_current_state_pending(zf)
            for repo_file, pattern in repo_pending_hits:
                errors.append(
                    f"Sprint-in-progress PENDING marker in repo file '{repo_file}': {pattern!r} "
                    f"— see docs/current-state-and-evidence-authority.md"
                )
            closure_contradiction_hits = check_closure_contradictions(metadata_files_content)
            for msg in closure_contradiction_hits:
                errors.append(msg)

        identity_hits = check_metadata_identity(
            metadata_files_content,
            require_identity=require_metadata_identity,
        )
        for msg in identity_hits:
            errors.append(msg)

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
    if normal_pass_min > 0:
        depth_status = "FAIL" if metadata_depth_fail else "PASS"
        print(f"NORMAL_PASS_METADATA_DEPTH ({depth_status}): {len(metadata_files)}/{normal_pass_min}")
    floor_fail = not emergency_blocker and len(metadata_files) < RUN_CONTRACT_METADATA_FLOOR
    floor_status = "FAIL" if floor_fail else "PASS"
    print(f"RUN_CONTRACT_METADATA_FLOOR ({floor_status}): {len(metadata_files)}/{RUN_CONTRACT_METADATA_FLOOR}")
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
        total_pending = len(pending_hits) + len(repo_pending_hits)
        pending_status = "PASS" if total_pending == 0 else "FAIL"
        print(f"No-PENDING check ({pending_status}): {len(pending_hits)} metadata PENDING + "
              f"{len(repo_pending_hits)} repo current-state PENDING marker(s)")
        if closure_contradiction_hits:
            print(f"Closure-contradiction check (FAIL): {len(closure_contradiction_hits)} contradiction(s)")
        else:
            print("Closure-contradiction check (PASS): no proof/verdict/summary contradictions")
    identity_status = "PASS"
    if 'identity_hits' in locals() and identity_hits:
        identity_status = "FAIL"
    print(f"Metadata identity check ({identity_status})")
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
