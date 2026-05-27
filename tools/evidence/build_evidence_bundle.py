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

    A path is forbidden if it exactly matches a pattern or is inside a forbidden
    directory (pattern + "/" prefix match). This mirrors validate_evidence_bundle.py
    so that .env.example is NOT caught by .env and .gitignore is NOT caught by .git/.
    """
    path_normalized = path.replace("\\", "/")
    for pattern in forbidden_patterns:
        pattern_clean = pattern.rstrip("/")
        # Exact match
        if fnmatch.fnmatch(path_normalized, pattern_clean):
            return True
        # Directory prefix match (path is inside a forbidden directory)
        if path_normalized.startswith(pattern_clean + "/"):
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


def auto_generate_git_metadata(repo_root, metadata_dir):
    """Auto-generate git-log.txt and git-status-final.txt in the metadata directory.

    These are the authoritative records of the exact final Git HEAD at bundle build time.
    See docs/current-state-and-evidence-authority.md — the exact Git HEAD is recorded here,
    not in committed repo files like master-plan.md.
    """
    metadata_path = Path(metadata_dir)
    generated = []

    # git-log.txt — full log (most recent 30 commits, one-line plus stats)
    log_result = subprocess.run(
        ["git", "log", "--oneline", "--stat", "-30"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if log_result.returncode == 0:
        log_path = metadata_path / "git-log.txt"
        log_path.write_text(log_result.stdout, encoding="utf-8")
        generated.append("git-log.txt")

    # git-status-final.txt — full git status at bundle build time
    status_result = subprocess.run(
        ["git", "status"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if status_result.returncode == 0:
        status_path = metadata_path / "git-status-final.txt"
        status_path.write_text(status_result.stdout, encoding="utf-8")
        generated.append("git-status-final.txt")

    # repo-tree.txt — sorted list of all tracked repo files at bundle build time
    tree_result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if tree_result.returncode == 0:
        tree_path = metadata_path / "repo-tree.txt"
        tree_path.write_text(tree_result.stdout, encoding="utf-8")
        generated.append("repo-tree.txt")

    return generated


def write_metadata_identity_report(contract, metadata_dir):
    """Write a sprint identity report into the metadata directory."""
    metadata_path = Path(metadata_dir)
    identity_path = metadata_path / "metadata-identity-report.md"
    sprint_id = contract.get("sprint_id", contract.get("contract_id", "null"))
    contract_id = contract.get("contract_id", "null")
    sprint_type = contract.get("sprint_type", "null")
    identity_path.write_text(
        "\n".join([
            "# Metadata Identity Report",
            "",
            f"sprint_id: {sprint_id}",
            f"contract_id: {contract_id}",
            f"sprint_type: {sprint_type}",
            "metadata_identity: primary",
            "",
            "This file is generated by build_evidence_bundle.py to bind the",
            "metadata directory to a single sprint identity.",
        ]),
        encoding="utf-8",
    )
    return "metadata-identity-report.md"


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
                 require_clean_git=True, allow_legacy_root_metadata=False):
    """Build the evidence bundle zip."""
    contract = load_contract(contract_path)
    repo_root = Path(repo_root).resolve()

    required_top_level = contract.get("required_top_level_folders", ["repo", "bundle-metadata"])
    forbidden_patterns = (
        contract.get("forbidden_paths", [])
        + contract.get("forbidden_patterns", [])
        + contract.get("exclude_patterns", [])
    )
    required_repo_files = contract.get("required_repo_files", [])
    required_metadata_files = contract.get("required_metadata_files", [])
    min_metadata_count = contract.get("min_metadata_count", 5)
    require_contract = contract.get("require_contract_in_bundle", False)
    contract_repo_path = contract.get("contract_repo_path", "")
    require_manifest_flag = contract.get("require_manifest", False)
    git_clean_required = contract.get("require_clean_git", require_clean_git)
    emergency_blocker = contract.get("emergency_blocker_bundle", False)

    metadata_path = Path(metadata_dir).resolve() if metadata_dir else None
    root_metadata_path = (repo_root / "bundle-metadata").resolve()
    if metadata_path == root_metadata_path and not allow_legacy_root_metadata:
        print("BUILD ERROR: root bundle-metadata/ is rejected for new evidence bundles.")
        print("Use a sprint-specific metadata directory under .local/<sprint-id>-metadata/.")
        print("For legacy bundle reconstruction only, pass --allow-legacy-root-metadata.")
        print("BUNDLE_BUILD: FAIL")
        return False
    if metadata_path == root_metadata_path and allow_legacy_root_metadata:
        print("  WARN: Using legacy root bundle-metadata/ directory.")

    # Check git cleanliness FIRST (before any file collection)
    # Rule: Dirty git ALWAYS causes BUNDLE_BUILD: FAIL unless emergency_blocker_bundle: true.
    # require_clean_git: false only disables the "missing git status file" check during validation.
    # It does NOT allow building with a dirty working tree.
    is_clean, git_porcelain = check_git_clean(repo_root)
    if not is_clean:
        if emergency_blocker:
            print("  WARN: Git working tree is not clean (emergency_blocker_bundle: true — exception).")
            for line in git_porcelain.splitlines()[:5]:
                print(f"  {line}")
        else:
            print("BUILD ERROR: Git working tree is not clean.")
            print("Uncommitted changes:")
            for line in git_porcelain.splitlines()[:20]:
                print(f"  {line}")
            print()
            print("Commit or stash all changes before building the evidence bundle.")
            print("NOTE: require_clean_git: false does NOT bypass this check.")
            print("To build a blocker/failed bundle with dirty git, set emergency_blocker_bundle: true.")
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

    # Collect metadata files (recursively — includes subdirectories like package-artifacts/)
    # R47: R46 defect fix — previously used iterdir() which skipped subdirectories.
    # Now uses rglob('*') with relative paths so bundle-metadata/package-artifacts/*.whl
    # entries are correctly included in the ZIP.
    metadata_files = []
    if metadata_path and metadata_path.exists():
        for mf in sorted(metadata_path.rglob("*")):
            if mf.is_file():
                rel = str(mf.relative_to(metadata_path)).replace("\\", "/")
                metadata_files.append(rel)

    # Auto-generate git-log.txt, git-status-final.txt, repo-tree.txt before validation
    # so required_metadata_files checks can see them.
    if metadata_path and metadata_path.exists() and not dry_run:
        identity_file = write_metadata_identity_report(contract, str(metadata_path))
        if identity_file not in metadata_files:
            metadata_files.append(identity_file)
        auto_generated = auto_generate_git_metadata(str(repo_root), str(metadata_path))
        for ag in auto_generated:
            if ag not in metadata_files:
                metadata_files.append(ag)

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
    # Note: bundle-manifest.yaml is auto-generated by the builder, so exclude it
    # from missing checks — it will be created before the zip is built.
    missing_metadata = []
    for mf in required_metadata_files:
        if mf not in metadata_files and mf != "bundle-manifest.yaml":
            missing_metadata.append(mf)

    if missing_metadata:
        errors.append(f"Missing required metadata files ({len(missing_metadata)}): {missing_metadata[:10]}")

    # Check min metadata count (+1 for manifest that will be auto-generated)
    effective_meta_count = len(metadata_files) + (1 if "bundle-manifest.yaml" not in metadata_files else 0)
    if effective_meta_count < min_metadata_count:
        errors.append(f"Metadata count {effective_meta_count} (incl. auto-manifest) < minimum {min_metadata_count}")

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
        # Append bundle-manifest.yaml BEFORE write_manifest so the count includes it
        if "bundle-manifest.yaml" not in metadata_files:
            metadata_files.append("bundle-manifest.yaml")
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
            print(f"  WARN: Extra top-level folders (not in required list): {sorted(unexpected)}")

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


def build_auto_proof_bundle(repo_root, contract_path, output_path, metadata_dir,
                            allow_legacy_root_metadata=False, require_clean_git=True):
    """Three-pass auto-proof bundle build (ACCEL-003 repaired).

    Pass 1: Write placeholder proof, build candidate zip, validate.
            Compute candidate metrics.
    Pass 2: Write proof with candidate metrics, build pre-proof final zip,
            validate. Compute pre-proof final metrics.
    Pass 3: Write complete proof (candidate + pre-proof final + self-reference
            note for final hash), rebuild final zip, validate.
            Update on-disk proof with Pass 3 hash for external verification.

    The proof embedded inside the final ZIP contains:
    - Candidate metrics (name, SHA-256, entries, bytes, metadata)
    - Pre-proof final metrics (name, SHA-256, entries, bytes, metadata)
    - Final entries + metadata count (deterministic — same file set as Pass 2)
    - Self-reference note explaining why final SHA-256/bytes are not pre-embedded
    - Final validation: PASS

    Self-reference problem: the proof file that is embedded in the final ZIP
    cannot contain the hash of the ZIP it is inside (circular dependency).
    The on-disk proof file (in metadata_dir) is updated after Pass 3 with the
    actual final ZIP SHA-256 and bytes for external chain verification.

    Does NOT leave a misleading final bundle on validation failure.
    Returns True on success (final BUNDLE_VALIDATION: PASS), False on failure.
    """
    import hashlib
    import zipfile as _zf

    def _compute_zip_metrics(zip_path):
        size = zip_path.stat().st_size
        sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        with _zf.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
        entries = len(names)
        metadata = sum(
            1 for n in names
            if n.startswith("bundle-metadata/") and not n.endswith("/")
        )
        return size, sha256, entries, metadata

    metadata_path = Path(metadata_dir).resolve() if metadata_dir else None
    output_path_obj = Path(output_path)
    candidate_path = output_path_obj.with_name(
        output_path_obj.stem + "-candidate" + output_path_obj.suffix
    )
    preproof_path = output_path_obj.with_name(
        output_path_obj.stem + "-preproof" + output_path_obj.suffix
    )
    proof_file = metadata_path / "final-bundle-validation-proof.txt" if metadata_path else None

    # Extract sprint_id for the proof from contract
    contract_data = load_contract(contract_path)
    sprint_id = contract_data.get("sprint_id", contract_data.get("contract_id", Path(contract_path).stem))

    validator = Path(__file__).parent / "validate_evidence_bundle.py"

    def _validate(zip_path, label):
        result = subprocess.run(
            [sys.executable, str(validator),
             "--bundle", str(zip_path),
             "--contract", contract_path,
             "--check-no-pending"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        out = result.stdout + result.stderr
        if "BUNDLE_VALIDATION: PASS" not in out:
            try:
                print(out[-2000:])
            except UnicodeEncodeError:
                print(out[-2000:].encode("ascii", errors="replace").decode("ascii"))
            return False, out
        return True, out

    # --- Write placeholder proof ---
    if proof_file:
        proof_file.write_text(
            "PLACEHOLDER — will be replaced after candidate validation\n",
            encoding="utf-8",
        )
        print(f"[AUTO-PROOF] Placeholder proof written: {proof_file.name}")

    # =========================================================
    # PASS 1: Build candidate, validate, compute candidate metrics
    # =========================================================
    print("[AUTO-PROOF PASS 1] Building candidate bundle...")
    ok = build_bundle(
        repo_root, contract_path, str(candidate_path), metadata_dir,
        dry_run=False,
        require_clean_git=require_clean_git,
        allow_legacy_root_metadata=allow_legacy_root_metadata,
    )
    if not ok:
        print("[AUTO-PROOF PASS 1] FAIL — candidate build failed. Stopping.")
        if candidate_path.exists():
            candidate_path.unlink()
        return False

    print("[AUTO-PROOF PASS 1] Validating candidate...")
    ok, _ = _validate(candidate_path, "PASS 1 candidate")
    if not ok:
        print("[AUTO-PROOF PASS 1] Candidate validation FAIL.")
        if candidate_path.exists():
            candidate_path.unlink()
        return False
    print("[AUTO-PROOF PASS 1] Candidate validation PASS.")

    c_bytes, c_sha256, c_entries, c_metadata = _compute_zip_metrics(candidate_path)

    # Write proof with candidate metrics (will be embedded in Pass 2 pre-proof build)
    if proof_file:
        proof_file.write_text("\n".join([
            "BUNDLE_VALIDATION: PASS",
            f"sprint_id: {sprint_id}",
            f"contract_id: {sprint_id}",
            "",
            "=== CANDIDATE (Pass 1) ===",
            f"Candidate: {candidate_path.name}",
            f"Candidate SHA-256: {c_sha256}",
            f"Candidate entries: {c_entries}",
            f"Candidate bytes: {c_bytes:,}",
            f"Candidate metadata: {c_metadata}",
            "",
            "Pass 2 pre-proof build: computing bundle metrics",
            "",
        ]), encoding="utf-8")
        print(f"[AUTO-PROOF] Pass 1 proof written (candidate metrics).")

    # =========================================================
    # PASS 2: Build pre-proof final, validate, compute pre-proof metrics
    # =========================================================
    print("[AUTO-PROOF PASS 2] Building pre-proof final bundle...")
    ok = build_bundle(
        repo_root, contract_path, str(preproof_path), metadata_dir,
        dry_run=False,
        require_clean_git=require_clean_git,
        allow_legacy_root_metadata=allow_legacy_root_metadata,
    )
    if not ok:
        print("[AUTO-PROOF PASS 2] FAIL — pre-proof final build failed.")
        if preproof_path.exists():
            preproof_path.unlink()
        return False

    print("[AUTO-PROOF PASS 2] Validating pre-proof final...")
    ok, _ = _validate(preproof_path, "PASS 2 pre-proof")
    if not ok:
        print("[AUTO-PROOF PASS 2] Pre-proof final validation FAIL.")
        if preproof_path.exists():
            preproof_path.unlink()
        return False
    print("[AUTO-PROOF PASS 2] Pre-proof final validation PASS.")

    pp_bytes, pp_sha256, pp_entries, pp_metadata = _compute_zip_metrics(preproof_path)

    # Write complete proof for embedding in Pass 3.
    # Self-reference note: the final ZIP's SHA-256 and bytes change when this proof is
    # embedded (circular dependency — the proof cannot know its own container's hash).
    # The on-disk proof is updated after Pass 3 with the actual final ZIP SHA-256/bytes.
    if proof_file:
        proof_file.write_text("\n".join([
            "BUNDLE_VALIDATION: PASS",
            f"sprint_id: {sprint_id}",
            f"contract_id: {sprint_id}",
            "",
            "=== CANDIDATE (Pass 1) ===",
            f"Candidate: {candidate_path.name}",
            f"Candidate SHA-256: {c_sha256}",
            f"Candidate entries: {c_entries}",
            f"Candidate bytes: {c_bytes:,}",
            f"Candidate metadata: {c_metadata}",
            "",
            "=== PRE-PROOF FINAL (Pass 2) ===",
            f"Pre-proof final: {output_path_obj.name}",
            f"Pre-proof SHA-256: {pp_sha256}",
            f"Pre-proof entries: {pp_entries}",
            f"Pre-proof bytes: {pp_bytes:,}",
            f"Pre-proof metadata: {pp_metadata}",
            "",
            "=== FINAL WITH PROOF EMBEDDED (Pass 3) ===",
            f"Final: {output_path_obj.name}",
            f"Final entries: {pp_entries}",
            f"Final metadata: {pp_metadata}",
            "Self-reference note: The SHA-256 and bytes of the final ZIP (Pass 3) cannot",
            "  be embedded in this proof before Pass 3 is built (circular dependency).",
            "  Pre-proof SHA-256 above verifies the Pass 2 build independently.",
            "  To verify Pass 3: compute SHA-256 of this ZIP externally.",
            "  The on-disk proof file (metadata_dir) contains the final SHA-256 after Pass 3.",
            "",
            "Validator: validate_evidence_bundle.py --check-no-pending",
            "Final validation: PASS",
            f"Timestamp: {datetime.now().astimezone().isoformat()}",
            "",
        ]), encoding="utf-8")
        print(f"[AUTO-PROOF] Complete proof written (candidate + pre-proof + self-ref note).")

    # =========================================================
    # PASS 3: Rebuild final ZIP with complete proof embedded, validate
    # =========================================================
    print("[AUTO-PROOF PASS 3] Building final bundle with embedded proof...")
    ok = build_bundle(
        repo_root, contract_path, str(output_path), metadata_dir,
        dry_run=False,
        require_clean_git=require_clean_git,
        allow_legacy_root_metadata=allow_legacy_root_metadata,
    )
    if not ok:
        print("[AUTO-PROOF PASS 3] FAIL — final build failed.")
        if Path(output_path).exists():
            Path(output_path).unlink()
        if preproof_path.exists():
            preproof_path.unlink()
        return False

    print("[AUTO-PROOF PASS 3] Validating final bundle...")
    ok, _ = _validate(Path(output_path), "PASS 3 final")
    if not ok:
        print("[AUTO-PROOF PASS 3] Final validation FAIL.")
        if Path(output_path).exists():
            Path(output_path).unlink()
        if preproof_path.exists():
            preproof_path.unlink()
        return False
    print("[AUTO-PROOF PASS 3] Final bundle validation PASS.")

    # Compute final ZIP metrics and update on-disk proof with actual final SHA-256/bytes
    f_bytes, f_sha256, f_entries, f_metadata = _compute_zip_metrics(Path(output_path))

    if proof_file:
        # Read the proof embedded in the final ZIP to verify it got in there
        with _zf.ZipFile(output_path, "r") as zf:
            zip_names = zf.namelist()
            proof_in_zip_name = "bundle-metadata/final-bundle-validation-proof.txt"
            proof_in_zip = (
                zf.read(proof_in_zip_name).decode("utf-8", errors="replace")
                if proof_in_zip_name in zip_names else ""
            )
        proof_embedded_ok = "Pre-proof SHA-256:" in proof_in_zip and "Final validation: PASS" in proof_in_zip

        # Update on-disk proof with actual Pass 3 metrics for external chain verification
        existing = proof_file.read_text(encoding="utf-8").rstrip()
        proof_file.write_text(existing + "\n".join([
            "",
            "=== PASS 3 EXTERNAL VERIFICATION RECORD ===",
            f"Final SHA-256: {f_sha256}",
            f"Final bytes: {f_bytes:,}",
            f"Final entries: {f_entries}",
            f"Final metadata: {f_metadata}",
            f"Proof embedded in ZIP: {'YES' if proof_embedded_ok else 'NO — check build'}",
            f"Pass 3 timestamp: {datetime.now().astimezone().isoformat()}",
            "",
        ]), encoding="utf-8")
        print(f"[AUTO-PROOF] On-disk proof updated with Pass 3 external verification record.")
        print(f"[AUTO-PROOF] Proof embedded in ZIP: {'YES' if proof_embedded_ok else 'WARNING: check proof inside ZIP'}")

    # Clean up intermediate ZIPs
    if candidate_path.exists():
        candidate_path.unlink()
    if preproof_path.exists():
        preproof_path.unlink()

    print(f"BUNDLE_VALIDATION: PASS")
    print(f"EVIDENCE_BUNDLE: {Path(output_path).resolve()}")
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
    parser.add_argument("--allow-legacy-root-metadata", action="store_true",
                        help="Allow root bundle-metadata/ for legacy bundle reconstruction only")
    parser.add_argument("--auto-proof", action="store_true",
                        help="Three-pass auto-proof build: candidate -> validate -> write proof -> final -> "
                             "validate final. Eliminates manual proof-placeholder pattern (ACCEL-003). "
                             "Incompatible with --dry-run.")
    args = parser.parse_args()

    if args.auto_proof:
        success = build_auto_proof_bundle(
            args.repo_root,
            args.contract,
            args.output,
            args.metadata_dir,
            allow_legacy_root_metadata=args.allow_legacy_root_metadata,
        )
    else:
        success = build_bundle(
            args.repo_root,
            args.contract,
            args.output,
            args.metadata_dir,
            args.dry_run,
            require_clean_git=not args.no_git_check,
            allow_legacy_root_metadata=args.allow_legacy_root_metadata,
        )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
