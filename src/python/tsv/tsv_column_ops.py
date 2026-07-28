"""tsv_column_ops.py — Extracted TSV column-statistics and row-operation functions.

Split out of tsv_parser.py (TC-PA-017 monolith healing) to keep each source module
under the 800-LOC architecture cap. These functions operate on parsed TSV data dicts;
behavior is unchanged from the original definitions. Core parser helpers, constants,
and column accessors that remain in tsv_parser.py are brought in via the star-import
below. Re-exported from tsv_parser.py so every public name stays importable from its
original path.
"""
from __future__ import annotations

from .tsv_parser import *  # noqa: F401,F403 - core parser helpers/constants reused at call time
from .tsv_parser import _load_tsv_data  # private helper; not covered by ``import *``


def average_column_tsv(data: Any, col_name: str) -> float:
    """Return the arithmetic mean of numeric values in a column.

    Non-numeric cells are skipped. Returns 0.0 if the column has no numeric values.

    Args:
        data: TSV bytes, path, or pre-loaded dict.
        col_name: Header name of the column to average.

    Returns:
        Float mean of numeric cells, or 0.0 if none found.

    Raises:
        TsvError: If col_name is not found in headers.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    return sum(vals) / len(vals) if vals else 0.0


# pige-rnext — median_column_tsv
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-003; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=b4b8bf4be603b13f62505f3990388204195fc462ec098fcd7f17a676ffe8bc8f; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def median_column_tsv(data: Any, col_name: str) -> float:
    """Return the median of numeric values in a column.

    Non-numeric cells are skipped. Returns 0.0 if the column has no numeric values.

    Args:
        data: TSV bytes, path, or pre-loaded dict.
        col_name: Header name of the column.

    Returns:
        Float median of numeric cells, or 0.0 if none found.

    Raises:
        TsvError: If col_name is not found in headers.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    if not vals:
        return 0.0
    vals.sort()
    n = len(vals)
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


# pige-rnext — std_column_tsv
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-003; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=5dd59adb627eca7302d0773437191827bd40ace09efb4e480d2f0a5bda94c802; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def std_column_tsv(data: Any, col_name: str) -> float:
    """Return the population standard deviation of numeric values in a column.

    Non-numeric cells are skipped. Returns 0.0 if the column has fewer than 1 numeric value.

    Args:
        data: TSV bytes, path, or pre-loaded dict.
        col_name: Header name of the column.

    Returns:
        Float standard deviation, or 0.0 if insufficient data.

    Raises:
        TsvError: If col_name is not found in headers.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    return variance ** 0.5


# ---------------------------------------------------------------------------
# broad-rnext — filter_rows
# ---------------------------------------------------------------------------

def filter_rows(
    data: Any,
    col_name: str,
    value: str,
    *,
    exact: bool = True,
    case_sensitive: bool = True,
) -> dict[str, Any]:
    """Return rows where col_name matches value. Supports exact/substring and case options."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        return {
            "format": "tsv",
            "path": result.get("path", "<bytes>"),
            "row_count": 0,
            "headers": result.get("headers"),
            "rows": [],
        }
    idx = result["headers"].index(col_name)
    matched: list[list[str]] = []
    for row in result["rows"]:
        if idx >= len(row):
            continue
        cell = row[idx]
        cmp_cell = cell if case_sensitive else cell.lower()
        cmp_val = value if case_sensitive else value.lower()
        matches = (cmp_cell == cmp_val) if exact else (cmp_val in cmp_cell)
        if matches:
            matched.append(row)
    return {
        "format": "tsv",
        "path": result.get("path", "<bytes>"),
        "row_count": len(matched),
        "headers": result["headers"],
        "rows": matched,
    }


# ---------------------------------------------------------------------------
# cap-append — append_row
# ---------------------------------------------------------------------------

def append_row(file_path: str | Path, row: list[Any]) -> None:
    """Append a single row to a TSV file. Creates file if it does not exist."""
    def _sanitize(val: Any) -> str:
        return str(val).replace("\t", " ").replace("\n", " ").replace("\r", " ")

    line = "\t".join(_sanitize(c) for c in row) + "\n"
    Path(file_path).open("a", encoding="utf-8").write(line)


# ---------------------------------------------------------------------------
# rnext3 — roundtrip
# ---------------------------------------------------------------------------

def roundtrip(src: Any, dest: str | Path) -> dict[str, Any]:
    """Read TSV from src (bytes or path), write to dest, return the neutral model dict."""
    result = _load_tsv_data(src)
    write_tsv(result.get("rows", []), dest, headers=result.get("headers"))
    return result


# FORMAT_FACTORY_EXECUTION: taskcard=SHQ-L2-001; method=QUEUE_DISPATCHED_EXECUTION; queue_item=shq-q-001; sprint_id=FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
def append_rows(data: Any, rows: "list[list[str]]") -> "dict[str, Any]":
    """Append multiple rows to a TSV data model (in-memory, returns updated model).

    Unlike append_row() which writes to a file path, this function operates on
    the neutral model dict and returns the updated model. Suitable for batch
    in-memory operations.

    Args:
        data: TSV data dict (with 'rows' key), or raw bytes/path for auto-loading.
        rows: List of rows to append; each row is a list of string values.
              Values are sanitized (tabs/newlines replaced with spaces).

    Returns:
        Updated data model dict with new rows appended and row_count updated.
    """
    if isinstance(data, dict):
        model = data
    else:
        model = _load_tsv_data(data)
    existing: list = list(model.get("rows", []))
    for row in rows:
        sanitized = [
            str(c).replace("\t", " ").replace("\n", " ").replace("\r", " ")
            for c in row
        ]
        existing.append(sanitized)
    model = dict(model)
    model["rows"] = existing
    model["row_count"] = len(existing)
    return model


def find_rows_containing(data: Any, text: str, case_sensitive: bool = True) -> list[int]:
    """Return 0-based indices of data rows where any cell contains text as a substring.

    Args:
        data: TSV data dict, file path, or raw bytes.
        text: The substring to search for in cell values.
        case_sensitive: If False, search is case-insensitive. Default True.

    Returns:
        Sorted list of 0-based row indices with a matching cell.
        Returns empty list if no matches found.
    """
    if isinstance(data, dict):
        model = data
    else:
        model = _load_tsv_data(data)
    rows: list[list[str]] = model.get("rows") or []
    search = text if case_sensitive else text.lower()
    result = []
    for idx, row in enumerate(rows):
        for cell in row:
            haystack = cell if case_sensitive else cell.lower()
            if search in haystack:
                result.append(idx)
                break
    return result


def get_numeric_columns(data: Any) -> list[str]:
    """Return the names of columns whose data rows are all parseable as float.

    A column is considered numeric if every non-empty value in that column
    can be converted to float. Columns with no data rows or all-empty values
    are excluded.

    Args:
        data: TSV data dict, file path, or raw bytes.

    Returns:
        List of column names (from header) that are entirely numeric.
        Returns empty list if no header or no data rows.
    """
    if isinstance(data, dict):
        model = data
    else:
        model = _load_tsv_data(data)
    headers: list[str] = model.get("headers") or []
    rows: list[list[str]] = model.get("rows") or []
    if not headers or not rows:
        return []

    numeric: list[str] = []
    for col_idx, col_name in enumerate(headers):
        values = []
        for row in rows:
            if col_idx < len(row):
                cell = row[col_idx].strip()
                if cell:
                    values.append(cell)
        if not values:
            continue
        all_numeric = True
        for v in values:
            try:
                float(v)
            except (ValueError, TypeError):
                all_numeric = False
                break
        if all_numeric:
            numeric.append(col_name)
    return numeric


def unique_column_values(data: Any, col_name: str) -> list[str]:
    """Return sorted list of unique values in a TSV column."""
    values = get_column_values(data, col_name)
    return sorted(set(values))


# ---------------------------------------------------------------------------
# Analytics functions moved to tsv_analytics.py (TC-HEAL-FORMATS-BATCH1)
# ---------------------------------------------------------------------------
try:
    from .tabular_document import *  # noqa: F401, F403
except ImportError:
    pass
