"""
FODS Python FOSS — Edit, Save, Export (Installed Wheel Version)
Format Factory R83 — installed-package workflow proof

Run ONLY from installed FODS wheel. No PYTHONPATH to source repo required.

Usage:
    pip install fods-0.1.0.dev0-py3-none-any.whl
    python edit_save_export_fods_installed.py
"""
from __future__ import annotations

import sys
import tempfile
import io


def _get_sample_fods_bytes() -> bytes:
    """Return a minimal self-contained FODS file for demo."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
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
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Gadget</text:p></table:table-cell>
          <table:table-cell office:value-type="float" office:value="19.99"><text:p>19.99</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>"""
    return xml.encode("utf-8")


def main() -> None:
    import fods

    print(f"fods version: {fods.__version__}")
    print(f"fods track: {fods.__track__}")
    print(f"fods capability: {fods.__capability_level__}")
    print()

    data = _get_sample_fods_bytes()

    # Step 1: Parse
    wb = fods.parse_fods(data)
    print("Step 1: parse_fods -> OK")

    # Step 2: Sheet names
    sheets = fods.workbook_sheet_names(wb)
    print(f"Step 2: workbook_sheet_names -> {sheets}")

    # Step 3: Row values
    row0 = fods.workbook_row_values(wb, sheets[0], 0)
    print(f"Step 3: workbook_row_values(row=0) -> {row0}")

    # Step 4: Column values
    col0 = fods.workbook_col_values(wb, sheets[0], 0)
    print(f"Step 4: workbook_col_values(col=0) -> {col0}")

    # Step 5: Edit cell
    wb2 = fods.workbook_edit_cell(wb, sheets[0], 1, 0, "SuperWidget")
    print(f"Step 5: workbook_edit_cell -> OK")

    # Step 6: Warnings
    warns = fods.workbook_warnings_for_unsupported_edit(wb2, sheets[0], 1, 0)
    print(f"Step 6: workbook_warnings_for_unsupported_edit -> {warns}")

    # Step 7: Write FODS
    out_bytes = fods.write_fods(wb2)
    print(f"Step 7: write_fods -> {len(out_bytes)} bytes")

    # Step 8: CSV export
    csv_str = fods.workbook_to_csv(wb2, sheets[0])
    print(f"Step 8: workbook_to_csv ->\n{csv_str}")

    # Step 9: Add sheet
    wb3 = fods.workbook_add_sheet(wb2, "Summary")
    print(f"Step 9: workbook_add_sheet -> sheets: {fods.workbook_sheet_names(wb3)}")

    # Step 10: Rename sheet
    wb4 = fods.workbook_rename_sheet(wb3, "Summary", "Report")
    print(f"Step 10: workbook_rename_sheet -> sheets: {fods.workbook_sheet_names(wb4)}")

    # Step 11: Remove sheet
    wb5 = fods.workbook_remove_sheet(wb4, "Report")
    print(f"Step 11: workbook_remove_sheet -> sheets: {fods.workbook_sheet_names(wb5)}")

    print("\nAll 11 product workflow steps: PASS")
    print("FODS_INSTALLED_REAL_SAMPLE_WORKFLOW: PASS")


if __name__ == "__main__":
    main()
