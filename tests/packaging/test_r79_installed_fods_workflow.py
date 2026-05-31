"""
tests/packaging/test_r79_installed_fods_workflow.py

R79 Train D — FODS installed-wheel end-to-end workflow.

Tests that the rebuilt FODS wheel (from R79 Train B) can be:
1. Installed in an isolated subprocess (no PYTHONPATH, no repo imports)
2. Imported as `import fods` (correct namespace)
3. Used to run the full API workflow
4. Has correct version, track, and all R77 APIs present

This addresses D78-03 (repo imports in smoke), D78-06 (wrong import namespace),
D78-07 (aspose_format_factory_fods import fails), D78-15/16 (stale API counts).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
FODS_WHEEL = (
    REPO_ROOT / ".local" / "package-builds" / "python-foss" /
    "aspose-format-factory-fods" / "dist" /
    "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl"
)
FODS_SAMPLE = REPO_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"

import pytest


def _run_isolated(code: str, extra_packages: list[str] | None = None) -> tuple[int, str, str]:
    """Install FODS wheel in a temp venv and run code without any PYTHONPATH."""
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_dir = Path(tmpdir) / "isolated_venv"
        # Create isolated venv
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True, capture_output=True
        )
        if sys.platform == "win32":
            pip = venv_dir / "Scripts" / "pip.exe"
            python = venv_dir / "Scripts" / "python.exe"
        else:
            pip = venv_dir / "bin" / "pip"
            python = venv_dir / "bin" / "python"

        # Install fods wheel
        subprocess.run(
            [str(pip), "install", "--quiet", str(FODS_WHEEL)],
            check=True, capture_output=True
        )
        if extra_packages:
            for pkg in extra_packages:
                subprocess.run(
                    [str(pip), "install", "--quiet", pkg],
                    check=True, capture_output=True
                )

        # Run code with NO PYTHONPATH (pure installed package test)
        env = {"PYTHONPATH": "", "PATH": str(venv_dir / "Scripts") + ";" + "C:\\Windows\\System32"}
        import os
        env.update({k: v for k, v in os.environ.items() if k not in ("PYTHONPATH",)})
        env["PYTHONPATH"] = ""

        result = subprocess.run(
            [str(python), "-c", code],
            capture_output=True, text=True, timeout=60, env=env,
            cwd=tmpdir  # NOT the repo — no repo in path
        )
        return result.returncode, result.stdout, result.stderr


@pytest.mark.skipif(
    not FODS_WHEEL.exists(),
    reason=f"FODS wheel not found at {FODS_WHEEL} — run build-local-packages.py first"
)
class TestFodsInstalledWheelImport:
    """D78-06/07: Installed wheel must be importable as `import fods`."""

    def test_import_fods_not_aspose_name(self):
        rc, stdout, stderr = _run_isolated("import fods; print('OK')")
        assert rc == 0, f"import fods failed: {stderr}"
        assert "OK" in stdout

    def test_wrong_namespace_fails(self):
        rc, stdout, stderr = _run_isolated(
            "try:\n"
            "    import aspose_format_factory_fods\n"
            "    print('WRONG_NAMESPACE_SUCCEEDED')\n"
            "except ImportError:\n"
            "    print('CORRECT_IMPORT_ERROR')"
        )
        assert rc == 0
        assert "CORRECT_IMPORT_ERROR" in stdout, (
            "aspose_format_factory_fods should NOT be importable — correct namespace is 'fods'"
        )

    def test_version_from_installed_wheel(self):
        rc, stdout, stderr = _run_isolated(
            "import fods; print(fods.__version__)"
        )
        assert rc == 0, f"Failed: {stderr}"
        assert "0.1.0.dev0" in stdout, f"Expected 0.1.0.dev0, got: {stdout.strip()}"

    def test_track_from_installed_wheel(self):
        rc, stdout, stderr = _run_isolated(
            "import fods; print(fods.__track__)"
        )
        assert rc == 0, f"Failed: {stderr}"
        assert "python-foss" in stdout, f"Expected python-foss, got: {stdout.strip()}"


@pytest.mark.skipif(
    not FODS_WHEEL.exists(),
    reason=f"FODS wheel not found at {FODS_WHEEL} — run build-local-packages.py first"
)
class TestFodsInstalledWheelApiPresence:
    """D78-15: R77 sheet APIs must be present in installed wheel."""

    def test_r77_sheet_apis_in_installed_wheel(self):
        rc, stdout, stderr = _run_isolated(
            "import fods\n"
            "apis = ['workbook_add_sheet', 'workbook_rename_sheet', 'workbook_remove_sheet']\n"
            "missing = [a for a in apis if not hasattr(fods, a)]\n"
            "if missing:\n"
            "    print('MISSING:', missing)\n"
            "else:\n"
            "    print('ALL_R77_APIS_PRESENT')"
        )
        assert rc == 0, f"Failed: {stderr}"
        assert "ALL_R77_APIS_PRESENT" in stdout, f"R77 APIs missing: {stdout}"

    def test_installed_api_count_at_least_28(self):
        rc, stdout, stderr = _run_isolated(
            "import fods\n"
            "public = [a for a in dir(fods) if not a.startswith('_')]\n"
            "print(len(public))"
        )
        assert rc == 0, f"Failed: {stderr}"
        count = int(stdout.strip())
        assert count >= 28, f"Installed fods API count {count} < 28 — wheel is stale"


@pytest.mark.skipif(
    not FODS_WHEEL.exists() or not FODS_SAMPLE.exists(),
    reason="FODS wheel or sample not found"
)
class TestFodsInstalledWheelWorkflow:
    """D78-03: Full workflow using ONLY installed wheel, no repo imports."""

    def test_parse_fods_from_installed_wheel(self):
        rc, stdout, stderr = _run_isolated(
            f"import fods\n"
            f"doc = fods.parse_fods(r'{FODS_SAMPLE}')\n"
            f"assert isinstance(doc, dict), f'parse_fods returned {{type(doc)}}'\n"
            f"sheets = fods.workbook_sheet_order(doc)\n"
            f"assert isinstance(sheets, list)\n"
            f"print('PARSE_OK sheets=' + str(len(sheets)))"
        )
        assert rc == 0, f"Installed workflow failed:\n{stderr}"
        assert "PARSE_OK" in stdout

    def test_workbook_sheet_management_from_installed_wheel(self):
        rc, stdout, stderr = _run_isolated(
            f"import fods\n"
            f"doc = fods.parse_fods(r'{FODS_SAMPLE}')\n"
            f"ok, msg = fods.workbook_add_sheet(doc, 'Sheet2')\n"
            f"assert ok, f'add_sheet failed: ' + msg\n"
            f"sheets = fods.workbook_sheet_order(doc)\n"
            f"assert 'Sheet2' in sheets, f'Sheet2 not found in ' + str(sheets)\n"
            f"print('SHEET_MGMT_OK')"
        )
        assert rc == 0, f"Sheet management failed:\n{stderr}"
        assert "SHEET_MGMT_OK" in stdout
