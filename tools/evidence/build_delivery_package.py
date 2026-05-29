"""
build_delivery_package.py — Build a transfer-safe delivery package.

The delivery package wraps an evidence ZIP + its external sidecar + a manifest
+ a supervisor-readme into a single outer ZIP for convenient transfer.
The sidecar remains external to the evidence ZIP it proves.

Usage:
    python tools/evidence/build_delivery_package.py \
        --evidence-zip .local/r65-pass2-final.zip \
        --sidecar .local/r65-pass2-final.sha256-proof.json \
        --contract tools/evidence/contracts/r65-....yaml \
        --output .local/r65-delivery-package.zip

R65 Sprint: FORMAT-FACTORY-R65-DELIVERY-PACKAGE-RC-REPLAY-AI-LIVE-WORKAHEAD-MEGA-TRAIN-001
R73 Update: Added supervisor-readme.md to delivery package for inspectability.
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


def _generate_supervisor_readme(
    run_id: str,
    evidence_zip_name: str,
    evidence_zip_sha: str,
    sidecar_name: str,
    sidecar_file_sha: str,
    sidecar_claimed_bundle_sha: str,
    manifest_name: str,
    validation_command: str,
) -> str:
    """Generate supervisor-readme.md content explaining the delivery structure."""
    return f"""# Supervisor Inspection Readme — {run_id} Delivery Package

## UPLOAD THIS FILE (the outer delivery package ZIP)

**DO NOT upload the inner evidence ZIP directly.**
The file to upload to the supervisor is: the outer delivery package ZIP itself.
This file contains everything the supervisor needs to verify the sprint evidence.

---

## Delivery Package Contents

| File | Role |
|---|---|
| {evidence_zip_name} | Inner evidence ZIP — the full sprint evidence bundle |
| {sidecar_name} | Sidecar proof JSON — proves the inner ZIP SHA |
| {manifest_name} | Delivery manifest — records all SHAs and validation commands |
| (this file) | Supervisor inspection readme |

---

## Layered SHA Model

The delivery package uses a layered SHA model. There are THREE different SHA values:

### Layer 1: Inner Evidence ZIP SHA
- SHA-256: {evidence_zip_sha}
- This is the SHA of `{evidence_zip_name}` (the inner evidence bundle)
- Recorded in: `{manifest_name}` (evidence_zip_sha256 field)
- Recorded in: `{sidecar_name}` (sha256 field)
- Recorded in: reports/{run_id.lower()}/final-verdict.md (BUNDLE_VALIDATION_PASS_2_SHA field)

### Layer 2: Sidecar File SHA
- SHA-256: {sidecar_file_sha}
- This is the SHA of `{sidecar_name}` (the sidecar proof JSON file)
- Recorded in: `{manifest_name}` (sidecar_sha256 field)
- Recorded in: reports/{run_id.lower()}/final-verdict.md (SIDECAR_SHA field)
- NOTE: This is the SHA of the sidecar FILE, not the inner ZIP SHA

### Layer 3: Outer Delivery Package SHA
- SHA-256: (computed after building — see final-verdict.md DELIVERY_PACKAGE_RECORDED_SHA)
- This is the SHA of the outer delivery package ZIP you are reading
- Recorded in: reports/{run_id.lower()}/final-verdict.md (DELIVERY_PACKAGE_RECORDED_SHA field)
- NOTE: The outer delivery package SHA cannot appear inside the manifest because the manifest
  is packaged inside the outer ZIP before the outer ZIP exists (circular dependency).
  The outer SHA is recorded in the final-verdict.md and in a standalone .sha256.txt file.

### Why the Sidecar Is NOT Inside the Inner ZIP
The sidecar `{sidecar_name}` proves the inner ZIP `{evidence_zip_name}` from outside it.
If the sidecar were inside the inner ZIP, it would be part of what it is proving (circular).
The sidecar is a companion file — it travels alongside the inner ZIP, not inside it.

---

## How to Verify This Delivery Package

1. Compute SHA-256 of `{evidence_zip_name}` — must match {evidence_zip_sha[:16]}...
2. Compute SHA-256 of `{sidecar_name}` — must match {sidecar_file_sha[:16]}...
3. Open `{sidecar_name}` and check that `sha256` field = {sidecar_claimed_bundle_sha[:16]}...
4. Confirm that sidecar sha256 == inner ZIP SHA (step 1 == step 3 sha256 field)
5. Run: {validation_command}

All five checks must pass.

---

## What the Supervisor SHA Mismatch Means

If you computed the SHA of the outer delivery package and compared it to
BUNDLE_VALIDATION_PASS_2_SHA in final-verdict.md — they WILL be different.
That is expected. They are different files:
- BUNDLE_VALIDATION_PASS_2_SHA = SHA of the inner evidence ZIP
- Outer delivery package SHA = SHA of the outer ZIP containing the inner ZIP + sidecar + manifest

This is not a corruption or tampering. It is correct layered-proof behavior.
"""


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
    sidecar_claimed_sha = sidecar_data.get("sha256", "")

    with zipfile.ZipFile(evidence_zip, "r") as zf:
        entry_count = len(zf.namelist())

    # Derive run_id from evidence zip name (e.g. "r73-pass2-final.zip" -> "r73")
    stem = evidence_zip.stem  # e.g. "r73-pass2-final"
    run_id = stem.split("-")[0].upper()  # "R73"

    validation_cmd = (
        f"python tools/evidence/validate_evidence_bundle.py "
        f"--bundle {evidence_zip.name} "
        f"--contract {contract_path} "
        f"--check-no-pending "
        f"--sidecar-proof {sidecar.name}"
    )

    manifest = {
        "delivery_package_version": "1.1",
        "evidence_zip_filename": evidence_zip.name,
        "evidence_zip_sha256": evidence_sha,
        "evidence_zip_size_bytes": evidence_zip.stat().st_size,
        "evidence_zip_entry_count": entry_count,
        "sidecar_filename": sidecar.name,
        "sidecar_sha256": sidecar_sha,
        "sidecar_claimed_bundle_sha256": sidecar_claimed_sha,
        "contract_path": contract_path,
        "validation_command": validation_cmd,
        "validation_result": sidecar_data.get("validation_result", "UNKNOWN"),
        "git_head": git_head or sidecar_data.get("git_head", ""),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "delivery_package_sha256_note": (
            "The outer delivery package SHA cannot be self-referential inside the manifest "
            "because the manifest is packaged before the outer ZIP is built. "
            "The outer package SHA is recorded in reports/{run}/final-verdict.md "
            "(DELIVERY_PACKAGE_RECORDED_SHA field) and in the standalone .sha256.txt file."
        ),
    }

    # Write manifest alongside output
    manifest_path = output.parent / output.name.replace(".zip", "-manifest.json").replace(
        "delivery-package", "delivery"
    )
    # Normalize: ensure name is r73-delivery-manifest.json style
    if "manifest" not in manifest_path.name:
        manifest_path = output.parent / (output.stem + "-manifest.json")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Generate supervisor-readme
    readme_name = output.name.replace("-delivery-package.zip", "-supervisor-inspection-readme.md")
    if readme_name == output.name:
        readme_name = output.stem + "-supervisor-inspection-readme.md"
    readme_path = output.parent / readme_name
    readme_content = _generate_supervisor_readme(
        run_id=run_id,
        evidence_zip_name=evidence_zip.name,
        evidence_zip_sha=evidence_sha,
        sidecar_name=sidecar.name,
        sidecar_file_sha=sidecar_sha,
        sidecar_claimed_bundle_sha=sidecar_claimed_sha,
        manifest_name=manifest_path.name,
        validation_command=validation_cmd,
    )
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Build outer ZIP
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as outer:
        outer.write(evidence_zip, evidence_zip.name)
        outer.write(sidecar, sidecar.name)
        outer.write(manifest_path, manifest_path.name)
        outer.write(readme_path, readme_path.name)

    pkg_sha = _sha256(output)
    pkg_size = output.stat().st_size
    pkg_entry_count = 4  # inner ZIP + sidecar + manifest + readme

    print(f"Delivery package built: {output}")
    print(f"  Evidence ZIP: {evidence_zip.name} ({evidence_sha[:16]}...)")
    print(f"  Sidecar: {sidecar.name} ({sidecar_sha[:16]}...)")
    print(f"  Manifest: {manifest_path.name}")
    print(f"  Supervisor readme: {readme_path.name}")
    print(f"  Package SHA-256: {pkg_sha}")
    print(f"  Package size: {pkg_size:,} bytes")
    print(f"  Package entries: {pkg_entry_count}")
    print(f"DELIVERY_PACKAGE_BUILD: PASS")

    manifest["delivery_package_sha256"] = pkg_sha
    manifest["delivery_package_size_bytes"] = pkg_size
    manifest["delivery_package_entry_count"] = pkg_entry_count
    manifest["manifest_path"] = str(manifest_path)
    manifest["supervisor_readme_path"] = str(readme_path)

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
    ez_path = Path(extract_dir) / results["evidence_zip"]
    with zipfile.ZipFile(ez_path, "r") as inner:
        inner_entries = inner.namelist()
        sidecar_inside = any(e.endswith(".sha256-proof.json") for e in inner_entries)
        results["checks"].append(("sidecar_not_inside_inner_zip", not sidecar_inside))

    # Check: sidecar SHA matches evidence ZIP
    sc_path = Path(extract_dir) / results["sidecar"]
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
        mf_path = Path(extract_dir) / results["manifest"]
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
