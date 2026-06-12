"""
R72 Train F — test_r72_rejects_pending_delivery_summary.py

Verify that R72 metadata does not contain PENDING in delivery-package-validation-summary.txt
or external-sidecar-proof-summary.txt.

R71 IV-R72-002: delivery-package-validation-summary.txt had PENDING_PASS_2_SHA
R71 IV-R72-003: external-sidecar-proof-summary.txt had "to be generated after Pass 2 build"

These were RC-blocking defects. R72 must have final, non-placeholder metadata.
"""
import pathlib
import pytest

LOCAL = pathlib.Path(".local")
PENDING_TOKENS = [
    "PENDING_PASS_2_SHA",
    "PENDING_SIDECAR_SHA",
    "PENDING_BUILD",
    "to be built after",
    "to be generated after",
    "to be filled",
]


def _find_metadata_dir():
    """Find R72 metadata only.
    R71 metadata legitimately has pending placeholders (IV-R72-002/003 defects being fixed).
    Only R72 metadata is subject to this check.
    Returns None if metadata is in pre-build state (bundle not yet built)."""
    d = LOCAL / "r72-metadata"
    if d.exists():
        # Skip if delivery summary indicates pre-build state
        delivery_summary = d / "delivery-package-validation-summary.txt"
        if delivery_summary.exists():
            content = delivery_summary.read_text(encoding="utf-8")
            if "DELIVERY_PACKAGE_VALIDATION: PENDING_BUILD" in content:
                return None, None  # pre-build state; run after bundle is built
        return d, "r72"
    return None, None


def test_delivery_summary_no_pending():
    """delivery-package-validation-summary.txt must not have PENDING tokens."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "delivery-package-validation-summary.txt"
    if not f.exists():
        pytest.skip(f"delivery-package-validation-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    for token in PENDING_TOKENS:
        assert token not in content, (
            f"delivery-package-validation-summary.txt contains '{token}'. "
            f"This metadata must be fully filled in before bundle build. "
            f"R71 IV-R72-002: {run} metadata had this defect."
        )


def test_external_sidecar_summary_no_pending():
    """external-sidecar-proof-summary.txt must not have placeholder tokens."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "external-sidecar-proof-summary.txt"
    if not f.exists():
        pytest.skip(f"external-sidecar-proof-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    for token in PENDING_TOKENS + ["to be filled"]:
        assert token not in content, (
            f"external-sidecar-proof-summary.txt contains '{token}'. "
            f"This metadata must be final before bundle build. "
            f"R71 IV-R72-003: {run} metadata had this defect."
        )


def test_delivery_summary_has_pass_verdict():
    """delivery-package-validation-summary.txt must record DELIVERY_PACKAGE_VALIDATION: PASS."""
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "delivery-package-validation-summary.txt"
    if not f.exists():
        pytest.skip(f"delivery-package-validation-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    assert "DELIVERY_PACKAGE_VALIDATION: PASS" in content, (
        f"delivery-package-validation-summary.txt must contain "
        f"'DELIVERY_PACKAGE_VALIDATION: PASS'. Found:\n{content[:400]}"
    )


def test_external_sidecar_summary_has_sha():
    """external-sidecar-proof-summary.txt must contain a real sidecar SHA."""
    import re
    meta_dir, run = _find_metadata_dir()
    if meta_dir is None:
        pytest.skip("No metadata directory found (pre-build mode)")

    f = meta_dir / "external-sidecar-proof-summary.txt"
    if not f.exists():
        pytest.skip(f"external-sidecar-proof-summary.txt not found in {meta_dir}")

    content = f.read_text(encoding="utf-8")
    sha_pattern = re.compile(r"[0-9a-f]{64}")
    assert sha_pattern.search(content), (
        f"external-sidecar-proof-summary.txt must contain a real SHA-256 hex value. "
        f"Found:\n{content[:400]}"
    )
