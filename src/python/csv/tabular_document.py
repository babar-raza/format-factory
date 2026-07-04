"""
CSV analytics — extracted analytics/computation functions.

Separated from csv_parser.py to keep it within policy limits (800 LOC / 60 functions).
All functions here call parse_csv_strict from the core parser.
"""

from __future__ import annotations


spec_qname = "csv:record"
spec_fact_ref = "FACT-CSV-001"
namespace_uri = "urn:ietf:rfc:4180"

from pathlib import Path

try:
    from .csv_parser import parse_csv_strict
except ImportError:
    from csv_parser import parse_csv_strict  # fallback for standalone import


def csv_to_dicts(file_path: "str | Path") -> "list[dict[str, str]]":
    """Return CSV rows as a list of dicts mapping column names to string values.

    If the file has a detected header row, column names come from the header.
    Otherwise, columns are named "col_0", "col_1", etc.

    Args:
        file_path: Path to the CSV file.

    Returns:
        List of dicts, one per data row. Empty list if file has no data rows.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return []
    headers = model.get("headers")
    if headers:
        keys = headers
    else:
        col_count = max(len(r) for r in rows)
        keys = [f"col_{i}" for i in range(col_count)]
    result = []
    for row in rows:
        d = {keys[i]: row[i] if i < len(row) else "" for i in range(len(keys))}
        result.append(d)
    return result


def csv_column_count(file_path: "str | Path") -> int:
    """Return the number of columns in the CSV file (length of the header/first row).

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer column count. Returns 0 for empty files.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    return model.get("column_count", 0)


def csv_has_header(file_path: "str | Path") -> bool:
    """Return True if the CSV file was detected as having a header row.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Boolean indicating whether a header row was detected.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    return bool(model.get("has_header", False))


def csv_numeric_row_count(file_path: "str | Path") -> int:
    """Return the count of rows where all non-empty cells are numeric.

    A row is considered numeric if every non-empty cell value can be parsed as float.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer count of all-numeric rows. Returns 0 if no such rows exist.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        non_empty = [str(c) for c in row if str(c).strip()]
        if not non_empty:
            continue
        try:
            for c in non_empty:
                float(c)
            count += 1
        except ValueError:
            pass
    return count


def count_distinct_values(file_path: "str | Path", col_name: str) -> int:
    """Return the count of distinct non-empty values in a CSV column.

    Args:
        file_path: Path to the CSV file.
        col_name: Column header name to inspect.

    Returns:
        Integer count of unique non-empty cell values.
        Returns 0 if the column is not found.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    headers = model.get("headers") or []
    rows = model.get("rows", [])
    # When header detection fails (all-text CSV), check the first data row
    if col_name not in headers and rows:
        first_row = rows[0]
        if col_name in first_row:
            headers = first_row
            rows = rows[1:]
    if col_name not in headers:
        return 0
    col_idx = headers.index(col_name)
    distinct: set[str] = set()
    for row in rows:
        if col_idx < len(row):
            val = str(row[col_idx]).strip()
            if val:
                distinct.add(val)
    return len(distinct)


def csv_duplicate_row_count(file_path: "str | Path") -> int:
    """Return the count of duplicate rows in the CSV file.

    Two rows are duplicates if they have identical cell values (as strings).
    The first occurrence of each unique row is not counted; only subsequent
    duplicates are counted. E.g. if a row appears 3 times, it contributes 2
    to the count.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer count of duplicate rows. Returns 0 if all rows are unique.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    seen: set[tuple[str, ...]] = set()
    count = 0
    for row in rows:
        key = tuple(str(c) for c in row)
        if key in seen:
            count += 1
        else:
            seen.add(key)
    return count


def csv_empty_cell_count(file_path: "str | Path") -> int:
    """Return the total count of empty cells across all rows.

    A cell is considered empty if its string value is empty after stripping.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer count of empty cells. Returns 0 if there are no empty cells.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        for cell in row:
            if not str(cell).strip():
                count += 1
    return count


def csv_row_count(file_path: "str | Path") -> int:
    """Return the number of data rows in a CSV file (excluding header).

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer row count.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    return len(model.get("rows", []))


def csv_average_field_length(file_path: "str | Path") -> float:
    """Return the average length of all field values across all rows.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Float average field length. Returns 0.0 if there are no fields.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    lengths: list[int] = []
    for row in model.get("rows", []):
        for cell in row:
            lengths.append(len(str(cell)))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def csv_numeric_density(file_path: "str | Path") -> float:
    """Return the ratio of numeric cells to total cells. 0.0 if no cells."""
    model = parse_csv_strict(file_path)
    total = 0
    numeric = 0
    for row in model.get("rows", []):
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


def csv_unique_row_count(file_path: "str | Path") -> int:
    """Return the number of distinct rows in the CSV file."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        seen.add(tuple(str(c) for c in row))
    return len(seen)


def csv_min_field_length(file_path: "str | Path") -> int:
    """Return the length of the shortest non-empty field in the CSV.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer minimum length. 0 if no non-empty fields.
    """
    model = parse_csv_strict(file_path)
    min_len = None
    for row in model.get("rows", []):
        for cell in row:
            if cell:
                if min_len is None or len(cell) < min_len:
                    min_len = len(cell)
    return min_len if min_len is not None else 0


def csv_has_duplicates(file_path: "str | Path") -> bool:
    """Return True if the CSV file contains duplicate rows.

    Args:
        file_path: Path to a CSV file.

    Returns:
        True if any two rows are identical.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(str(c) for c in row)
        if key in seen:
            return True
        seen.add(key)
    return False


def csv_all_rows_same_length(file_path: "str | Path") -> bool:
    """Return True if all rows have the same number of fields.

    Args:
        file_path: Path to a CSV file.

    Returns:
        True if every row has an identical field count; True for empty files.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return True
    expected = len(rows[0])
    return all(len(row) == expected for row in rows)


def csv_max_row_length(file_path: "str | Path") -> int:
    """Return the maximum number of fields in any single row.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer max field count. Returns 0 for empty files.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return max(len(row) for row in rows)


def csv_field_type_ratio(file_path: "str | Path") -> float:
    """Return the ratio of numeric fields to string fields.

    Fields that can be parsed as float are numeric; all others are string.
    Empty cells are excluded from both counts.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Float ratio (numeric / string). Returns 0.0 if no string fields.
        Returns float('inf') if all non-empty fields are numeric.
    """
    model = parse_csv_strict(file_path)
    numeric = 0
    string = 0
    for row in model.get("rows", []):
        for cell in row:
            val = str(cell).strip()
            if not val:
                continue
            try:
                float(val)
                numeric += 1
            except (ValueError, TypeError):
                string += 1
    if string == 0:
        return float("inf") if numeric > 0 else 0.0
    return numeric / string


def csv_all_rows(file_path: "str | Path") -> list:
    """Return all data rows from a CSV file as a list of lists.

    Args:
        file_path: Path to a CSV file.

    Returns:
        List of lists, where each inner list is a row of string values.
    """
    model = parse_csv_strict(file_path)
    return list(model.get("rows", []))


def csv_distinct_value_count(file_path: "str | Path") -> int:
    """Return the count of distinct non-empty cell values across all rows.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer count of unique non-empty values.
    """
    model = parse_csv_strict(file_path)
    seen: set = set()
    for row in model.get("rows", []):
        for cell in row:
            val = str(cell).strip()
            if val:
                seen.add(val)
    return len(seen)


def csv_empty_cell_ratio(file_path: "str | Path") -> float:
    """Return the ratio of empty cells to total cells.

    A cell is empty if its stripped string value is empty.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Float ratio in [0.0, 1.0]. Returns 0.0 if no cells exist.
    """
    model = parse_csv_strict(file_path)
    total = 0
    empty = 0
    for row in model.get("rows", []):
        for cell in row:
            total += 1
            if not str(cell).strip():
                empty += 1
    if total == 0:
        return 0.0
    return empty / total


def csv_total_cell_count(file_path: "str | Path") -> int:
    """Return the total number of cells across all rows."""
    model = parse_csv_strict(file_path)
    return sum(len(row) for row in model.get("rows", []))


def csv_min_row_length(file_path: "str | Path") -> int:
    """Return the number of fields in the narrowest row."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return min(len(row) for row in rows)


def csv_max_numeric_value(file_path: "str | Path"):
    """Return the maximum numeric value across all cells, or None if no numeric cells."""
    model = parse_csv_strict(file_path)
    nums = []
    for row in model.get("rows", []):
        for field in row:
            try:
                nums.append(float(field))
            except (ValueError, TypeError):
                pass
    return max(nums) if nums else None


def csv_has_empty_rows(file_path: "str | Path") -> bool:
    """Return True if any row has all-empty fields."""
    model = parse_csv_strict(file_path)
    for row in model.get("rows", []):
        if all(f.strip() == "" for f in row):
            return True
    return False


def csv_header_count(file_path: "str | Path") -> int:
    """Return the number of header columns. 0 if no header detected."""
    model = parse_csv_strict(file_path)
    header = model.get("header", [])
    return len(header)


def csv_is_rectangular(file_path: "str | Path") -> bool:
    """Return True if all rows have the same number of fields."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return True
    first_len = len(rows[0])
    return all(len(row) == first_len for row in rows)


def csv_nonempty_cell_count(file_path: "str | Path") -> int:
    """Return the count of non-empty cells across all rows."""
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        for f in row:
            if f.strip():
                count += 1
    return count


def csv_string_density(file_path: "str | Path") -> float:
    """Return ratio of non-numeric cells to total cells. 0.0 if no cells."""
    total = csv_total_cell_count(file_path)
    if total == 0:
        return 0.0
    numeric = 0
    model = parse_csv_strict(file_path)
    for row in model.get("rows", []):
        for f in row:
            try:
                float(f)
                numeric += 1
            except (ValueError, TypeError):
                pass
    return (total - numeric) / total


def csv_min_numeric_value(file_path: "str | Path"):
    """Return the minimum numeric value across all cells, or None if no numerics."""
    model = parse_csv_strict(file_path)
    nums = []
    for row in model.get("rows", []):
        for f in row:
            try:
                nums.append(float(f))
            except (ValueError, TypeError):
                pass
    return min(nums) if nums else None


def csv_data_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = csv_total_cell_count(file_path)
    if total == 0:
        return 0.0
    nonempty = csv_nonempty_cell_count(file_path)
    return nonempty / total


def csv_avg_row_length(file_path: "str | Path") -> float:
    """Return the average number of fields per row. 0.0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0.0
    return sum(len(row) for row in rows) / len(rows)


def csv_numeric_column_count(file_path: "str | Path") -> int:
    """Return the count of columns where all non-empty values are numeric.

    A column is numeric if every non-empty cell can be parsed as float.
    Empty columns (all empty) are not counted.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    col_count = max(len(row) for row in rows)
    numeric_cols = 0
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
            numeric_cols += 1
    return numeric_cols


# Analytics functions moved to tabular_document_analytics.py (RULE-LIB-004 split)
try:
    from .tabular_document_analytics import *  # noqa: F401, F403
except ImportError:
    try:
        from tabular_document_analytics import *  # noqa: F401, F403
    except ImportError:
        pass
