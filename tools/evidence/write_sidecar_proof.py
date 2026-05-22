"""
write_sidecar_proof.py — Generate an external sidecar proof file for an evidence bundle.

Problem solved:
  A ZIP file cannot contain its own final SHA-256 because the SHA depends on the
  file's bytes, which include the content inside it. R52 left PASS 2 fields as
  PENDING inside the bundle for exactly this reason.

Solution:
  The internal bundle proof records only PASS 1 details (pre-final-SHA).
  After the final bundle is built and validated, this script writes an external
  sidecar JSON file alongside the ZIP. The sidecar is the authoritative final
  proof record.

Sidecar filename convention:
  <bundle-name>.sha256-proof.json
  Example: r53-baseline.zip -> r53-baseline.sha256-proof.json

Usage:
  python tools/evidence/write_sidecar_proof.py \\
    --bundle .local/evidence-bundles/r53-baseline.zip \\
    --contract tools/evidence/contracts/r53-baseline.yaml \\
    --run-number R53 \\
    --validation-result PASS \\
    [--output <custom-sidecar-path>]

R53: Addresses final-proof-sidecar-protocol as defined in reports/r53/final-proof-sidecar-protocol.md

License: Apache-2.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def build_sidecar(
    bundle_path: Path,
    contract_path: str,
    run_number: str,
    validation_result: str,
    validation_command: str | None = None,
) -> dict:
    sha256 = compute_sha256(bundle_path)
    size_bytes = bundle_path.stat().st_size
    with zipfile.ZipFile(bundle_path) as zf:
        entry_count = len(zf.namelist())

    if validation_command is None:
        validation_command = (
            f"python tools/evidence/validate_evidence_bundle.py "
            f"--bundle {bundle_path} --contract {contract_path} --check-no-pending"
        )

    return {
        "sidecar_version": "1.0",
        "run_number": run_number,
        "bundle_path": str(bundle_path.resolve()),
        "bundle_filename": bundle_path.name,
        "sha256": sha256,
        "size_bytes": size_bytes,
        "entry_count": entry_count,
        "contract_path": str(contract_path),
        "validation_command": validation_command,
        "validation_exit_code": 0 if validation_result == "PASS" else 1,
        "validation_result": validation_result,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": get_git_head(),
    }


def write_sidecar(sidecar: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write external sidecar proof for an evidence bundle"
    )
    parser.add_argument("--bundle", required=True, help="Bundle ZIP path")
    parser.add_argument("--contract", required=True, help="Contract YAML path")
    parser.add_argument("--run-number", required=True, help="Run number (e.g. R53)")
    parser.add_argument("--validation-result", default="PASS",
                        choices=["PASS", "FAIL"], help="Validation result")
    parser.add_argument("--validation-command", default=None,
                        help="Validation command used (optional)")
    parser.add_argument("--output", default=None,
                        help="Sidecar output path (default: <bundle>.sha256-proof.json)")
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    if not bundle_path.exists():
        print(f"ERROR: bundle not found: {bundle_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else bundle_path.with_suffix(".sha256-proof.json")

    sidecar = build_sidecar(
        bundle_path=bundle_path,
        contract_path=args.contract,
        run_number=args.run_number,
        validation_result=args.validation_result,
        validation_command=args.validation_command,
    )

    write_sidecar(sidecar, output_path)

    print(f"Sidecar proof written: {output_path}")
    print(f"  SHA-256:     {sidecar['sha256']}")
    print(f"  Size bytes:  {sidecar['size_bytes']:,}")
    print(f"  Entries:     {sidecar['entry_count']}")
    print(f"  Result:      {sidecar['validation_result']}")
    print(f"  Timestamp:   {sidecar['timestamp_utc']}")
    print(f"  Git HEAD:    {sidecar['git_head']}")
    print("SIDECAR_PROOF: WRITTEN")


if __name__ == "__main__":
    main()
