#!/usr/bin/env python3
"""
Replay an extracted evidence bundle without Git.

Given a directory that was extracted from a bundle ZIP (containing repo/ and
bundle-metadata/ subdirectories), runs validate_evidence_bundle.py against
the original contract to verify the bundle is still self-consistent.

This enables offline/no-Git verification — reviewers can extract a bundle
ZIP and run this script to confirm authenticity without needing the full
git repository or network access.

Usage:
    python tools/evidence/replay_extracted_bundle.py \\
        --extracted /path/to/extracted-bundle/ \\
        --contract tools/evidence/contracts/r43-*.yaml \\
        [--check-no-pending]

Exit codes:
    0 = REPLAY_VALIDATION: PASS
    1 = REPLAY_VALIDATION: FAIL

Sprint: FORMAT-FACTORY-R43-AUTHORITY-PROOF-COMPLETE-001
"""

import argparse
import hashlib
import io
import pathlib
import sys
import zipfile

# Suppress .pyc bytecode generation during import to avoid __pycache__ directories
# appearing inside the extracted repo/ tree when we later repack it.
sys.dont_write_bytecode = True

# Locate validate_evidence_bundle.py relative to this script
_TOOLS_EVIDENCE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS_EVIDENCE))
from validate_evidence_bundle import validate_bundle  # noqa: E402

# Paths that must never appear in a repacked bundle (mirrors common contract exclude_patterns)
_REPACK_EXCLUDE_SUFFIXES = (".pyc", ".pdb")
_REPACK_EXCLUDE_PARTS = ("__pycache__", ".pytest_cache", ".mypy_cache")


def _should_exclude(fpath: pathlib.Path) -> bool:
    """Return True if this file should be excluded when repacking."""
    parts = fpath.parts
    for part in parts:
        if part in _REPACK_EXCLUDE_PARTS:
            return True
    if fpath.suffix in _REPACK_EXCLUDE_SUFFIXES:
        return True
    return False


def extracted_dir_to_zip(extracted_dir: pathlib.Path) -> io.BytesIO:
    """Re-pack an extracted bundle directory into an in-memory ZIP.

    Expects:
        extracted_dir/repo/...
        extracted_dir/bundle-metadata/...

    Returns an io.BytesIO containing the re-packed ZIP.
    Excludes __pycache__, .pyc, .pytest_cache, and other bytecode artifacts
    so the repacked ZIP passes the standard forbidden-file checks.
    """
    buf = io.BytesIO()
    excluded_count = 0
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(extracted_dir.rglob("*")):
            if fpath.is_file():
                if _should_exclude(fpath):
                    excluded_count += 1
                    continue
                # zip path relative to extracted_dir
                zip_name = fpath.relative_to(extracted_dir).as_posix()
                zf.write(fpath, zip_name)
    if excluded_count:
        print(f"  (excluded {excluded_count} bytecode/cache files from repack)")
    buf.seek(0)
    return buf


def sha256_of_buffer(buf: io.BytesIO) -> str:
    pos = buf.tell()
    buf.seek(0)
    h = hashlib.sha256(buf.read()).hexdigest()
    buf.seek(pos)
    return h


def write_temp_zip(buf: io.BytesIO, output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(buf.getvalue())


def main():
    parser = argparse.ArgumentParser(
        description="Replay an extracted evidence bundle (no-Git offline verification)."
    )
    parser.add_argument(
        "--extracted",
        required=True,
        help="Path to extracted bundle directory (must contain repo/ and bundle-metadata/).",
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Path to the evidence contract YAML file.",
    )
    parser.add_argument(
        "--check-no-pending",
        action="store_true",
        default=False,
        help="Pass --check-no-pending to the validator (checks for PENDING markers).",
    )
    parser.add_argument(
        "--output-zip",
        default=None,
        help="Optional: write re-packed ZIP to this path for inspection.",
    )
    args = parser.parse_args()

    extracted_dir = pathlib.Path(args.extracted).resolve()
    contract_path = pathlib.Path(args.contract).resolve()

    if not extracted_dir.exists():
        print(f"ERROR: Extracted directory not found: {extracted_dir}")
        print("REPLAY_VALIDATION: FAIL")
        sys.exit(1)

    if not contract_path.exists():
        print(f"ERROR: Contract not found: {contract_path}")
        print("REPLAY_VALIDATION: FAIL")
        sys.exit(1)

    # Check expected structure
    repo_dir = extracted_dir / "repo"
    meta_dir = extracted_dir / "bundle-metadata"
    has_repo = repo_dir.exists()
    has_meta = meta_dir.exists()

    if not has_repo or not has_meta:
        print(f"ERROR: Extracted directory missing expected structure.")
        print(f"  repo/          present: {has_repo}")
        print(f"  bundle-metadata/ present: {has_meta}")
        print("REPLAY_VALIDATION: FAIL")
        sys.exit(1)

    # Count entries
    repo_files = list(repo_dir.rglob("*"))
    meta_files = list(meta_dir.rglob("*"))
    print(f"Extracted bundle: {extracted_dir}")
    print(f"  repo/ files:            {sum(1 for f in repo_files if f.is_file())}")
    print(f"  bundle-metadata/ files: {sum(1 for f in meta_files if f.is_file())}")

    # Re-pack into in-memory ZIP
    print("Re-packing extracted directory into in-memory ZIP...")
    buf = extracted_dir_to_zip(extracted_dir)
    sha = sha256_of_buffer(buf)
    print(f"Re-packed ZIP SHA-256: {sha}")

    # Optionally write to disk
    if args.output_zip:
        out_path = pathlib.Path(args.output_zip)
        write_temp_zip(buf, out_path)
        print(f"Written re-packed ZIP to: {out_path}")
        zip_path = out_path
    else:
        # Write to a temp file so validate_bundle can open it
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp.write(buf.getvalue())
            zip_path = pathlib.Path(tmp.name)

    # Run validator
    print(f"\nRunning validator against: {contract_path}")
    print(f"Bundle path: {zip_path}")
    print("---")

    try:
        ok = validate_bundle(
            str(contract_path),
            str(zip_path),
            strict_git=False,
            no_pending=args.check_no_pending,
        )
    finally:
        if args.output_zip is None:
            zip_path.unlink(missing_ok=True)

    print("---")
    if ok:
        print("REPLAY_VALIDATION: PASS")
        sys.exit(0)
    else:
        print("REPLAY_VALIDATION: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
