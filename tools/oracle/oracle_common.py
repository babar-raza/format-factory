#!/usr/bin/env python3
"""
oracle_common.py — Shared constants and path discovery for FODS Gate 6 oracle tools.

All tools/oracle/ scripts import from this module to ensure consistent:
- LibreOffice binary discovery (env var, CLI arg, PATH, standard install paths)
- Local output path model (.local/oracle/fods/)
- Sample list
- Diagnostic output

Rules:
    - No network calls
    - No LLM calls
    - No product source
    - Local outputs under .local/oracle/fods/ only
    - Gate 6 approval is human-only
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

# --- Canonical path model ---

SAMPLES_DIR = Path("samples/by-format/fods")
ORACLE_LOCAL_DIR = Path(".local/oracle/fods")
RAW_EXPORTS_DIR = ORACLE_LOCAL_DIR / "raw-exports"
PER_SAMPLE_DIR = ORACLE_LOCAL_DIR / "per-sample-results"
PREFLIGHT_OUTPUT = ORACLE_LOCAL_DIR / "oracle-preflight.yaml"
MANIFEST_PATH = ORACLE_LOCAL_DIR / "oracle-manifest.yaml"
SUMMARY_PATH = ORACLE_LOCAL_DIR / "comparison-summary.json"
SANITIZED_YAML_PATH = ORACLE_LOCAL_DIR / "oracle-summary-sanitized.yaml"

# Committed report path (sanitized summary only)
COMPARISON_REPORT_PATH = Path("acquisition-packs/fods/gate6-oracle-comparison-report.md")

# Blocker report path
BLOCKER_REPORT_PATH = Path("acquisition-packs/fods/gate6-oracle-blocker-report.md")

# --- Sample list ---

EXPECTED_SAMPLES = [
    "minimal-spreadsheet.fods",
    "multi-sheet-basic.fods",
    "typed-values-basic.fods",
    "formula-basic.fods",
]

# --- Environment variable for explicit oracle binary override ---

SOFFICE_ENV_VAR = "FORMAT_FACTORY_SOFFICE"

# --- Standard candidate paths (in discovery priority order) ---
# NOTE: On Windows, soffice.exe is a GUI wrapper that opens a dialog box when
# --version is called and does not write to stdout in subprocess capture mode.
# soffice.com is the console-mode variant that correctly writes to stdout.
# soffice.com is always tried before soffice.exe on Windows paths.

LIBREOFFICE_CANDIDATES = [
    # PATH discovery
    "soffice",
    "libreoffice",
    # Windows standard install paths — .com (console) before .exe (GUI wrapper)
    r"C:\Program Files\LibreOffice\program\soffice.com",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.com",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    # Linux standard paths
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/usr/lib/libreoffice/program/soffice",
    # macOS standard path
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice(override=None, verbose=False):
    """
    Discover the LibreOffice soffice binary.

    Priority order:
    1. `override` argument (e.g., from --soffice-path CLI option)
    2. FORMAT_FACTORY_SOFFICE environment variable
    3. Standard candidates (PATH + common install paths)

    Returns:
        (path: str, version: str) on success
        (None, None) if not found

    If verbose=True, prints each candidate tried and the result.
    """
    candidates = []
    source_labels = {}

    # 1. CLI override
    if override:
        candidates.append(override)
        source_labels[override] = f"--soffice-path / CLI override"

    # 2. Environment variable
    env_path = os.environ.get(SOFFICE_ENV_VAR, "").strip()
    if env_path and env_path not in candidates:
        # On Windows, if the env var points to soffice.exe, also try soffice.com
        # (console-mode variant that writes to stdout in subprocess capture)
        if platform.system() == "Windows" and env_path.lower().endswith(".exe"):
            com_path = env_path[:-4] + ".com"
            if com_path not in candidates:
                candidates.append(com_path)
                source_labels[com_path] = f"env:{SOFFICE_ENV_VAR} (.com variant)"
        candidates.append(env_path)
        source_labels[env_path] = f"env:{SOFFICE_ENV_VAR}"

    # 3. Standard candidates
    for c in LIBREOFFICE_CANDIDATES:
        if c not in candidates:
            candidates.append(c)
            source_labels[c] = "standard-path"

    if verbose:
        print(f"  Discovery: checking {len(candidates)} candidates...")

    for candidate in candidates:
        label = source_labels.get(candidate, "standard-path")
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                if verbose:
                    print(f"  FOUND [{label}]: {candidate}")
                    print(f"  Version: {result.stdout.strip()}")
                return candidate, result.stdout.strip()
            else:
                if verbose:
                    print(f"  MISS  [{label}]: {candidate} (rc={result.returncode})")
        except FileNotFoundError:
            if verbose:
                print(f"  MISS  [{label}]: {candidate} (not found)")
        except PermissionError:
            if verbose:
                print(f"  MISS  [{label}]: {candidate} (permission denied)")
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"  MISS  [{label}]: {candidate} (timeout)")

    return None, None


def check_samples(samples_dir=None):
    """
    Check that all expected FODS samples exist.

    Returns:
        list of missing sample filenames (empty if all present)
    """
    if samples_dir is None:
        samples_dir = SAMPLES_DIR
    samples_dir = Path(samples_dir)
    missing = []
    for s in EXPECTED_SAMPLES:
        if not (samples_dir / s).exists():
            missing.append(s)
    return missing


def print_discovery_summary(soffice_path, version, missing_samples):
    """Print a standard discovery/preflight summary."""
    print(f"Platform: {platform.system()} {platform.version()[:40]}")
    print(f"Python: {sys.version.split()[0]}")
    print()
    if soffice_path:
        print(f"Oracle binary: FOUND")
        print(f"  Path: {soffice_path}")
        print(f"  Version: {version}")
    else:
        print("Oracle binary: NOT FOUND")
        print(f"  Checked env var: {SOFFICE_ENV_VAR}")
        print(f"  Checked {len(LIBREOFFICE_CANDIDATES)} standard paths")
        print()
        print("To install: https://www.libreoffice.org/download/libreoffice-still/")
        print("To override: set FORMAT_FACTORY_SOFFICE=<path> or use --soffice-path")
    print()
    if missing_samples:
        print(f"FODS samples: MISSING ({len(missing_samples)} files)")
        for s in missing_samples:
            print(f"  - {s}")
    else:
        print(f"FODS samples: {len(EXPECTED_SAMPLES)} files found")
