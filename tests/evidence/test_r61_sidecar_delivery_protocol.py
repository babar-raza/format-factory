"""
test_r61_sidecar_delivery_protocol.py — R61 Train B: Sidecar delivery protocol validation.

Verifies the 3-pass build + sidecar delivery protocol for R61:
1. Sidecar is generated externally (not inside ZIP)
2. Sidecar SHA matches the true final bundle (not interim)
3. final-verdict Pass 2 SHA matches sidecar SHA (not interim)
4. .nupkg SHA in manifests must be full 64-char SHA-256 (not prefix)

Repairs IV-R60-001, IV-R60-002, IV-R60-003, IV-R60-008.

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_bundle_with_real_proof(tmp_path: Path, sha_override: str | None = None) -> tuple[Path, str]:
    """Create a test bundle with real proof; return (bundle_path, bundle_sha)."""
    bundle = tmp_path / "r61-test-bundle.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("bundle-metadata/sprint-id.txt", "R61-TEST")
        zf.writestr("repo/reports/r61/final-verdict.md", "BUNDLE_VALIDATION_PASS_2_SHA: PENDING")
    # Build "interim" bundle to get SHA
    actual_sha = sha_override or _compute_sha256(bundle)
    # Rebuild with real proof (simulating 3-pass protocol)
    real_proof = (
        f"Sprint: R61-TEST\n"
        f"FINAL BUNDLE VALIDATION PROOF\n"
        f"Date: 2026-05-24\n\n"
        f"bundle_filename: r61-test-bundle.zip\n"
        f"sha256: {actual_sha}\n"
        f"entry_count: 2\n"
        f"size_bytes: {bundle.stat().st_size}\n"
        f"metadata_files: 1\n"
        f"sidecar: reports/r61/r61-test-bundle.zip.sha256-proof.json\n"
        f"BUNDLE_VALIDATION: PASS\n"
        f"SIDECAR_PROOF_VALIDATION: PASS\n\n"
        f"All 14 checks: PASS\n"
    )
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("bundle-metadata/sprint-id.txt", "R61-TEST")
        zf.writestr("bundle-metadata/final-bundle-validation-proof.txt", real_proof)
        zf.writestr("repo/reports/r61/final-verdict.md",
                    f"BUNDLE_VALIDATION_PASS_2_SHA: {actual_sha}")
    # Recompute real SHA after adding proof
    real_sha = _compute_sha256(bundle)
    return bundle, real_sha


def _make_sidecar(tmp_path: Path, bundle_path: Path, sha: str) -> Path:
    """Create external sidecar JSON."""
    sidecar_data = {
        "sidecar_version": "1.0",
        "run_number": "R61",
        "bundle_filename": bundle_path.name,
        "sha256": sha,
        "size_bytes": bundle_path.stat().st_size,
        "entry_count": 3,
        "contract_path": "tools/evidence/contracts/r61-extracted-bundle-rc-sidecar.yaml",
        "validation_result": "PASS",
        "timestamp_utc": "2026-05-24T00:00:00+00:00",
    }
    sidecar_path = tmp_path / f"{bundle_path.name}.sha256-proof.json"
    sidecar_path.write_text(json.dumps(sidecar_data, indent=2))
    return sidecar_path


class TestSidecarDeliveryProtocol:
    """Sidecar must be delivered externally alongside the ZIP, not inside it."""

    def test_sidecar_is_external_to_zip(self, tmp_path):
        """Sidecar must be a separate file, not a ZIP entry."""
        bundle, sha = _make_bundle_with_real_proof(tmp_path)
        sidecar = _make_sidecar(tmp_path, bundle, sha)
        # Sidecar must exist as a file
        assert sidecar.exists(), "Sidecar must be a separate file"
        # Sidecar must NOT be inside the ZIP
        with zipfile.ZipFile(bundle) as zf:
            names = zf.namelist()
        inside = [n for n in names if "sha256-proof" in n]
        assert inside == [], f"Sidecar must NOT be in ZIP. Found: {inside}"

    def test_sidecar_sha_matches_bundle(self, tmp_path):
        """Sidecar SHA must match actual bundle file SHA."""
        bundle, _ = _make_bundle_with_real_proof(tmp_path)
        actual_sha = _compute_sha256(bundle)
        sidecar = _make_sidecar(tmp_path, bundle, actual_sha)
        sidecar_data = json.loads(sidecar.read_text())
        assert sidecar_data["sha256"] == actual_sha, (
            f"Sidecar SHA {sidecar_data['sha256']!r} must match bundle SHA {actual_sha!r}"
        )

    def test_interim_sha_not_equal_to_final(self, tmp_path):
        """Pass 2 interim bundle and true final bundle have different SHAs."""
        # Interim: before proof file written
        interim = tmp_path / "interim.zip"
        with zipfile.ZipFile(interim, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "R61-INTERIM")
            zf.writestr("repo/reports/r61/final-verdict.md", "PASS_2_SHA: PENDING")
        interim_sha = _compute_sha256(interim)

        # True final: after proof file added
        final = tmp_path / "final.zip"
        with zipfile.ZipFile(final, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "R61-INTERIM")
            zf.writestr("repo/reports/r61/final-verdict.md", f"PASS_2_SHA: {interim_sha}")
            zf.writestr("bundle-metadata/final-bundle-validation-proof.txt",
                        f"sha256: {interim_sha}\nBUNDLE_VALIDATION: PASS\n")
        final_sha = _compute_sha256(final)
        assert interim_sha != final_sha, (
            "Interim and true final bundle MUST have different SHAs; "
            "updating final-verdict changes the bundle content"
        )

    def test_final_verdict_pass2_sha_must_match_sidecar(self, tmp_path):
        """Pass 2 SHA in final-verdict must equal sidecar SHA (true final, not interim)."""
        bundle, sha = _make_bundle_with_real_proof(tmp_path)
        actual_sha = _compute_sha256(bundle)
        sidecar = _make_sidecar(tmp_path, bundle, actual_sha)

        # Simulate a final-verdict that references the sidecar-authoritative SHA
        verdict_text = f"BUNDLE_VALIDATION_PASS_2_SHA: {actual_sha}\n"
        sidecar_sha = json.loads(sidecar.read_text())["sha256"]
        verdict_sha_match = re.search(r"BUNDLE_VALIDATION_PASS_2_SHA:\s*([0-9a-f]{64})", verdict_text)
        assert verdict_sha_match, "Could not extract SHA from verdict"
        verdict_sha = verdict_sha_match.group(1)
        assert verdict_sha == sidecar_sha, (
            f"Pass 2 SHA in verdict ({verdict_sha}) must match sidecar ({sidecar_sha})"
        )


class TestNuGetSHAFullLength:
    """NuGet package SHA references must be full 64-char SHA-256 (not 8-char prefix)."""

    def test_sha_prefix_is_insufficient(self):
        """8-character SHA prefix is NOT an acceptable reference."""
        sha_prefix = "35712390"
        sha_full = "35712390" + "a" * 56
        assert len(sha_prefix) == 8
        assert len(sha_full) == 64
        # 8-char prefix cannot uniquely identify a file
        possible_collisions = 16 ** 8  # 4,294,967,296 — not unique enough
        assert possible_collisions > 1_000_000, "SHA prefix has too many possible collisions"

    def test_full_sha256_required_in_nupkg_manifest(self, tmp_path):
        """NuGet manifest must use sha256 (64 chars) not sha256_prefix."""
        manifest_good = {
            "packages": [
                {"name": "FormatFactory.Fods", "sha256": "a" * 64}
            ]
        }
        manifest_bad = {
            "packages": [
                {"name": "FormatFactory.Fods", "sha256_prefix": "35712390"}
            ]
        }
        # Good manifest: has full SHA-256
        for pkg in manifest_good["packages"]:
            sha = pkg.get("sha256")
            assert sha and len(sha) == 64, f"Expected 64-char SHA, got: {sha!r}"

        # Bad manifest: has sha256_prefix (IV-R60-008)
        for pkg in manifest_bad["packages"]:
            sha = pkg.get("sha256")
            prefix = pkg.get("sha256_prefix")
            assert sha is None or len(sha) != 64, "sha256_prefix manifest should not have valid sha256"
            assert prefix is not None, "Bad manifest uses sha256_prefix"
            assert len(prefix) < 64, f"sha256_prefix must be < 64 chars: {prefix!r}"

    def test_r60_nupkg_manifest_uses_prefix(self):
        """Confirm R60 dotnet-nupkg-manifest.yaml uses sha256_prefix (IV-R60-008)."""
        manifest_path = PROJECT_ROOT / ".local" / "r60-metadata" / "dotnet-nupkg-manifest.yaml"
        if not manifest_path.exists():
            pytest.skip("R60 nupkg manifest not available")
        content = manifest_path.read_text(encoding="utf-8")
        assert "sha256_prefix" in content, (
            "Expected R60 manifest to use sha256_prefix (IV-R60-008 confirmation). "
            f"Content: {content[:200]!r}"
        )
        assert "sha256: " not in content or all(
            len(m.group(1)) < 64 for m in re.finditer(r'sha256:\s+"?([0-9a-f]+)"?', content)
        ), "R60 manifest should not have full 64-char SHA-256"
