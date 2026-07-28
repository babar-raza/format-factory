"""
csv_tabular_document_analytics.py — additional analytics for CSV (split from tabular_document.py).

Separated from tabular_document.py to keep each file within policy limits (800 LOC / 60 functions).
All functions call parse_csv_strict from the core parser.
"""

from __future__ import annotations

from pathlib import Path

try:
    from .csv_parser import parse_csv_strict
except ImportError:
    from csv_parser import parse_csv_strict  # fallback for standalone import


def csv_is_single_column(file_path: "str | Path") -> bool:
    """Return True if all rows have exactly one field."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return False
    return all(len(row) == 1 for row in rows)


def csv_is_all_numeric(file_path: "str | Path") -> bool:
    """Return True if every non-empty cell value can be parsed as a number."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    found_any = False
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                found_any = True
                try:
                    float(v)
                except (ValueError, TypeError):
                    return False
    return found_any


def csv_max_field_value_length(file_path: "str | Path") -> int:
    """Return the length of the longest cell value. 0 if no cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return max((len(f) for row in rows for f in row), default=0)


def csv_unique_value_count(file_path: "str | Path") -> int:
    """Return the count of distinct non-empty cell values."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    values = set()
    for row in rows:
        for f in row:
            v = f.strip()
            if v:
                values.add(v)
    return len(values)


def csv_column_type_counts(file_path: "str | Path") -> dict:
    """Return dict with counts of numeric and string columns."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
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


def csv_row_length_variance(file_path: "str | Path") -> float:
    """Return variance of row lengths. 0.0 if fewer than 2 rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if len(rows) < 2:
        return 0.0
    lengths = [len(row) for row in rows]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def csv_is_empty(file_path: "str | Path") -> bool:
    """Return True if the CSV has no data rows."""
    model = parse_csv_strict(file_path)
    return len(model.get("rows", [])) == 0


def csv_column_name_lengths(file_path: "str | Path") -> list:
    """Return list of header column name lengths. Empty list if no header."""
    model = parse_csv_strict(file_path)
    headers = model.get("headers", [])
    return [len(h) for h in headers]


def csv_max_field_count(file_path: "str | Path") -> int:
    """Return the maximum number of fields in any row. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return max(len(row) for row in rows)


def csv_is_multi_row(file_path: "str | Path") -> bool:
    """Return True if the file has more than one data row."""
    model = parse_csv_strict(file_path)
    return len(model.get("rows", [])) > 1


def csv_column_count_variance(file_path: "str | Path") -> float:
    """Return variance of field counts across rows. 0.0 if fewer than 2 rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if len(rows) < 2:
        return 0.0
    counts = [len(row) for row in rows]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def csv_has_numeric_header(file_path: "str | Path") -> bool:
    """Return True if any header column name is purely numeric."""
    model = parse_csv_strict(file_path)
    headers = model.get("headers", [])
    for h in headers:
        if h.strip():
            try:
                float(h.strip())
                return True
            except (ValueError, TypeError):
                pass
    return False


def csv_nonempty_row_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty rows to total rows. 0.0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0.0
    nonempty = sum(1 for row in rows if any(v.strip() for v in row))
    return nonempty / len(rows)


def csv_avg_cell_length(file_path: "str | Path") -> float:
    """Return average character length of all cells. 0.0 if no cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    total_len = 0
    total_count = 0
    for row in rows:
        for val in row:
            total_len += len(val)
            total_count += 1
    if total_count == 0:
        return 0.0
    return total_len / total_count


def csv_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
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


def csv_avg_numeric_value(file_path: "str | Path") -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    nums = []
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                try:
                    nums.append(float(v))
                except (ValueError, TypeError):
                    pass
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def csv_is_single_row(file_path: "str | Path") -> bool:
    """Return True if the file has exactly one data row."""
    model = parse_csv_strict(file_path)
    return len(model.get("rows", [])) == 1


def csv_empty_column_count(file_path: "str | Path") -> int:
    """Return number of columns that are entirely empty across all data rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    col_count = max(len(row) for row in rows)
    empty_cols = 0
    for ci in range(col_count):
        if all(ci >= len(row) or not row[ci].strip() for row in rows):
            empty_cols += 1
    return empty_cols


def csv_longest_row_index(file_path: "str | Path") -> int:
    """Return 0-based index of the row with the most fields. -1 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return -1
    return max(range(len(rows)), key=lambda i: len(rows[i]))


def csv_total_string_length(file_path: "str | Path") -> int:
    """Return total character count of all cell values combined."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return sum(len(val) for row in rows for val in row)


def csv_min_row_field_count(file_path: "str | Path") -> int:
    """Return the minimum number of fields in any row. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return min(len(row) for row in rows)


def csv_is_square(file_path: "str | Path") -> bool:
    """Return True if row count equals the field count of the first row."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return False
    return len(rows) == len(rows[0])


def csv_column_value_variance(file_path: "str | Path") -> float:
    """Return variance of numeric cell values across all cells. 0.0 if fewer than 2 numeric values."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
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


def csv_is_multi_column(file_path: "str | Path") -> bool:
    """Return True if the file has more than one column in any row."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return any(len(row) > 1 for row in rows)


def csv_field_type_variance(file_path: "str | Path") -> float:
    """Return variance of numeric vs string field counts per row. 0.0 if fewer than 2 rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if len(rows) < 2:
        return 0.0
    numeric_counts = []
    for row in rows:
        nc = 0
        for val in row:
            v = val.strip()
            if v:
                try:
                    float(v)
                    nc += 1
                except (ValueError, TypeError):
                    pass
        numeric_counts.append(nc)
    mean = sum(numeric_counts) / len(numeric_counts)
    return sum((n - mean) ** 2 for n in numeric_counts) / len(numeric_counts)


def csv_header_length_sum(file_path: "str | Path") -> int:
    """Return total character length of all header (first row) fields. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return sum(len(field) for field in rows[0])


def csv_row_length_sum(file_path: "str | Path") -> int:
    """Return total character length of all field values across all rows."""
    model = parse_csv_strict(file_path)
    return sum(len(val) for row in model.get("rows", []) for val in row)


def csv_empty_field_ratio(file_path: "str | Path") -> float:
    """Return ratio of empty fields to total fields. 0.0 if no fields."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
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


def csv_string_cell_count(file_path: "str | Path") -> int:
    """Return count of cells with non-numeric string values."""
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        for val in row:
            s = val.strip()
            if s:
                try:
                    float(s)
                except (ValueError, TypeError):
                    count += 1
    return count


def csv_nonempty_row_count(file_path: "str | Path") -> int:
    """Return count of rows that have at least one non-empty field."""
    model = parse_csv_strict(file_path)
    return sum(
        1 for row in model.get("rows", [])
        if any(val.strip() for val in row)
    )


def csv_avg_fields_per_row(file_path: "str | Path") -> float:
    """Return average number of fields per row. 0.0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0.0
    return sum(len(row) for row in rows) / len(rows)


def csv_nonempty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    total = sum(len(row) for row in rows)
    if total == 0:
        return 0.0
    nonempty = sum(1 for row in rows for val in row if val.strip())
    return nonempty / total


def csv_numeric_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of numeric cells to total cells. 0.0 if no cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    total = sum(len(row) for row in rows)
    if total == 0:
        return 0.0
    numeric = 0
    for row in rows:
        for val in row:
            s = val.strip()
            if s:
                try:
                    float(s)
                    numeric += 1
                except (ValueError, TypeError):
                    pass
    return numeric / total


def csv_numeric_range(file_path: "str | Path") -> float:
    """Return max - min of all numeric cell values. 0.0 if fewer than 2 numeric values."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    nums = []
    for row in rows:
        for val in row:
            s = val.strip()
            if s:
                try:
                    nums.append(float(s))
                except (ValueError, TypeError):
                    pass
    if len(nums) < 2:
        return 0.0
    return float(max(nums) - min(nums))


def csv_has_only_one_row(file_path: "str | Path") -> bool:
    """Return True if the CSV has exactly one data row (excluding header)."""
    model = parse_csv_strict(file_path)
    return len(model.get("rows", [])) == 1


def csv_empty_field_count(file_path: "str | Path") -> int:
    """Return count of empty (blank) cells in data rows."""
    model = parse_csv_strict(file_path)
    return sum(
        1 for row in model.get("rows", []) for cell in row
        if cell is None or not str(cell).strip()
    )


def csv_numeric_field_count(file_path: "str | Path") -> int:
    """Return count of cells whose values are parseable as float."""
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        for cell in row:
            if cell is not None and str(cell).strip():
                try:
                    float(str(cell).strip())
                    count += 1
                except (ValueError, TypeError):
                    pass
    return count


def csv_row_width_avg(file_path: "str | Path") -> float:
    """Return average number of fields per data row. 0.0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0.0
    return float(sum(len(row) for row in rows)) / len(rows)


def csv_distinct_header_count(file_path: "str | Path") -> int:
    """Return count of distinct header values. 0 if no headers."""
    model = parse_csv_strict(file_path)
    headers = model.get("headers") or []
    return len(set(str(h) for h in headers))


def csv_field_value_variance(file_path: "str | Path") -> float:
    """Return variance of numeric cell values. 0.0 if fewer than 2 numeric values."""
    model = parse_csv_strict(file_path)
    nums = []
    for row in model.get("rows", []):
        for cell in row:
            if cell is not None and str(cell).strip():
                try:
                    nums.append(float(str(cell).strip()))
                except (ValueError, TypeError):
                    pass
    if len(nums) < 2:
        return 0.0
    mean = sum(nums) / len(nums)
    return float(sum((x - mean) ** 2 for x in nums) / len(nums))


def csv_row_text_total(file_path: "str | Path") -> int:
    """Return total character count of all cell values in data rows."""
    model = parse_csv_strict(file_path)
    return sum(len(str(cell)) for row in model.get("rows", []) for cell in row if cell is not None)
