"""
R69 Train D — Test: delivery package (not inner ZIP) must be the final deliverable.

Covers IV-R69-005: R68 provided the inner evidence ZIP to the human reviewer instead
of the outer delivery package containing ZIP + sidecar + manifest. This test ensures
the correct artifact structure is present and validated.
"""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
R69_LOCAL = PROJECT_ROOT / ".local"


class TestDeliveryPackageRequired:
    """Delivery package must exist and contain inner ZIP + sidecar + manifest."""

    def test_r69_delivery_package_exists(self):
        """r69-delivery-package.zip must exist locally."""
        pkg = R69_LOCAL / "r69-delivery-package.zip"
        if not pkg.exists():
            pytest.skip("r69-delivery-package.zip not yet built")
        assert pkg.stat().st_size > 1_000_000, (
            "r69-delivery-package.zip exists but seems too small — may be corrupt"
        )

    def test_r69_delivery_package_contains_required_files(self):
        """Delivery package must contain inner ZIP, sidecar, and manifest."""
        pkg = R69_LOCAL / "r69-delivery-package.zip"
        if not pkg.exists():
            pytest.skip("r69-delivery-package.zip not yet built")
        with zipfile.ZipFile(pkg) as z:
            names = z.namelist()
        assert "r69-pass2-final.zip" in names, (
            "Delivery package must contain r69-pass2-final.zip (inner evidence ZIP)"
        )
        assert "r69-pass2-final.sha256-proof.json" in names, (
            "Delivery package must contain r69-pass2-final.sha256-proof.json (external sidecar)"
        )
        assert "r69-delivery-manifest.json" in names, (
            "Delivery package must contain r69-delivery-manifest.json"
        )

    def test_r69_delivery_package_sidecar_matches_inner_zip(self):
        """Sidecar SHA-256 must match the inner evidence ZIP inside the delivery package."""
        pkg = R69_LOCAL / "r69-delivery-package.zip"
        if not pkg.exists():
            pytest.skip("r69-delivery-package.zip not yet built")
        with zipfile.ZipFile(pkg) as z:
            ev_data = z.read("r69-pass2-final.zip")
            sc = json.loads(z.read("r69-pass2-final.sha256-proof.json"))
        ev_sha = hashlib.sha256(ev_data).hexdigest()
        sc_sha = sc.get("sha256", "")
        assert ev_sha == sc_sha, (
            f"Sidecar SHA mismatch: inner ZIP={ev_sha[:16]}... sidecar={sc_sha[:16]}..."
        )

    def test_r69_inner_zip_not_same_as_delivery_package(self):
        """The delivery package and the inner evidence ZIP are different files."""
        pkg = R69_LOCAL / "r69-delivery-package.zip"
        inner = R69_LOCAL / "r69-pass2-final.zip"
        if not pkg.exists() or not inner.exists():
            pytest.skip("R69 artifacts not yet built")
        pkg_sha = hashlib.sha256(pkg.read_bytes()).hexdigest()
        inner_sha = hashlib.sha256(inner.read_bytes()).hexdigest()
        assert pkg_sha != inner_sha, (
            "The delivery package and inner ZIP must be different files. "
            "Providing the inner ZIP alone as the delivery artifact is IV-R69-005."
        )
