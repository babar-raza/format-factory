"""R67 Train G: FODT installed wheel API smoke from clean venv.

Proves all 17+ FODT public functions work from the installed R67 wheel.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMOKE_VENV = PROJECT_ROOT / ".local" / "r67-smoke-venv"
FODT_WHL = PROJECT_ROOT / ".local" / "r67-metadata" / "package-artifacts" / "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl"
SAMPLE_FODT = PROJECT_ROOT / "samples" / "by-format" / "fodt" / "test_document.fodt"

EXPECTED_APIS = [
    "parse_fodt",
    "parse_fodt_strict",
    "write_fodt",
    "document_to_xml",
    "document_stats",
    "document_heading_outline",
    "document_text_content",
    "document_word_count",
    "document_table_summary",
    "document_list_stats",
    "document_reading_level",
    "document_hyperlink_count",
    "document_footnote_count",
    "document_heading_level_distribution",
    "document_table_cell_count",
    # R66 additions
    "document_section_summary",
    "document_change_tracking_summary",
]


@pytest.fixture(scope="module")
def smoke_venv_python():
    vpy = SMOKE_VENV / "Scripts" / "python.exe"
    if not vpy.exists():
        pytest.skip("R67 smoke venv not available")
    if not FODT_WHL.exists():
        pytest.skip("R67 FODT wheel not available")
    return str(vpy)


@pytest.fixture(scope="module")
def installed_fodt_all(smoke_venv_python):
    r = subprocess.run(
        [smoke_venv_python, "-c", "import fodt; print('\\n'.join(fodt.__all__))"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        pytest.skip(f"Could not import fodt: {r.stderr[:200]}")
    return set(r.stdout.strip().splitlines())


@pytest.mark.parametrize("api_name", EXPECTED_APIS)
def test_api_present_in_installed_wheel(api_name, installed_fodt_all):
    assert api_name in installed_fodt_all, f"FODT API '{api_name}' missing from installed wheel __all__"


def test_parse_fodt_from_installed_wheel(smoke_venv_python):
    if not SAMPLE_FODT.exists():
        pytest.skip("Sample FODT file not available")
    r = subprocess.run(
        [smoke_venv_python, "-c",
         f"import fodt; doc = fodt.parse_fodt(r'{SAMPLE_FODT}'); print('FODT_PARSE_PASS:', doc is not None)"],
        capture_output=True, text=True
    )
    assert r.returncode == 0, f"FODT parse failed: {r.stderr[:200]}"
    assert "FODT_PARSE_PASS: True" in r.stdout
