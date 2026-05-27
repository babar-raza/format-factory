"""
R70 Train D — test_r70_final_verdict_hash_truth.py
Verify final-verdict.md SHAs match actual delivery artifacts.
"""

import hashlib
import pathlib
import re
import pytest

LOCAL = pathlib.Path(".local")
FINAL_VERDICT = pathlib.Path("reports/r69/final-verdict.md")
INNER_ZIP = LOCAL / "r69-pass2-final.zip"
DELIVERY_PKG = LOCAL / "r69-delivery-package.zip"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_sha(verdict_text, label):
    """Extract SHA value from 'LABEL: <sha>' lines in final-verdict.md."""
    m = re.search(rf"{re.escape(label)}:\s*([0-9a-f]{{64}})", verdict_text)
    return m.group(1) if m else None


def test_final_verdict_exists():
    """R69 final-verdict.md must exist."""
    assert FINAL_VERDICT.exists(), f"Missing: {FINAL_VERDICT}"


def test_pass2_sha_matches_inner_zip():
    """final-verdict BUNDLE_VALIDATION_PASS_2_SHA must match actual inner ZIP."""
    if not FINAL_VERDICT.exists():
        pytest.skip("final-verdict.md missing")
    if not INNER_ZIP.exists():
        pytest.skip("r69-pass2-final.zip not present (pre-build)")
    text = FINAL_VERDICT.read_text()
    recorded = _extract_sha(text, "BUNDLE_VALIDATION_PASS_2_SHA")
    actual = _sha256(INNER_ZIP)
    assert recorded is not None, "BUNDLE_VALIDATION_PASS_2_SHA not found or not 64-char hex in final-verdict.md"
    assert recorded == actual, (
        f"BUNDLE_VALIDATION_PASS_2_SHA={recorded!r} != actual inner ZIP SHA={actual!r}"
    )


def test_sidecar_sha_matches_pass2_sha():
    """SIDECAR_SHA must equal BUNDLE_VALIDATION_PASS_2_SHA (sidecar records inner ZIP SHA)."""
    if not FINAL_VERDICT.exists():
        pytest.skip("final-verdict.md missing")
    text = FINAL_VERDICT.read_text()
    pass2 = _extract_sha(text, "BUNDLE_VALIDATION_PASS_2_SHA")
    sidecar = _extract_sha(text, "SIDECAR_SHA")
    assert pass2 is not None, "BUNDLE_VALIDATION_PASS_2_SHA not found"
    assert sidecar is not None, "SIDECAR_SHA not found"
    assert pass2 == sidecar, (
        f"BUNDLE_VALIDATION_PASS_2_SHA={pass2!r} != SIDECAR_SHA={sidecar!r}"
    )


def test_delivery_package_sha_matches_actual():
    """DELIVERY_PACKAGE_SHA must match actual delivery package file."""
    if not FINAL_VERDICT.exists():
        pytest.skip("final-verdict.md missing")
    if not DELIVERY_PKG.exists():
        pytest.skip("r69-delivery-package.zip not present (pre-build)")
    text = FINAL_VERDICT.read_text()
    recorded = _extract_sha(text, "DELIVERY_PACKAGE_SHA")
    actual = _sha256(DELIVERY_PKG)
    assert recorded is not None, "DELIVERY_PACKAGE_SHA not found or not 64-char hex in final-verdict.md"
    assert recorded == actual, (
        f"DELIVERY_PACKAGE_SHA={recorded!r} != actual delivery package SHA={actual!r}"
    )
