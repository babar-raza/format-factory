"""
build_delivery_package.py — Build a transfer-safe delivery package.

The delivery package wraps an evidence ZIP + its external sidecar + a manifest
into a single outer ZIP for convenient transfer. The sidecar remains external
to the evidence ZIP it proves.

Usage:
    python tools/evidence/build_delivery_package.py \
        --evidence-zip .local/r65-pass2-final.zip \
        --sidecar .local/r65-pass2-final.sha256-proof.json \
        --contract tools/evidence/contracts/r65-....yaml \
        --output .local/r65-delivery-package.zip

R65 Sprint: FORMAT-FACTORY-R65-DELIVERY-PACKAGE-RC-REPLAY-AI-LIVE-WORKAHEAD-MEGA-TRAIN-001
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_delivery_package(
    evidence_zip: Path,
    sidecar: Path,
    contract_path: str,
    output: Path,
    git_head: str = "",
) -> dict:
    """Build the outer delivery package.

    Returns the delivery manifest as a dict.
    """
    if not evidence_zip.is_file():
        raise FileNotFoundError(f"Evidence ZIP not found: {evidence_zip}")
    if not sidecar.is_file():
        raise FileNotFoundError(f"Sidecar not found: {sidecar}")

    # Read sidecar to get validation info
    with open(sidecar, "r", encoding="utf-8") as f:
        sidecar_data = json.load(f)

    evidence_sha = _sha256(evidence_zip)
    sidecar_sha = _sha256(sidecar)

    with zipfile.ZipFile(evidence_zip, "r") as zf:
        entry_count = len(zf.namelist())

    manifest = {
        "delivery_package_version": "1.0",
        "evidence_zip_filename": evidence_zip.name,
        "evidence_zip_sha256": evidence_sha,
        "evidence_zip_size_bytes": evidence_zip.stat().st_size,
        "evidence_zip_entry_count": entry_count,
        "sidecar_filename": sidecar.name,
        "sidecar_sha256": sidecar_sha,
        "contract_path": contract_path,
        "validation_command": (
            f"python tools/evidence/validate_evidence_bundle.py "
            f"--bundle {evidence_zip.name} "
            f"--contract {contract_path} "
            f"--check-no-pending "
            f"--sidecar-proof {sidecar.name}"
        ),
        "validation_result": sidecar_data.get("validation_result", "UNKNOWN"),
        "git_head": git_head or sidecar_data.get("git_head", ""),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    # Write manifest alongside output
    manifest_path = output.parent / output.name.replace(".zip", "-manifest.json").replace(
        "delivery-package", "delivery"
    )
    # Normalize: ensure name is r65-delivery-manifest.json style
    if "manifest" not in manifest_path.name:
        manifest_path = output.parent / (output.stem + "-manifest.json")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Build outer ZIP
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as outer:
        outer.write(evidence_zip, evidence_zip.name)
        outer.write(sidecar, sidecar.name)
        outer.write(manifest_path, manifest_path.name)

    pkg_sha = _sha256(output)
    pkg_size = output.stat().st_size

    print(f"Delivery package built: {output}")
    print(f"  Evidence ZIP: {evidence_zip.name} ({evidence_sha[:16]}...)")
    print(f"  Sidecar: {sidecar.name} ({sidecar_sha[:16]}...)")
    print(f"  Manifest: {manifest_path.name}")
    print(f"  Package SHA-256: {pkg_sha}")
    print(f"  Package size: {pkg_size:,} bytes")
    print(f"DELIVERY_PACKAGE_BUILD: PASS")

    manifest["delivery_package_sha256"] = pkg_sha
    manifest["delivery_package_size_bytes"] = pkg_size
    manifest["manifest_path"] = str(manifest_path)

    return manifest


def validate_delivery_package(package_path: Path, extract_dir: Path) -> dict:
    """Extract and validate a delivery package.

    Returns dict with validation results.
    """
    results = {
        "package_path": str(package_path),
        "extract_dir": str(extract_dir),
        "checks": [],
    }

    # Extract
    with zipfile.ZipFile(package_path, "r") as zf:
        entries = zf.namelist()
        zf.extractall(extract_dir)

    results["entries"] = entries

    # Find components
    evidence_zips = [e for e in entries if e.endswith(".zip")]
    sidecars = [e for e in entries if e.endswith(".sha256-proof.json")]
    manifests = [e for e in entries if e.endswith("-manifest.json")]

    # Check: evidence ZIP present
    if evidence_zips:
        results["evidence_zip"] = evidence_zips[0]
        results["checks"].append(("evidence_zip_present", True))
    else:
        results["checks"].append(("evidence_zip_present", False))
        results["validation_result"] = "FAIL"
        return results

    # Check: sidecar present
    if sidecars:
        results["sidecar"] = sidecars[0]
        results["checks"].append(("sidecar_present", True))
    else:
        results["checks"].append(("sidecar_present", False))
        results["validation_result"] = "FAIL"
        return results

    # Check: manifest present
    if manifests:
        results["manifest"] = manifests[0]
        results["checks"].append(("manifest_present", True))
    else:
        results["checks"].append(("manifest_present", False))

    # Check: sidecar NOT inside evidence ZIP
    ez_path = extract_dir / results["evidence_zip"]
    with zipfile.ZipFile(ez_path, "r") as inner:
        inner_entries = inner.namelist()
        sidecar_inside = any(e.endswith(".sha256-proof.json") for e in inner_entries)
        results["checks"].append(("sidecar_not_inside_inner_zip", not sidecar_inside))

    # Check: sidecar SHA matches evidence ZIP
    sc_path = extract_dir / results["sidecar"]
    with open(sc_path, "r", encoding="utf-8") as f:
        sidecar_data = json.load(f)

    actual_sha = _sha256(ez_path)
    sidecar_sha = sidecar_data.get("sha256", "")
    sha_match = actual_sha == sidecar_sha
    results["checks"].append(("sidecar_sha_matches_evidence_zip", sha_match))
    results["evidence_zip_sha256"] = actual_sha
    results["sidecar_claimed_sha256"] = sidecar_sha

    # Check: manifest matches both files
    if manifests:
        mf_path = extract_dir / results["manifest"]
        with open(mf_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        mf_sha = manifest_data.get("evidence_zip_sha256", "")
        results["checks"].append(("manifest_sha_matches_evidence_zip", mf_sha == actual_sha))

    all_pass = all(ok for _, ok in results["checks"])
    results["validation_result"] = "PASS" if all_pass else "FAIL"

    return results


def main():
    parser = argparse.ArgumentParser(description="Build delivery package")
    parser.add_argument("--evidence-zip", required=True, help="Inner evidence ZIP")
    parser.add_argument("--sidecar", required=True, help="External sidecar proof JSON")
    parser.add_argument("--contract", required=True, help="Contract path")
    parser.add_argument("--output", required=True, help="Output delivery package path")
    parser.add_argument("--git-head", default="", help="Git HEAD SHA")

    args = parser.parse_args()
    build_delivery_package(
        evidence_zip=Path(args.evidence_zip),
        sidecar=Path(args.sidecar),
        contract_path=args.contract,
        output=Path(args.output),
        git_head=args.git_head,
    )


if __name__ == "__main__":
    main()
