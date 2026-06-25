"""
TSV analytics functions extracted from tsv_parser.py (TC-HEAL-FORMATS-BATCH1).
"""
from __future__ import annotations


spec_qname = "tsv:record"
spec_fact_ref = "FACT-TSV-001"
namespace_uri = "urn:iana:tsv:tab-separated-values"

from pathlib import Path
from typing import Any

from .tsv_parser import (
    parse_tsv_strict,
    get_column_values,
)

def tsv_numeric_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells that contain a numeric value across all rows.

    Scans both the header row (if present) and all data rows. A cell is
    counted as numeric if its string value (after strip) can be converted to
    a float. Empty cells and non-numeric strings are excluded.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer count of numeric cells.

    Raises:
        TsvError subclasses on parse failure.
    """
    parsed = parse_tsv_strict(file_path)

    def _count_in_rows(rows_list):
        c = 0
        for row in rows_list:
            for cell in row:
                if isinstance(cell, str):
                    stripped = cell.strip()
                    if stripped:
                        try:
                            float(stripped)
                            c += 1
                        except ValueError:
                            pass
        return c

    count = _count_in_rows(parsed.get("rows", []))
    headers = parsed.get("headers")
    if headers:
        count += _count_in_rows([headers])
    return count


def tsv_nonempty_cell_count(file_path: "str | Path") -> int:
    """Return the count of all non-empty cells across all rows and columns.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer count of cells where the string value is non-empty after strip.

    Raises:
        TsvError subclasses on parse failure.
    """
    parsed = parse_tsv_strict(file_path)
    count = 0
    for row in parsed.get("rows", []):
        for cell in row:
            if isinstance(cell, str) and cell.strip() != "":
                count += 1
    return count


def tsv_empty_row_count(file_path: "str | Path") -> int:
    """Return the count of rows where all cells are empty strings.

    A row is considered empty if every cell value is an empty string or
    contains only whitespace after stripping.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer count of completely empty rows.

    Raises:
        TsvError subclasses on parse failure.
    """
    parsed = parse_tsv_strict(file_path)
    count = 0
    for row in parsed.get("rows", []):
        if all(not (isinstance(cell, str) and cell.strip()) for cell in row):
            count += 1
    return count


def tsv_row_count(file_path: "str | Path") -> int:
    """Return the number of data rows in the TSV file.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer count of rows. Returns 0 for empty files.

    Raises:
        TsvError subclasses on parse failure.
    """
    parsed = parse_tsv_strict(file_path)
    return len(parsed.get("rows", []))


def tsv_max_cell_length(file_path: "str | Path") -> int:
    """Return the character length of the longest cell value in the TSV file.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer length of the longest cell string. Returns 0 for empty files.

    Raises:
        TsvError subclasses on parse failure.
    """
    parsed = parse_tsv_strict(file_path)
    rows = parsed.get("rows", [])
    if not rows:
        return 0
    return max((len(str(cell)) for row in rows for cell in row), default=0)


def tsv_column_count(file_path: "str | Path") -> int:
    """Return the number of columns (headers) in a TSV file.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer column count based on headers. Returns 0 if no headers.
    """
    parsed = parse_tsv_strict(file_path)
    return len(parsed.get("headers", []))


def count_distinct_values(data: Any, col_name: str) -> int:
    """Return the count of distinct non-empty values in a TSV column.

    Args:
        data: TSV data dict, file path, or raw bytes.
        col_name: Header name of the column to inspect.

    Returns:
        Integer count of unique non-empty cell values.

    Raises:
        TsvError: If the column is not found.
    """
    values = get_column_values(data, col_name)
    distinct: set[str] = set()
    for v in values:
        if v is not None and v != "":
            distinct.add(v)
    return len(distinct)


def tsv_has_header(file_path: "str | Path") -> bool:
    """Return True if the TSV file has a header row.

    Uses the parser's built-in header detection. The parser separates headers
    from data rows when a header is detected.

    Args:
        file_path: Path to a TSV file.

    Returns:
        True if a header is detected, False otherwise.
    """
    doc = parse_tsv_strict(file_path)
    return bool(doc.get("has_header", False))


def tsv_duplicate_row_count(file_path: "str | Path") -> int:
    """Return the count of duplicate rows in the TSV file.

    Two rows are duplicates if they have identical cell values. The first
    occurrence of each unique row is not counted; only subsequent duplicates
    contribute to the count.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer count of duplicate rows. Returns 0 if all rows are unique.
    """
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    seen: set[tuple[str, ...]] = set()
    count = 0
    for row in rows:
        key = tuple(row)
        if key in seen:
            count += 1
        else:
            seen.add(key)
    return count


def tsv_total_cell_count(file_path: "str | Path") -> int:
    """Return the total number of cells in the TSV file (rows * columns).

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer total cell count.
    """
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    return sum(len(row) for row in rows)


def tsv_average_cell_length(file_path: "str | Path") -> float:
    """Return the average character length of non-empty cells.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Float average length. Returns 0.0 if no non-empty cells exist.
    """
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    lengths = [len(cell) for row in rows for cell in row if cell]
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def tsv_numeric_density(file_path: "str | Path") -> float:
    """Return the fraction of cells that are numeric.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Float in [0.0, 1.0]. 0.0 if no cells.
    """
    doc = parse_tsv_strict(file_path)
    total = 0
    numeric = 0
    for row in doc.get("rows", []):
        for cell in row:
            total += 1
            try:
                float(cell)
                numeric += 1
            except (ValueError, TypeError):
                pass
    if total == 0:
        return 0.0
    return numeric / total


def tsv_unique_row_count(file_path: "str | Path") -> int:
    """Return the number of unique rows in the TSV file.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer count of distinct rows.
    """
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        seen.add(tuple(str(c) for c in row))
    return len(seen)


def tsv_header_count(file_path: "str | Path") -> int:
    """Return the number of header columns in the TSV file."""
    doc = parse_tsv_strict(file_path)
    headers = doc.get("headers", [])
    return len(headers) if headers else 0


def tsv_min_cell_length(file_path: "str | Path") -> int:
    """Return the minimum cell length across all data rows.

    Args:
        file_path: Path to a TSV file.

    Returns:
        Integer min cell length, or 0 for empty files.
    """
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    min_len = None
    for row in rows:
        for cell in row:
            cell_str = str(cell) if cell is not None else ""
            if min_len is None or len(cell_str) < min_len:
                min_len = len(cell_str)
    return min_len if min_len is not None else 0


def tsv_all_rows_same_length(file_path: "str | Path") -> bool:
    """Return True if all data rows have the same number of fields.

    Args:
        file_path: Path to a TSV file.

    Returns:
        True if every row has equal field count; True for empty files.
    """
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return True
    expected = len(rows[0])
    return all(len(row) == expected for row in rows)


def tsv_all_rows(file_path: "str | Path") -> list:
    """Return all data rows from a TSV file as a list of lists.

    Args:
        file_path: Path to a TSV file.

    Returns:
        List of lists, where each inner list is a row of string values.
    """
    doc = parse_tsv_strict(file_path)
    return list(doc.get("rows", []))


def tsv_max_numeric_value(file_path: "str | Path"):
    """Return the maximum numeric value across all cells, or None if no numeric cells."""
    doc = parse_tsv_strict(file_path)
    nums = []
    for row in doc.get("rows", []):
        for field in row:
            try:
                nums.append(float(field))
            except (ValueError, TypeError):
                pass
    return max(nums) if nums else None


def tsv_has_empty_rows(file_path: "str | Path") -> bool:
    """Return True if any row has all-empty fields."""
    doc = parse_tsv_strict(file_path)
    for row in doc.get("rows", []):
        if all(f.strip() == "" for f in row):
            return True
    return False


def tsv_is_rectangular(file_path: "str | Path") -> bool:
    """Return True if all rows have the same number of fields."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return True
    first_len = len(rows[0])
    return all(len(row) == first_len for row in rows)


def tsv_empty_cell_count(file_path: "str | Path") -> int:
    """Return the count of empty cells across all rows."""
    doc = parse_tsv_strict(file_path)
    count = 0
    for row in doc.get("rows", []):
        for f in row:
            if f.strip() == "":
                count += 1
    return count


def tsv_data_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = tsv_total_cell_count(file_path)
    if total == 0:
        return 0.0
    nonempty = tsv_nonempty_cell_count(file_path)
    return nonempty / total


def tsv_min_numeric_value(file_path: "str | Path"):
    """Return the minimum numeric value across all cells, or None if no numeric cells."""
    doc = parse_tsv_strict(file_path)
    nums = []
    for row in doc.get("rows", []):
        for field in row:
            try:
                nums.append(float(field))
            except (ValueError, TypeError):
                pass
    return min(nums) if nums else None


def tsv_is_single_column(file_path: "str | Path") -> bool:
    """Return True if all rows have exactly one field."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return False
    return all(len(row) == 1 for row in rows)


def tsv_is_all_numeric(file_path: "str | Path") -> bool:
    """Return True if every non-empty field can be parsed as a number."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    found_any = False
    for row in rows:
        for field in row:
            v = field.strip()
            if v:
                found_any = True
                try:
                    float(v)
                except (ValueError, TypeError):
                    return False
    return found_any


def tsv_max_field_length(file_path: "str | Path") -> int:
    """Return the length of the longest cell value. 0 if no cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0
    return max((len(f) for row in rows for f in row), default=0)


def tsv_unique_value_count(file_path: "str | Path") -> int:
    """Return the count of distinct non-empty cell values."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    values = set()
    for row in rows:
        for f in row:
            v = f.strip()
            if v:
                values.add(v)
    return len(values)


def tsv_row_length_variance(file_path: "str | Path") -> float:
    """Return variance of row lengths (field counts). 0.0 if fewer than 2 rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if len(rows) < 2:
        return 0.0
    lengths = [len(row) for row in rows]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def tsv_column_type_counts(file_path: "str | Path") -> dict:
    """Return dict with counts of numeric and string columns."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return {"numeric": 0, "string": 0}
    col_count = max(len(row) for row in rows)
    numeric = 0
    for ci in range(col_count):
        has_value = False
        all_numeric = True
        for row in rows:
            if ci < len(row):
                val = row[ci].strip()
                if val:
                    has_value = True
                    try:
                        float(val)
                    except (ValueError, TypeError):
                        all_numeric = False
                        break
        if has_value and all_numeric:
            numeric += 1
    return {"numeric": numeric, "string": col_count - numeric}


def tsv_string_density(file_path: "str | Path") -> float:
    """Return ratio of non-numeric cells to total cells. 0.0 if no cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    total = sum(len(row) for row in rows)
    if total == 0:
        return 0.0
    numeric = 0
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                try:
                    float(v)
                    numeric += 1
                except (ValueError, TypeError):
                    pass
    return (total - numeric) / total


def tsv_avg_row_length(file_path: "str | Path") -> float:
    """Return average number of fields per row. 0.0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0.0
    return sum(len(row) for row in rows) / len(rows)


def tsv_max_field_count(file_path: "str | Path") -> int:
    """Return the maximum number of fields in any row. 0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0
    return max(len(row) for row in rows)


def tsv_is_multi_row(file_path: "str | Path") -> bool:
    """Return True if the file has more than one data row."""
    doc = parse_tsv_strict(file_path)
    return len(doc.get("rows", [])) > 1


def tsv_min_field_count(file_path: "str | Path") -> int:
    """Return the minimum number of fields in any row. 0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0
    return min(len(row) for row in rows)


def tsv_nonempty_row_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty rows to total rows. 0.0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0.0
    nonempty = sum(1 for row in rows if any(v.strip() for v in row))
    return nonempty / len(rows)


def tsv_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    total = 0.0
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                try:
                    total += float(v)
                except (ValueError, TypeError):
                    pass
    return total


def tsv_avg_numeric_value(file_path: "str | Path") -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    values = []
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                try:
                    values.append(float(v))
                except (ValueError, TypeError):
                    pass
    if not values:
        return 0.0
    return sum(values) / len(values)


def tsv_has_duplicates(file_path: "str | Path") -> bool:
    """Return True if any duplicate rows exist (including header)."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    seen = set()
    for row in rows:
        key = tuple(row)
        if key in seen:
            return True
        seen.add(key)
    return False


def tsv_empty_column_count(file_path: "str | Path") -> int:
    """Return number of columns that are entirely empty across all rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0
    col_count = max(len(row) for row in rows)
    empty_cols = 0
    for ci in range(col_count):
        if all(ci >= len(row) or not row[ci].strip() for row in rows):
            empty_cols += 1
    return empty_cols


def tsv_is_single_row(file_path: "str | Path") -> bool:
    """Return True if the file has exactly one data row."""
    doc = parse_tsv_strict(file_path)
    return len(doc.get("rows", [])) == 1


def tsv_longest_row_index(file_path: "str | Path") -> int:
    """Return the 0-based index of the row with the most fields. -1 if empty."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return -1
    return max(range(len(rows)), key=lambda i: len(rows[i]))


def tsv_max_row_cell_count(file_path: "str | Path") -> int:
    """Return the maximum number of cells in any row. 0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0
    return max(len(row) for row in rows)


def tsv_distinct_value_ratio(file_path: "str | Path") -> float:
    """Return ratio of distinct cell values to total cells. 0.0 if no cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    all_vals = []
    for row in rows:
        all_vals.extend(row)
    if not all_vals:
        return 0.0
    return len(set(all_vals)) / len(all_vals)


def tsv_empty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of empty cells to total cells. 0.0 if no cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    total = 0
    empty = 0
    for row in rows:
        for val in row:
            total += 1
            if not val.strip():
                empty += 1
    if total == 0:
        return 0.0
    return empty / total


def tsv_column_value_variance(file_path: "str | Path") -> float:
    """Return variance of numeric cell values. 0.0 if fewer than 2 numeric values."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    nums = []
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                try:
                    nums.append(float(v))
                except (ValueError, TypeError):
                    pass
    if len(nums) < 2:
        return 0.0
    mean = sum(nums) / len(nums)
    return sum((n - mean) ** 2 for n in nums) / len(nums)


def tsv_field_length_sum(file_path: "str | Path") -> int:
    """Return total character length of all field values. 0 if no fields."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    return sum(len(val) for row in rows for val in row)


def tsv_numeric_field_ratio(file_path: "str | Path") -> float:
    """Return ratio of numeric fields to total fields. 0.0 if no fields."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    total = 0
    numeric = 0
    for row in rows:
        for val in row:
            total += 1
            v = val.strip()
            if v:
                try:
                    float(v)
                    numeric += 1
                except (ValueError, TypeError):
                    pass
    if total == 0:
        return 0.0
    return numeric / total


def tsv_is_square(file_path: "str | Path") -> bool:
    """Return True if row count equals column count."""
    return tsv_row_count(file_path) == tsv_column_count(file_path)


def tsv_cell_to_row_ratio(file_path: "str | Path") -> float:
    """Return total cell count divided by row count. 0.0 if no rows."""
    rows = tsv_row_count(file_path)
    if rows == 0:
        return 0.0
    return tsv_total_cell_count(file_path) / rows


def tsv_string_cell_count(file_path: "str | Path") -> int:
    """Return count of cells with non-numeric string values."""
    doc = parse_tsv_strict(file_path)
    count = 0
    for row in doc.get("rows", []):
        for cell in row:
            if cell is not None:
                s = str(cell).strip()
                if s:
                    try:
                        float(s)
                    except (ValueError, TypeError):
                        count += 1
    return count


def tsv_total_string_length(file_path: "str | Path") -> int:
    """Return sum of character lengths of all cell values."""
    doc = parse_tsv_strict(file_path)
    total = 0
    for row in doc.get("rows", []):
        for cell in row:
            if cell is not None:
                total += len(str(cell))
    return total


def tsv_nonempty_row_count(file_path: "str | Path") -> int:
    """Return count of rows that have at least one non-empty field."""
    doc = parse_tsv_strict(file_path)
    count = 0
    for row in doc.get("rows", []):
        if any(cell is not None and str(cell).strip() for cell in row):
            count += 1
    return count


def tsv_avg_fields_per_row(file_path: "str | Path") -> float:
    """Return average number of fields per row. 0.0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0.0
    return sum(len(row) for row in rows) / len(rows)


def tsv_nonempty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    total = sum(len(row) for row in rows)
    if total == 0:
        return 0.0
    nonempty = sum(
        1 for row in rows for cell in row
        if cell is not None and str(cell).strip()
    )
    return nonempty / total
