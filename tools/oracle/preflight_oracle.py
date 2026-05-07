#!/usr/bin/env python3
"""
preflight_oracle.py — Gate 6 oracle preflight check for FODS.

Checks that LibreOffice is installed and available for headless operation.
Records the version found and confirms it can locate the expected binary.

Usage:
    python tools/oracle/preflight_oracle.py [--samples-dir SAMPLES_DIR]

Outputs:
    - Prints preflight result to stdout
    - Writes .local/oracle/fods/oracle-preflight.yaml (local-only)

Exit codes:
    0 — preflight PASS (LibreOffice found and version recorded)
    1 — preflight FAIL (LibreOffice not found or error)

Rules:
    - No network calls
    - No LLM calls
    - No product source
    - Local outputs under .local/oracle/fods/ only
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

# Candidate binary paths for LibreOffice on various platforms
LIBREOFFICE_CANDIDATES = [
    "soffice",
    "libreoffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/usr/lib/libreoffice/program/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]

SAMPLES_DIR = Path("samples/by-format/fods")
ORACLE_LOCAL_DIR = Path(".local/oracle/fods")
PREFLIGHT_OUTPUT = ORACLE_LOCAL_DIR / "oracle-preflight.yaml"

EXPECTED_SAMPLES = [
    "minimal-spreadsheet.fods",
    "multi-sheet-basic.fods",
    "typed-values-basic.fods",
    "formula-basic.fods",
]


def find_soffice():
    """Return (path, version_string) for the first working soffice binary, or (None, None)."""
    for candidate in LIBREOFFICE_CANDIDATES:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                return candidate, result.stdout.strip()
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            continue
    return None, None


def check_samples(samples_dir: Path) -> list:
    """Return list of missing expected sample files."""
    missing = []
    for s in EXPECTED_SAMPLES:
        if not (samples_dir / s).exists():
            missing.append(s)
    return missing


def write_preflight_yaml(oracle_dir: Path, soffice_path, version, missing_samples, passed):
    """Write oracle-preflight.yaml to the local oracle directory."""
    oracle_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Oracle preflight result — auto-generated, local-only",
        f"passed: {'true' if passed else 'false'}",
        f"platform: {platform.system()} {platform.version()[:40]}",
        f"python: {sys.version.split()[0]}",
        f"soffice_found: {'true' if soffice_path else 'false'}",
        f"soffice_path: {soffice_path or 'null'}",
        f"soffice_version: {version or 'null'}",
        f"samples_dir: {SAMPLES_DIR}",
        "missing_samples:",
    ]
    for m in missing_samples:
        lines.append(f"  - {m}")
    if not missing_samples:
        lines.append("  # (none)")
    lines.append(f"candidates_checked: {len(LIBREOFFICE_CANDIDATES)}")
    Path(PREFLIGHT_OUTPUT).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    print("=" * 60)
    print("FODS Oracle Preflight Check")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.version()[:40]}")
    print(f"Checking {len(LIBREOFFICE_CANDIDATES)} LibreOffice candidate paths...")
    print()

    soffice_path, version = find_soffice()

    if soffice_path:
        print(f"FOUND: {soffice_path}")
        print(f"Version: {version}")
    else:
        print("NOT FOUND: LibreOffice (soffice) not available on this machine.")
        print("Checked candidates:")
        for c in LIBREOFFICE_CANDIDATES:
            print(f"  - {c}")
        print()
        print("To install: https://www.libreoffice.org/download/libreoffice-still/")

    print()
    print("Checking FODS samples...")
    missing = check_samples(SAMPLES_DIR)
    if missing:
        print(f"MISSING samples ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")
    else:
        print(f"All {len(EXPECTED_SAMPLES)} expected samples found.")

    passed = soffice_path is not None and not missing

    print()
    write_preflight_yaml(ORACLE_LOCAL_DIR, soffice_path, version, missing, passed)
    print(f"Preflight result written to: {PREFLIGHT_OUTPUT}")
    print()

    if passed:
        print("ORACLE_PREFLIGHT: PASS")
        print("Ready to run: python tools/oracle/run_fods_oracle.py")
        return 0
    else:
        reasons = []
        if not soffice_path:
            reasons.append("LibreOffice (soffice) not found")
        if missing:
            reasons.append(f"Missing samples: {missing}")
        print("ORACLE_PREFLIGHT: FAIL")
        print("Reasons:")
        for r in reasons:
            print(f"  - {r}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
