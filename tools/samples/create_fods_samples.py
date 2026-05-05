"""
create_fods_samples.py — FODS Synthetic Sample Generator
format-factory / tools/samples/

Purpose:
    Generate synthetic FODS (Flat OpenDocument Spreadsheet) sample files
    for Gate 3 corpus. Samples are project-owned (Apache-2.0) and contain
    no copied spec text or third-party content.

    Produces 4 samples in samples/by-format/fods/:
    1. minimal-spreadsheet.fods   — minimal conforming FODS
    2. multi-sheet-basic.fods     — two named sheets, string values
    3. typed-values-basic.fods    — float, string, boolean value types
    4. formula-basic.fods         — SUM formula with cached result

Policy:
    - Output directory: samples/by-format/fods/ (relative to repo root)
    - All samples are Apache-2.0 licensed, project-owned synthetic content.
    - No spec text copied into samples.
    - No network calls.
    - No LLM calls.

Spec basis:
    §2.2.4  Spreadsheet conformance (ODF 1.3)
    §3.1.2  office:document root element
    §3.7    office:spreadsheet body
    §9.4    Table structure, cell types, formulas
"""

import argparse
import pathlib
import sys

# Required XML namespaces for FODS per ODF 1.3
FODS_NS = (
    'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"\n'
    '    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"\n'
    '    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"\n'
    '    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
)
FODS_MIMETYPE = "application/vnd.oasis.opendocument.spreadsheet-flat-xml"
FODS_VERSION = "1.3"


def make_document_header(namespaces: str = FODS_NS) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<office:document\n    {namespaces}\n'
        f'    office:mimetype="{FODS_MIMETYPE}"\n'
        f'    office:version="{FODS_VERSION}">'
    )


DOCUMENT_FOOTER = "</office:document>"


def string_cell(value: str) -> str:
    return (
        f'          <table:table-cell office:value-type="string">\n'
        f'            <text:p>{value}</text:p>\n'
        f'          </table:table-cell>'
    )


def float_cell(value: float) -> str:
    return (
        f'          <table:table-cell office:value-type="float" office:value="{value}">\n'
        f'            <text:p>{value}</text:p>\n'
        f'          </table:table-cell>'
    )


def boolean_cell(value: bool) -> str:
    bv = "true" if value else "false"
    display = "TRUE" if value else "FALSE"
    return (
        f'          <table:table-cell office:value-type="boolean" office:boolean-value="{bv}">\n'
        f'            <text:p>{display}</text:p>\n'
        f'          </table:table-cell>'
    )


def formula_cell(formula: str, result_type: str, result_value: str) -> str:
    return (
        f'          <table:table-cell table:formula="{formula}" '
        f'office:value-type="{result_type}" office:value="{result_value}">\n'
        f'            <text:p>{result_value}</text:p>\n'
        f'          </table:table-cell>'
    )


def make_row(*cells: str) -> str:
    joined = "\n".join(cells)
    return f"        <table:table-row>\n{joined}\n        </table:table-row>"


def make_table(name: str, *rows: str) -> str:
    joined = "\n".join(rows)
    return (
        f'      <table:table table:name="{name}">\n'
        f"{joined}\n"
        f"      </table:table>"
    )


def make_spreadsheet(*tables: str) -> str:
    joined = "\n".join(tables)
    return (
        "  <office:body>\n"
        "    <office:spreadsheet>\n"
        f"{joined}\n"
        "    </office:spreadsheet>\n"
        "  </office:body>"
    )


def generate_minimal() -> str:
    """Sample 1: minimal conforming FODS — single sheet, one string cell."""
    table = make_table(
        "Sheet1",
        make_row(string_cell("Hello")),
    )
    return "\n".join([
        make_document_header(),
        make_spreadsheet(table),
        DOCUMENT_FOOTER,
    ])


def generate_multi_sheet() -> str:
    """Sample 2: two named sheets with string values."""
    data_table = make_table(
        "Data",
        make_row(string_cell("Name"), string_cell("Value")),
        make_row(string_cell("Alpha"), string_cell("Beta")),
    )
    summary_table = make_table(
        "Summary",
        make_row(string_cell("Summary Sheet")),
    )
    return "\n".join([
        make_document_header(),
        make_spreadsheet(data_table, summary_table),
        DOCUMENT_FOOTER,
    ])


def generate_typed_values() -> str:
    """Sample 3: float, string, and boolean value types."""
    table = make_table(
        "Sheet1",
        make_row(string_cell("Type"), string_cell("Value")),
        make_row(string_cell("string"), string_cell("Hello World")),
        make_row(string_cell("float"), float_cell(42.5)),
        make_row(string_cell("boolean"), boolean_cell(True)),
    )
    return "\n".join([
        make_document_header(),
        make_spreadsheet(table),
        DOCUMENT_FOOTER,
    ])


def generate_formula_basic() -> str:
    """Sample 4: SUM formula with cached result."""
    table = make_table(
        "Sheet1",
        make_row(float_cell(10)),
        make_row(float_cell(20)),
        make_row(float_cell(30)),
        make_row(formula_cell("oooc:=SUM([.A1:.A3])", "float", "60")),
    )
    return "\n".join([
        make_document_header(),
        make_spreadsheet(table),
        DOCUMENT_FOOTER,
    ])


SAMPLES = {
    "minimal-spreadsheet.fods": generate_minimal,
    "multi-sheet-basic.fods": generate_multi_sheet,
    "typed-values-basic.fods": generate_typed_values,
    "formula-basic.fods": generate_formula_basic,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate FODS synthetic sample files for Gate 3 corpus"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory (e.g. samples/by-format/fods)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing files",
    )
    args = parser.parse_args()

    out_dir = pathlib.Path(args.output_dir)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    print(f"create_fods_samples.py — output: {out_dir}")
    print()

    for filename, generator in SAMPLES.items():
        content = generator()
        out_path = out_dir / filename
        if args.dry_run:
            print(f"  [dry-run] Would write: {out_path} ({len(content)} chars)")
        else:
            out_path.write_text(content, encoding="utf-8")
            print(f"  Written: {out_path} ({len(content)} chars)")

    print()
    print(f"Total: {len(SAMPLES)} samples {'(dry-run)' if args.dry_run else 'written'}")
    print("License: Apache-2.0 (project-owned synthetic)")
    print("No spec text copied. No network calls. No LLM calls.")


if __name__ == "__main__":
    main()
