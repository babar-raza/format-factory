# tests/packaging/test_python_installed_wheels.py
# R23 Gate 3 — Installed-wheel validation for Python FOSS packages
# Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
# publication_authorized: false
#
# These tests install each built wheel into an isolated directory using pip,
# then import the package from the installed location (NOT from src/python/).
# This validates that the wheel artifacts are self-contained and installable.
#
# Isolation strategy: each test installs into a temp directory using
#   pip install --target <tmpdir> <wheel>
# and then imports from that target, not from src/python/.

import importlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILD_DIR = os.path.join(REPO_ROOT, ".local", "package-builds", "python-foss")

PACKAGES = [
    ("aspose-format-factory-zst",      "aspose_format_factory_zst",      "zst"),
    ("aspose-format-factory-fodp",     "aspose_format_factory_fodp",     "fodp"),
    ("aspose-format-factory-fodg",     "aspose_format_factory_fodg",     "fodg"),
    ("aspose-format-factory-gnumeric", "aspose_format_factory_gnumeric", "gnumeric"),
    ("aspose-format-factory-abw",      "aspose_format_factory_abw",      "abw"),
]

VERSION = "0.1.0.dev0"


def wheel_path(pkg_dir_name: str, pkg_mod: str) -> str:
    return os.path.join(
        BUILD_DIR, pkg_dir_name, "dist",
        f"{pkg_mod}-{VERSION}-py3-none-any.whl"
    )


@pytest.fixture(scope="module")
def install_dir():
    """Shared temp install dir for the module — created once, cleaned up after all tests."""
    with tempfile.TemporaryDirectory(prefix="foss-wheel-install-") as tmpdir:
        yield tmpdir


@pytest.mark.parametrize("pkg_dir,pkg_mod,fmt", PACKAGES)
def test_wheel_installs_without_error(pkg_dir, pkg_mod, fmt):
    """Each wheel must install into an isolated target directory without errors."""
    whl = wheel_path(pkg_dir, pkg_mod)
    assert os.path.isfile(whl), f"Wheel not found: {whl}"

    with tempfile.TemporaryDirectory(prefix=f"install-{fmt}-") as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "--target", tmpdir,
             "--no-deps",
             "--quiet",
             whl],
            capture_output=True, text=True
        )
        assert result.returncode == 0, (
            f"pip install failed for {pkg_dir}:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


@pytest.mark.parametrize("pkg_dir,pkg_mod,fmt", PACKAGES)
def test_installed_wheel_is_importable(pkg_dir, pkg_mod, fmt):
    """Package installed from wheel must be importable (not from src/python/)."""
    whl = wheel_path(pkg_dir, pkg_mod)

    with tempfile.TemporaryDirectory(prefix=f"import-{fmt}-") as tmpdir:
        # Install wheel into tmpdir
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "--target", tmpdir,
             "--no-deps",
             "--quiet",
             whl],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Install failed: {result.stderr}"

        # Import from the installed target, not from src/python/
        verify_script = f"""
import sys
sys.path.insert(0, {repr(tmpdir)})

# Remove src/python from path to ensure we're not importing from source
src_python = {repr(os.path.join(REPO_ROOT, 'src', 'python'))}
sys.path = [p for p in sys.path if p != src_python]

import {fmt}
print('version:', {fmt}.__version__)
print('track:', {fmt}.__track__)
print('capability_level:', {fmt}.__capability_level__)
print('IMPORT_OK')
"""
        r = subprocess.run(
            [sys.executable, "-c", verify_script],
            capture_output=True, text=True
        )
        assert r.returncode == 0, (
            f"Import failed for {pkg_mod}:\nstdout: {r.stdout}\nstderr: {r.stderr}"
        )
        assert "IMPORT_OK" in r.stdout, f"Import did not succeed: {r.stdout}"


@pytest.mark.parametrize("pkg_dir,pkg_mod,fmt", PACKAGES)
def test_installed_wheel_version_correct(pkg_dir, pkg_mod, fmt):
    """Installed package must report correct version."""
    whl = wheel_path(pkg_dir, pkg_mod)

    with tempfile.TemporaryDirectory(prefix=f"ver-{fmt}-") as tmpdir:
        subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "--target", tmpdir, "--no-deps", "--quiet", whl],
            capture_output=True, text=True, check=True
        )

        verify_script = f"""
import sys
sys.path.insert(0, {repr(tmpdir)})
src_python = {repr(os.path.join(REPO_ROOT, 'src', 'python'))}
sys.path = [p for p in sys.path if p != src_python]
import {fmt}
print({fmt}.__version__)
"""
        r = subprocess.run([sys.executable, "-c", verify_script],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"Version check failed: {r.stderr}"
        assert "{VERSION}" in r.stdout.strip() or "0.1.0.dev0" in r.stdout.strip(), (
            f"Unexpected version: {r.stdout.strip()}"
        )


@pytest.mark.parametrize("pkg_dir,pkg_mod,fmt", PACKAGES)
def test_installed_wheel_capability_level_set(pkg_dir, pkg_mod, fmt):
    """Installed package __capability_level__ must be non-empty."""
    whl = wheel_path(pkg_dir, pkg_mod)

    with tempfile.TemporaryDirectory(prefix=f"cap-{fmt}-") as tmpdir:
        subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "--target", tmpdir, "--no-deps", "--quiet", whl],
            capture_output=True, text=True, check=True
        )

        verify_script = f"""
import sys
sys.path.insert(0, {repr(tmpdir)})
src_python = {repr(os.path.join(REPO_ROOT, 'src', 'python'))}
sys.path = [p for p in sys.path if p != src_python]
import {fmt}
level = {fmt}.__capability_level__
assert level is not None and str(level).strip(), f"Empty capability_level: {{level!r}}"
print('OK:', level)
"""
        r = subprocess.run([sys.executable, "-c", verify_script],
                           capture_output=True, text=True)
        assert r.returncode == 0, (
            f"capability_level check failed for {pkg_mod}:\n{r.stdout}\n{r.stderr}"
        )


@pytest.mark.parametrize("pkg_dir,pkg_mod,fmt", PACKAGES)
def test_installed_wheel_no_pypi_upload_keys(pkg_dir, pkg_mod, fmt):
    """Build report for installed package must not contain PyPI upload keys."""
    report_path = os.path.join(BUILD_DIR, "build-report.json")
    if not os.path.isfile(report_path):
        pytest.skip("build-report.json not found")

    with open(report_path, encoding="utf-8") as f:
        entries = json.load(f)

    for entry in entries:
        assert "upload_url" not in entry, f"upload_url found in report for {pkg_dir}"
        assert "pypi_url" not in entry, f"pypi_url found in report for {pkg_dir}"
