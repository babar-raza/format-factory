"""
build_supervisor_review_package.py — Build the supervisor review package.

The supervisor review package is the single artifact that must be uploaded
for supervisor inspection. It contains EVERYTHING needed to verify the sprint:

    r<N>-supervisor-review-package.zip
    ├── r<N>-delivery-package.zip          (outer delivery wrapper)
    ├── r<N>-delivery-package.sha256.txt   (standalone outer SHA — NEW R76)
    ├── r<N>-final-artifact-authority.json (cross-layer SHA authority — NEW R76)
    ├── r<N>-pass-final.zip               (inner evidence ZIP)
    ├── r<N>-pass-final.sha256-proof.json  (sidecar)
    ├── r<N>-delivery-manifest.json        (delivery manifest)
    ├── r<N>-supervisor-inspection-readme.md
    ├── r<N>-final-response-summary.md
    └── review-package-manifest.json       (list of all included files + their SHAs)

R75 DEFECT REPAIR:
R75 generated r75-final-artifact-authority.json and r75-delivery-package.sha256.txt
as external companion files alongside the delivery package but did NOT include them
in the supervisor upload. The supervisor received only the delivery package (4 entries)
and could not verify the artifact authority.

R76 FIX:
This script wraps the delivery package and ALL its companion authority files into one
single upload artifact. The supervisor only needs to upload one file.

Usage:
    python tools/evidence/build_supervisor_review_package.py \\
        --delivery-package .local/r76-delivery-package.zip \\
        --sha-file .local/r76-delivery-package.sha256.txt \\
        --authority-json .local/r76-final-artifact-authority.json \\
        --evidence-zip .local/r76-pass1-final.zip \\
        --sidecar .local/r76-pass1-final.sha256-proof.json \\
        --manifest .local/r76-delivery-manifest.json \\
        --supervisor-readme .local/r76-supervisor-inspection-readme.md \\
        --final-response-summary reports/r76/final-response-summary.md \\
        --output .local/r76-supervisor-review-package.zip
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


def _verify_authority_json(authority_path: Path, expected_inner_sha: str | None = None) -> dict:
    """Load and validate the artifact authority JSON. Returns parsed data."""
    with open(authority_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["schema_version", "sprint_id", "source_evidence_authority", "final_artifact_authority"]
    for field in required:
        if field not in data:
            raise ValueError(f"final-artifact-authority.json missing required field: {field!r}")

    sea = data.get("source_evidence_authority", {})
    faa = data.get("final_artifact_authority", {})

    for field in ["inner_zip_sha256", "sidecar_sha256", "sidecar_validates_inner_zip"]:
        if field not in sea:
            raise ValueError(f"source_evidence_authority missing field: {field!r}")

    for field in ["delivery_package_sha256", "standalone_sha_file"]:
        if field not in faa:
            raise ValueError(f"final_artifact_authority missing field: {field!r}")

    if expected_inner_sha and sea.get("inner_zip_sha256") != expected_inner_sha:
        raise ValueError(
            f"Authority JSON inner_zip_sha256 {sea['inner_zip_sha256'][:16]}... "
            f"does not match evidence ZIP SHA {expected_inner_sha[:16]}..."
        )

    # Check no delegation labels (must be actual SHAs in the review package)
    for sha_field in ["inner_zip_sha256", "sidecar_sha256"]:
        val = sea.get(sha_field, "")
        if "delegated" in str(val).lower() or val == "":
            raise ValueError(
                f"Authority JSON {sha_field} must be an actual SHA-256 value, not a delegation label"
            )

    return data


def build_supervisor_review_package(
    delivery_package: Path,
    sha_file: Path,
    authority_json: Path,
    evidence_zip: Path,
    sidecar: Path,
    manifest: Path,
    supervisor_readme: Path,
    final_response_summary: Path | None,
    output: Path,
    extra_top_level_dirs: list[tuple[str, Path]] | None = None,
) -> dict:
    """Build the supervisor review package.

    Returns a dict with build results including the review package SHA-256.
    """
    # Verify all required files exist
    required = {
        "delivery_package": delivery_package,
        "sha_file": sha_file,
        "authority_json": authority_json,
        "evidence_zip": evidence_zip,
        "sidecar": sidecar,
        "manifest": manifest,
        "supervisor_readme": supervisor_readme,
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required files: {missing}")

    if final_response_summary and not final_response_summary.is_file():
        print(f"WARNING: final-response-summary not found: {final_response_summary}", file=sys.stderr)
        final_response_summary = None

    # Validate evidence ZIP SHA matches authority JSON
    actual_evidence_sha = _sha256(evidence_zip)
    authority_data = _verify_authority_json(authority_json, expected_inner_sha=actual_evidence_sha)

    # Validate sidecar
    with open(sidecar, "r", encoding="utf-8") as f:
        sidecar_data = json.load(f)
    sidecar_claimed_sha = sidecar_data.get("sha256", "")
    if sidecar_claimed_sha != actual_evidence_sha:
        raise ValueError(
            f"Sidecar SHA mismatch: sidecar claims {sidecar_claimed_sha[:16]}... "
            f"but evidence ZIP actual SHA is {actual_evidence_sha[:16]}..."
        )

    # Validate standalone SHA file
    with open(sha_file, "r", encoding="utf-8") as f:
        sha_line = f.read().strip()
    actual_delivery_sha = _sha256(delivery_package)
    if not sha_line.startswith(actual_delivery_sha):
        raise ValueError(
            f"Standalone SHA file mismatch: file records {sha_line[:16]}... "
            f"but delivery package actual SHA is {actual_delivery_sha[:16]}..."
        )

    # Compute all included file SHAs for the review package manifest
    included_files: dict[str, dict] = {}
    files_to_include = [
        delivery_package,
        sha_file,
        authority_json,
        evidence_zip,
        sidecar,
        manifest,
        supervisor_readme,
    ]
    if final_response_summary:
        files_to_include.append(final_response_summary)

    for fp in files_to_include:
        sha = _sha256(fp)
        included_files[fp.name] = {
            "sha256": sha,
            "size_bytes": fp.stat().st_size,
        }

    # Derive run_id
    stem = evidence_zip.stem  # e.g. "r76-pass1-final"
    run_id = stem.split("-")[0].upper()  # "R76"

    # Build review package manifest
    review_manifest = {
        "review_package_version": "1.0",
        "sprint_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_authority": authority_data,
        "included_files": included_files,
        "validation_checks": {
            "evidence_zip_sha_verified": True,
            "sidecar_proves_evidence_zip": True,
            "delivery_sha_file_verified": True,
            "authority_json_schema_valid": True,
        },
        "supervisor_instructions": (
            "Upload ONLY this supervisor-review-package.zip. "
            "Do NOT upload the inner delivery package or evidence ZIP separately. "
            "All required authority files are inside this package."
        ),
    }

    review_manifest_path = output.parent / output.name.replace(
        "-supervisor-review-package.zip", "-review-package-manifest.json"
    )
    if review_manifest_path == output:
        review_manifest_path = output.parent / (output.stem + "-review-package-manifest.json")

    with open(review_manifest_path, "w", encoding="utf-8") as f:
        json.dump(review_manifest, f, indent=2)

    # Include review-package-manifest.json in its own SHA listing
    review_manifest_sha = _sha256(review_manifest_path)
    included_files[review_manifest_path.name] = {
        "sha256": review_manifest_sha,
        "size_bytes": review_manifest_path.stat().st_size,
    }

    # Build the review package ZIP (includes flat files + optional top-level directories)
    extra_dir_entry_count = 0
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in files_to_include:
            zf.write(fp, fp.name)
        zf.write(review_manifest_path, review_manifest_path.name)
        # Add extra top-level directories for self-containment
        if extra_top_level_dirs:
            for dir_name, dir_path in extra_top_level_dirs:
                if dir_path.is_dir():
                    for item in sorted(dir_path.rglob("*")):
                        if item.is_file():
                            rel = item.relative_to(dir_path)
                            arc_name = f"{dir_name}/{rel.as_posix()}"
                            zf.write(item, arc_name)
                            extra_dir_entry_count += 1
                    print(f"  Added top-level dir: {dir_name}/ ({sum(1 for _ in dir_path.rglob('*') if _.is_file())} files)")

    review_pkg_sha = _sha256(output)
    review_pkg_size = output.stat().st_size
    entry_count = len(included_files) + extra_dir_entry_count

    # Generate standalone SHA file for the review package
    review_sha_path = output.parent / output.name.replace(".zip", ".sha256.txt")
    with open(review_sha_path, "w", encoding="utf-8") as f:
        f.write(f"{review_pkg_sha}  {output.name}\n")

    print(f"Supervisor review package built: {output}")
    print(f"  Review package SHA-256: {review_pkg_sha}")
    print(f"  Review package size: {review_pkg_size:,} bytes")
    print(f"  Entry count: {entry_count}")
    print(f"  Standalone SHA: {review_sha_path.name}")
    print(f"  Included files:")
    for name, info in included_files.items():
        print(f"    {name}: {info['sha256'][:16]}... ({info['size_bytes']:,} bytes)")
    print(f"REVIEW_PACKAGE_BUILD: PASS")

    return {
        "review_package_path": str(output),
        "review_package_sha256": review_pkg_sha,
        "review_package_size_bytes": review_pkg_size,
        "review_package_entry_count": entry_count,
        "standalone_sha_path": str(review_sha_path),
        "review_manifest_path": str(review_manifest_path),
        "included_files": included_files,
        "validation_result": "PASS",
    }


def main():
    parser = argparse.ArgumentParser(description="Build supervisor review package")
    parser.add_argument("--delivery-package", required=True, help="Outer delivery package ZIP")
    parser.add_argument("--sha-file", required=True, help="Standalone outer SHA file (.sha256.txt)")
    parser.add_argument("--authority-json", required=True, help="Final artifact authority JSON")
    parser.add_argument("--evidence-zip", required=True, help="Inner evidence ZIP")
    parser.add_argument("--sidecar", required=True, help="Sidecar proof JSON")
    parser.add_argument("--manifest", required=True, help="Delivery manifest JSON")
    parser.add_argument("--supervisor-readme", required=True, help="Supervisor inspection readme")
    parser.add_argument("--final-response-summary", default="", help="Final response summary MD")
    parser.add_argument("--output", required=True, help="Output review package ZIP path")
    parser.add_argument(
        "--extra-top-level-dirs",
        default="",
        help=(
            "Comma-separated name:path pairs of directories to include at top level. "
            "Example: 'package-artifacts:.local/r84-package-artifacts,raw-test-logs:.local/r84-raw-logs'"
        ),
    )

    args = parser.parse_args()

    final_response = Path(args.final_response_summary) if args.final_response_summary else None

    # Parse extra top-level dirs
    extra_dirs: list[tuple[str, Path]] | None = None
    if args.extra_top_level_dirs:
        extra_dirs = []
        for entry in args.extra_top_level_dirs.split(","):
            entry = entry.strip()
            if ":" in entry:
                name, path_str = entry.split(":", 1)
                extra_dirs.append((name.strip(), Path(path_str.strip())))

    build_supervisor_review_package(
        delivery_package=Path(args.delivery_package),
        sha_file=Path(args.sha_file),
        authority_json=Path(args.authority_json),
        evidence_zip=Path(args.evidence_zip),
        sidecar=Path(args.sidecar),
        manifest=Path(args.manifest),
        supervisor_readme=Path(args.supervisor_readme),
        final_response_summary=final_response,
        output=Path(args.output),
        extra_top_level_dirs=extra_dirs,
    )


if __name__ == "__main__":
    main()
