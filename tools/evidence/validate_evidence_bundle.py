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
import hashlib
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
    # R57: SHA-keyed PENDING markers — final verdict must not contain these
    # before the actual SHA is known. These appear when a verdict is written
    # before the 2-pass bundle protocol completes. (IV-R56-003/004)
    "BUNDLE_VALIDATION_PASS_2_SHA: PENDING",
    "BUNDLE_VALIDATION_PASS_1_SHA: PENDING",
    "TO BE UPDATED AFTER BUNDLE",
    "PENDING — building evidence bundle",
    # Gate/sprint status markers — sprint must be COMPLETE before final bundle
    # Catches markdown table rows like "| Gate 19 | ... | IN PROGRESS |"
    # and YAML-style "| IN_PROGRESS |" table entries.
    # P-EVID-002: final bundles must not contain IN_PROGRESS gate status.
    "| IN PROGRESS |",
    "| IN_PROGRESS |",
    # R37: Placeholder stub metadata — prevents R36-style evidence-depth caveat
    # where metadata files contained only "placeholder: true" instead of real content.
    "placeholder: true",
    # R38: Status-only stubs — files that contain only a status/result line
    # without substantive evidence content (outcome, evidence-path, or analysis).
    "status: pending",
    "status: stub",
    "result: PENDING",
    # R69: Source-commit proof pending markers (IV-R69-001) — source-commit-proof.txt
    # must not contain PENDING_PASS2_SHA_COMMIT or PENDING_FINAL_COMMIT. These tokens
    # indicate the proof was never updated with the actual final commit SHA after the
    # pass-2 bundle was built and the final commit was created.
    "PENDING_PASS2_SHA_COMMIT",
    "PENDING_FINAL_COMMIT",
    "PENDING_PASS2_COMMIT",
    # R71: Outer delivery package SHA must not appear as PENDING inside inner evidence ZIP.
    # Inner ZIP cannot know the outer package SHA (outer is built after inner).
    # Use: DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative
    "DELIVERY_PACKAGE_SHA: PENDING",
]

# R38: Minimum meaningful content threshold for metadata files.
# Files below this byte count are likely stubs that passed count checks
# but lack real evidence. Exemptions: git-status-final.txt and similar
# system-generated files that are legitimately short.
METADATA_MINIMUM_CONTENT_BYTES = 50

# Files exempt from the minimum content depth check because they are
# legitimately short (system-generated or fixed-format).
METADATA_DEPTH_EXEMPT_FILES = frozenset({
    "git-status-final.txt",
    "git-status.txt",
    "bundle-manifest.yaml",
    "git-log.txt",
    "final-bundle-validation-proof.txt",
    "validation-command-log.txt",
})

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


def check_repo_reports_pending(zf):
    """R46: Scan repo/reports/<RUN>/final-verdict.md files for PENDING marker patterns.

    The R45 post-mortem revealed that a bundle was shipped with
    'BUNDLE_VALIDATION: PENDING' inside repo/reports/r45/final-verdict.md because
    the bundle was built before the final-verdict was updated.  The existing
    check_no_pending_reports() only scans bundle-metadata/ files; this function
    closes the gap by also scanning every repo/reports/*/final-verdict.md entry.

    To avoid false positives from historical references (e.g. "- BUNDLE_VALIDATION:
    PENDING forward-documented" in R32), only lines that begin with the pattern
    (optionally preceded by whitespace, but NOT by a list marker like "- ") are
    treated as genuine status lines.

    Returns a list of (zip_path, matched_pattern) tuples for any hits.
    """
    # Patterns checked as standalone status lines (not as markdown list references)
    STATUS_LINE_PATTERNS = [
        "BUNDLE_VALIDATION: PENDING",
        "BUNDLE_VALIDATION: [PENDING]",
        # R57: SHA-keyed PENDING markers in final verdict lines (IV-R56-003/004)
        "BUNDLE_VALIDATION_PASS_2_SHA: PENDING",
        "BUNDLE_VALIDATION_PASS_1_SHA: PENDING",
        "TO BE UPDATED AFTER BUNDLE",
        "PENDING — building evidence bundle",
        "validation_status: PENDING",
        # R71: Outer delivery package SHA must not be PENDING inside inner evidence ZIP.
        "DELIVERY_PACKAGE_SHA: PENDING",
    ]

    hits = []
    all_entries = zf.namelist()
    for entry in all_entries:
        # Match repo/reports/<anything>/final-verdict.md (one subdirectory level)
        if not entry.startswith("repo/reports/"):
            continue
        parts = entry.split("/")
        # Expected: ["repo", "reports", "<run>", "final-verdict.md"]
        if len(parts) != 4:
            continue
        if parts[3] != "final-verdict.md":
            continue
        try:
            content = zf.read(entry).decode("utf-8", errors="replace")
        except Exception:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            # Skip lines that are markdown list items (start with "- " or "* ")
            # These are documentation references, not live status lines.
            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("# "):
                continue
            for pattern in STATUS_LINE_PATTERNS:
                if pattern in stripped:
                    hits.append((entry, pattern))
                    break  # one hit per file is enough
            else:
                continue
            break  # already found a hit in this file
    return hits


def check_artifact_inventory(zf):
    """R47: Verify that package-artifact-manifest.yaml claims match actual ZIP entries.

    The R46 post-mortem revealed that build_evidence_bundle.py silently omitted
    bundle-metadata/package-artifacts/ subdirectory files because the builder only
    iterated top-level files. The validator passed because check_package_proof_present()
    only checked for the manifest text file, not for actual artifact bytes.

    This function closes that gap:
    1. Parse bundle-metadata/package-artifact-manifest.yaml to find claimed artifact filenames.
    2. For each claimed .whl / .tar.gz / .nupkg, verify the file exists in the ZIP.
    3. If a SHA-256 is associated with the artifact, validate it against actual bytes.

    Returns a list of error strings. Empty list means PASS.
    """
    ARTIFACT_EXTENSIONS = (".whl", ".tar.gz", ".nupkg")
    MANIFEST_ENTRY = "bundle-metadata/package-artifact-manifest.yaml"

    all_entries = set(zf.namelist())

    if MANIFEST_ENTRY not in all_entries:
        return []  # No manifest — nothing to check (check_package_proof_present handles the missing-manifest case)

    try:
        manifest_text = zf.read(MANIFEST_ENTRY).decode("utf-8", errors="replace")
    except Exception:
        return ["ARTIFACT_INVENTORY: could not read package-artifact-manifest.yaml"]

    errors = []

    # Extract claimed artifact filenames and their SHA-256 values from the manifest.
    # Manifest formats supported (line-by-line scan, not strict YAML parser):
    #   YAML list style (R49+):
    #     "  - file: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl"
    #     "    sha256: <64-hex-hash>"
    #   Text/markdown style (R46-R48):
    #     "  - aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl"
    #     "  SHA-256: <hash>"
    #   Inline style:
    #     "FODS wheel: aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl"
    # We scan each line for a token ending with a known extension, then look for
    # either "sha256: <hash>" (YAML) or "SHA-256: <hash>" (text) on subsequent lines.

    claimed_artifacts = []  # list of (filename, sha256_or_None)
    last_filename = None
    for line in manifest_text.splitlines():
        stripped = line.strip()
        # Find artifact filenames in the line
        for token in stripped.replace(",", " ").split():
            for ext in ARTIFACT_EXTENSIONS:
                if token.endswith(ext) and "/" not in token:
                    last_filename = token
                    claimed_artifacts.append((token, None))
                    break
        # Find SHA-256 values on lines following artifact filenames.
        # Accepts both uppercase text format ("SHA-256: <hash>") and
        # lowercase YAML format ("sha256: <hash>") — R50 fix for manifest parsing.
        sha_match = re.search(r'(?:SHA-256|sha256):\s*([0-9a-fA-F]{64})', stripped)
        if sha_match and last_filename:
            sha256 = sha_match.group(1).lower()
            # Associate this SHA with the most recently seen filename (update last entry)
            for i in range(len(claimed_artifacts) - 1, -1, -1):
                if claimed_artifacts[i][0] == last_filename:
                    claimed_artifacts[i] = (last_filename, sha256)
                    break

    # R57: Check for truncated (non-64-char) SHA values in manifest.
    # wheel_sha256: values that are 32 chars are MD5 length — not SHA-256.
    # These would be silently skipped by the 64-char regex above (IV-R56-007).
    for line in manifest_text.splitlines():
        stripped = line.strip()
        # Match any sha256 key with a short hex value (not exactly 64 chars)
        short_sha = re.search(r'(?:SHA-256|sha256|wheel_sha256):\s*([0-9a-fA-F]{16,63})\b', stripped)
        if short_sha:
            val = short_sha.group(1)
            if len(val) != 64:
                errors.append(
                    f"ARTIFACT_SHA_TRUNCATED: manifest contains SHA value of length {len(val)} "
                    f"(expected 64 for SHA-256): {val!r}. "
                    f"This is likely an MD5 or truncated hash. Recompute using hashlib.sha256(). "
                    f"(IV-R56-007 R57 guard)"
                )

    if not claimed_artifacts:
        return []  # Manifest exists but names no artifacts — nothing to validate

    # Deduplicate while preserving first SHA if multiple lines reference same file
    seen = {}
    deduped = []
    for fname, sha in claimed_artifacts:
        if fname not in seen:
            seen[fname] = sha
            deduped.append((fname, sha))
        elif sha and not seen[fname]:
            seen[fname] = sha
            deduped = [(f, seen[f] if f == fname else s) for f, s in deduped]
    claimed_artifacts = deduped

    # Check each claimed artifact actually exists in the ZIP
    # Accept under bundle-metadata/package-artifacts/<name> or bundle-metadata/<name>
    for fname, expected_sha in claimed_artifacts:
        candidate_paths = [
            f"bundle-metadata/package-artifacts/{fname}",
            f"bundle-metadata/{fname}",
        ]
        found_path = None
        for cp in candidate_paths:
            if cp in all_entries:
                found_path = cp
                break

        if found_path is None:
            errors.append(
                f"ARTIFACT_INVENTORY: manifest claims '{fname}' but it is absent from bundle ZIP. "
                f"Checked: {candidate_paths}. "
                f"Root cause: build_evidence_bundle.py previously omitted subdirectory files. "
                f"Fix: ensure artifacts are in --metadata-dir and builder includes subdirectories (R47 fix)."
            )
            continue

        # Validate SHA-256 if manifest provides it
        if expected_sha:
            try:
                artifact_bytes = zf.read(found_path)
                actual_sha = hashlib.sha256(artifact_bytes).hexdigest()
                if actual_sha != expected_sha:
                    errors.append(
                        f"ARTIFACT_SHA_MISMATCH: '{fname}' SHA-256 mismatch. "
                        f"manifest={expected_sha} actual={actual_sha}. "
                        f"Artifact may have been rebuilt since manifest was written."
                    )
            except Exception as e:
                errors.append(f"ARTIFACT_INVENTORY: could not read '{found_path}' for SHA check: {e}")

    return errors


def check_installed_artifact_policy(contract: dict, metadata_files_content: dict, zf, verdict_content: str = "") -> "list[str]":
    """R54 Lane 3: Enforce installed_artifact_policy contract field.

    Policy values:
      none (default): verdict must not contain installed-artifact baseline tokens.
      external_ref: manifest must include prior_bundle_sha256, prior_bundle_filename, and a verification statement.
      self_contained: manifest must exist AND actual .whl/.tar.gz/.nupkg files in bundle-metadata/package-artifacts/.

    Returns a list of error strings. Empty list means PASS.
    """
    policy = contract.get("installed_artifact_policy", "none")
    errors: list[str] = []

    INSTALLED_BASELINE_TOKENS = [
        "INSTALLED_ARTIFACT_BASELINE_CLEAN",
        "INSTALLED_ARTIFACT_BASELINE",
        "SELF_CONTAINED_ARTIFACT",
    ]
    verdict_upper = verdict_content.upper() if verdict_content else ""

    if policy == "none":
        # Verdict must not claim installed-artifact baseline
        for token in INSTALLED_BASELINE_TOKENS:
            if token in verdict_upper:
                errors.append(
                    f"ARTIFACT_POLICY_VIOLATION: installed_artifact_policy is 'none' but "
                    f"verdict contains clean-baseline token {token!r}. "
                    f"Use installed_artifact_policy: external_ref or self_contained if artifacts are claimed."
                )
                break

    elif policy == "external_ref":
        # Manifest must include prior SHA and prior filename
        manifest_content = metadata_files_content.get("package-artifact-manifest.yaml", "")
        if not manifest_content:
            errors.append(
                "ARTIFACT_POLICY_EXTERNAL_REF: installed_artifact_policy is 'external_ref' but "
                "bundle-metadata/package-artifact-manifest.yaml is missing. "
                "External ref policy requires a manifest with prior_bundle_sha256, "
                "prior_bundle_filename, and a verification statement."
            )
        else:
            # Check for keys (field: value format — comments with the key name don't count)
            required_fields = ["prior_bundle_sha256", "prior_bundle_filename"]
            missing = [f for f in required_fields if (f + ":") not in manifest_content]
            if missing:
                errors.append(
                    f"ARTIFACT_POLICY_EXTERNAL_REF: manifest is missing required fields: {missing}. "
                    f"A vague reference (e.g., 'see R51 manifest') is not sufficient. "
                    f"Provide exact prior_bundle_sha256 and prior_bundle_filename."
                )

    elif policy == "self_contained":
        # Actual artifact files must be in bundle
        ARTIFACT_EXTENSIONS = (".whl", ".tar.gz", ".nupkg")
        all_entries = set(zf.namelist())
        artifact_entries = [
            e for e in all_entries
            if e.startswith("bundle-metadata/package-artifacts/")
            and any(e.endswith(ext) for ext in ARTIFACT_EXTENSIONS)
        ]
        if not artifact_entries:
            errors.append(
                "ARTIFACT_POLICY_SELF_CONTAINED: installed_artifact_policy is 'self_contained' but "
                "no .whl, .tar.gz, or .nupkg files found under bundle-metadata/package-artifacts/. "
                "Self-contained policy requires actual artifact files in the bundle."
            )

    return errors


def check_no_pending_reports(metadata_files_content):
    """Scan all metadata files for PENDING marker patterns.

    Returns a list of (filename, matched_pattern) tuples for any file that
    contains a PENDING marker. An empty list means no PENDING markers found.
    """
    # Files that naturally reference historical PENDING states (e.g., commit messages
    # in git-log.txt) and should not be scanned for PENDING markers.
    PENDING_SCAN_SKIP_FILES = frozenset({
        "git-log.txt",
        "git-status-final.txt",
        "git-status.txt",
    })
    hits = []
    for fname, content in metadata_files_content.items():
        if fname in PENDING_SCAN_SKIP_FILES:
            continue
        for pattern in PENDING_MARKER_PATTERNS:
            if pattern in content:
                hits.append((fname, pattern))
                break  # one hit per file is enough
    return hits


def check_metadata_content_depth(metadata_files_content):
    """Check that metadata files have minimum substantive content.

    R38: Catches status-only stub files that pass pending-pattern checks
    but lack real evidence (e.g., a 30-byte file with just 'status: pass').
    Returns a list of (filename, reason) tuples for shallow files.
    """
    hits = []
    for fname, content in metadata_files_content.items():
        if fname in METADATA_DEPTH_EXEMPT_FILES:
            continue
        # Skip test-padding metadata files (metadata-pad-NNN.md, meta_NN.txt)
        if fname.startswith("metadata-pad-") or fname.startswith("meta_"):
            continue
        byte_count = len(content.encode("utf-8"))
        if byte_count < METADATA_MINIMUM_CONTENT_BYTES:
            hits.append((fname, f"only {byte_count} bytes (minimum {METADATA_MINIMUM_CONTENT_BYTES})"))
    return hits


def check_authoritative_test_result_present(metadata_files_content):
    """Check that at least one metadata file contains AUTHORITATIVE_TEST_RESULT.

    P-EVID-003: validation-command-log.txt (or any metadata file) must contain
    the AUTHORITATIVE_TEST_RESULT line so test counts are unambiguous across
    the bundle. Called when --check-no-pending is active.

    Returns a list of error strings (empty if the check passes).
    """
    for content in metadata_files_content.values():
        if "AUTHORITATIVE_TEST_RESULT" in content:
            return []
    return [
        "P-EVID-003 VIOLATION: No metadata file contains AUTHORITATIVE_TEST_RESULT. "
        "Add 'AUTHORITATIVE_TEST_RESULT: N passed, M skipped' to validation-command-log.txt."
    ]


# R49: Stale placeholder patterns in proof/closeout files. These indicate a file was
# written as a stub or in-progress placeholder and never updated with real evidence.
# Checked against final-bundle-validation-proof.txt when --check-no-pending is active.
PROOF_FILE_PLACEHOLDER_PATTERNS = [
    # R48 original patterns
    "(updated after",
    "to be recorded",
    "STATUS: PASS 2 IN PROGRESS",
    "pass 2 in progress",
    "SHA-256: (updated",
    "SHA: (updated",
    "final SHA to be recorded",
    # R50: additional patterns missed in R49 (stale computed-after placeholders)
    "computed after pass 2 build",
    "computed after pass 2",
    "pass 2 sha to follow",
    "entries: (computed",
    "size: (computed",
    "validation: (computed",
    # R51: patterns from R50 bundle proof placeholder (missed by R50 validator)
    "PLACEHOLDER",
    "will be replaced",
    "candidate validation",
    "IN PROGRESS",
    "TBD",
    "sha to follow",
    "updated after",
    # R59 Train C: proof file must not claim PENDING validation result
    "BUNDLE_VALIDATION: PENDING",
    "validation: pending",
]


_AUTO_PROOF_TRANSIENT_PLACEHOLDER = (
    "placeholder \u2014 will be replaced after candidate validation"
)

# R68 Train E: Closeout-hygiene tokens that must NOT appear in final reports.
# These indicate incomplete closeout — the report was written as a template but
# never filled in with actual results before bundle build.
CLOSEOUT_HYGIENE_TOKENS = [
    "[to be filled]",
    "[to be filled at closeout]",
    "[commit sha to be filled]",
    "post-bundle authoritative count: tbd",
    "unknown (3 —",   # unresolved unknown failures in python-tests-summary
]

# Final report filenames scanned for closeout-hygiene tokens.
# These are repo files where incomplete templates cause silent close-out failure.
CLOSEOUT_HYGIENE_REPORT_FILES = frozenset({
    "final-independent-verification.md",
    "python-tests-summary.txt",
    "lane-ownership.md",
    "final-verdict.md",
})


def check_closeout_hygiene_tokens(zf):
    """R68 Train E: Scan final report files for incomplete-closeout tokens.

    Detects the R67 defect class where reports were written as templates
    (e.g. final-independent-verification.md with '[to be filled]') and never
    updated before bundle build.

    Scans:
    - repo/reports/<run>/final-independent-verification.md
    - bundle-metadata/python-tests-summary.txt
    - repo/reports/<run>/lane-ownership.md
    - repo/reports/<run>/final-verdict.md (supplements check_repo_reports_pending)

    Returns a list of (zip_path, token) tuples for any hits.
    """
    hits = []
    for entry in zf.namelist():
        parts = entry.replace("\\", "/").split("/")
        # Match either bundle-metadata/<file> or repo/reports/<run>/<file>
        fname = parts[-1]
        if fname not in CLOSEOUT_HYGIENE_REPORT_FILES:
            continue
        try:
            content = zf.read(entry).decode("utf-8", errors="replace").lower()
        except Exception:
            continue
        for token in CLOSEOUT_HYGIENE_TOKENS:
            if token in content:
                hits.append((entry, token))
                break  # one hit per file
    return hits


def check_source_commit_proof_no_pending(metadata_files_content):
    """R69 Train D: Check that source-commit-proof.txt has no PENDING_PASS2_SHA_COMMIT.

    Detects the IV-R69-001 defect class where source-commit-proof.txt was written
    before the final pass-2 commit and never updated with the actual commit SHA.
    The token PENDING_PASS2_SHA_COMMIT must be replaced with the real git commit SHA.

    Also caught by check_no_pending_reports via PENDING_MARKER_PATTERNS, but this
    dedicated function provides a clearer error message.

    Returns a list of error strings (empty if the check passes).
    """
    SOURCE_COMMIT_TOKENS = [
        "PENDING_PASS2_SHA_COMMIT",
        "PENDING_FINAL_COMMIT",
        "PENDING_PASS2_COMMIT",
    ]
    content = metadata_files_content.get("source-commit-proof.txt", "")
    if not content:
        return []  # File absent — not our check to fail
    errors = []
    for token in SOURCE_COMMIT_TOKENS:
        if token in content:
            errors.append(
                f"R69: source-commit-proof.txt contains prohibited token {token!r}. "
                f"Replace with actual final commit SHA (IV-R69-001 defect class). "
                f"The source-commit-proof must be updated after the final git commit."
            )
    return errors


def check_inner_verdict_delivery_sha_authority(zf) -> "list[str]":
    """R71 Train B: Enforce layered proof authority for delivery package SHA.

    The inner evidence ZIP cannot know the outer delivery package SHA — the outer
    package is built after the inner ZIP, so any attempt to record it inside creates
    a circular dependency (IV-R71-001, IV-R71-002).

    Rules (apply ONLY to the current sprint's final-verdict — not historical ones):
      - Inner final-verdict MUST NOT contain 'DELIVERY_PACKAGE_SHA: PENDING'
        (already caught by check_repo_reports_pending STATUS_LINE_PATTERNS, but
        this check adds a clearer error message).
      - Inner final-verdict MUST NOT contain 'DELIVERY_PACKAGE_SHA: <64-char hex>'
        (a concrete outer package SHA inside the inner ZIP is always stale).
      - Inner final-verdict MAY contain 'DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative'
        (semantic label delegating authority to the delivery manifest).
      - Inner final-verdict MAY omit 'DELIVERY_PACKAGE_SHA:' entirely.

    Historical reports from prior sprints (e.g. repo/reports/r65/final-verdict.md) are
    excluded — they legitimately contain concrete SHAs from when those sprints were delivered.

    Returns a list of error strings. Empty list means PASS.
    """
    import re
    errors = []
    all_entries = zf.namelist()

    # Detect current sprint's run_number from bundle-metadata/sprint-id.txt
    current_run = None
    sprint_id_candidates = [
        e for e in all_entries if e.endswith("sprint-id.txt")
    ]
    for candidate in sprint_id_candidates:
        try:
            sprint_id_content = zf.read(candidate).decode("utf-8", errors="replace").strip()
            # Extract run number: "FORMAT-FACTORY-R71-..." -> "r71"
            m = re.search(r"-R(\d+)-", sprint_id_content, re.IGNORECASE)
            if m:
                current_run = f"r{m.group(1).lower()}"
                break
        except Exception:
            continue

    for entry in all_entries:
        if not entry.startswith("repo/reports/"):
            continue
        parts = entry.split("/")
        if len(parts) != 4 or parts[3] != "final-verdict.md":
            continue
        sprint_dir = parts[2]  # e.g. "r71"

        # Only enforce on the current sprint's final-verdict
        # Historical reports are excluded — they have valid concrete SHAs from prior deliveries
        if current_run and sprint_dir.lower() != current_run.lower():
            continue

        try:
            content = zf.read(entry).decode("utf-8", errors="replace")
        except Exception:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("# "):
                continue
            if not stripped.startswith("DELIVERY_PACKAGE_SHA:"):
                continue
            # Line is a DELIVERY_PACKAGE_SHA status line — check value
            value = stripped[len("DELIVERY_PACKAGE_SHA:"):].strip()
            if value == "PENDING":
                errors.append(
                    f"R71: {entry} contains 'DELIVERY_PACKAGE_SHA: PENDING'. "
                    f"Inner evidence ZIP cannot own the outer delivery package SHA. "
                    f"Use: DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative"
                )
            elif re.fullmatch(r"[0-9a-f]{64}", value):
                errors.append(
                    f"R71: {entry} contains a concrete outer delivery package SHA "
                    f"({value[:16]}...) inside the inner evidence ZIP. "
                    f"The outer package SHA cannot be known when the inner ZIP is built. "
                    f"Use: DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative"
                )
    return errors


def check_negative_sidecar_proofs_present(metadata_files_content):
    """R69 Train D: Check that negative sidecar proof files are present and confirmed.

    The missing-sidecar-negative-proof.txt and wrong-sidecar-negative-proof.txt
    prove the sidecar protocol is fail-closed. Both must be present in metadata
    and contain evidence of the expected failures.

    Returns a list of warning strings (not hard errors — some legacy contracts
    don't require these files, but R69+ sprints should include them).
    """
    warnings = []
    for fname, expected_token in [
        ("missing-sidecar-negative-proof.txt", "BUNDLE_VALIDATION: FAIL"),
        ("wrong-sidecar-negative-proof.txt", "SIDECAR_PROOF_VALIDATION: FAIL"),
    ]:
        content = metadata_files_content.get(fname, "")
        if not content:
            warnings.append(
                f"R69: {fname} not found in bundle metadata. "
                f"Negative sidecar proofs are required to demonstrate fail-closed behavior."
            )
        elif expected_token not in content and "CONFIRMED" not in content:
            warnings.append(
                f"R69: {fname} is present but does not contain {expected_token!r} or CONFIRMED. "
                f"The file may be a stub without actual negative proof."
            )
    return warnings


def check_proof_file_finality(metadata_files_content):
    """R49: Check that final-bundle-validation-proof.txt contains no stale placeholders.

    Detects the R48 caveat: proof file was written as a placeholder before the 2-pass
    build was complete. Catches strings like '(updated after pass 2 build)',
    'to be recorded', 'IN PROGRESS', etc.

    Called when --check-no-pending is active.

    R52 note: The auto_proof builder writes a transient placeholder during Pass 1
    ("PLACEHOLDER — will be replaced after candidate validation"). This exact text
    is excluded because the builder replaces it with actual metrics before Pass 3,
    which is the only pass that produces a final bundle.

    Returns a list of error strings (empty if the check passes).
    """
    proof_content = metadata_files_content.get("final-bundle-validation-proof.txt", "")
    if not proof_content:
        # File absent: caught by required_metadata_files check — not our job here.
        return []
    # R52: Skip if this is the exact auto-proof transient placeholder written during Pass 1.
    # By Pass 3 (final build), the builder has replaced this with actual metrics.
    if proof_content.strip().lower() == _AUTO_PROOF_TRANSIENT_PLACEHOLDER:
        return []

    hits = []
    lower_content = proof_content.lower()
    for pattern in PROOF_FILE_PLACEHOLDER_PATTERNS:
        if pattern.lower() in lower_content:
            hits.append(
                f"PROOF_FILE_PLACEHOLDER: final-bundle-validation-proof.txt contains "
                f"unresolved placeholder {pattern!r} — update proof file with actual "
                f"bundle path, SHA-256, size, entries, and validation output before "
                f"claiming clean closeout."
            )
            break  # one error per file is sufficient
    return hits


def check_proof_sha_consistency(metadata_files_content, bundle_path):
    """R52 Lane 2A: Check that the final-bundle-validation-proof.txt SHA/size
    values describe an actual bundle whose bytes match a claimed final SHA.

    The fundamental problem: a file inside a ZIP cannot contain the SHA-256 of
    that same ZIP (self-referential). The acceptable approach:

    Approach A (sidecar): Proof inside bundle records the PASS 1 SHA only. The
    authoritative final SHA is in a sidecar file OUTSIDE the ZIP. This function
    issues a warning if it detects the proof claims a SHA that clearly does not
    match the actual bundle bytes being validated.

    Approach B (internal, approximate): If the proof SHA matches the actual
    bundle SHA, it can only be correct if the proof was written BEFORE final
    bundle build and the bundle was rebuilt deterministically. We warn but do
    not fail, since this is mathematically impossible for a proper final proof.

    Returns a list of warning strings (not errors) for SHA mismatches.
    """
    warnings = []
    proof_content = metadata_files_content.get("final-bundle-validation-proof.txt", "")
    if not proof_content:
        return warnings

    # Parse claimed SHA-256 values from the proof file
    claimed_shas = re.findall(r"\bSHA-256:\s*([0-9a-f]{64})\b", proof_content, re.IGNORECASE)
    if not claimed_shas:
        return warnings  # No SHA claims to check

    # Compute actual bundle SHA
    try:
        actual_sha = hashlib.sha256(Path(bundle_path).read_bytes()).hexdigest()
    except Exception:
        return warnings

    # The proof may list multiple SHAs (pass 1 + pass 2). We check if the
    # LAST claimed SHA matches the actual bundle. If no SHA matches the actual
    # bundle, it is likely a stale/recursive proof.
    if actual_sha not in claimed_shas:
        warnings.append(
            f"PROOF_SHA_SIDECAR_RECOMMENDED: final-bundle-validation-proof.txt claims SHA(s) "
            f"{claimed_shas} but actual bundle SHA is {actual_sha}. "
            f"A file inside a ZIP cannot contain the SHA of the ZIP containing it. "
            f"Use an external sidecar proof file (outside the ZIP) for the authoritative final SHA, "
            f"or record only the PASS 1 SHA inside the bundle and the final SHA outside."
        )
    return warnings


# R51 Lane 1C: Unresolved closeout text patterns in final verdicts.
# These indicate a verdict was written mid-process and not updated to final form.
VERDICT_UNRESOLVED_CLOSEOUT_PATTERNS = [
    "pass 2 sha to follow",
    "candidate validation",
    "computed after",
    "sha to follow",
    "entries to follow",
    "size to follow",
    "validation to follow",
    "will be updated after",
    "will be replaced after build",
    "hash pending",
]

# R51 Lane 1C: Keywords that indicate a verdict claims clean/complete closure.
VERDICT_CLEAN_CLOSURE_KEYWORDS = [
    "COMPLETE",
    "CLEAN",
    "BASELINE",
    "RC_",
    "_RC",
    "CLOSEOUT",
    "POC_PROVEN",
    "PASS",
]


def check_verdict_unresolved_closeout(zf):
    """R51 Lane 1C: Detect unresolved closeout text inside bundled final verdicts.

    Catches patterns like 'pass 2 SHA to follow', 'to follow', 'candidate validation'
    that indicate a verdict was written before the 2-pass bundle was complete.

    Returns a list of error strings (empty if check passes).
    """
    errors = []
    for entry in zf.namelist():
        if not entry.startswith("repo/reports/"):
            continue
        parts = entry.split("/")
        if len(parts) != 4 or parts[3] != "final-verdict.md":
            continue
        try:
            content = zf.read(entry).decode("utf-8", errors="replace")
        except Exception:
            continue
        lower = content.lower()
        for pattern in VERDICT_UNRESOLVED_CLOSEOUT_PATTERNS:
            if pattern.lower() in lower:
                errors.append(
                    f"VERDICT_UNRESOLVED_CLOSEOUT: '{entry}' contains unresolved "
                    f"closeout text {pattern!r} — final verdict must be written after "
                    f"2-pass bundle is complete, not before."
                )
                break
    return errors


def check_contract_clean_git_strictness(contract, zf):
    """R51 Lane 1D: Warn when a clean-complete contract uses require_clean_git: false.

    Contracts whose verdict tokens include COMPLETE, BASELINE, RC, CLOSEOUT etc.
    must use require_clean_git: true unless the verdict explicitly contains
    DIRTY_TREE_BLOCKED or similar.

    Returns a list of warning strings (empty if check passes).
    """
    require_clean_git = contract.get("require_clean_git", True)
    if require_clean_git:
        return []

    # Look for a final verdict in the bundle to check its content
    for entry in zf.namelist():
        if not entry.startswith("repo/reports/"):
            continue
        parts = entry.split("/")
        if len(parts) != 4 or parts[3] != "final-verdict.md":
            continue
        try:
            content = zf.read(entry).decode("utf-8", errors="replace")
        except Exception:
            continue
        # Check if verdict claims clean closure
        upper = content.upper()
        # Exempt verdicts that explicitly state DIRTY_TREE or BLOCKED
        if "DIRTY_TREE" in upper or "EVIDENCE_CLOSEOUT_BLOCKED" in upper:
            return []
        for keyword in VERDICT_CLEAN_CLOSURE_KEYWORDS:
            if keyword in upper:
                return [
                    f"CONTRACT_CLEAN_GIT_WEAK: contract has require_clean_git: false "
                    f"but bundled verdict '{entry}' contains clean-closure keyword "
                    f"'{keyword}'. Clean-completion contracts must use "
                    f"require_clean_git: true."
                ]
    return []


COMMAND_LOG_STALE_PATTERNS = [
    # State snapshot ran before final verdict was written — stale pre-final result.
    # Pattern: "STATE_SNAPSHOT: PASS (R49 no_final_verdict)" etc.
    "no_final_verdict",
    # R52: validation log written before bundle was built — contains unfinished closeout text.
    "to be completed in mt",
    "pass 1: pending",
    "pass 2: pending",
    "pending final validation",
    "to be completed",
]

COMMAND_LOG_CANDIDATE_FILES = [
    "validation-command-log.txt",
    "validation-command-log.md",
    "command-log.txt",
]


def check_validation_command_log_freshness(metadata_files_content):
    """R50 Lane 1D: Detect stale pre-final results in the validation command log.

    The R49 closeout failure included 'STATE_SNAPSHOT: PASS (R49 no_final_verdict)'
    in the validation command log — the state snapshot was run before the final verdict
    was written, so the log captured a pre-final sprint state.

    A valid final bundle must have a command log reflecting post-verdict state.
    We detect the token 'no_final_verdict' which appears when state_snapshot.py
    runs before the final verdict file exists.

    Returns a list of error strings (empty if the check passes).
    """
    for candidate in COMMAND_LOG_CANDIDATE_FILES:
        content = metadata_files_content.get(candidate, "")
        if not content:
            continue
        lower = content.lower()
        for pattern in COMMAND_LOG_STALE_PATTERNS:
            if pattern.lower() in lower:
                return [
                    f"COMMAND_LOG_STALE_RESULT: '{candidate}' contains "
                    f"pre-final state snapshot token {pattern!r}. "
                    f"Re-run state_snapshot.py after writing the final verdict, "
                    f"update the command log, and rebuild the bundle."
                ]
        return []  # File found, no stale patterns
    return []  # No command log file present — not our job to require it here


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

    # R42 check (Rule C-LOCAL-002): *_COMPLETE verdict + dirty git tree.
    # A sprint must not claim final completion while git-status-final.txt shows
    # uncommitted changes, unless the verdict is explicitly DIRTY_TREE_BLOCKED or SUPERSEDED.
    git_status_dirty = False
    for candidate in GIT_STATUS_CANDIDATE_FILES:
        text = metadata_files_content.get(candidate, "")
        if text:
            dirty_indicators = [
                "Changes not staged", "Changes to be committed",
                "Untracked files", "modified:", "new file:", "deleted:",
            ]
            for indicator in dirty_indicators:
                if indicator in text:
                    git_status_dirty = True
                    break
            break

    if git_status_dirty:
        for fname in ["final-verdict.md", "final-verdict.txt", "verdict.md"]:
            content = metadata_files_content.get(fname, "")
            if content:
                m = re.search(r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}([A-Z][A-Z0-9_]+)", content, re.IGNORECASE)
                if m:
                    verdict_val = m.group(1)
                    if (verdict_val.endswith("_COMPLETE")
                            and "DIRTY_TREE" not in verdict_val
                            and "SUPERSEDED" not in verdict_val):
                        hits.append(
                            f"DIRTY_TREE_COMPLETE_CONTRADICTION: {fname} has VERDICT: {verdict_val} "
                            "but git-status-final.txt shows uncommitted changes. "
                            "A sprint must not claim *_COMPLETE with a dirty tree (Rule C-LOCAL-002). "
                            "Use *_DIRTY_TREE_BLOCKED or *_PROGRESS_ACCEPTED_CLOSEOUT_SUPERSEDED."
                        )
                break

    return hits


def check_package_proof_present(metadata_files_content, zf):
    """R43/R45: If verdict claims *_POC_READY or *_LOCAL_RC* or *_BASELINE_READY*,
    require package proof artifacts in bundle.

    A bundle claiming POC/RC readiness must contain at minimum one of:
    - bundle-metadata/package-artifact-manifest.yaml
    - repo/reports/r*/package-artifact-manifest.yaml
    - repo/reports/r*/package-proof/ directory entries

    Returns a list of error strings.
    """
    # Verdict suffixes/substrings that require package proof
    REQUIRES_PACKAGE_PROOF = (
        "POC_READY",
        "LOCAL_RC",
        "BASELINE_READY",
        "RELEASE_CANDIDATE",
        "TWO_PRODUCT",
    )

    hits = []
    verdict_val = None
    for fname in ("final-verdict.md", "final-verdict.txt", "verdict.md"):
        content = metadata_files_content.get(fname, "")
        if content:
            m = re.search(r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}([A-Z][A-Z0-9_]+)", content, re.IGNORECASE)
            if m:
                verdict_val = m.group(1)
            break

    if verdict_val is None:
        return hits

    requires_proof = any(kw in verdict_val for kw in REQUIRES_PACKAGE_PROOF)
    if not requires_proof:
        return hits

    # Check for package proof in metadata or repo
    all_entries = set(zf.namelist())
    has_proof = (
        "bundle-metadata/package-artifact-manifest.yaml" in all_entries
        or "bundle-metadata/package-proof-summary.md" in all_entries
        or any("package-artifact-manifest.yaml" in e for e in all_entries)
        or any("package-proof" in e and not e.endswith("/") for e in all_entries)
    )
    if not has_proof:
        matched_kw = next(kw for kw in REQUIRES_PACKAGE_PROOF if kw in verdict_val)
        hits.append(
            f"PACKAGE_PROOF_MISSING: VERDICT is {verdict_val} (contains *_{matched_kw}*) but no "
            f"package-artifact-manifest.yaml or package-proof/ entries found in bundle. "
            f"POC_READY, LOCAL_RC, BASELINE_READY, RELEASE_CANDIDATE, and TWO_PRODUCT verdicts "
            f"require package build proof (R43/R45 Rule)."
        )
    return hits


def _parse_verdict_from_text(content):
    """Parse verdict value from final-verdict.md content, handling all known formats.

    Formats:
    A: inline "VERDICT: VALUE" / "**VERDICT:** VALUE"
    B: "**Verdict:** **VALUE**"
    C: "## Verdict" heading + "`VALUE`" code-block (R51+)
    """
    verdict_val = None
    # Format A/B
    m = re.search(r"(?:^|\n)\s*\*{0,2}(?:VERDICT|Verdict):\*{0,2}\s*\*{0,2}([A-Z][A-Z0-9_]+)\*{0,2}", content)
    if m:
        verdict_val = m.group(1)
    # Format C
    if not verdict_val:
        m = re.search(r"##\s+Verdict\s*\n+\s*`([A-Z][A-Z0-9_]+)`", content)
        if m:
            verdict_val = m.group(1)
    # Sanity: must be a real identifier, not just noise
    if verdict_val and not re.match(r"[A-Z][A-Z0-9_]{3,}", verdict_val):
        verdict_val = None
    return verdict_val


def check_state_verdict_agreement(metadata_files_content, zf):
    """R43/R52: Detect state/verdict disagreement.

    If final-verdict.md (bundle-metadata) claims a *_COMPLETE or *_POC_READY verdict
    but repo/state/current-state.md shows 'unknown' or 'no_final_verdict', the bundle
    is internally inconsistent — the state file was not regenerated after final-verdict
    was written.

    R52 extension: also handles R51's code-block verdict format (## Verdict + `VALUE`).
    R52 extension: also catches INV-003 false blocker — state says final-verdict.md is
    MISSING even though the file exists in the bundle.

    Returns a list of error strings.
    """
    hits = []
    verdict_val = None
    # First look in bundle-metadata/ (legacy path)
    for fname in ("final-verdict.md", "final-verdict.txt", "verdict.md"):
        content = metadata_files_content.get(fname, "")
        if content:
            verdict_val = _parse_verdict_from_text(content)
            break
    # Then scan the bundle's repo/reports/*/final-verdict.md (primary path)
    if verdict_val is None:
        all_entries_pre = set(zf.namelist())
        for entry in sorted(all_entries_pre, reverse=True):  # reverse: latest run first
            if entry.startswith("repo/reports/") and entry.endswith("/final-verdict.md"):
                try:
                    content = zf.read(entry).decode("utf-8", errors="replace")
                    verdict_val = _parse_verdict_from_text(content)
                    if verdict_val:
                        break
                except Exception:
                    pass

    if verdict_val is None:
        # No verdict found in any location — still check for INV-003 false blocker below
        pass

    is_positive_verdict = verdict_val is not None and (
        verdict_val.endswith("_COMPLETE")
        or verdict_val.endswith("_READY")
        or verdict_val.endswith("_PASS")
        or "_COMPLETE_" in verdict_val
        or "_READY_" in verdict_val
    )

    # Read repo/state/current-state.md from the bundle
    state_content = ""
    all_entries = set(zf.namelist())
    for candidate in ("repo/state/current-state.md", "repo/state/current-state.json"):
        if candidate in all_entries:
            try:
                state_content = zf.read(candidate).decode("utf-8", errors="replace")
            except Exception:
                pass
            if state_content:
                break

    if not state_content:
        return hits  # state file not in bundle — skip

    if not is_positive_verdict:
        # Still check for INV-003 false blocker even without a positive verdict
        all_bundle_entries_inv = set(zf.namelist())
        for entry in all_bundle_entries_inv:
            if entry.startswith("repo/reports/") and entry.endswith("/final-verdict.md"):
                run_dir = entry.split("/")[2]
                inv_blocker = f"INV-003: MISSING: reports/{run_dir}/final-verdict.md"
                if inv_blocker in state_content:
                    hits.append(
                        f"STATE_FALSE_INV003_BLOCKER: state/current-state.md reports "
                        f"'{inv_blocker}' but '{entry}' exists in the bundle. "
                        f"The state snapshot was generated before the final-verdict file was present. "
                        f"Regenerate state after writing final-verdict.md."
                    )
        return hits

    # Check if state says unknown or no_final_verdict for the latest sprint.
    # State output format: "**Latest sprint:** R51 - unknown" (hyphen, not em-dash).
    stale_indicators = [
        "no_final_verdict",
        "— unknown",        # em-dash format (older)
        "— no_final_verdict",  # em-dash format (older)
        " - unknown",       # hyphen format (current state_snapshot.py output)
        " - no_final_verdict",  # hyphen format
        ": unknown",
        ": no_final_verdict",
    ]
    state_stale = any(ind in state_content for ind in stale_indicators)
    if state_stale:
        hits.append(
            f"STATE_VERDICT_MISMATCH: final-verdict.md has VERDICT: {verdict_val} "
            f"but state/current-state.md shows 'unknown' or 'no_final_verdict'. "
            f"The state file was not regenerated after the final verdict was written. "
            f"Run: python tools/state/state_snapshot.py (R52 fix: handles code-block verdict format)."
        )

    # R52: Also check for INV-003 false blocker — state says final-verdict.md MISSING
    # but the file exists in the bundle (state was snapshotted before verdict was written).
    all_bundle_entries = set(zf.namelist())
    for entry in all_bundle_entries:
        if entry.startswith("repo/reports/") and entry.endswith("/final-verdict.md"):
            run_dir = entry.split("/")[2]  # e.g. "r51"
            inv_blocker = f"INV-003: MISSING: reports/{run_dir}/final-verdict.md"
            if inv_blocker in state_content:
                hits.append(
                    f"STATE_FALSE_INV003_BLOCKER: state/current-state.md reports "
                    f"'{inv_blocker}' but '{entry}' exists in the bundle. "
                    f"The state snapshot was generated before the final-verdict file was present. "
                    f"Regenerate state after writing final-verdict.md."
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


def validate_bundle(contract_path, bundle_path, strict_git=True, no_pending=False, sidecar_path=None):
    """Validate a bundle zip against a contract."""
    contract = load_contract(contract_path)
    bundle_path = Path(bundle_path)

    if not bundle_path.exists():
        print(f"ERROR: Bundle not found: {bundle_path}")
        print("BUNDLE_VALIDATION: FAIL")
        return False

    required_top_level = contract.get("required_top_level_folders", ["repo", "bundle-metadata"])
    forbidden_patterns = (
        contract.get("forbidden_paths", [])
        + contract.get("forbidden_patterns", [])
        + contract.get("exclude_patterns", [])
    )
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

    # R54 Lane 2: Fail-closed sidecar enforcement (before ZIP is opened)
    sidecar_required_errors = check_sidecar_required(contract, sidecar_path)
    for msg in sidecar_required_errors:
        errors.append(msg)

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
            warnings.append(f"Extra top-level folders (not in required list): {sorted(unexpected)}")

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
        # R42 check (Rule C-LOCAL-003): emergency_blocker_bundle misuse.
        # If emergency_blocker is true, the final verdict in metadata must signal
        # a genuine emergency/blocked/failed state. A normal sprint using
        # emergency_blocker_bundle to get around the metadata floor is misuse.
        if emergency_blocker and no_pending:
            for fname in ["final-verdict.md", "final-verdict.txt", "verdict.md"]:
                content = metadata_files_content.get(fname, "")
                if content:
                    m = re.search(r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}([A-Z][A-Z0-9_]+)", content, re.IGNORECASE)
                    if m:
                        verdict_val = m.group(1)
                        is_genuine_emergency = (
                            "EMERGENCY" in verdict_val
                            or "BLOCKED" in verdict_val
                            or "SUPERSEDED" in verdict_val
                            or "DIRTY_TREE" in verdict_val
                            or "FAIL" in verdict_val
                            or "PARTIAL" in verdict_val
                        )
                        if not is_genuine_emergency:
                            warnings.append(
                                f"EMERGENCY_BLOCKER_MISUSE: contract has emergency_blocker_bundle: true "
                                f"but {fname} has VERDICT: {verdict_val} — "
                                "emergency_blocker_bundle is for genuine blockers/failures, "
                                "not normal sprint closure (Rule C-LOCAL-003)."
                            )
                    break

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
            repo_reports_pending_hits = check_repo_reports_pending(zf)
            for zip_path, pattern in repo_reports_pending_hits:
                errors.append(
                    f"R46: PENDING marker in bundled final-verdict '{zip_path}': {pattern!r} "
                    f"— bundle was built before final-verdict was updated. "
                    f"Regenerate final-verdict.md before building bundle."
                )
            closure_contradiction_hits = check_closure_contradictions(metadata_files_content)
            for msg in closure_contradiction_hits:
                errors.append(msg)
            state_verdict_hits = check_state_verdict_agreement(metadata_files_content, zf)
            for msg in state_verdict_hits:
                errors.append(msg)
            package_proof_hits = check_package_proof_present(metadata_files_content, zf)
            for msg in package_proof_hits:
                errors.append(msg)
            artifact_inventory_hits = check_artifact_inventory(zf)
            for msg in artifact_inventory_hits:
                errors.append(msg)
            authoritative_test_hits = check_authoritative_test_result_present(metadata_files_content)
            for msg in authoritative_test_hits:
                errors.append(msg)
            proof_finality_hits = check_proof_file_finality(metadata_files_content)
            for msg in proof_finality_hits:
                errors.append(msg)
            proof_sha_warnings = check_proof_sha_consistency(metadata_files_content, bundle_path)
            # R54 Lane 2: Suppress SHA mismatch warning if a valid sidecar is provided.
            # The sidecar is the authoritative final proof; internal SHA mismatch is expected.
            sidecar_is_valid = sidecar_path and not check_sidecar_proof(bundle_path, sidecar_path)
            if not sidecar_is_valid:
                for msg in proof_sha_warnings:
                    warnings.append(msg)
            command_log_hits = check_validation_command_log_freshness(metadata_files_content)
            for msg in command_log_hits:
                errors.append(msg)
            verdict_closeout_hits = check_verdict_unresolved_closeout(zf)
            for msg in verdict_closeout_hits:
                errors.append(msg)
            clean_git_warnings = check_contract_clean_git_strictness(contract, zf)
            for msg in clean_git_warnings:
                warnings.append(msg)
            depth_hits = check_metadata_content_depth(metadata_files_content)
            for fname, reason in depth_hits:
                errors.append(f"Shallow metadata file '{fname}': {reason}")
            # R54 Lane 3: Artifact policy enforcement
            # Get verdict content for policy check
            _verdict_for_policy = ""
            for _vf in ("final-verdict.md", "final-verdict.txt", "verdict.md"):
                _verdict_for_policy = metadata_files_content.get(_vf, "")
                if _verdict_for_policy:
                    break
            artifact_policy_hits = check_installed_artifact_policy(
                contract, metadata_files_content, zf, _verdict_for_policy
            )
            for msg in artifact_policy_hits:
                errors.append(msg)

            # R56 unwired checks — wired in R58 Train C
            scoreboard_hits = check_scoreboard_finality(zf, metadata_files_content)
            for msg in scoreboard_hits:
                errors.append(msg)
            embedded_sidecar_hits = check_embedded_sidecar_bundle_match(zf, str(bundle_path))
            for msg in embedded_sidecar_hits:
                errors.append(msg)
            nested_zip_hits = check_nested_zips_allowed(zf, contract)
            for msg in nested_zip_hits:
                errors.append(msg)
            package_claim_hits = check_package_claim_policy_consistency(metadata_files_content, contract)
            for msg in package_claim_hits:
                errors.append(msg)

            # R58 Train C: new hardening checks
            pycache_hits = check_pycache_in_bundle(zf)
            for msg in pycache_hits:
                errors.append(msg)
            state_pending_hits = check_state_sprint_pending(zf)
            for msg in state_pending_hits:
                errors.append(msg)
            repo_sidecar_hits = check_repo_sidecar_not_inside_zip(zf, str(bundle_path))
            for msg in repo_sidecar_hits:
                errors.append(msg)
            # R59 Train B: pass run_number so validator targets only the current-run final-verdict
            _run_number = contract.get("run_number", "")
            scoreboard_lane_hits = check_scoreboard_lanes_in_progress(zf, run_number=_run_number)
            for msg in scoreboard_lane_hits:
                errors.append(msg)

            # R68 Train E: closeout-hygiene token scan
            closeout_hits = check_closeout_hygiene_tokens(zf)
            for zip_path, token in closeout_hits:
                errors.append(
                    f"R68: Closeout-hygiene token {token!r} found in bundled file '{zip_path}' "
                    f"— report was not filled in before bundle build."
                )

            # R69 Train D: source-commit proof no pending markers (IV-R69-001)
            source_proof_hits = check_source_commit_proof_no_pending(metadata_files_content)
            for msg in source_proof_hits:
                errors.append(msg)

            # R69 Train D: negative sidecar proofs present check
            neg_proof_warnings = check_negative_sidecar_proofs_present(metadata_files_content)
            for msg in neg_proof_warnings:
                warnings.append(msg)

            # R71 Train B: layered proof authority — inner verdict must not own outer delivery pkg SHA
            delivery_sha_authority_hits = check_inner_verdict_delivery_sha_authority(zf)
            for msg in delivery_sha_authority_hits:
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
        total_pending = len(pending_hits) + len(repo_pending_hits) + len(repo_reports_pending_hits)
        pending_status = "PASS" if total_pending == 0 else "FAIL"
        print(f"No-PENDING check ({pending_status}): {len(pending_hits)} metadata PENDING + "
              f"{len(repo_pending_hits)} repo current-state PENDING + "
              f"{len(repo_reports_pending_hits)} repo/reports final-verdict PENDING marker(s)")
        if closure_contradiction_hits:
            print(f"Closure-contradiction check (FAIL): {len(closure_contradiction_hits)} contradiction(s)")
        else:
            print("Closure-contradiction check (PASS): no proof/verdict/summary contradictions")
        artifact_inv_status = "FAIL" if artifact_inventory_hits else "PASS"
        print(f"Artifact inventory check ({artifact_inv_status}): "
              f"{len(artifact_inventory_hits)} error(s)")
        auth_status = "FAIL" if authoritative_test_hits else "PASS"
        print(f"AUTHORITATIVE_TEST_RESULT check ({auth_status}): "
              f"{'missing — P-EVID-003 violation' if authoritative_test_hits else 'present in metadata'}")
        proof_fin_status = "FAIL" if proof_finality_hits else "PASS"
        print(f"Proof-file finality check ({proof_fin_status}): "
              f"{'placeholder text found — R49 guard' if proof_finality_hits else 'no stale placeholders'}")
        proof_sha_status = "WARN" if proof_sha_warnings else "PASS"
        print(f"Proof-SHA sidecar check ({proof_sha_status}): "
              f"{'SHA mismatch — use sidecar protocol — R52 guard' if proof_sha_warnings else 'proof SHA consistent or sidecar not required'}")
        cmd_log_status = "FAIL" if command_log_hits else "PASS"
        print(f"Command log freshness check ({cmd_log_status}): "
              f"{'stale pre-final token found — R50 guard' if command_log_hits else 'no stale tokens'}")
        state_verdict_status = "FAIL" if state_verdict_hits else "PASS"
        print(f"State/verdict agreement check ({state_verdict_status}): "
              f"{'state contradicts final-verdict — R52 guard' if state_verdict_hits else 'state and verdict agree'}")
        verdict_closeout_status = "FAIL" if verdict_closeout_hits else "PASS"
        print(f"Verdict unresolved-closeout check ({verdict_closeout_status}): "
              f"{'unresolved closeout text found — R51 guard' if verdict_closeout_hits else 'no unresolved closeout text'}")
        clean_git_strict_status = "WARN" if clean_git_warnings else "PASS"
        print(f"Contract clean-git strictness ({clean_git_strict_status}): "
              f"{'require_clean_git: false with clean verdict — R51 guard' if clean_git_warnings else 'clean-git policy OK'}")
        delivery_sha_status = "FAIL" if delivery_sha_authority_hits else "PASS"
        print(f"Layered proof authority check ({delivery_sha_status}): "
              f"{'inner verdict must not own outer delivery pkg SHA — R71 guard' if delivery_sha_authority_hits else 'inner verdict correctly delegates outer pkg SHA'}")
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


def check_sidecar_required(contract: dict, sidecar_path: "str | None", verdict_content: str = "") -> "list[str]":
    """R54 Lane 2: Fail-closed sidecar enforcement.

    If the contract specifies `sidecar_required: true` and --sidecar-proof is not
    supplied, validation fails. Additionally, if the verdict claims a self-verifying
    or clean-baseline state and no sidecar is provided, validation fails.

    Contract fields:
      sidecar_required: true/false
      final_proof_policy: external_sidecar (implies required)

    Verdict tokens that imply sidecar is required:
      SELF_VERIFYING, BASELINE_CLEAN, SELF_CONTAINED, INSTALLED_ARTIFACT_BASELINE

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []
    sidecar_req = contract.get("sidecar_required", False)
    final_proof_policy = contract.get("final_proof_policy", "")

    if final_proof_policy == "external_sidecar":
        sidecar_req = True

    SIDECAR_REQUIRED_VERDICT_TOKENS = [
        "SELF_VERIFYING",
        "BASELINE_CLEAN",
        "SELF_CONTAINED",
        "INSTALLED_ARTIFACT_BASELINE",
    ]
    verdict_upper = verdict_content.upper() if verdict_content else ""
    for token in SIDECAR_REQUIRED_VERDICT_TOKENS:
        if token in verdict_upper:
            sidecar_req = True
            break

    if sidecar_req and not sidecar_path:
        errors.append(
            "SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof "
            "(sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) "
            "but --sidecar-proof was not supplied. "
            "Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>."
        )
    return errors


def check_sidecar_filename_match(sidecar_path: str, bundle_path: str) -> "list[str]":
    """R54: Verify sidecar bundle_filename matches actual bundle filename.

    Returns a list of error strings. Empty list means PASS.
    """
    import json as _json
    errors: list[str] = []
    try:
        sidecar = _json.loads(Path(sidecar_path).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"SIDECAR_PROOF: cannot read sidecar for filename check: {exc}")
        return errors

    sidecar_bundle_filename = sidecar.get("bundle_filename", "")
    actual_bundle_filename = Path(bundle_path).name
    if sidecar_bundle_filename and sidecar_bundle_filename != actual_bundle_filename:
        errors.append(
            f"SIDECAR_BUNDLE_FILENAME_MISMATCH: sidecar bundle_filename={sidecar_bundle_filename!r} "
            f"but actual bundle filename is {actual_bundle_filename!r}. "
            f"Sidecar was written for a different bundle."
        )

    sidecar_run = sidecar.get("run_number", "")
    contract_run = ""  # checked separately
    return errors


def check_sidecar_proof(bundle_path: str, sidecar_path: str) -> "list[str]":
    """R53 Lane 2B: Validate an external sidecar proof against the actual bundle bytes.

    The sidecar JSON (written by tools/evidence/write_sidecar_proof.py) contains:
      sha256, size_bytes, entry_count, validation_result

    This function verifies that each field matches the actual bundle.

    Returns a list of error strings. Empty list means PASS.
    """
    import json as _json
    errors: list[str] = []

    try:
        sidecar = _json.loads(Path(sidecar_path).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"SIDECAR_PROOF: cannot read sidecar file {sidecar_path!r}: {exc}")
        return errors

    # Validate SHA
    try:
        actual_sha = hashlib.sha256(Path(bundle_path).read_bytes()).hexdigest()
    except Exception as exc:
        errors.append(f"SIDECAR_PROOF: cannot read bundle for SHA check: {exc}")
        return errors

    # R58: backward-compat — accept bundle_sha256 if sha256 not present
    claimed_sha = sidecar.get("sha256") or sidecar.get("bundle_sha256", "")
    if actual_sha.lower() != str(claimed_sha).lower():
        errors.append(
            f"SIDECAR_PROOF_SHA_MISMATCH: sidecar claims sha256={claimed_sha!r} "
            f"but actual bundle SHA is {actual_sha!r}"
        )

    # Validate size
    actual_size = Path(bundle_path).stat().st_size
    claimed_size = sidecar.get("size_bytes")
    if claimed_size is not None and int(claimed_size) != actual_size:
        errors.append(
            f"SIDECAR_PROOF_SIZE_MISMATCH: sidecar claims size_bytes={claimed_size} "
            f"but actual bundle size is {actual_size}"
        )

    # Validate entry count
    try:
        with zipfile.ZipFile(bundle_path) as zf:
            actual_entries = len(zf.namelist())
    except Exception as exc:
        errors.append(f"SIDECAR_PROOF: cannot open bundle for entry count: {exc}")
        return errors

    claimed_entries = sidecar.get("entry_count")
    if claimed_entries is not None and int(claimed_entries) != actual_entries:
        errors.append(
            f"SIDECAR_PROOF_ENTRY_COUNT_MISMATCH: sidecar claims entry_count={claimed_entries} "
            f"but actual bundle has {actual_entries} entries"
        )

    # Validate result field
    validation_result = sidecar.get("validation_result", "")
    if validation_result != "PASS":
        errors.append(
            f"SIDECAR_PROOF_RESULT_NOT_PASS: sidecar validation_result={validation_result!r} (expected 'PASS')"
        )

    return errors


def check_embedded_sidecar_bundle_match(zf, bundle_path: str) -> "list[str]":
    """R56 Train B: If bundle contains an embedded sidecar, it must match the bundle being validated.

    An embedded sidecar is a .sha256-proof.json under bundle-metadata/.
    If it refers to a different bundle file (different bundle_filename), it must be explicitly
    marked as external_reference: true in the sidecar JSON.

    Returns a list of error strings. Empty list means PASS.
    """
    import json as _json
    errors: list[str] = []
    actual_bundle_filename = Path(bundle_path).name

    sidecar_entries = [
        e for e in zf.namelist()
        if e.startswith("bundle-metadata/") and e.endswith(".sha256-proof.json")
    ]
    for entry in sidecar_entries:
        try:
            sidecar = _json.loads(zf.read(entry).decode("utf-8"))
        except Exception as exc:
            errors.append(f"EMBEDDED_SIDECAR_UNREADABLE: {entry!r}: {exc}")
            continue

        # If marked as external reference, skip the match check
        if sidecar.get("external_reference", False):
            continue

        sidecar_bundle_filename = sidecar.get("bundle_filename", "")
        if sidecar_bundle_filename and sidecar_bundle_filename != actual_bundle_filename:
            errors.append(
                f"EMBEDDED_SIDECAR_BUNDLE_MISMATCH: embedded sidecar {entry!r} references "
                f"bundle_filename={sidecar_bundle_filename!r} but the bundle being validated is "
                f"{actual_bundle_filename!r}. The embedded sidecar is for a different bundle. "
                f"Either update the sidecar to match the final bundle or mark it as "
                f"external_reference: true. (R56-IV-R55-003)"
            )
    return errors


def check_nested_zips_allowed(zf, contract: dict) -> "list[str]":
    """R56 Train B: Nested .zip files under bundle-metadata/ must be explicitly allowed by contract.

    If the contract does not declare `allow_nested_bundle_zips: true`, any nested .zip files
    under bundle-metadata/ cause a validation failure.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []
    if contract.get("allow_nested_bundle_zips", False):
        return errors

    nested_zips = [
        e for e in zf.namelist()
        if e.startswith("bundle-metadata/") and e.endswith(".zip")
    ]
    if nested_zips:
        errors.append(
            f"NESTED_ZIPS_NOT_ALLOWED: bundle-metadata/ contains nested .zip files: "
            f"{nested_zips}. "
            f"Nested ZIPs inflate bundle size and cause sidecar confusion. "
            f"Add allow_nested_bundle_zips: true to the contract to explicitly permit this, "
            f"or remove the nested ZIPs from the metadata directory before building. "
            f"(R56-IV-R55-009)"
        )
    return errors


def check_scoreboard_finality(zf, metadata_files_content: dict) -> "list[str]":
    """R56 Train B: Scoreboard cannot remain IN_PROGRESS/PENDING when verdict says COMPLETE.

    If the repo contains a multi-mega-train-scoreboard.md with status IN_PROGRESS or
    trains showing PENDING, and the verdict claims a COMPLETE state, this is a contradiction.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []

    # Get verdict from metadata
    verdict_content = ""
    for fname in ("final-verdict.md", "final-verdict.txt"):
        verdict_content = metadata_files_content.get(fname, "")
        if verdict_content:
            break
    if not verdict_content:
        # Try to find in repo
        for entry in zf.namelist():
            if entry.endswith("final-verdict.md"):
                try:
                    verdict_content = zf.read(entry).decode("utf-8", errors="replace")
                except Exception:
                    pass
                break

    COMPLETE_VERDICT_TOKENS = ["_COMPLETE", "_PASS", "_PHASE", "_VERIFIED"]
    verdict_upper = verdict_content.upper() if verdict_content else ""
    is_complete_claimed = any(t in verdict_upper for t in COMPLETE_VERDICT_TOKENS)

    # Find scoreboard in repo — use LAST sorted entry (most recent sprint)
    scoreboard_content = ""
    scoreboard_entries = sorted([
        e for e in zf.namelist()
        if "multi-mega-train-scoreboard" in e and e.endswith(".md")
    ])
    if scoreboard_entries:
        try:
            scoreboard_content = zf.read(scoreboard_entries[-1]).decode("utf-8", errors="replace")
        except Exception:
            pass

    if not scoreboard_content or not is_complete_claimed:
        return errors

    scoreboard_upper = scoreboard_content.upper()
    if "**STATUS:** IN_PROGRESS" in scoreboard_content or "Status:** IN_PROGRESS" in scoreboard_content:
        errors.append(
            "SCOREBOARD_NOT_FINALIZED: multi-mega-train-scoreboard.md has status IN_PROGRESS "
            "but the final verdict claims COMPLETE/PASS. "
            "The scoreboard must be updated to reflect actual train outcomes before final closure. "
            "(R56-IV-R55-004)"
        )
    return errors


def check_package_claim_policy_consistency(metadata_files_content: dict, contract: dict) -> "list[str]":
    """R56 Train B: installed_artifact_policy: none cannot coexist with package RC language in verdict.

    If the contract or manifest declares installed_artifact_policy: none, the final verdict
    must not contain language claiming package RC completion, wheels built, or installed smoke PASS.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []

    # Determine effective policy
    policy = contract.get("installed_artifact_policy", "none")
    manifest_content = metadata_files_content.get("package-artifact-manifest.yaml", "")
    if "installed_artifact_policy: none" in manifest_content or "r55_installed_artifact_policy: none" in manifest_content:
        policy = "none"

    if policy != "none":
        return errors

    # Check final verdict for package RC language
    verdict_content = ""
    for fname in ("final-verdict.md", "final-verdict.txt"):
        verdict_content = metadata_files_content.get(fname, "")
        if verdict_content:
            break

    PACKAGE_RC_TOKENS = [
        "packages built",
        "wheels built",
        "installed smoke pass",
        "package rc complete",
        "7 packages built",
        "wheel artifacts",
        "installed wheel",
        "clean venv",
        "package smoke",
    ]
    verdict_lower = verdict_content.lower() if verdict_content else ""
    found_tokens = [t for t in PACKAGE_RC_TOKENS if t in verdict_lower]

    if found_tokens:
        errors.append(
            f"PACKAGE_CLAIM_POLICY_CONTRADICTION: installed_artifact_policy is 'none' "
            f"(no artifacts built this sprint) but final verdict contains package RC language: "
            f"{found_tokens}. "
            f"Either remove the package RC language from the verdict, or change the policy to "
            f"'external_ref' or 'self_contained' and supply actual artifacts. (R56-IV-R55-002)"
        )
    return errors


def check_pycache_in_bundle(zf) -> "list[str]":
    """R58 Train C: Detect __pycache__ directories or .pyc files in the repo portion of the bundle.

    These compiled artifacts are environment-specific, not version-controlled, and must
    not appear in evidence bundles. Their presence indicates the bundle was built from an
    unclean working tree or a non-standard include list.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []
    pycache_entries = [
        e for e in zf.namelist()
        if e.startswith("repo/") and ("__pycache__" in e or e.endswith(".pyc"))
    ]
    if pycache_entries:
        sample = pycache_entries[:5]
        errors.append(
            f"BUNDLE_PYCACHE_PRESENT: bundle contains {len(pycache_entries)} __pycache__/__pyc file(s). "
            f"Sample: {sample}. "
            f"These compiled artifacts must not be in evidence bundles. "
            f"Add __pycache__/ and *.pyc to forbidden_patterns in the contract, or clean build artifacts "
            f"before bundling. (R58-IV-R57-012)"
        )
    return errors


def check_state_sprint_pending(zf) -> "list[str]":
    """R58 Train C: Detect if state/current-state.md latest sprint shows PENDING verdict.

    A PENDING verdict in state/current-state.md means state_snapshot.py was run before
    the sprint completed, leaving the bundle in an inconsistent state.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []
    state_content = ""
    for candidate in ("repo/state/current-state.md", "repo/state/current-state.json"):
        if candidate in zf.namelist():
            try:
                state_content = zf.read(candidate).decode("utf-8", errors="replace")
            except Exception:
                pass
            if state_content:
                break

    if not state_content:
        return errors

    # Detect "Latest sprint: RXX - PENDING" pattern
    if re.search(r"Latest sprint:.*PENDING", state_content, re.IGNORECASE):
        errors.append(
            "STATE_SPRINT_PENDING: state/current-state.md shows latest sprint with PENDING verdict. "
            "Run state_snapshot.py AFTER writing the final verdict and before building the bundle. "
            "(R58-IV-R57-004)"
        )
    # Detect JSON verdict: PENDING
    if '"verdict": "PENDING"' in state_content or "'verdict': 'PENDING'" in state_content:
        errors.append(
            "STATE_SPRINT_PENDING: state/current-state.json shows verdict=PENDING. "
            "Run state_snapshot.py after final verdict is complete. (R58-IV-R57-004)"
        )
    return errors


def check_repo_sidecar_not_inside_zip(zf, bundle_path: str) -> "list[str]":
    """R58 Train B: A sidecar proof file for the current bundle must not appear inside the ZIP.

    The sidecar (*.sha256-proof.json) must live OUTSIDE the ZIP it proves. If the sidecar
    is committed to the repo and the repo is bundled, the sidecar ends up inside the ZIP,
    making it impossible to be the authoritative external proof of the final ZIP's SHA.

    Also catches the case where a sidecar committed to reports/<run>/ has SHA matching
    a prior build (not the final build), causing SHA mismatch.

    Returns a list of error strings. Empty list means PASS.
    """
    import json as _json
    errors: list[str] = []
    bundle_name = Path(bundle_path).name

    # Find any .sha256-proof.json files in the repo portion of the bundle
    sidecar_in_repo = [
        e for e in zf.namelist()
        if e.startswith("repo/") and e.endswith(".sha256-proof.json")
    ]
    for entry in sidecar_in_repo:
        try:
            sidecar = _json.loads(zf.read(entry).decode("utf-8", errors="replace"))
        except Exception:
            continue
        sidecar_bundle_filename = sidecar.get("bundle_filename", "")
        if sidecar_bundle_filename == bundle_name or bundle_name in sidecar_bundle_filename:
            errors.append(
                f"SIDECAR_INSIDE_ZIP: {entry!r} is a sidecar for this bundle ({bundle_name!r}) "
                f"but it is committed to the repo and thus INSIDE the ZIP. "
                f"A sidecar cannot prove its own containing ZIP's SHA. "
                f"Do not commit the sidecar to the repo. Write it to .local/ (gitignored) only. "
                f"(R58-IV-R57-002)"
            )
    return errors


def check_scoreboard_lanes_in_progress(zf, run_number: str = "") -> "list[str]":
    """R58 Train C / R59 Train B: Detect IN_PROGRESS in current-run scoreboard and final-verdict.

    R59 fix (IV-R58-006): use run_number to target ONLY the current-run final-verdict.
    Without this guard, historical final-verdict files (e.g. skills-system-hardening/...) can
    overwrite the current-run verdict content, causing the IN_PROGRESS check to miss defects.

    Any lane remaining IN_PROGRESS when the bundle is built invalidates the closure claim.

    Returns a list of error strings. Empty list means PASS.
    """
    errors: list[str] = []

    # Determine the canonical path for the current-run final-verdict.
    # run_number e.g. "R59" → look for repo/reports/r59/final-verdict.md
    current_run_verdict_path = ""
    if run_number:
        run_lower = run_number.lower()
        current_run_verdict_path = f"repo/reports/{run_lower}/final-verdict.md"

    # Find scoreboard in repo — use LAST sorted entry (most recent sprint)
    scoreboard_content = ""
    scoreboard_entries = sorted([
        e for e in zf.namelist()
        if "multi-mega-train-scoreboard" in e and e.endswith(".md")
    ])
    if scoreboard_entries:
        try:
            scoreboard_content = zf.read(scoreboard_entries[-1]).decode("utf-8", errors="replace")
        except Exception:
            pass

    # Load current-run final-verdict using run_number (R59 fix IV-R58-006).
    # If run_number is provided, load ONLY that specific file.
    # If not provided, fall back to scanning all (legacy behaviour).
    verdict_content = ""
    if current_run_verdict_path:
        if current_run_verdict_path in zf.namelist():
            try:
                verdict_content = zf.read(current_run_verdict_path).decode("utf-8", errors="replace")
            except Exception:
                pass
        # If not found, that itself is a problem but not this check's responsibility.
    else:
        # Legacy fallback: scan all final-verdicts; last in namelist wins (may be unreliable)
        for entry in zf.namelist():
            if entry.startswith("repo/reports/") and entry.endswith("/final-verdict.md"):
                try:
                    verdict_content = zf.read(entry).decode("utf-8", errors="replace")
                except Exception:
                    pass

    # Check scoreboard for IN_PROGRESS
    if scoreboard_content and "IN_PROGRESS" in scoreboard_content:
        errors.append(
            "SCOREBOARD_LANE_IN_PROGRESS: multi-mega-train-scoreboard.md contains IN_PROGRESS lane(s). "
            "All lanes must be COMPLETE or documented as deferred before final bundle closure. "
            "(R58-IV-R57-006)"
        )
    # Check SCOREBOARD_STATUS line
    if scoreboard_content and "SCOREBOARD_STATUS" in scoreboard_content:
        if "IN_PROGRESS" in scoreboard_content.split("SCOREBOARD_STATUS")[-1][:200]:
            if "SCOREBOARD_LANE_IN_PROGRESS" not in str(errors):
                errors.append(
                    "SCOREBOARD_STATUS_IN_PROGRESS: SCOREBOARD_STATUS line shows IN_PROGRESS. "
                    "Update scoreboard before final bundle build. (R58-IV-R57-006)"
                )

    # Check current-run final-verdict for IN_PROGRESS / PENDING / NOT_STARTED
    INCOMPLETE_TOKENS = ["IN_PROGRESS", "NOT_STARTED", "BUNDLE_VALIDATION: PENDING"]
    for token in INCOMPLETE_TOKENS:
        if verdict_content and token in verdict_content:
            errors.append(
                f"VERDICT_TRAIN_INCOMPLETE: current-run final-verdict contains '{token}'. "
                f"All trains must be COMPLETE and bundle validation resolved before final closure. "
                f"(R59-IV-R58-003, R59-IV-R58-005, R59-IV-R58-006)"
            )
            break  # One error per verdict is sufficient

    # Scoreboard vs verdict cross-check: scoreboard ALL_COMPLETE but verdict has incomplete trains
    if (scoreboard_content and "SCOREBOARD_STATUS: ALL_COMPLETE" in scoreboard_content
            and verdict_content and any(t in verdict_content for t in INCOMPLETE_TOKENS)):
        errors.append(
            "SCOREBOARD_VERDICT_CONTRADICTION: scoreboard claims ALL_COMPLETE but current-run "
            "final-verdict contains incomplete train markers. Both must agree. "
            "(R59-IV-R58-004)"
        )
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate evidence bundle against contract")
    parser.add_argument("--contract", required=True, help="Contract YAML path")
    parser.add_argument("--bundle", required=True, help="Bundle zip path")
    parser.add_argument("--no-strict-git", action="store_true",
                        help="Skip git cleanliness check even if contract requires it")
    parser.add_argument("--check-no-pending", action="store_true",
                        help="Fail if any metadata file contains PENDING marker patterns "
                             "(use as final validation after report files are updated)")
    parser.add_argument("--sidecar-proof", default=None,
                        help="Path to external sidecar proof JSON (write_sidecar_proof.py output). "
                             "If provided, validates sidecar SHA/size/entries against actual bundle.")
    args = parser.parse_args()

    success = validate_bundle(
        args.contract,
        args.bundle,
        strict_git=not args.no_strict_git,
        no_pending=args.check_no_pending,
        sidecar_path=args.sidecar_proof,
    )

    if args.sidecar_proof:
        sidecar_errors = check_sidecar_proof(args.bundle, args.sidecar_proof)
        sidecar_errors += check_sidecar_filename_match(args.sidecar_proof, args.bundle)
        if sidecar_errors:
            print()
            print("SIDECAR PROOF ERRORS:")
            for e in sidecar_errors:
                print(f"  - {e}")
            print("SIDECAR_PROOF_VALIDATION: FAIL")
            success = False
        else:
            sidecar_path_obj = Path(args.sidecar_proof)
            import json as _json
            try:
                sidecar = _json.loads(sidecar_path_obj.read_text(encoding="utf-8"))
                print(f"Sidecar proof check (PASS): SHA/size/entries match — {sidecar.get('sha256', '')[:16]}...")
            except Exception:
                pass
            print("SIDECAR_PROOF_VALIDATION: PASS")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
