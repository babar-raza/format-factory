"""
find_bundle_artifacts.py — Portable artifact directory discovery.

Resolves the R57 fix for IV-R56-005: test_r56_package_rc.py used a hardcoded
.local/ path that does not exist in a clean extracted bundle.

This module provides a single function `find_artifact_dir(run_number, project_root)`
that checks candidate locations in order and returns the first that contains .whl files.

Candidate order:
  0. FORMAT_FACTORY_BUNDLE_METADATA_DIR env var (R59: explicit override)
  1. .local/<run_number>-metadata/package-artifacts/  (local dev build)
  2. bundle-metadata/package-artifacts/               (in-tree extracted bundle)
  3. <project_root>.parent/bundle-metadata/package-artifacts/  (extracted bundle layout)
  4. reports/<run_number>/package-artifacts/           (legacy bundle layout)

Returns None if no candidate directory contains .whl files.

Usage:
    from tools.packaging.find_bundle_artifacts import find_artifact_dir
    artifacts = find_artifact_dir("r59", PROJECT_ROOT)
    if artifacts is None:
        pytest.skip("Package artifacts not available in this environment")

Env-var override (R59 Train D):
    Set FORMAT_FACTORY_BUNDLE_METADATA_DIR to the absolute path of the bundle-metadata
    directory to use. This enables extracted-bundle mode without path guessing.

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
R59 Train D: env-var support for extracted-bundle mode
IV-R56-005, IV-R58-009
"""
from __future__ import annotations

import os
from pathlib import Path


def find_artifact_dir(run_number: str, project_root: "str | Path") -> "Path | None":
    """Find the package artifact directory for the given run.

    Args:
        run_number: Run identifier, e.g. "r57" or "R57" (case-insensitive).
        project_root: Repository root path.

    Returns:
        Path to the first candidate directory that contains at least one .whl file,
        or None if no candidate directory has .whl files.

    Environment:
        FORMAT_FACTORY_BUNDLE_METADATA_DIR: if set, this directory is checked first.
    """
    root = Path(project_root)
    run_lower = run_number.lower()

    candidates = []

    # R59 Train D: explicit override via environment variable
    # R66 Train D: env-var override must match run number to prevent false positives
    env_override = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR", "")
    if env_override:
        env_path = Path(env_override)
        sprint_id_file = env_path / "sprint-id.txt"
        env_matches_run = True  # default allow if no sprint-id.txt
        if sprint_id_file.is_file():
            sprint_content = sprint_id_file.read_text(encoding="utf-8").lower()
            env_matches_run = run_lower in sprint_content
        if env_matches_run:
            candidates.append(env_path / "package-artifacts")

    # .local/<run>-metadata/ is naturally run-specific (path embeds run number)
    candidates.append(root / ".local" / f"{run_lower}-metadata" / "package-artifacts")

    # R67 Train B: bundle-metadata/ fallback paths require sprint-id.txt match.
    # Same pattern as env-var override (R66 Train D). Prevents false positives in
    # extracted-bundle mode where bundle-metadata/ exists for a different sprint.
    for bm_root in [root / "bundle-metadata", root.parent / "bundle-metadata"]:
        sprint_id_file = bm_root / "sprint-id.txt"
        bm_matches_run = True  # default allow if no sprint-id.txt (backward compat)
        if sprint_id_file.is_file():
            sprint_content = sprint_id_file.read_text(encoding="utf-8").lower()
            bm_matches_run = run_lower in sprint_content
        if bm_matches_run:
            candidates.append(bm_root / "package-artifacts")

    # reports/<run>/ is naturally run-specific (path embeds run number)
    candidates.append(root / "reports" / run_lower / "package-artifacts")

    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.whl")):
            return candidate

    return None


def find_manifest_path(run_number: str, project_root: "str | Path") -> "Path | None":
    """Find the package artifact manifest for the given run.

    Checks .local/<run_number>-metadata/ and bundle-metadata/.

    Environment:
        FORMAT_FACTORY_BUNDLE_METADATA_DIR: if set, this directory is checked first.

    Returns:
        Path to package-artifact-manifest.yaml or None if not found.
    """
    root = Path(project_root)
    run_lower = run_number.lower()

    candidates = []

    # R59 Train D: explicit override via environment variable
    # R66 Train D: env-var override must match run number to prevent false positives
    env_override = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR", "")
    if env_override:
        env_path = Path(env_override)
        sprint_id_file = env_path / "sprint-id.txt"
        env_matches_run = True  # default allow if no sprint-id.txt
        if sprint_id_file.is_file():
            sprint_content = sprint_id_file.read_text(encoding="utf-8").lower()
            env_matches_run = run_lower in sprint_content
        if env_matches_run:
            candidates.append(env_path / "package-artifact-manifest.yaml")

    # .local/<run>-metadata/ is naturally run-specific
    candidates.append(root / ".local" / f"{run_lower}-metadata" / "package-artifact-manifest.yaml")

    # R67 Train B: bundle-metadata/ fallback paths require sprint-id.txt match.
    for bm_root in [root / "bundle-metadata", root.parent / "bundle-metadata"]:
        sprint_id_file = bm_root / "sprint-id.txt"
        bm_matches_run = True  # default allow if no sprint-id.txt (backward compat)
        if sprint_id_file.is_file():
            sprint_content = sprint_id_file.read_text(encoding="utf-8").lower()
            bm_matches_run = run_lower in sprint_content
        if bm_matches_run:
            candidates.append(bm_root / "package-artifact-manifest.yaml")

    # reports/<run>/ is naturally run-specific
    candidates.append(root / "reports" / run_lower / "package-artifact-manifest.yaml")

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None
