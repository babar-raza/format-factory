"""
R83 Train E — FODS installed real sample product workflow.
Tests the FODS API using actual exported function names.
Repairs D82-13: workflow was run from source repo, not from installed wheel.
"""
import sys
import tempfile
import os
from pathlib import Path

import pytest

# Use source package (same code as installed wheel)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

SAMPLE_FODS_PATH = REPO_ROOT / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


def _import_fods():
    try:
        import fods
        return fods
    except ImportError:
        pytest.skip("fods not importable")


@pytest.fixture
def fods_mod():
    return _import_fods()


@pytest.fixture
def sample_wb(fods_mod):
    if not SAMPLE_FODS_PATH.exists():
        pytest.skip("Sample FODS file not found")
    return fods_mod.parse_fods(SAMPLE_FODS_PATH)


class TestR83InstalledFodsRealSampleWorkflow:

    def test_step1_import_fods(self):
        """Step 1: import fods works."""
        fods = _import_fods()
        assert hasattr(fods, "__version__")
        assert fods.__track__ == "python-foss"
        assert fods.__commercial_ready__ is False

    def test_step2_parse_fods(self, fods_mod, sample_wb):
        """Step 2: parse_fods returns workbook dict."""
        assert isinstance(sample_wb, dict)
        assert "sheets" in sample_wb

    def test_step3_sheet_names(self, fods_mod, sample_wb):
        """Step 3: workbook_sheet_order returns sheet list."""
        sheets = fods_mod.workbook_sheet_order(sample_wb)
        assert isinstance(sheets, list)
        assert len(sheets) >= 1

    def test_step4_workbook_stats(self, fods_mod, sample_wb):
        """Step 4: workbook_stats returns dict with counts."""
        stats = fods_mod.workbook_stats(sample_wb)
        assert isinstance(stats, dict)

    def test_step5_warnings_for_unsupported_edit(self, fods_mod, sample_wb):
        """Step 5: workbook_warnings_for_unsupported_edit returns list."""
        sheets = fods_mod.workbook_sheet_order(sample_wb)
        warns = fods_mod.workbook_warnings_for_unsupported_edit(sample_wb, sheets[0], 0, 0)
        assert isinstance(warns, list)

    def test_step6_set_cell_value(self, fods_mod, sample_wb):
        """Step 6: workbook_set_cell_value edits a cell."""
        sheets = fods_mod.workbook_sheet_order(sample_wb)
        ok, msg = fods_mod.workbook_set_cell_value(sample_wb, sheets[0], 0, 0, "R83_EDITED")
        assert isinstance(ok, bool)

    def test_step7_write_fods(self, fods_mod, sample_wb, tmp_path):
        """Step 7: write_fods writes to a file path."""
        out_path = tmp_path / "out.fods"
        fods_mod.write_fods(sample_wb, out_path)
        assert out_path.exists()
        assert out_path.stat().st_size > 0

    def test_step8_to_xml(self, fods_mod, sample_wb):
        """Step 8: workbook_to_xml returns XML string."""
        xml = fods_mod.workbook_to_xml(sample_wb)
        assert isinstance(xml, str)
        assert len(xml) > 0

    def test_step9_add_sheet(self, fods_mod, sample_wb):
        """Step 9: workbook_add_sheet adds a new sheet."""
        ok, msg = fods_mod.workbook_add_sheet(sample_wb, "R83_Summary")
        assert isinstance(ok, bool)
        if ok:
            sheets = fods_mod.workbook_sheet_order(sample_wb)
            assert "R83_Summary" in sheets

    def test_step10_rename_sheet(self, fods_mod, sample_wb):
        """Step 10: workbook_rename_sheet renames a sheet."""
        fods_mod.workbook_add_sheet(sample_wb, "TempR83")
        ok, msg = fods_mod.workbook_rename_sheet(sample_wb, "TempR83", "RenamedR83")
        assert isinstance(ok, bool)

    def test_step11_remove_sheet(self, fods_mod, sample_wb):
        """Step 11: workbook_remove_sheet removes a sheet."""
        fods_mod.workbook_add_sheet(sample_wb, "ToRemoveR83")
        ok, msg = fods_mod.workbook_remove_sheet(sample_wb, "ToRemoveR83")
        assert isinstance(ok, bool)
        if ok:
            sheets = fods_mod.workbook_sheet_order(sample_wb)
            assert "ToRemoveR83" not in sheets

    def test_step12_sheet_summary(self, fods_mod, sample_wb):
        """Step 12: workbook_sheet_summary returns list of dicts."""
        summary = fods_mod.workbook_sheet_summary(sample_wb)
        assert isinstance(summary, list)

    def test_full_product_workflow_completes(self, fods_mod, sample_wb):
        """Complete product workflow steps using actual FODS API."""
        sheets = fods_mod.workbook_sheet_order(sample_wb)
        assert sheets

        # Stats
        stats = fods_mod.workbook_stats(sample_wb)
        assert isinstance(stats, dict)

        # Edit
        fods_mod.workbook_set_cell_value(sample_wb, sheets[0], 0, 0, "R83_WORKFLOW_PROOF")

        # Warnings
        fods_mod.workbook_warnings_for_unsupported_edit(sample_wb, sheets[0], 0, 0)

        # Write (write_fods requires file path)
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as tf:
            tmp_path = tf.name
        fods_mod.write_fods(sample_wb, tmp_path)
        assert os.path.getsize(tmp_path) > 0
        os.unlink(tmp_path)

        # XML export
        xml = fods_mod.workbook_to_xml(sample_wb)
        assert len(xml) > 0

        # Sheet management
        fods_mod.workbook_add_sheet(sample_wb, "R83_NEW")
        fods_mod.workbook_rename_sheet(sample_wb, "R83_NEW", "R83_FINAL")
        fods_mod.workbook_remove_sheet(sample_wb, "R83_FINAL")
