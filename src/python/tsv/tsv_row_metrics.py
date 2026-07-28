"""tsv_row_metrics.py — Extracted TSV analytics functions.

Split out of tabular_document.py (TC-PA-017 monolith healing) to keep each source
module under the 800-LOC architecture cap. Pure analytics functions over parsed TSV
rows; behavior is unchanged from the original definitions. Base parser helpers and
sibling metrics that remain in tabular_document.py are brought in via the star-import
below. Re-exported from tabular_document.py so every public name stays importable from
its original path.
"""
from __future__ import annotations

from .tabular_document import *  # noqa: F401,F403 - base parser/metrics reused at call time


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


def tsv_header_length_avg(file_path: "str | Path") -> float:
    """Return average character length of header field strings. 0.0 if no headers."""
    doc = parse_tsv_strict(file_path)
    headers = doc.get("headers") or []
    if not headers:
        return 0.0
    return float(sum(len(str(h)) for h in headers)) / len(headers)


def tsv_data_completeness(file_path: "str | Path") -> float:
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
    return float(nonempty) / total


def tsv_empty_field_count(file_path: "str | Path") -> int:
    """Return count of empty (blank) cells in data rows."""
    doc = parse_tsv_strict(file_path)
    return sum(
        1 for row in doc.get("rows", []) for cell in row
        if cell is None or not str(cell).strip()
    )


def tsv_distinct_field_count(file_path: "str | Path") -> int:
    """Return count of distinct non-empty cell values in data rows."""
    doc = parse_tsv_strict(file_path)
    values = set()
    for row in doc.get("rows", []):
        for cell in row:
            if cell is not None and str(cell).strip():
                values.add(str(cell).strip())
    return len(values)


def tsv_column_text_sum(file_path: "str | Path") -> int:
    """Return total character count of all cell values in data rows."""
    doc = parse_tsv_strict(file_path)
    return sum(len(str(cell)) for row in doc.get("rows", []) for cell in row if cell is not None)


def tsv_row_density_avg(file_path: "str | Path") -> float:
    """Return average ratio of non-empty cells to row width across all data rows. 0.0 if no rows."""
    doc = parse_tsv_strict(file_path)
    rows = doc.get("rows", [])
    if not rows:
        return 0.0
    densities = []
    for row in rows:
        if not row:
            densities.append(0.0)
        else:
            nonempty = sum(1 for cell in row if cell is not None and str(cell).strip())
            densities.append(float(nonempty) / len(row))
    return sum(densities) / len(densities)
