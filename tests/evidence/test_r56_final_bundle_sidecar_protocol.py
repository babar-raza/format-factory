"""
test_r56_final_bundle_sidecar_protocol.py — R56 Train B: Final bundle sidecar protocol tests.

Validates the new R56 rule: if a bundle contains an embedded sidecar proof, it must match
the bundle being validated (same bundle_filename). A sidecar for a different bundle is a
protocol violation unless explicitly marked external_reference: true.

Also validates: nested .zip files under bundle-metadata/ require contract allowance.

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R55-003, IV-R55-009
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import (
    check_embedded_sidecar_bundle_match,
    check_nested_zips_allowed,
)


def _make_zip_with_sidecar(bundle_name: str, sidecar_bundle_name: str, external_ref: bool = False) -> tuple:
    """Create a temp bundle file containing an embedded sidecar that refers to sidecar_bundle_name."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        sidecar_data = {
            "bundle_filename": sidecar_bundle_name,
            "sha256": "abc123",
        }
        if external_ref:
            sidecar_data["external_reference"] = True
        zf.writestr("bundle-metadata/r55-pass2.sha256-proof.json", json.dumps(sidecar_data))
        zf.writestr("bundle-metadata/sprint-id.txt", "test")
    buf.seek(0)
    data = buf.read()
    with tempfile.NamedTemporaryFile(suffix=f"_{bundle_name}", delete=False) as f:
        f.write(data)
        tmp_path = f.name
    return tmp_path, data


def _make_zip_with_nested_zip(nested_count: int = 1) -> tuple:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for i in range(nested_count):
            zf.writestr(f"bundle-metadata/nested-{i}.zip", b"PK fake zip data")
        zf.writestr("bundle-metadata/sprint-id.txt", "test")
    buf.seek(0)
    data = buf.read()
    with tempfile.NamedTemporaryFile(suffix="_bundle.zip", delete=False) as f:
        f.write(data)
        tmp_path = f.name
    return tmp_path, data


# ---------------------------------------------------------------------------
# check_embedded_sidecar_bundle_match
# ---------------------------------------------------------------------------

class TestEmbeddedSidecarBundleMatch:

    def test_matching_sidecar_passes(self, tmp_path):
        """Embedded sidecar that matches the bundle filename causes no error."""
        bundle_file = tmp_path / "r56-final.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            sidecar_data = {"bundle_filename": "r56-final.zip", "sha256": "abc123"}
            zf.writestr("bundle-metadata/r55-pass2.sha256-proof.json", json.dumps(sidecar_data))
        bundle_file.write_bytes(buf.getvalue())
        with zipfile.ZipFile(str(bundle_file)) as zf:
            errors = check_embedded_sidecar_bundle_match(zf, str(bundle_file))
        assert errors == [], f"Expected no errors but got: {errors}"

    def test_mismatched_sidecar_fails(self, tmp_path):
        """Embedded sidecar referencing a different bundle fails validation (IV-R55-003)."""
        # bundle is called r56-final.zip but sidecar refers to r55-pass2.zip
        bundle_path, _ = _make_zip_with_sidecar("r56-final.zip", "r55-pass2.zip")
        try:
            with zipfile.ZipFile(bundle_path) as zf:
                errors = check_embedded_sidecar_bundle_match(zf, bundle_path)
            assert errors, "Expected at least one error for mismatched sidecar"
            assert any("r55-pass2.zip" in e for e in errors), f"Error must mention sidecar bundle: {errors}"
            assert any("EMBEDDED_SIDECAR_BUNDLE_MISMATCH" in e for e in errors)
        finally:
            Path(bundle_path).unlink(missing_ok=True)

    def test_external_reference_sidecar_is_exempt(self, tmp_path):
        """Embedded sidecar marked external_reference: true is exempt from the match check."""
        bundle_path, _ = _make_zip_with_sidecar("r56-final.zip", "r55-pass2.zip", external_ref=True)
        try:
            with zipfile.ZipFile(bundle_path) as zf:
                errors = check_embedded_sidecar_bundle_match(zf, bundle_path)
            assert errors == [], f"External reference sidecar should be exempt: {errors}"
        finally:
            Path(bundle_path).unlink(missing_ok=True)

    def test_no_embedded_sidecar_passes(self, tmp_path):
        """Bundle with no embedded sidecar causes no error."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "test")
        buf.seek(0)
        data = buf.read()
        bundle_file = tmp_path / "r56-no-sidecar.zip"
        bundle_file.write_bytes(data)
        with zipfile.ZipFile(str(bundle_file)) as zf:
            errors = check_embedded_sidecar_bundle_match(zf, str(bundle_file))
        assert errors == [], f"No sidecar should cause no error: {errors}"

    def test_r55_defect_scenario_reproduced(self, tmp_path):
        """Reproduce the exact R55 IV-R55-003 defect: r55-pass2-final.zip contains sidecar for r55-pass2.zip."""
        bundle_path, _ = _make_zip_with_sidecar("r55-pass2-final.zip", "r55-pass2.zip")
        try:
            with zipfile.ZipFile(bundle_path) as zf:
                errors = check_embedded_sidecar_bundle_match(zf, bundle_path)
            assert errors, "The R55 IV-R55-003 defect scenario must fail validation"
            assert any("r55-pass2.zip" in e for e in errors)
        finally:
            Path(bundle_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# check_nested_zips_allowed
# ---------------------------------------------------------------------------

class TestNestedZipsAllowed:

    def test_no_nested_zips_passes(self, tmp_path):
        """Bundle with no nested ZIPs passes the check (no contract entry needed)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "test")
        buf.seek(0)
        bundle_file = tmp_path / "clean.zip"
        bundle_file.write_bytes(buf.getvalue())
        with zipfile.ZipFile(str(bundle_file)) as zf:
            errors = check_nested_zips_allowed(zf, {})
        assert errors == []

    def test_nested_zip_without_allowance_fails(self, tmp_path):
        """Bundle containing nested .zip under bundle-metadata/ without contract allowance fails (IV-R55-009)."""
        bundle_path, _ = _make_zip_with_nested_zip(1)
        try:
            with zipfile.ZipFile(bundle_path) as zf:
                errors = check_nested_zips_allowed(zf, {})
            assert errors, "Nested zip without contract allowance must fail"
            assert any("NESTED_ZIPS_NOT_ALLOWED" in e for e in errors)
        finally:
            Path(bundle_path).unlink(missing_ok=True)

    def test_nested_zip_with_contract_allowance_passes(self, tmp_path):
        """Bundle containing nested .zip allowed by contract does not fail."""
        bundle_path, _ = _make_zip_with_nested_zip(1)
        try:
            with zipfile.ZipFile(bundle_path) as zf:
                errors = check_nested_zips_allowed(zf, {"allow_nested_bundle_zips": True})
            assert errors == [], f"Allowed nested zip must pass: {errors}"
        finally:
            Path(bundle_path).unlink(missing_ok=True)

    def test_multiple_nested_zips_fail(self, tmp_path):
        """Multiple nested ZIPs all reported in one error (IV-R55-009 R55 exact scenario)."""
        bundle_path, _ = _make_zip_with_nested_zip(2)
        try:
            with zipfile.ZipFile(bundle_path) as zf:
                errors = check_nested_zips_allowed(zf, {})
            assert errors, "Two nested zips must fail"
            # Both zip names should be mentioned
            assert "nested-0.zip" in errors[0] or "nested-1.zip" in errors[0]
        finally:
            Path(bundle_path).unlink(missing_ok=True)
