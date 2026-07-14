"""
DIF interchange analytics — pure analytics functions extracted from interchange_document.py.

These functions operate on DIF file paths and return computed statistics.
Extracted to keep interchange_document.py within the 800 LOC / 60 function policy limits.

Functions dif_total_cell_count, dif_row_count, dif_has_string_cells are NOT included here;
they already exist in dif_stats.py with identical implementations.
"""

from __future__ import annotations

from .dif_parser import parse_dif, parse_dif_strict


def dif_nonempty_row_count(file_path: "str | Path") -> int:
    """Return the count of rows that contain at least one non-empty cell."""
    doc = parse_dif_strict(file_path)
    count = 0
    for row in doc.rows:
        for cell in row:
            val = cell.value if hasattr(cell, "value") else cell
            if val is not None and str(val).strip() != "":
                count += 1
                break
    return count


def dif_max_row_length(file_path: "str | Path") -> int:
    """Return the maximum number of cells in any single row of the DIF file. 0 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0
    return max(len(row) for row in doc.rows)


def dif_string_row_count(file_path: "str | Path") -> int:
    """Return the count of rows containing at least one string cell value."""
    doc = parse_dif_strict(file_path)
    count = 0
    for row in doc.rows:
        if any(isinstance(cell.value, str) for cell in row):
            count += 1
    return count


def dif_column_unique_count(file_path: "str | Path", col_idx: int) -> int:
    """Return the count of unique non-None values in a specific column (0-based)."""
    doc = parse_dif_strict(file_path)
    values = set()
    for row in doc.rows:
        if col_idx < len(row):
            v = row[col_idx].value
            if v is not None:
                values.add(str(v))
    return len(values)


def dif_vectors_count(file_path: "str | Path") -> int:
    """Return the number of vectors (columns) declared in a DIF file. 0 if header absent."""
    doc = parse_dif_strict(file_path)
    return doc.vectors


def dif_column_types(file_path: "str | Path") -> list:
    """Infer the dominant data type for each column.

    Returns list of 'numeric', 'string', 'special', or 'empty' — one per column.
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return []
    max_cols = max(len(row) for row in doc.rows) if doc.rows else 0
    result = []
    for col_idx in range(max_cols):
        counts = {"numeric": 0, "string": 0, "special": 0}
        for row in doc.rows:
            if col_idx < len(row):
                vt = row[col_idx].value_type
                if vt in counts:
                    counts[vt] += 1
        total = sum(counts.values())
        if total == 0:
            result.append("empty")
        elif counts["numeric"] >= counts["string"] and counts["numeric"] >= counts["special"]:
            result.append("numeric")
        elif counts["string"] >= counts["special"]:
            result.append("string")
        else:
            result.append("special")
    return result


def dif_row_value_counts(file_path: "str | Path") -> list:
    """Return the count of non-empty cells per row as a list."""
    doc = parse_dif_strict(file_path)
    return [sum(1 for cell in row if cell.value is not None) for row in doc.rows]


def dif_empty_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells with None value across all rows."""
    doc = parse_dif_strict(file_path)
    return sum(1 for row in doc.rows for cell in row if cell.value is None)


def dif_has_header(file_path: "str | Path") -> bool:
    """Heuristic: return True if the first row appears to be a header (all string-type cells)."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return False
    first_row = doc.rows[0]
    if not first_row:
        return False
    return all(cell.value_type == "string" for cell in first_row)


def dif_column_count(file_path: "str | Path") -> int:
    """Return the number of columns (max row width) in a DIF file. 0 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0
    return max(len(row) for row in doc.rows)


def dif_string_density(file_path: "str | Path") -> float:
    """Return the fraction of cells that are string type. 0.0 if no cells."""
    doc = parse_dif_strict(file_path)
    total = 0
    string_count = 0
    for row in doc.rows:
        for cell in row:
            total += 1
            if cell.value_type == "string":
                string_count += 1
    if total == 0:
        return 0.0
    return string_count / total


def dif_max_cell_length(file_path: "str | Path") -> int:
    """Return the length of the longest cell value string. 0 if no cells."""
    doc = parse_dif_strict(file_path)
    max_len = 0
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            max_len = max(max_len, len(str(val)))
    return max_len


def dif_has_empty_cells(file_path: "str | Path") -> bool:
    """Return True if any cell has an empty or None value."""
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            if str(val).strip() == "":
                return True
    return False


def dif_avg_row_length(file_path: "str | Path") -> float:
    """Return the average number of cells per row. 0.0 if no rows."""
    doc = parse_dif_strict(file_path)
    rows = doc.rows
    if not rows:
        return 0.0
    total = sum(len(row) for row in rows)
    return total / len(rows)


def dif_all_numeric(file_path: "str | Path") -> bool:
    """Return True if all non-empty cells contain numeric values (vacuously True if none)."""
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            s = str(val).strip()
            if not s:
                continue
            try:
                float(s)
            except (ValueError, TypeError):
                return False
    return True


def dif_all_numeric_column(file_path: "str | Path", col_index: int = 0) -> bool:
    """Return True if all non-empty cells in a column are numeric (vacuously True if none)."""
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        if col_index >= len(row):
            continue
        cell = row[col_index]
        val = cell.value if cell.value is not None else ""
        s = str(val).strip()
        if not s:
            continue
        try:
            float(s)
        except (ValueError, TypeError):
            return False
    return True


def dif_numeric_density(file_path: "str | Path") -> float:
    """Return the ratio of numeric cells to total cells. 0.0 if no cells."""
    doc = parse_dif_strict(file_path)
    total = sum(len(row) for row in doc.rows)
    if total == 0:
        return 0.0
    numeric = sum(1 for row in doc.rows for cell in row if cell.value_type == "numeric")
    return numeric / total


def dif_min_cell_length(file_path: "str | Path") -> int:
    """Return the length of the shortest non-empty cell value. 0 if no data."""
    doc = parse_dif_strict(file_path)
    min_len = None
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            s = str(val).strip()
            if s:
                if min_len is None or len(s) < min_len:
                    min_len = len(s)
    return min_len if min_len is not None else 0


def dif_max_numeric_value(file_path: "str | Path"):
    """Return the maximum numeric cell value, or None if no numeric cells."""
    doc = parse_dif_strict(file_path)
    nums = [cell.value for row in doc.rows for cell in row if isinstance(cell.value, float)]
    return max(nums) if nums else None


def dif_min_numeric_value(file_path: "str | Path"):
    """Return the minimum numeric cell value, or None if no numeric cells."""
    doc = parse_dif_strict(file_path)
    nums = [cell.value for row in doc.rows for cell in row if isinstance(cell.value, float)]
    return min(nums) if nums else None


def dif_is_rectangular(file_path: "str | Path") -> bool:
    """Return True if all rows have the same number of cells."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return True
    first_len = len(doc.rows[0])
    return all(len(row) == first_len for row in doc.rows)


def dif_data_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    doc = parse_dif_strict(file_path)
    total = sum(len(row) for row in doc.rows)
    if total == 0:
        return 0.0
    empty = sum(1 for row in doc.rows for cell in row if cell.value is None)
    return (total - empty) / total


def dif_avg_cell_length(file_path: "str | Path") -> float:
    """Return the average string length of all cell values. 0.0 if no cells."""
    doc = parse_dif_strict(file_path)
    lengths = []
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            lengths.append(len(str(val)))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def dif_is_single_column(file_path: "str | Path") -> bool:
    """Return True if the DIF file has exactly one column."""
    return dif_column_count(file_path) == 1


def dif_max_string_length(file_path: "str | Path") -> int:
    """Return the maximum length of any string cell value. 0 if no string cells."""
    doc = parse_dif_strict(file_path)
    lengths = [
        len(str(cell.value))
        for row in doc.rows
        for cell in row
        if isinstance(cell.value, str)
    ]
    return max(lengths) if lengths else 0


def dif_col_count_variance(file_path: "str | Path") -> float:
    """Return variance of column counts per row. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    counts = [len(row) for row in doc.rows]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def dif_numeric_mean(file_path: "str | Path") -> float:
    """Return mean of all numeric cell values. 0.0 if none."""
    doc = parse_dif_strict(file_path)
    nums = []
    for row in doc.rows:
        for cell in row:
            if isinstance(cell.value, (int, float)):
                nums.append(float(cell.value))
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def dif_is_empty(file_path: "str | Path") -> bool:
    """Return True if the DIF document has no data rows."""
    doc = parse_dif_strict(file_path)
    return len(doc.rows) == 0


def dif_unique_value_count(file_path: "str | Path") -> int:
    """Return total number of unique cell values across all rows."""
    doc = parse_dif_strict(file_path)
    values = set()
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                values.add(str(cell.value))
    return len(values)


def dif_tuple_count(file_path: "str | Path") -> int:
    """Return the TUPLES dimension from the DIF header (declared row count)."""
    result = parse_dif(file_path)
    return result.get("tuples", 0)


def dif_is_multi_vector(file_path: "str | Path") -> bool:
    """Return True if the DIF file has more than one vector (column)."""
    result = parse_dif(file_path)
    return result.get("vectors", 0) > 1


def dif_is_single_vector(file_path: "str | Path") -> bool:
    """Return True if the DIF file has exactly one vector (column)."""
    result = parse_dif(file_path)
    return result.get("vectors", 0) == 1


def dif_vector_length_variance(file_path: "str | Path") -> float:
    """Return variance of cell counts per row. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    counts = [len(row) for row in doc.rows]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def dif_is_all_string(file_path: "str | Path") -> bool:
    """Return True if all non-empty cells contain string (non-numeric) values."""
    doc = parse_dif_strict(file_path)
    has_data = False
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            s = str(val).strip()
            if not s:
                continue
            has_data = True
            try:
                float(s)
                return False
            except (ValueError, TypeError):
                pass
    return has_data


def dif_nonempty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    doc = parse_dif_strict(file_path)
    total = sum(len(row) for row in doc.rows)
    if total == 0:
        return 0.0
    nonempty = 0
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            if str(val).strip():
                nonempty += 1
    return nonempty / total


def dif_avg_numeric_value(file_path: "str | Path") -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_dif_strict(file_path)
    nums = []
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                try:
                    nums.append(float(str(cell.value)))
                except (ValueError, TypeError):
                    pass
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def dif_row_length_variance(file_path: "str | Path") -> float:
    """Return variance of row lengths. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    lengths = [len(row) for row in doc.rows]
    mean = sum(lengths) / len(lengths)
    return sum((length - mean) ** 2 for length in lengths) / len(lengths)


def dif_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_dif_strict(file_path)
    total = 0.0
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                try:
                    total += float(str(cell.value))
                except (ValueError, TypeError):
                    pass
    return total


def dif_is_single_row(file_path: "str | Path") -> bool:
    """Return True if the document has exactly one data row."""
    doc = parse_dif_strict(file_path)
    return len(doc.rows) == 1


def dif_empty_column_count(file_path: "str | Path") -> int:
    """Return number of columns that are entirely empty across all rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0
    col_count = max(len(row) for row in doc.rows)
    empty_cols = 0
    for ci in range(col_count):
        if all(
            ci >= len(row) or row[ci].value is None or str(row[ci].value).strip() == ""
            for row in doc.rows
        ):
            empty_cols += 1
    return empty_cols


def dif_longest_row_index(file_path: "str | Path") -> int:
    """Return 0-based index of the row with the most cells. -1 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return -1
    return max(range(len(doc.rows)), key=lambda i: len(doc.rows[i]))


def dif_total_string_length(file_path: "str | Path") -> int:
    """Return total character count of all string cell values combined."""
    doc = parse_dif_strict(file_path)
    total = 0
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                total += len(str(cell.value))
    return total


def dif_nonempty_row_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty rows to total rows. 0.0 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0.0
    nonempty = sum(
        1 for row in doc.rows
        if any(cell.value is not None and str(cell.value).strip() for cell in row)
    )
    return nonempty / len(doc.rows)


def dif_numeric_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells with numeric values."""
    doc = parse_dif_strict(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == "numeric"
    )


def dif_avg_cell_length_variance(file_path: "str | Path") -> float:
    """Return variance of cell value string lengths. 0.0 if fewer than 2 cells."""
    doc = parse_dif_strict(file_path)
    lengths = []
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                lengths.append(len(str(cell.value)))
    if len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    return sum((length - mean) ** 2 for length in lengths) / len(lengths)


def dif_column_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty columns to total columns. 0.0 if no columns."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0.0
    max_cols = max(len(row) for row in doc.rows) if doc.rows else 0
    if max_cols == 0:
        return 0.0
    nonempty_cols = 0
    for c in range(max_cols):
        for row in doc.rows:
            if c < len(row) and row[c].value is not None and str(row[c].value).strip():
                nonempty_cols += 1
                break
    return nonempty_cols / max_cols


def dif_string_value_count(file_path: "str | Path") -> int:
    """Return count of cells with string-type values."""
    doc = parse_dif_strict(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == "string"
    )


def dif_max_numeric_length(file_path: "str | Path") -> int:
    """Return max string length of any numeric cell value. 0 if no numeric cells."""
    doc = parse_dif_strict(file_path)
    max_len = 0
    for row in doc.rows:
        for cell in row:
            if cell.value_type == "numeric" and cell.value is not None:
                length = len(str(cell.value))
                if length > max_len:
                    max_len = length
    return max_len


def dif_value_type_variance(file_path: "str | Path") -> float:
    """Return variance of numeric vs string cell counts per row. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    numeric_counts = []
    for row in doc.rows:
        nc = sum(1 for cell in row if cell.value_type == "numeric")
        numeric_counts.append(nc)
    mean = sum(numeric_counts) / len(numeric_counts)
    return sum((n - mean) ** 2 for n in numeric_counts) / len(numeric_counts)


def dif_total_cell_length(file_path: "str | Path") -> int:
    """Return total string length of all cell values. 0 if no cells."""
    doc = parse_dif_strict(file_path)
    return sum(
        len(str(cell.value)) for row in doc.rows for cell in row
        if cell.value is not None
    )
