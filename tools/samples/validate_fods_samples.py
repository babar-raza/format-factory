"""
validate_fods_samples.py — FODS Sample Corpus Validator
format-factory / tools/samples/

Purpose:
    Validate FODS synthetic sample files against Gate 3 acceptance criteria.
    Checks structural correctness, required elements, required attributes,
    and XML well-formedness. Does not require LibreOffice or external tools.

    Checks per sample:
    1. File exists and is non-empty
    2. XML well-formed (Python xml.etree)
    3. Root element is office:document
    4. office:mimetype == application/vnd.oasis.opendocument.spreadsheet-flat-xml
    5. office:version == 1.3
    6. Contains office:body > office:spreadsheet
    7. Contains at least one table:table
    8. Contains at least one table:table-row
    9. Contains at least one table:table-cell
    10. Sample-specific checks (formula, value types, multi-sheet)

Policy:
    - Reads from samples/by-format/fods/
    - No writes except validation-report.txt if --report is specified.
    - No network calls.
    - No LLM calls.

Exit codes:
    0 — All samples PASS
    1 — One or more samples FAIL
"""

import argparse
import pathlib
import sys
import xml.etree.ElementTree as ET

# ODF XML namespaces
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
}

FODS_MIMETYPE = "application/vnd.oasis.opendocument.spreadsheet-flat-xml"
REQUIRED_VERSION = "1.3"


def qname(ns_prefix: str, local: str) -> str:
    return f"{{{NS[ns_prefix]}}}{local}"


class ValidationResult:
    def __init__(self, filename: str):
        self.filename = filename
        self.checks: list[tuple[str, bool, str]] = []  # (check_name, passed, detail)

    def check(self, name: str, passed: bool, detail: str = ""):
        self.checks.append((name, passed, detail))

    @property
    def passed(self) -> bool:
        return all(p for _, p, _ in self.checks)

    @property
    def fail_count(self) -> int:
        return sum(1 for _, p, _ in self.checks if not p)

    @property
    def pass_count(self) -> int:
        return sum(1 for _, p, _ in self.checks if p)


def validate_sample(sample_path: pathlib.Path) -> ValidationResult:
    result = ValidationResult(sample_path.name)

    # Check 1: file exists and non-empty
    if not sample_path.exists():
        result.check("file_exists", False, f"File not found: {sample_path}")
        return result
    size = sample_path.stat().st_size
    result.check("file_exists", True, f"{size} bytes")
    if size == 0:
        result.check("file_non_empty", False, "File is empty")
        return result
    result.check("file_non_empty", True)

    # Check 2: XML well-formed
    try:
        tree = ET.parse(str(sample_path))
        root = tree.getroot()
        result.check("xml_well_formed", True)
    except ET.ParseError as e:
        result.check("xml_well_formed", False, str(e))
        return result

    # Check 3: root element is office:document
    expected_root = qname("office", "document")
    result.check(
        "root_is_office_document",
        root.tag == expected_root,
        f"got: {root.tag}",
    )

    # Check 4: office:mimetype
    mimetype_attr = qname("office", "mimetype")
    mimetype = root.get(mimetype_attr, "")
    result.check(
        "mimetype_correct",
        mimetype == FODS_MIMETYPE,
        f"got: '{mimetype}'",
    )

    # Check 5: office:version
    version_attr = qname("office", "version")
    version = root.get(version_attr, "")
    result.check(
        "version_1_3",
        version == REQUIRED_VERSION,
        f"got: '{version}'",
    )

    # Check 6: office:body > office:spreadsheet
    body = root.find(qname("office", "body"))
    if body is None:
        result.check("has_office_body", False, "office:body not found")
        return result
    result.check("has_office_body", True)

    spreadsheet = body.find(qname("office", "spreadsheet"))
    if spreadsheet is None:
        result.check("has_office_spreadsheet", False, "office:spreadsheet not found in office:body")
        return result
    result.check("has_office_spreadsheet", True)

    # Check 7: at least one table:table
    tables = spreadsheet.findall(qname("table", "table"))
    result.check(
        "has_table_table",
        len(tables) >= 1,
        f"found: {len(tables)} table(s)",
    )

    if not tables:
        return result

    # Check 8: at least one table:table-row across all tables
    all_rows = []
    for t in tables:
        all_rows.extend(t.findall(qname("table", "table-row")))
    result.check(
        "has_table_row",
        len(all_rows) >= 1,
        f"found: {len(all_rows)} row(s)",
    )

    # Check 9: at least one table:table-cell
    all_cells = []
    for row in all_rows:
        all_cells.extend(row.findall(qname("table", "table-cell")))
    result.check(
        "has_table_cell",
        len(all_cells) >= 1,
        f"found: {len(all_cells)} cell(s)",
    )

    return result


def validate_multi_sheet(sample_path: pathlib.Path) -> ValidationResult:
    """Additional checks for multi-sheet sample."""
    result = validate_sample(sample_path)
    if not result.passed:
        return result

    tree = ET.parse(str(sample_path))
    root = tree.getroot()
    spreadsheet = root.find(f".//{{{NS['office']}}}spreadsheet")
    tables = spreadsheet.findall(qname("table", "table"))

    result.check(
        "multi_sheet_has_two_tables",
        len(tables) >= 2,
        f"found: {len(tables)} table(s); expected >= 2",
    )

    # Check table names
    names = [t.get(qname("table", "name"), "") for t in tables]
    result.check(
        "tables_have_names",
        all(n for n in names),
        f"names: {names}",
    )

    return result


def validate_typed_values(sample_path: pathlib.Path) -> ValidationResult:
    """Additional checks for typed-values sample."""
    result = validate_sample(sample_path)
    if not result.passed:
        return result

    tree = ET.parse(str(sample_path))
    root = tree.getroot()
    vt_attr = qname("office", "value-type")
    all_cells = root.findall(f".//{{{NS['table']}}}table-cell")
    value_types = {c.get(vt_attr) for c in all_cells if c.get(vt_attr)}

    result.check("has_float_type", "float" in value_types, f"types found: {value_types}")
    result.check("has_string_type", "string" in value_types, f"types found: {value_types}")
    result.check("has_boolean_type", "boolean" in value_types, f"types found: {value_types}")

    return result


def validate_formula(sample_path: pathlib.Path) -> ValidationResult:
    """Additional checks for formula sample."""
    result = validate_sample(sample_path)
    if not result.passed:
        return result

    tree = ET.parse(str(sample_path))
    root = tree.getroot()
    formula_attr = qname("table", "formula")
    all_cells = root.findall(f".//{{{NS['table']}}}table-cell")
    formula_cells = [c for c in all_cells if c.get(formula_attr)]

    result.check(
        "has_formula_cell",
        len(formula_cells) >= 1,
        f"formula cells: {len(formula_cells)}",
    )

    if formula_cells:
        fc = formula_cells[0]
        formula_val = fc.get(formula_attr, "")
        result.check(
            "formula_has_oooc_prefix",
            formula_val.startswith("oooc:"),
            f"formula: '{formula_val}'",
        )
        cached = fc.get(qname("office", "value"), "")
        result.check(
            "formula_has_cached_result",
            bool(cached),
            f"office:value: '{cached}'",
        )

    return result


SAMPLE_VALIDATORS = {
    "minimal-spreadsheet.fods": validate_sample,
    "multi-sheet-basic.fods": validate_multi_sheet,
    "typed-values-basic.fods": validate_typed_values,
    "formula-basic.fods": validate_formula,
}


def main():
    parser = argparse.ArgumentParser(
        description="Validate FODS Gate 3 sample corpus"
    )
    parser.add_argument(
        "--samples-dir",
        required=True,
        help="Path to samples/by-format/fods/",
    )
    parser.add_argument(
        "--report",
        help="Write validation report to this file path",
    )
    args = parser.parse_args()

    samples_dir = pathlib.Path(args.samples_dir)
    print(f"validate_fods_samples.py — samples: {samples_dir}")
    print()

    results: list[ValidationResult] = []

    for filename, validator in SAMPLE_VALIDATORS.items():
        sample_path = samples_dir / filename
        result = validator(sample_path)
        results.append(result)

        status = "PASS" if result.passed else "FAIL"
        print(f"  {status}  {filename}  ({result.pass_count} checks pass, {result.fail_count} fail)")
        if not result.passed:
            for check_name, passed, detail in result.checks:
                if not passed:
                    print(f"       FAIL  {check_name}: {detail}")

    print()
    total_pass = sum(1 for r in results if r.passed)
    total_fail = sum(1 for r in results if not r.passed)
    print(f"Results: {total_pass}/{len(results)} samples PASS, {total_fail} FAIL")

    if args.report:
        report_path = pathlib.Path(args.report)
        lines = [f"FODS Sample Validation Report\n{'='*40}\n"]
        for r in results:
            lines.append(f"{'PASS' if r.passed else 'FAIL'}  {r.filename}")
            for check_name, passed, detail in r.checks:
                lines.append(f"  {'[OK]' if passed else '[FAIL]'}  {check_name}: {detail}")
            lines.append("")
        lines.append(f"Total: {total_pass}/{len(results)} PASS")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Report written: {report_path}")

    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
