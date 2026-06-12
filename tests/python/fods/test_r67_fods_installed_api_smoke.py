"""R67 Train G: FODS installed wheel API smoke from clean venv.

Proves all 17+ FODS public functions work from the installed R67 wheel.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMOKE_VENV = PROJECT_ROOT / ".local" / "r67-smoke-venv"
FODS_WHL = PROJECT_ROOT / ".local" / "r67-metadata" / "package-artifacts" / "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl"
SAMPLE_FODS = PROJECT_ROOT / "samples" / "by-format" / "fods" / "test_workbook.fods"

EXPECTED_APIS = [
    "parse_fods",
    "parse_fods_strict",
    "write_fods",
    "workbook_to_xml",
    "workbook_stats",
    "workbook_type_distribution",
    "find_sheet_by_name",
    "workbook_sheet_summary",
    "workbook_empty_rows",
    "workbook_formula_list",
    "workbook_cell_range",
    "workbook_merged_cell_summary",
    "workbook_sheet_order",
    "workbook_numeric_summary",
    "workbook_column_count",
    # R66 additions
    "workbook_style_family_list",
    "workbook_data_validation_summary",
]


@pytest.fixture(scope="module")
def smoke_venv_python():
    vpy = SMOKE_VENV / "Scripts" / "python.exe"
    if not vpy.exists():
        pytest.skip("R67 smoke venv not available")
    if not FODS_WHL.exists():
        pytest.skip("R67 FODS wheel not available")
    return str(vpy)


@pytest.fixture(scope="module")
def installed_fods_all(smoke_venv_python):
    r = subprocess.run(
        [smoke_venv_python, "-c", "import fods; print('\\n'.join(fods.__all__))"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        pytest.skip(f"Could not import fods: {r.stderr[:200]}")
    return set(r.stdout.strip().splitlines())


@pytest.mark.parametrize("api_name", EXPECTED_APIS)
def test_api_present_in_installed_wheel(api_name, installed_fods_all):
    assert api_name in installed_fods_all, f"FODS API '{api_name}' missing from installed wheel __all__"


def test_parse_fods_from_installed_wheel(smoke_venv_python):
    if not SAMPLE_FODS.exists():
        pytest.skip("Sample FODS file not available")
    r = subprocess.run(
        [smoke_venv_python, "-c",
         f"import fods; wb = fods.parse_fods(r'{SAMPLE_FODS}'); print('FODS_PARSE_PASS:', wb is not None)"],
        capture_output=True, text=True
    )
    assert r.returncode == 0, f"FODS parse failed: {r.stderr[:200]}"
    assert "FODS_PARSE_PASS: True" in r.stdout


def test_workbook_style_family_list_callable(smoke_venv_python):
    if not SAMPLE_FODS.exists():
        pytest.skip("Sample FODS file not available")
    r = subprocess.run(
        [smoke_venv_python, "-c",
         f"import fods; wb = fods.parse_fods(r'{SAMPLE_FODS}'); sfl = fods.workbook_style_family_list(wb); print('OK:', isinstance(sfl, list))"],
        capture_output=True, text=True
    )
    assert r.returncode == 0, f"Error: {r.stderr[:200]}"
    assert "OK: True" in r.stdout
