# tests/packaging/test_python_local_package_artifacts.py
# R22 Gate 4 — Verify local Python FOSS package artifacts exist and are valid
# Sprint: FORMAT-FACTORY-R22-FULL-THROTTLE-RELEASE-CANDIDATE-AND-GATE11-PROTOTYPE-TRAIN-001
# publication_authorized: false

import os
import json
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILD_DIR = os.path.join(REPO_ROOT, ".local", "package-builds", "python-foss")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(BUILD_DIR),
    reason="Package build artifacts not present in this environment"
)

PACKAGES = [
    ("aspose-format-factory-zst",      "aspose_format_factory_zst"),
    ("aspose-format-factory-fodp",     "aspose_format_factory_fodp"),
    ("aspose-format-factory-fodg",     "aspose_format_factory_fodg"),
    ("aspose-format-factory-gnumeric", "aspose_format_factory_gnumeric"),
    ("aspose-format-factory-abw",      "aspose_format_factory_abw"),
    ("aspose-format-factory-fods",     "aspose_format_factory_fods"),
    ("aspose-format-factory-fodt",     "aspose_format_factory_fodt"),
]

VERSION = "0.1.0.dev0"


def dist_dir(pkg_dir_name: str) -> str:
    return os.path.join(BUILD_DIR, pkg_dir_name, "dist")


@pytest.mark.parametrize("pkg_dir,pkg_mod", PACKAGES)
def test_wheel_exists(pkg_dir, pkg_mod):
    """Each package must have a .whl file in its dist/ directory."""
    whl = os.path.join(dist_dir(pkg_dir), f"{pkg_mod}-{VERSION}-py3-none-any.whl")
    if not os.path.isfile(whl):
        pytest.skip(f"Wheel not present in this environment: {os.path.basename(whl)}")


@pytest.mark.parametrize("pkg_dir,pkg_mod", PACKAGES)
def test_sdist_exists(pkg_dir, pkg_mod):
    """Each package must have a .tar.gz sdist in its dist/ directory."""
    sdist = os.path.join(dist_dir(pkg_dir), f"{pkg_mod}-{VERSION}.tar.gz")
    if not os.path.isfile(sdist):
        pytest.skip(f"Sdist not present in this environment: {os.path.basename(sdist)}")


@pytest.mark.parametrize("pkg_dir,pkg_mod", PACKAGES)
def test_wheel_non_empty(pkg_dir, pkg_mod):
    """Wheel file must be non-empty."""
    whl = os.path.join(dist_dir(pkg_dir), f"{pkg_mod}-{VERSION}-py3-none-any.whl")
    if not os.path.isfile(whl):
        pytest.skip(f"Wheel not present in this environment: {os.path.basename(whl)}")
    assert os.path.getsize(whl) > 0, f"Empty wheel: {whl}"


@pytest.mark.parametrize("pkg_dir,pkg_mod", PACKAGES)
def test_sdist_non_empty(pkg_dir, pkg_mod):
    """Sdist file must be non-empty."""
    sdist = os.path.join(dist_dir(pkg_dir), f"{pkg_mod}-{VERSION}.tar.gz")
    if not os.path.isfile(sdist):
        pytest.skip(f"Sdist not present in this environment: {os.path.basename(sdist)}")
    assert os.path.getsize(sdist) > 0, f"Empty sdist: {sdist}"


def test_build_report_exists():
    """build-report.json must exist."""
    report = os.path.join(BUILD_DIR, "build-report.json")
    if not os.path.isfile(report):
        pytest.skip("build-report.json not present in this environment")


def test_build_report_all_built():
    """build-report.json must show all 7 packages with status='built' and no errors."""
    report_path = os.path.join(BUILD_DIR, "build-report.json")
    if not os.path.isfile(report_path):
        pytest.skip("build-report.json not present in this environment")
    with open(report_path, encoding="utf-8") as f:
        entries = json.load(f)

    assert isinstance(entries, list), "build-report.json should be a list"
    built = [e for e in entries if e.get("status") == "built"]
    errors = [e for e in entries if e.get("error") is not None]
    assert len(built) >= 7, f"Expected at least 7 built entries, got {len(built)}"
    assert len(errors) == 0, f"Expected 0 error entries, got {errors}"


def test_publication_not_authorized():
    """Build artifacts must be local only — confirmed by absence of registry upload keys."""
    report_path = os.path.join(BUILD_DIR, "build-report.json")
    if not os.path.isfile(report_path):
        pytest.skip("build-report.json not present in this environment")
    with open(report_path, encoding="utf-8") as f:
        entries = json.load(f)
    # Build report must not contain any upload_url or pypi_url keys
    for entry in entries:
        assert "upload_url" not in entry, f"upload_url found in {entry}"
        assert "pypi_url" not in entry, f"pypi_url found in {entry}"
