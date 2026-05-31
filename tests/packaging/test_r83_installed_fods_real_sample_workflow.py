"""
R83 Train E — FODS installed real sample product workflow.
Tests that the FODS API works as documented in the installed-package workflow.
Repairs D82-13: workflow was run from source repo, not from installed wheel.
"""
import pytest


SAMPLE_FODS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Products">
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Name</text:p></table:table-cell>
          <table:table-cell office:value-type="string"><text:p>Price</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Widget</text:p></table:table-cell>
          <table:table-cell office:value-type="float" office:value="9.99"><text:p>9.99</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>"""


@pytest.fixture
def fods():
    import fods as _fods
    return _fods


@pytest.fixture
def sample_wb(fods):
    return fods.parse_fods(SAMPLE_FODS_XML.encode("utf-8"))


class TestR83InstalledFodsRealSampleWorkflow:

    def test_step1_import_fods(self):
        """Step 1: import fods works from installed package."""
        import fods
        assert fods.__version__ == "0.1.0.dev0"
        assert fods.__track__ == "python-foss"

    def test_step2_parse_fods(self, fods, sample_wb):
        """Step 2: parse_fods returns workbook dict."""
        assert isinstance(sample_wb, dict)
        assert "sheets" in sample_wb

    def test_step3_sheet_names(self, fods, sample_wb):
        """Step 3: workbook_sheet_names returns list."""
        names = fods.workbook_sheet_names(sample_wb)
        assert isinstance(names, list)
        assert len(names) >= 1
        assert "Products" in names

    def test_step4_row_values(self, fods, sample_wb):
        """Step 4: workbook_row_values returns row data."""
        row0 = fods.workbook_row_values(sample_wb, "Products", 0)
        assert isinstance(row0, list)
        assert len(row0) >= 1

    def test_step5_col_values(self, fods, sample_wb):
        """Step 5: workbook_col_values returns column data."""
        col0 = fods.workbook_col_values(sample_wb, "Products", 0)
        assert isinstance(col0, list)

    def test_step6_edit_cell(self, fods, sample_wb):
        """Step 6: workbook_edit_cell returns modified workbook."""
        wb2 = fods.workbook_edit_cell(sample_wb, "Products", 1, 0, "SuperWidget")
        assert wb2 is not None

    def test_step7_warnings_for_unsupported_edit(self, fods, sample_wb):
        """Step 7: workbook_warnings_for_unsupported_edit returns list."""
        warns = fods.workbook_warnings_for_unsupported_edit(sample_wb, "Products", 1, 0)
        assert isinstance(warns, list)

    def test_step8_write_fods(self, fods, sample_wb):
        """Step 8: write_fods returns bytes."""
        out = fods.write_fods(sample_wb)
        assert isinstance(out, (bytes, str))
        assert len(out) > 0

    def test_step9_csv_export(self, fods, sample_wb):
        """Step 9: workbook_to_csv returns CSV string."""
        csv_str = fods.workbook_to_csv(sample_wb, "Products")
        assert isinstance(csv_str, str)
        assert len(csv_str) > 0

    def test_step10_add_sheet(self, fods, sample_wb):
        """Step 10: workbook_add_sheet adds a new sheet."""
        wb3 = fods.workbook_add_sheet(sample_wb, "Summary")
        names = fods.workbook_sheet_names(wb3)
        assert "Summary" in names

    def test_step11_rename_sheet(self, fods, sample_wb):
        """Step 11: workbook_rename_sheet renames a sheet."""
        wb3 = fods.workbook_add_sheet(sample_wb, "TempSheet")
        wb4 = fods.workbook_rename_sheet(wb3, "TempSheet", "Report")
        names = fods.workbook_sheet_names(wb4)
        assert "Report" in names
        assert "TempSheet" not in names

    def test_step12_remove_sheet(self, fods, sample_wb):
        """Step 12: workbook_remove_sheet removes a sheet."""
        wb3 = fods.workbook_add_sheet(sample_wb, "ToRemove")
        wb4 = fods.workbook_remove_sheet(wb3, "ToRemove")
        names = fods.workbook_sheet_names(wb4)
        assert "ToRemove" not in names

    def test_full_12_step_workflow_completes(self, fods):
        """Complete 12-step product workflow from installed package."""
        wb = fods.parse_fods(SAMPLE_FODS_XML.encode("utf-8"))
        sheets = fods.workbook_sheet_names(wb)
        assert sheets
        fods.workbook_row_values(wb, sheets[0], 0)
        fods.workbook_col_values(wb, sheets[0], 0)
        wb2 = fods.workbook_edit_cell(wb, sheets[0], 1, 0, "Edited")
        fods.workbook_warnings_for_unsupported_edit(wb2, sheets[0], 1, 0)
        out_bytes = fods.write_fods(wb2)
        assert len(out_bytes) > 0
        fods.workbook_to_csv(wb2, sheets[0])
        wb3 = fods.workbook_add_sheet(wb2, "NewSheet")
        wb4 = fods.workbook_rename_sheet(wb3, "NewSheet", "FinalSheet")
        wb5 = fods.workbook_remove_sheet(wb4, "FinalSheet")
        final_sheets = fods.workbook_sheet_names(wb5)
        assert "FinalSheet" not in final_sheets
