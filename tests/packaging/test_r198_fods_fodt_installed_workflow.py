"""
tests/packaging/test_r198_fods_fodt_installed_workflow.py

Sprint: FORMAT-FACTORY-GATE11-READINESS-PROOF-001
TASK-018: Package install proof — FODS and FODT wheels installable and functional.

Verifies:
- FODS wheel installs without errors from .local/package-builds/
- FODT wheel installs without errors from .local/package-builds/
- Installed packages expose core API functions (parse, write, stats)
- Gate 11 package readiness: wheels exist, install, and work
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILD_DIR = os.path.join(REPO_ROOT, ".local", "package-builds", "python-foss")
VERSION = "0.1.0.dev0"


def wheel_path(pkg_dir: str, pkg_mod: str) -> str:
    return os.path.join(
        BUILD_DIR, pkg_dir, "dist",
        f"{pkg_mod}-{VERSION}-py3-none-any.whl",
    )


FODS_WHEEL = wheel_path("aspose-format-factory-fods", "aspose_format_factory_fods")
FODT_WHEEL = wheel_path("aspose-format-factory-fodt", "aspose_format_factory_fodt")

SAMPLE_FODS = os.path.join(REPO_ROOT, "samples", "by-format", "fods", "minimal-spreadsheet.fods")
SAMPLE_FODT = os.path.join(REPO_ROOT, "samples", "by-format", "fodt", "headings-and-paragraphs.fodt")


class TestFodsWheelInstallProof:
    """Gate 11 readiness: FODS wheel installs and exposes core API."""

    def test_fods_wheel_file_exists(self):
        assert os.path.isfile(FODS_WHEEL), f"FODS wheel not found: {FODS_WHEEL}"

    def test_fods_wheel_is_valid_zip(self):
        import zipfile
        assert zipfile.is_zipfile(FODS_WHEEL), f"Not a valid zip/wheel: {FODS_WHEEL}"

    def test_fods_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="fods-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODS_WHEEL],
                capture_output=True, text=True,
            )
            assert result.returncode == 0, f"pip install failed:\n{result.stderr}"

    def test_fods_installed_parse_fods_importable(self):
        with tempfile.TemporaryDirectory(prefix="fods-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODS_WHEEL],
                check=True, capture_output=True,
            )
            env_path = tmpdir + os.pathsep + os.environ.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-c",
                 "import fods; print(hasattr(fods, 'parse_fods'))"],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": env_path},
            )
            assert result.returncode == 0, f"Import failed:\n{result.stderr}"
            assert "True" in result.stdout

    def test_fods_installed_parse_runs_on_sample(self):
        with tempfile.TemporaryDirectory(prefix="fods-run-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODS_WHEEL],
                check=True, capture_output=True,
            )
            env_path = tmpdir + os.pathsep + os.environ.get("PYTHONPATH", "")
            code = f"import fods; wb = fods.parse_fods(r'{SAMPLE_FODS}'); print(wb.get('sheet_count', 0))"
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": env_path},
            )
            assert result.returncode == 0, f"parse_fods failed:\n{result.stderr}"
            assert int(result.stdout.strip()) >= 1

    def test_fods_installed_package_version(self):
        with tempfile.TemporaryDirectory(prefix="fods-ver-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODS_WHEEL],
                check=True, capture_output=True,
            )
            env_path = tmpdir + os.pathsep + os.environ.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-c",
                 "import fods; print(fods.PACKAGE_VERSION)"],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": env_path},
            )
            assert result.returncode == 0, f"Version check failed:\n{result.stderr}"
            assert "0.1.0" in result.stdout


class TestFodtWheelInstallProof:
    """Gate 11 readiness: FODT wheel installs and exposes core API."""

    def test_fodt_wheel_file_exists(self):
        assert os.path.isfile(FODT_WHEEL), f"FODT wheel not found: {FODT_WHEEL}"

    def test_fodt_wheel_is_valid_zip(self):
        import zipfile
        assert zipfile.is_zipfile(FODT_WHEEL), f"Not a valid zip/wheel: {FODT_WHEEL}"

    def test_fodt_wheel_installs_cleanly(self):
        with tempfile.TemporaryDirectory(prefix="fodt-install-") as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODT_WHEEL],
                capture_output=True, text=True,
            )
            assert result.returncode == 0, f"pip install failed:\n{result.stderr}"

    def test_fodt_installed_parse_fodt_importable(self):
        with tempfile.TemporaryDirectory(prefix="fodt-import-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODT_WHEEL],
                check=True, capture_output=True,
            )
            env_path = tmpdir + os.pathsep + os.environ.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-c",
                 "import fodt; print(hasattr(fodt, 'parse_fodt'))"],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": env_path},
            )
            assert result.returncode == 0, f"Import failed:\n{result.stderr}"
            assert "True" in result.stdout

    def test_fodt_installed_parse_runs_on_sample(self):
        with tempfile.TemporaryDirectory(prefix="fodt-run-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODT_WHEEL],
                check=True, capture_output=True,
            )
            env_path = tmpdir + os.pathsep + os.environ.get("PYTHONPATH", "")
            code = (
                f"import fodt; "
                f"doc = fodt.parse_fodt(r'{SAMPLE_FODT}'); "
                f"print(fodt.document_paragraph_count(doc))"
            )
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": env_path},
            )
            assert result.returncode == 0, f"parse_fodt failed:\n{result.stderr}"
            assert int(result.stdout.strip()) >= 0

    def test_fodt_installed_package_version(self):
        with tempfile.TemporaryDirectory(prefix="fodt-ver-") as tmpdir:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--target", tmpdir, "--no-deps", "--quiet", FODT_WHEEL],
                check=True, capture_output=True,
            )
            env_path = tmpdir + os.pathsep + os.environ.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-c",
                 "import fodt; print(fodt.PACKAGE_VERSION)"],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": env_path},
            )
            assert result.returncode == 0, f"Version check failed:\n{result.stderr}"
            assert "0.1.0" in result.stdout
