#!/usr/bin/env python3
"""
preflight_oracle.py — Gate 6 oracle preflight check for FODS.

Checks that LibreOffice is installed and available for headless operation.
Records the version found and confirms it can locate the expected binary.

Usage:
    python tools/oracle/preflight_oracle.py [--soffice-path PATH] [--verbose]

Environment:
    FORMAT_FACTORY_SOFFICE — explicit path to soffice binary (overrides discovery)

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

import argparse
import platform
import sys
from pathlib import Path

# Import shared oracle discovery from oracle_common.py
sys.path.insert(0, str(Path(__file__).parent))
from oracle_common import (
    LIBREOFFICE_CANDIDATES,
    ORACLE_LOCAL_DIR,
    PREFLIGHT_OUTPUT,
    SAMPLES_DIR,
    SOFFICE_ENV_VAR,
    check_samples,
    find_soffice,
    print_discovery_summary,
)


def write_preflight_yaml(oracle_dir, soffice_path, version, missing_samples, passed,
                         candidates_tried):
    """Write oracle-preflight.yaml to the local oracle directory."""
    oracle_dir = Path(oracle_dir)
    oracle_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Oracle preflight result — auto-generated, local-only",
        f"passed: {'true' if passed else 'false'}",
        f"platform: {platform.system()} {platform.version()[:40]}",
        f"python: {sys.version.split()[0]}",
        f"soffice_found: {'true' if soffice_path else 'false'}",
        f"soffice_path: {soffice_path or 'null'}",
        f"soffice_version: {version or 'null'}",
        f"env_var_checked: {SOFFICE_ENV_VAR}",
        f"samples_dir: {SAMPLES_DIR}",
        "missing_samples:",
    ]
    for m in missing_samples:
        lines.append(f"  - {m}")
    if not missing_samples:
        lines.append("  # (none)")
    lines.append(f"candidates_tried: {candidates_tried}")
    lines.append("standard_candidates:")
    for c in LIBREOFFICE_CANDIDATES:
        lines.append(f"  - {c}")
    PREFLIGHT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="FODS oracle preflight check")
    parser.add_argument("--soffice-path", default=None,
                        help="Explicit path to soffice binary (overrides discovery)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print each candidate path tried")
    parser.add_argument("--samples-dir", default=None,
                        help="Override samples directory path")
    args = parser.parse_args()

    print("=" * 60)
    print("FODS Oracle Preflight Check")
    print("=" * 60)

    soffice_path, version = find_soffice(override=args.soffice_path, verbose=args.verbose)

    missing = check_samples(args.samples_dir)

    print_discovery_summary(soffice_path, version, missing)

    passed = soffice_path is not None and not missing

    # Count candidates tried (env var override + standard list)
    candidates_tried = len(LIBREOFFICE_CANDIDATES) + (1 if args.soffice_path else 0)

    write_preflight_yaml(
        ORACLE_LOCAL_DIR,
        soffice_path,
        version,
        missing,
        passed,
        candidates_tried,
    )
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
            reasons.append(f"  To fix: install LibreOffice or set {SOFFICE_ENV_VAR}=<path>")
        if missing:
            reasons.append(f"Missing samples: {missing}")
        print("ORACLE_PREFLIGHT: FAIL")
        print("Reasons:")
        for r in reasons:
            print(f"  {r}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
