"""
ODS analytics functions extracted from ods_parser.py (TC-HEAL-FORMATS-BATCH1).
"""
from __future__ import annotations


spec_qname = "office:document"
spec_fact_ref = "FACT-ODS-001"
namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

from pathlib import Path
from typing import Any

from .ods_parser import (
    parse_ods,
    parse_ods_strict,
    get_row_count,
    get_column_count,
    get_cell_value,
)


def ods_max_row_length(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the maximum number of cells in any single row of a sheet.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer max cell count. Returns 0 if sheet is empty or not found.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    if not sheet.rows:
        return 0
    return max(len(row.cells) for row in sheet.rows)


def ods_numeric_cell_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the count of cells containing numeric (int or float) values.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer count of numeric cells. Returns 0 if sheet is empty or not found.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    count = 0
    for row in sheet.rows:
        for cell in row.cells:
            val = cell.value
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                count += 1
    return count


def ods_string_cell_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the count of cells that contain non-numeric, non-empty string values.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer count of string cells. Returns 0 if sheet is empty or not found.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    count = 0
    for row in sheet.rows:
        for cell in row.cells:
            val = cell.value
            if val is None or val == "":
                continue
            try:
                float(str(val))
            except (ValueError, TypeError):
                count += 1
    return count


def ods_row_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the number of rows in an ODS sheet.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer row count. Returns 0 if sheet is empty or not found.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    return len(doc.sheets[sheet_index].rows)


def ods_empty_cell_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the count of cells with no value (None or empty string).

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer count of empty cells. Returns 0 if sheet is empty or not found.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    count = 0
    for row in sheet.rows:
        for cell in row.cells:
            val = cell.value
            if val is None or val == "":
                count += 1
    return count


def ods_column_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the maximum number of columns across all rows in a sheet.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer max column count. Returns 0 if sheet is empty or not found.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    if not sheet.rows:
        return 0
    return max(len(row.cells) for row in sheet.rows)


def ods_empty_row_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the count of rows where all cells are empty (None or empty string).

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer count of fully-empty rows. Returns 0 if sheet is empty or not found.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    count = 0
    for row in sheet.rows:
        if all(
            cell.value is None or cell.value == ""
            for cell in row.cells
        ):
            count += 1
    return count


def ods_total_cell_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the total number of cells (including empty) in a sheet.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer total cell count. Returns 0 if sheet is empty or not found.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    return sum(len(row.cells) for row in sheet.rows)


def ods_sheet_count(file_path: "str | Path") -> int:
    """Return the number of sheets in an ODS file.

    Args:
        file_path: Path to ODS file.

    Returns:
        Integer sheet count.
    """
    doc = parse_ods_strict(file_path)
    return len(doc.sheets)


def ods_has_merged_cells(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the sheet contains any merged cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False
    sheet = doc.sheets[sheet_index]
    for row in sheet.rows:
        for cell in row.cells:
            cols_span = getattr(cell, "number_columns_spanned", 1) or 1
            rows_span = getattr(cell, "number_rows_spanned", 1) or 1
            if cols_span > 1 or rows_span > 1:
                return True
    return False


def ods_numeric_density(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return the ratio of numeric cells to total cells. 0.0 if no cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    total = 0
    numeric = 0
    for row in sheet.rows:
        for cell in row.cells:
            total += 1
            vt = getattr(cell, "value_type", "")
            if vt in ("float", "currency", "percentage"):
                numeric += 1
    if total == 0:
        return 0.0
    return numeric / total


def ods_average_cells_per_row(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return the average number of cells per row in the specified sheet.

    Args:
        file_path: Path to an ODS file.
        sheet_index: 0-based sheet index.

    Returns:
        Float average. 0.0 if no rows.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    if not sheet.rows:
        return 0.0
    total_cells = sum(len(row.cells) for row in sheet.rows)
    return total_cells / len(sheet.rows)


def ods_has_empty_rows(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the specified sheet contains any completely empty rows.

    Args:
        file_path: Path to an ODS file.
        sheet_index: 0-based sheet index.

    Returns:
        True if at least one row has all empty/None cells.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False
    sheet = doc.sheets[sheet_index]
    for row in sheet.rows:
        if not row.cells:
            return True
        all_empty = all(
            not getattr(cell, "value", None) and not getattr(cell, "text", None)
            for cell in row.cells
        )
        if all_empty:
            return True
    return False


def ods_merged_cell_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the number of merged cells in the specified sheet.

    A cell is considered merged if its column span or row span is greater than 1.

    Args:
        file_path: Path to an ODS file.
        sheet_index: 0-based sheet index.

    Returns:
        Integer count of merged cells. Returns 0 if sheet_index is out of range.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    count = 0
    for row in sheet.rows:
        for cell in row.cells:
            cols_span = getattr(cell, "number_columns_spanned", 1) or 1
            rows_span = getattr(cell, "number_rows_spanned", 1) or 1
            if cols_span > 1 or rows_span > 1:
                count += 1
    return count


def ods_avg_cells_per_sheet(file_path: "str | Path") -> float:
    """Return the average number of cells per sheet across all sheets.

    Args:
        file_path: Path to an ODS file.

    Returns:
        Float average cells per sheet, or 0.0 if no sheets.
    """
    doc = parse_ods_strict(file_path)
    if not doc.sheets:
        return 0.0
    total = sum(sum(len(row.cells) for row in sheet.rows) for sheet in doc.sheets)
    return total / len(doc.sheets)


def ods_data_density(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return the ratio of non-empty cells to total cells in a sheet.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Float ratio 0.0-1.0. Returns 0.0 if no cells.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    total = 0
    nonempty = 0
    for row in sheet.rows:
        for cell in row.cells:
            total += 1
            val = cell.value
            if val is not None and val != "":
                nonempty += 1
    if total == 0:
        return 0.0
    return nonempty / total


def ods_max_cell_value_length(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the length of the longest cell value (as string) in a sheet.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer max length. Returns 0 if no cells or all cells empty.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    max_len = 0
    for row in sheet.rows:
        for cell in row.cells:
            val = cell.value
            if val is not None:
                max_len = max(max_len, len(str(val)))
    return max_len


def ods_min_cell_value_length(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the length of the shortest non-empty cell value (as string) in a sheet.

    Returns 0 if no non-empty cells.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    min_len = None
    for row in sheet.rows:
        for cell in row.cells:
            val = cell.value
            if val is not None:
                s = str(val).strip()
                if s:
                    length = len(str(val))
                    if min_len is None or length < min_len:
                        min_len = length
    return min_len if min_len is not None else 0


def ods_all_sheets_have_data(file_path: "str | Path") -> bool:
    """Return True if every sheet has at least one non-empty cell; False otherwise."""
    doc = parse_ods_strict(file_path)
    if not doc.sheets:
        return False
    for sheet in doc.sheets:
        has_data = False
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    has_data = True
                    break
            if has_data:
                break
        if not has_data:
            return False
    return True


def ods_is_single_sheet(file_path: "str | Path") -> bool:
    """Return True if the ODS file contains exactly one sheet."""
    doc = parse_ods_strict(file_path)
    return len(doc.sheets) == 1


def ods_string_density(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return the ratio of string cells to total cells. 0.0 if no cells."""
    total = ods_total_cell_count(file_path, sheet_index)
    if total == 0:
        return 0.0
    strings = ods_string_cell_count(file_path, sheet_index)
    return strings / total


def ods_max_numeric_value(file_path: "str | Path", sheet_index: int = 0):
    """Return the maximum numeric cell value in the specified sheet, or None."""
    doc = parse_ods_strict(file_path)
    sheet = doc.sheets[sheet_index]
    nums = [
        c.value
        for row in sheet.rows
        for c in row.cells
        if c is not None and isinstance(c.value, (int, float))
    ]
    return max(nums) if nums else None


def ods_has_string_cells(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the specified sheet has any string cell values."""
    doc = parse_ods_strict(file_path)
    sheet = doc.sheets[sheet_index]
    return any(
        isinstance(c.value, str) and c.value.strip()
        for row in sheet.rows
        for c in row.cells
        if c is not None
    )


def ods_min_numeric_value(file_path: "str | Path", sheet_index: int = 0):
    """Return the minimum numeric cell value, or None if no numeric cells."""
    doc = parse_ods_strict(file_path)
    sheet = doc.sheets[sheet_index]
    nums = [
        c.value
        for row in sheet.rows
        for c in row.cells
        if c is not None and isinstance(c.value, (int, float))
    ]
    return min(nums) if nums else None


def ods_has_numeric_cells(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the specified sheet has any numeric cell values."""
    doc = parse_ods_strict(file_path)
    sheet = doc.sheets[sheet_index]
    return any(
        isinstance(c.value, (int, float))
        for row in sheet.rows
        for c in row.cells
        if c is not None
    )


def ods_nonempty_row_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the count of rows that have at least one non-empty cell."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    count = 0
    for row in sheet.rows:
        if any(
            cell.value is not None and cell.value != ""
            for cell in row.cells
        ):
            count += 1
    return count


def ods_is_empty(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the specified sheet has no non-empty cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return True
    sheet = doc.sheets[sheet_index]
    return not any(
        cell.value is not None and cell.value != ""
        for row in sheet.rows
        for cell in row.cells
    )


def ods_is_single_row(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the sheet has exactly one non-empty row."""
    return ods_nonempty_row_count(file_path, sheet_index) == 1


def ods_avg_row_length(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return average number of non-empty cells per non-empty row. 0.0 if no non-empty rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    nonempty_rows = [
        row for row in sheet.rows
        if any(cell.value is not None and cell.value != "" for cell in row.cells)
    ]
    if not nonempty_rows:
        return 0.0
    total = sum(
        sum(1 for cell in row.cells if cell.value is not None and cell.value != "")
        for row in nonempty_rows
    )
    return total / len(nonempty_rows)


def ods_nonempty_cell_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the count of non-empty cells in a sheet."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    return sum(
        1 for row in sheet.rows for cell in row.cells
        if cell.value is not None and str(cell.value).strip()
    )


def ods_cell_value_variance(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return variance of numeric cell values. 0.0 if fewer than 2 numeric cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    nums = []
    for row in sheet.rows:
        for cell in row.cells:
            if cell.value is not None:
                try:
                    nums.append(float(cell.value))
                except (ValueError, TypeError):
                    pass
    if len(nums) < 2:
        return 0.0
    mean = sum(nums) / len(nums)
    return sum((n - mean) ** 2 for n in nums) / len(nums)


def ods_column_value_variance(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return variance of cell counts per column. 0.0 if fewer than 2 columns."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    if not sheet.rows:
        return 0.0
    max_cols = max((len(row.cells) for row in sheet.rows), default=0)
    if max_cols < 2:
        return 0.0
    col_counts = []
    for c in range(max_cols):
        count = sum(1 for row in sheet.rows if c < len(row.cells) and row.cells[c].value is not None and str(row.cells[c].value).strip())
        col_counts.append(count)
    mean = sum(col_counts) / len(col_counts)
    return sum((v - mean) ** 2 for v in col_counts) / len(col_counts)


def ods_has_formulas(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if any cell in the sheet contains a formula."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False
    sheet = doc.sheets[sheet_index]
    for row in sheet.rows:
        for cell in row.cells:
            if hasattr(cell, 'formula') and cell.formula:
                return True
    return False


def ods_row_value_variance(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return variance of non-empty cell counts across rows. 0.0 if fewer than 2 rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    counts = []
    for row in sheet.rows:
        n = sum(1 for c in row.cells if c.value is not None and str(c.value).strip())
        counts.append(n)
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def ods_is_multi_sheet(file_path: "str | Path") -> bool:
    """Return True if the document has more than one sheet."""
    doc = parse_ods_strict(file_path)
    return len(doc.sheets) > 1


def ods_is_single_cell(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if the sheet has exactly one non-empty cell."""
    return ods_nonempty_cell_count(file_path, sheet_index) == 1


def ods_max_sheet_row_count(file_path: "str | Path") -> int:
    """Return the maximum row count across all sheets. 0 if no sheets."""
    doc = parse_ods_strict(file_path)
    if not doc.sheets:
        return 0
    return max(len(s.rows) for s in doc.sheets)


def ods_is_rectangular(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if all non-empty rows have the same number of cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return True
    sheet = doc.sheets[sheet_index]
    nonempty = [row for row in sheet.rows if any(c.value is not None and str(c.value).strip() for c in row.cells)]
    if len(nonempty) < 2:
        return True
    lengths = [len(row.cells) for row in nonempty]
    return len(set(lengths)) == 1


def ods_total_string_length(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return total character length of all string cell values. 0 if none."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    total = 0
    for row in doc.sheets[sheet_index].rows:
        for cell in row.cells:
            if cell.value is not None and isinstance(cell.value, str):
                total += len(cell.value)
    return total


def ods_is_all_numeric(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if all non-empty cells have numeric values. False if no cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False
    has_data = False
    for row in doc.sheets[sheet_index].rows:
        for cell in row.cells:
            if cell.value is None or str(cell.value).strip() == "":
                continue
            has_data = True
            try:
                float(str(cell.value))
            except (ValueError, TypeError):
                return False
    return has_data


def ods_empty_sheet_count(file_path: "str | Path") -> int:
    """Return number of sheets with zero non-empty cells."""
    doc = parse_ods_strict(file_path)
    count = 0
    for sheet in doc.sheets:
        has_data = False
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    has_data = True
                    break
            if has_data:
                break
        if not has_data:
            count += 1
    return count


def ods_numeric_sum(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    total = 0.0
    for row in doc.sheets[sheet_index].rows:
        for cell in row.cells:
            if cell.value is not None:
                try:
                    total += float(str(cell.value))
                except (ValueError, TypeError):
                    pass
    return total


def ods_min_row_length(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the minimum number of non-empty cells in any non-empty row. 0 if no rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    nonempty_rows = [
        row for row in sheet.rows
        if any(cell.value is not None and cell.value != "" for cell in row.cells)
    ]
    if not nonempty_rows:
        return 0
    return min(
        sum(1 for cell in row.cells if cell.value is not None and cell.value != "")
        for row in nonempty_rows
    )


def ods_avg_numeric_value(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    values = []
    for row in doc.sheets[sheet_index].rows:
        for cell in row.cells:
            if cell.value is not None:
                try:
                    values.append(float(str(cell.value)))
                except (ValueError, TypeError):
                    pass
    return sum(values) / len(values) if values else 0.0


def ods_nonempty_row_ratio(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return ratio of non-empty rows to total rows. 0.0 if no rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    rows = doc.sheets[sheet_index].rows
    if not rows:
        return 0.0
    nonempty = sum(
        1 for row in rows
        if any(cell.value is not None and str(cell.value).strip() for cell in row.cells)
    )
    return nonempty / len(rows)


def ods_longest_row_index(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return 0-based index of the row with the most non-empty cells. -1 if no rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return -1
    rows = doc.sheets[sheet_index].rows
    if not rows:
        return -1
    best_idx, best_count = 0, 0
    for i, row in enumerate(rows):
        count = sum(1 for cell in row.cells if cell.value is not None and str(cell.value).strip())
        if count > best_count:
            best_count = count
            best_idx = i
    return best_idx


def ods_numeric_sum_all(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values across all sheets."""
    doc = parse_ods_strict(file_path)
    total = 0.0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None:
                    try:
                        total += float(str(cell.value))
                    except (ValueError, TypeError):
                        pass
    return total


def ods_empty_column_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return number of columns that are entirely empty."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    rows = doc.sheets[sheet_index].rows
    if not rows:
        return 0
    max_cols = max((len(row.cells) for row in rows), default=0)
    empty_count = 0
    for col_idx in range(max_cols):
        col_empty = all(
            col_idx >= len(row.cells) or row.cells[col_idx].value is None
            or str(row.cells[col_idx].value).strip() == ""
            for row in rows
        )
        if col_empty:
            empty_count += 1
    return empty_count


def ods_max_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values across all sheets. 0.0 if none."""
    doc = parse_ods_strict(file_path)
    total = 0.0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None:
                    try:
                        total += float(str(cell.value))
                    except (ValueError, TypeError):
                        pass
    return total


def ods_cell_density(file_path: "str | Path") -> float:
    """Return average number of non-empty cells per row. 0.0 if no rows."""
    doc = parse_ods_strict(file_path)
    total_rows = 0
    nonempty_cells = 0
    for sheet in doc.sheets:
        for row in sheet.rows:
            total_rows += 1
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    nonempty_cells += 1
    if total_rows == 0:
        return 0.0
    return nonempty_cells / total_rows


def ods_numeric_ratio(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return numeric cell count divided by total cell count. 0.0 if no cells."""
    total = ods_total_cell_count(file_path, sheet_index)
    if total == 0:
        return 0.0
    return ods_numeric_cell_count(file_path, sheet_index) / total


def ods_is_square(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if row count equals column count for the given sheet."""
    return ods_row_count(file_path, sheet_index) == ods_column_count(file_path, sheet_index)


def ods_numeric_column_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return count of columns that contain at least one numeric value."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    numeric_cols: set[int] = set()
    for row in sheet.rows:
        for ci, cell in enumerate(row.cells):
            if cell.value is not None:
                try:
                    float(str(cell.value))
                    numeric_cols.add(ci)
                except (ValueError, TypeError):
                    pass
    return len(numeric_cols)


def ods_row_cell_variance(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return variance of cell counts across rows. 0.0 if fewer than 2 rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    counts = [len(row.cells) for row in sheet.rows]
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)
