"""
tests/packaging/test_r1222_abw_gnumeric_installed_workflow.py

Closes gaps:
  GAP-ABW-FOSS-INSTALLED_WO-001     — missing test coverage for ABW installed workflow
  GAP-GNUMERIC-FOSS-INSTALLED_WO-001 — missing test coverage for Gnumeric installed workflow

Verifies that the wheel for each format:
  1. Exists as a valid .whl file in .local/package-builds/python-foss/
  2. Is a valid zip archive (valid wheel structure)
  3. Installs cleanly into an isolated temp dir via pip --target
  4. Exposes a core API symbol that can be imported from the installed location
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import zipfile
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILD_DIR = os.path.join(REPO_ROOT, ".local", "package-builds", "python-foss")
VERSION = "0.1.0.dev0"

pytestmark = pytest.mark.skipif(
    not os.path.isdir(BUILD_DIR),
    reason="Package build artifacts not present in this environment",
)


def wheel_path(pkg_dir: str, pkg_mod: str) -> str:
    return os.path.join(
        BUILD_DIR, pkg_dir, "dist",
        f"{pkg_mod}-{VERSION}-py3-none-any.whl",
    )


ABW_WHEEL = wheel_path("aspose-format-factory-abw", "aspose_format_factory_abw")
GNUMERIC_WHEEL = wheel_path("aspose-format-factory-gnumeric", "aspose_format_factory_gnumeric")


# ---------------------------------------------------------------------------
# ABW
# ---------------------------------------------------------------------------

class TestAbwInstalledWorkflow:
    """GAP-ABW-FOSS-INSTALLED_WO-001: ABW wheel installs and exposes core API."""

    def test_abw_wheel_exists(self):
        assert os.path.isfile(ABW_WHEEL), f"ABW wheel not found: {ABW_WHEEL}"

    def test_abw_wheel_is_valid_zip(self):
        assert zipfile.is_zipfile(ABW_WHEEL), f"Not a valid zip/wheel: {ABW_WHEEL}"

    def test_abw_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="abw-wheel-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir,
                 "--no-deps",
                 "--quiet",
                 ABW_WHEEL],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"pip install failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

    def test_abw_exposes_core_symbol_from_installed_wheel(self):
        with tempfile.TemporaryDirectory(prefix="abw-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", ABW_WHEEL],
                capture_output=True, check=True
            )
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {tmpdir!r}); "
                 "import abw; "
                 "assert hasattr(abw, 'load'), 'abw.load missing'; "
                 "assert hasattr(abw, 'export_to_csv'), 'abw.export_to_csv missing'; "
                 "print('ABW OK:', abw.__version__)"],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"ABW import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )
            assert "ABW OK:" in result.stdout


# ---------------------------------------------------------------------------
# Gnumeric
# ---------------------------------------------------------------------------

class TestGnumericInstalledWorkflow:
    """GAP-GNUMERIC-FOSS-INSTALLED_WO-001: Gnumeric wheel installs and exposes core API."""

    def test_gnumeric_wheel_exists(self):
        assert os.path.isfile(GNUMERIC_WHEEL), f"Gnumeric wheel not found: {GNUMERIC_WHEEL}"

    def test_gnumeric_wheel_is_valid_zip(self):
        assert zipfile.is_zipfile(GNUMERIC_WHEEL), f"Not a valid zip/wheel: {GNUMERIC_WHEEL}"

    def test_gnumeric_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="gnumeric-wheel-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir,
                 "--no-deps",
                 "--quiet",
                 GNUMERIC_WHEEL],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"pip install failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

    def test_gnumeric_exposes_core_symbol_from_installed_wheel(self):
        with tempfile.TemporaryDirectory(prefix="gnumeric-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", GNUMERIC_WHEEL],
                capture_output=True, check=True
            )
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {tmpdir!r}); "
                 "import gnumeric; "
                 "assert hasattr(gnumeric, 'load'), 'gnumeric.load missing'; "
                 "assert hasattr(gnumeric, 'export_to_csv'), 'gnumeric.export_to_csv missing'; "
                 "print('Gnumeric OK:', gnumeric.__version__)"],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"Gnumeric import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )
            assert "Gnumeric OK:" in result.stdout
