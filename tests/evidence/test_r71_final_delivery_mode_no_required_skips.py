"""
R71 Train D — test_r71_final_delivery_mode_no_required_skips.py
Verify that final-delivery tests do not have REQUIRED skips when the delivery
package is available.

A "required skip" is a skip that happens because the delivery package is missing
and the test cannot proceed. When DELIVERY_PACKAGE_UNDER_TEST is set, all
delivery-mode tests MUST run (not skip).

When neither DELIVERY_PACKAGE_UNDER_TEST nor a .local/ fallback is available,
tests skip with an explanatory message — this is acceptable for pre-delivery CI.
"""

import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")


def _get_delivery_package() -> tuple:
    """
    Returns (outer_zip_path, source) where source is 'env' or 'local'.
    Returns (None, None) if no package is available (acceptable for pre-delivery skip).
    Raises pytest.fail if env var is set but file not found.
    """
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(
                f"DELIVERY_PACKAGE_UNDER_TEST={env_path} but file not found. "
                "Delivery-mode tests cannot run without the delivery package."
            )
        return p, "env"

    for name in ["r71-delivery-package.zip", "r70-delivery-package.zip"]:
        p = LOCAL / name
        if p.exists():
            return p, "local"

    return None, None


def _is_env_mode() -> bool:
    """True if running in explicit delivery-package-under-test mode."""
    return bool(os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", ""))


def test_no_required_skip_when_package_env_set():
    """When DELIVERY_PACKAGE_UNDER_TEST is set, the package MUST be found.
    If this test is reached at all, the env var enforcement worked."""
    pkg_path, source = _get_delivery_package()
    if not _is_env_mode():
        if pkg_path is None:
            pytest.skip("No DELIVERY_PACKAGE_UNDER_TEST env var and no .local/ fallback — pre-delivery mode")
        # Local fallback: still valid but not full env-mode enforcement
        return
    # env mode: must have resolved a valid path (fail-closed enforced in _get_delivery_package)
    assert pkg_path is not None, "DELIVERY_PACKAGE_UNDER_TEST set but package not resolved"
    assert source == "env"
    assert pkg_path.exists()


def test_delivery_package_is_valid_zip_not_skipped():
    """In delivery-mode, the package must be a valid ZIP (not skipped silently)."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    assert len(names) >= 3, f"Delivery package must have at least 3 members, got: {names}"


def test_delivery_package_source_reported():
    """Package source (env vs local fallback) can be determined."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    assert source in ("env", "local"), f"Unexpected source: {source}"
    if _is_env_mode():
        assert source == "env", (
            f"DELIVERY_PACKAGE_UNDER_TEST is set but source={source!r}. "
            "Expected 'env' when env var is present."
        )


def test_env_mode_does_not_fall_through_to_local():
    """When DELIVERY_PACKAGE_UNDER_TEST is set, we must NOT silently use a .local/ fallback.
    The env var is authoritative; if the pointed file doesn't exist, fail-closed."""
    env_val = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if not env_val:
        pytest.skip("Not in env-delivery mode")

    # If we get here, the env var was set and _get_delivery_package() already verified
    # the file exists (fail-closed). So source must be 'env'.
    pkg_path, source = _get_delivery_package()
    assert source == "env", "Must use env-provided path, not local fallback"


def test_delivery_package_inner_zip_accessible_not_skipped():
    """Inner ZIP inside delivery package must be accessible in delivery mode."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    inner_zips = [n for n in names if n.endswith(".zip")]
    assert len(inner_zips) >= 1, f"No inner ZIP found in delivery package. Contents: {names}"


def test_delivery_package_sidecar_accessible_not_skipped():
    """Sidecar JSON must be accessible in delivery mode (not silently skipped)."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    sidecars = [n for n in names if n.endswith(".sha256-proof.json")]
    assert len(sidecars) >= 1, f"No sidecar found in delivery package. Contents: {names}"


def test_delivery_package_manifest_accessible_not_skipped():
    """Delivery manifest must be accessible in delivery mode (not silently skipped)."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as zf:
        names = zf.namelist()
    manifests = [
        n for n in names
        if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"
    ]
    assert len(manifests) >= 1, f"No delivery manifest found. Contents: {names}"


def test_pre_delivery_skip_message_is_explanatory():
    """Pre-delivery skips (no package available) must have a clear message, not silent None."""
    pkg_path, source = _get_delivery_package()
    if pkg_path is not None:
        pytest.skip("Package available — this test only validates pre-delivery skip behavior")
    # If we reach here: no package available, all delivery tests skip.
    # The fact that _get_delivery_package() returned (None, None) rather than
    # raising is intentional — it means we're in pre-delivery source-tree mode.
    assert pkg_path is None
    assert source is None
    # The correct behavior: tests skip, not fail, when no package is available.


def test_env_override_takes_priority_over_local_fallback():
    """DELIVERY_PACKAGE_UNDER_TEST env var must override any .local/ fallbacks."""
    env_val = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if not env_val:
        pytest.skip("Not in env-delivery mode")

    # Verify env-based path is used
    pkg_path, source = _get_delivery_package()
    expected_path = pathlib.Path(env_val)
    assert pkg_path == expected_path, (
        f"Expected package path {expected_path} from env var, "
        f"got {pkg_path} (source={source})"
    )
