"""
tests/packaging/test_r1221_fodg_ndjson_tsv_installed_workflow.py

Closes gaps:
  GAP-FODG-FOSS-INSTALLED_WO-001  — missing test coverage for FODG installed workflow
  GAP-NDJSON-FOSS-INSTALLED_WO-001 — missing test coverage for NDJSON installed workflow
  GAP-TSV-FOSS-INSTALLED_WO-001   — missing test coverage for TSV installed workflow

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


FODG_WHEEL = wheel_path("aspose-format-factory-fodg", "aspose_format_factory_fodg")
NDJSON_WHEEL = wheel_path("aspose-format-factory-ndjson", "aspose_format_factory_ndjson")
TSV_WHEEL = wheel_path("aspose-format-factory-tsv", "aspose_format_factory_tsv")


# ---------------------------------------------------------------------------
# FODG
# ---------------------------------------------------------------------------

class TestFodgInstalledWorkflow:
    """GAP-FODG-FOSS-INSTALLED_WO-001: FODG wheel installs and exposes core API."""

    def test_fodg_wheel_exists(self):
        assert os.path.isfile(FODG_WHEEL), f"FODG wheel not found: {FODG_WHEEL}"

    def test_fodg_wheel_is_valid_zip(self):
        assert zipfile.is_zipfile(FODG_WHEEL), f"Not a valid zip/wheel: {FODG_WHEEL}"

    def test_fodg_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="fodg-wheel-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir,
                 "--no-deps",
                 "--quiet",
                 FODG_WHEEL],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"pip install failed (exit {result.returncode}):\n{result.stderr}"
            )

    def test_fodg_exposes_load_from_installed_wheel(self):
        with tempfile.TemporaryDirectory(prefix="fodg-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODG_WHEEL],
                capture_output=True, text=True, check=True
            )
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {repr(tmpdir)}); "
                 f"from fodg.fodg_codec import load; print('FODG_LOAD_OK')"],
                capture_output=True, text=True
            )
            assert "FODG_LOAD_OK" in result.stdout, (
                f"FODG load symbol not importable from installed wheel.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )


# ---------------------------------------------------------------------------
# NDJSON
# ---------------------------------------------------------------------------

class TestNdjsonInstalledWorkflow:
    """GAP-NDJSON-FOSS-INSTALLED_WO-001: NDJSON wheel installs and exposes core API."""

    def test_ndjson_wheel_exists(self):
        assert os.path.isfile(NDJSON_WHEEL), f"NDJSON wheel not found: {NDJSON_WHEEL}"

    def test_ndjson_wheel_is_valid_zip(self):
        assert zipfile.is_zipfile(NDJSON_WHEEL), f"Not a valid zip/wheel: {NDJSON_WHEEL}"

    def test_ndjson_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="ndjson-wheel-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir,
                 "--no-deps",
                 "--quiet",
                 NDJSON_WHEEL],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"pip install failed (exit {result.returncode}):\n{result.stderr}"
            )

    def test_ndjson_exposes_core_symbol_from_installed_wheel(self):
        with tempfile.TemporaryDirectory(prefix="ndjson-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", NDJSON_WHEEL],
                capture_output=True, text=True, check=True
            )
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {repr(tmpdir)}); "
                 f"import ndjson; print('NDJSON_OK')"],
                capture_output=True, text=True
            )
            assert "NDJSON_OK" in result.stdout, (
                f"NDJSON package not importable from installed wheel.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )


# ---------------------------------------------------------------------------
# TSV
# ---------------------------------------------------------------------------

class TestTsvInstalledWorkflow:
    """GAP-TSV-FOSS-INSTALLED_WO-001: TSV wheel installs and exposes core API."""

    def test_tsv_wheel_exists(self):
        assert os.path.isfile(TSV_WHEEL), f"TSV wheel not found: {TSV_WHEEL}"

    def test_tsv_wheel_is_valid_zip(self):
        assert zipfile.is_zipfile(TSV_WHEEL), f"Not a valid zip/wheel: {TSV_WHEEL}"

    def test_tsv_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="tsv-wheel-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir,
                 "--no-deps",
                 "--quiet",
                 TSV_WHEEL],
                capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"pip install failed (exit {result.returncode}):\n{result.stderr}"
            )

    def test_tsv_exposes_core_symbol_from_installed_wheel(self):
        with tempfile.TemporaryDirectory(prefix="tsv-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", TSV_WHEEL],
                capture_output=True, text=True, check=True
            )
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; sys.path.insert(0, {repr(tmpdir)}); "
                 f"import tsv; print('TSV_OK')"],
                capture_output=True, text=True
            )
            assert "TSV_OK" in result.stdout, (
                f"TSV package not importable from installed wheel.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
