"""
find_bundle_artifacts.py — Portable artifact directory discovery.

Resolves the R57 fix for IV-R56-005: test_r56_package_rc.py used a hardcoded
.local/ path that does not exist in a clean extracted bundle.

This module provides a single function `find_artifact_dir(run_number, project_root)`
that checks candidate locations in order and returns the first that contains .whl files.

Candidate order:
  1. .local/<run_number>-metadata/package-artifacts/  (local dev build)
  2. bundle-metadata/package-artifacts/               (extracted bundle)
  3. reports/<run_number>/package-artifacts/           (legacy bundle layout)

Returns None if no candidate directory contains .whl files.

Usage:
    from tools.packaging.find_bundle_artifacts import find_artifact_dir
    artifacts = find_artifact_dir("r57", PROJECT_ROOT)
    if artifacts is None:
        pytest.skip("Package artifacts not available in this environment")

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
IV-R56-005
"""
from __future__ import annotations

from pathlib import Path


def find_artifact_dir(run_number: str, project_root: "str | Path") -> "Path | None":
    """Find the package artifact directory for the given run.

    Args:
        run_number: Run identifier, e.g. "r57" or "R57" (case-insensitive).
        project_root: Repository root path.

    Returns:
        Path to the first candidate directory that contains at least one .whl file,
        or None if no candidate directory has .whl files.
    """
    root = Path(project_root)
    run_lower = run_number.lower()

    candidates = [
        root / ".local" / f"{run_lower}-metadata" / "package-artifacts",
        root / "bundle-metadata" / "package-artifacts",
        root / "reports" / run_lower / "package-artifacts",
    ]

    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.whl")):
            return candidate

    return None


def find_manifest_path(run_number: str, project_root: "str | Path") -> "Path | None":
    """Find the package artifact manifest for the given run.

    Checks .local/<run_number>-metadata/ and bundle-metadata/.

    Returns:
        Path to package-artifact-manifest.yaml or None if not found.
    """
    root = Path(project_root)
    run_lower = run_number.lower()

    candidates = [
        root / ".local" / f"{run_lower}-metadata" / "package-artifact-manifest.yaml",
        root / "bundle-metadata" / "package-artifact-manifest.yaml",
        root / "reports" / run_lower / "package-artifact-manifest.yaml",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None
