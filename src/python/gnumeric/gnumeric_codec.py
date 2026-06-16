"""
Gnumeric codec — minimal Gnumeric spreadsheet API.

Gnumeric (.gnumeric) — gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Uses gzip + xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
"""

from __future__ import annotations

import gzip
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Gnumeric XML namespace
GNM_NS = "http://www.gnumeric.org/v10.dtd"
GNM_MIME = "application/x-gnumeric"

# Gzip magic bytes
GZIP_MAGIC = b"\x1f\x8b"

# Maximum compressed file size guard (64 MiB)
MAX_FILE_SIZE = 64 * 1024 * 1024


class GnumericError(Exception):
    """Base exception for Gnumeric codec errors."""


class GnumericParseError(GnumericError):
    """Raised when Gnumeric parsing fails."""


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse a Gnumeric file.

    The returned model contains:
        is_gnumeric (bool): True if valid Gnumeric file.
        sheet_count (int): Number of gnm:Sheet elements.
        sheets (list[dict]): Per-sheet data.
        cell_count (int): Total cell count across all sheets.

    Args:
        source: Path to .gnumeric file or bytes.

    Returns:
        Parsed workbook model dict.

    Raises:
        GnumericParseError: If source cannot be parsed.
        GnumericError: For other load errors.
    """
    raw = _read_source(source)
    xml_bytes = _decompress(raw)
    root = _parse_xml(xml_bytes)
    return _build_model(root)


def get_sheet_count(source: str | bytes | Path) -> int:
    """Return number of sheets in the workbook."""
    return load(source)["sheet_count"]


def get_cell_count(source: str | bytes | Path) -> int:
    """Return total cell count across all sheets."""
    return load(source)["cell_count"]


def extract_values(source: str | bytes | Path) -> list[str]:
    """Extract all non-empty cell values from all sheets."""
    model = load(source)
    values: list[str] = []
    for sheet in model.get("sheets", []):
        values.extend(sheet.get("cell_values", []))
    return [v for v in values if v]


def get_sheet_metadata(source: str | bytes | Path) -> list[dict[str, Any]]:
    """Return per-sheet metadata list.

    Each dict contains: name, cell_count, cell_values.
    """
    return load(source).get("sheets", [])


def export_to_csv(
    source: str | bytes | Path,
    sheet_index: int = 0,
    delimiter: str = ",",
) -> str:
    """Export a Gnumeric sheet to CSV string.

    Cells are placed at their declared Row/Col positions.  Empty positions
    are rendered as empty fields.

    Args:
        source:      Path to .gnumeric file or raw bytes.
        sheet_index: Zero-based sheet index to export (default 0).
        delimiter:   CSV delimiter character (default ',').

    Returns:
        CSV string (rows separated by CRLF per RFC 4180).

    Raises:
        GnumericError: If sheet_index is out of range.
        GnumericParseError: If source cannot be parsed.
    """
    model = load(source)
    sheets = model.get("sheets", [])
    if not sheets:
        return ""
    if sheet_index < 0 or sheet_index >= len(sheets):
        raise GnumericError(
            f"sheet_index {sheet_index} out of range (0–{len(sheets) - 1})"
        )
    sheet = sheets[sheet_index]
    grid = sheet.get("cell_grid", {})
    if not grid:
        return ""

    max_row = max(r for r, _ in grid)
    max_col = max(c for _, c in grid)

    lines = []
    for row in range(max_row + 1):
        fields = [_csv_field(grid.get((row, col), ""), delimiter) for col in range(max_col + 1)]
        lines.append(delimiter.join(fields))
    return "\r\n".join(lines) + "\r\n"


def export_to_json(source: str | bytes | Path) -> str:
    """Export a Gnumeric workbook to a JSON string.

    Produces a JSON array — one object per sheet — where each object has:
      ``name`` (str): sheet name.
      ``rows`` (list[list[str]]): grid of cell values, row-major order.
        Empty trailing cells in a row are included if other rows are wider.
        Rows with no data are represented as lists of empty strings.

    Args:
        source: Path to .gnumeric file or raw gzipped bytes.

    Returns:
        JSON string (UTF-8 safe, ASCII-escaped).

    Raises:
        GnumericParseError: If source cannot be parsed.
        GnumericError: For other load errors.
    """
    import json as _json

    model = load(source)
    sheets_out = []
    for sheet in model.get("sheets", []):
        grid: dict[tuple[int, int], str] = sheet.get("cell_grid", {})
        if grid:
            max_row = max(r for r, _ in grid)
            max_col = max(c for _, c in grid)
        else:
            max_row = -1
            max_col = -1
        rows: list[list[str]] = []
        for row in range(max_row + 1):
            rows.append([grid.get((row, col), "") for col in range(max_col + 1)])
        sheets_out.append({"name": sheet.get("name", ""), "rows": rows})
    return _json.dumps(sheets_out, ensure_ascii=True, indent=2)


def probe_gnumeric(source) -> bool:
    """Probe whether source is a valid Gnumeric document.

    Checks gzip magic bytes then decompresses the header to verify
    the Gnumeric XML namespace without full parsing.
    Does not raise on malformed input — returns False instead.

    Args:
        source: Path to a file or bytes to probe.

    Returns:
        True if source appears to be a Gnumeric document, False otherwise.
    """
    try:
        raw = _read_source(source)
        if raw[:2] != GZIP_MAGIC:
            return False
        header = gzip.decompress(raw[:8192])
        snippet = header[:2048].decode("utf-8", errors="replace")
        return GNM_NS in snippet
    except Exception:
        return False


def create_gnumeric(sheets: list[dict]) -> dict[str, Any]:
    """Create a minimal Gnumeric workbook model from a list of sheet dicts.

    Args:
        sheets: List of sheet dicts, each with optional:
                  'name' (str) — sheet name (default 'Sheet<n>').
                  'rows' (list[list[str]]) — row-major cell data.

    Returns:
        Workbook model dict compatible with write_gnumeric() and load().
    """
    built = []
    for i, sheet in enumerate(sheets):
        name = sheet.get("name", f"Sheet{i + 1}")
        rows = sheet.get("rows", [])
        grid: dict[tuple[int, int], str] = {}
        cell_values: list[str] = []
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                v = str(val) if val is not None else ""
                grid[(r, c)] = v
                if v:
                    cell_values.append(v)
        built.append({
            "name": name,
            "cell_count": len(grid),
            "cell_values": cell_values,
            "cell_grid": grid,
        })
    total = sum(s["cell_count"] for s in built)
    return {
        "is_gnumeric": True,
        "sheet_count": len(built),
        "sheets": built,
        "cell_count": total,
    }


def write_gnumeric(model: dict[str, Any], dest: str | Path) -> None:
    """Serialize a Gnumeric workbook model to a .gnumeric file.

    Writes a gzip-compressed Gnumeric XML file.

    Args:
        model: Workbook model dict as returned by load() or create_gnumeric().
        dest:  Destination file path.

    Raises:
        GnumericError: If model is invalid or dest cannot be written.
    """
    if not isinstance(model, dict) or not model.get("is_gnumeric"):
        raise GnumericError("model must be a valid Gnumeric dict (is_gnumeric=True)")

    dest = Path(dest)
    ns = GNM_NS

    root = ET.Element(f"{{{ns}}}Workbook")
    sheets_el = ET.SubElement(root, f"{{{ns}}}Sheets")

    for sheet_data in model.get("sheets", []):
        sheet_el = ET.SubElement(sheets_el, f"{{{ns}}}Sheet")
        name_el = ET.SubElement(sheet_el, f"{{{ns}}}Name")
        name_el.text = sheet_data.get("name", "Sheet1")
        cells_el = ET.SubElement(sheet_el, f"{{{ns}}}Cells")
        grid = sheet_data.get("cell_grid", {})
        for (row, col), value in sorted(grid.items()):
            if value:
                cell_el = ET.SubElement(cells_el, f"{{{ns}}}Cell")
                cell_el.set("Row", str(row))
                cell_el.set("Col", str(col))
                val_el = ET.SubElement(cell_el, f"{{{ns}}}Value")
                val_el.text = value

    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    xml_bytes = content.encode("utf-8")
    compressed = gzip.compress(xml_bytes)

    try:
        dest.write_bytes(compressed)
    except OSError as exc:
        raise GnumericError(f"Cannot write {dest}: {exc}") from exc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _csv_field(value: str, delimiter: str = ",") -> str:
    """Quote a CSV field if it contains the delimiter, a quote, or a newline."""
    if delimiter in value or '"' in value or "\n" in value or "\r" in value:
        return '"' + value.replace('"', '""') + '"'
    return value

def _read_source(source: str | bytes | Path) -> bytes:
    if isinstance(source, Path):
        _check_size(source)
        return source.read_bytes()
    elif isinstance(source, str) and not source.strip().startswith("<"):
        path = Path(source)
        _check_size(path)
        return path.read_bytes()
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise GnumericError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise GnumericError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise GnumericParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise GnumericError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _decompress(raw: bytes) -> bytes:
    if raw[:2] == GZIP_MAGIC:
        try:
            return gzip.decompress(raw)
        except OSError as exc:
            raise GnumericParseError(f"Gzip decompression failed: {exc}") from exc
    return raw


def _parse_xml(xml_bytes: bytes) -> ET.Element:
    """Parse XML bytes safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise GnumericParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a workbook model from the parsed XML root."""
    expected_tag = f"{{{GNM_NS}}}Workbook"
    if root.tag != expected_tag:
        raise GnumericParseError(
            f"Root element must be gnm:Workbook, got {root.tag!r}"
        )

    sheets = _extract_sheets(root)
    total_cells = sum(s["cell_count"] for s in sheets)

    return {
        "is_gnumeric": True,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "cell_count": total_cells,
    }


def _extract_sheets(root: ET.Element) -> list[dict[str, Any]]:
    """Extract per-sheet metadata from all gnm:Sheet elements."""
    sheets = []
    for sheet in root.iter(f"{{{GNM_NS}}}Sheet"):
        name_el = sheet.find(f"{{{GNM_NS}}}Name")
        name = name_el.text if name_el is not None and name_el.text else ""
        cells = list(sheet.iter(f"{{{GNM_NS}}}Cell"))
        cell_values = []
        cell_grid: dict[tuple[int, int], str] = {}
        for cell in cells:
            val_el = cell.find(f"{{{GNM_NS}}}Value")
            value = val_el.text.strip() if val_el is not None and val_el.text else ""
            if value:
                cell_values.append(value)
            try:
                row = int(cell.get("Row", 0))
                col = int(cell.get("Col", 0))
                cell_grid[(row, col)] = value
            except (ValueError, TypeError):
                pass
        sheets.append({
            "name": name,
            "cell_count": len(cells),
            "cell_values": cell_values,
            "cell_grid": cell_grid,
        })
    return sheets


# ---------------------------------------------------------------------------
# Cell accessor functions (Sprint 3+, R123/R125/R126)
# ---------------------------------------------------------------------------

def get_cell_value(model: dict[str, Any], sheet_idx: int, row: int, col: int) -> str:
    """Return the value of a cell as a string.

    Returns '' for empty/missing cells.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range (0-{len(sheets)-1})")
    return sheets[sheet_idx].get("cell_grid", {}).get((row, col), "")


def set_cell_value(
    model: dict[str, Any], sheet_idx: int, row: int, col: int, value: str
) -> dict[str, Any]:
    """Return a new model with the specified cell set to value (immutable).

    Raises:
        TypeError: If model is not a dict or value is not a str.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(value, str):
        raise TypeError("value must be a str")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    new_sheets = []
    for i, sheet in enumerate(sheets):
        if i == sheet_idx:
            new_grid = dict(sheet.get("cell_grid", {}))
            new_grid[(row, col)] = value
            new_cell_values = [v for v in new_grid.values() if v]
            new_sheets.append({
                **sheet,
                "cell_grid": new_grid,
                "cell_count": len(new_grid),
                "cell_values": new_cell_values,
            })
        else:
            new_sheets.append(sheet)
    total = sum(s["cell_count"] for s in new_sheets)
    return {**model, "sheets": new_sheets, "cell_count": total}


def get_sheet_names(source: "str | bytes | Path") -> list[str]:
    """Return a list of sheet names from a Gnumeric source (path, bytes, or str path).

    Args:
        source: Path to .gnumeric file or raw bytes.

    Returns:
        List of sheet names in order.
    """
    model = load(source)
    return [s.get("name", "") for s in model.get("sheets", [])]


# ---------------------------------------------------------------------------
# Sheet operations (Sprint 2, R130)
# ---------------------------------------------------------------------------

def get_row(model: dict[str, Any], sheet_idx: int, row_idx: int) -> list[str]:
    """Return all cell values in a row as a list (left to right).

    Returns [] if row is empty or sheet is valid but row has no cells.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    row_cells = {c: v for (r, c), v in grid.items() if r == row_idx}
    if not row_cells:
        return []
    max_col = max(row_cells)
    return [row_cells.get(c, "") for c in range(max_col + 1)]


def get_column(model: dict[str, Any], sheet_idx: int, col_idx: int) -> list[str]:
    """Return all cell values in a column as a list (top to bottom).

    Returns [] if the column is empty.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    col_cells = {r: v for (r, c), v in grid.items() if c == col_idx}
    if not col_cells:
        return []
    max_row = max(col_cells)
    return [col_cells.get(r, "") for r in range(max_row + 1)]


def delete_sheet(model: dict[str, Any], sheet_idx: int) -> dict[str, Any]:
    """Return a new model with the sheet at sheet_idx removed (immutable).

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range or negative.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    new_sheets = [s for i, s in enumerate(sheets) if i != sheet_idx]
    total = sum(s["cell_count"] for s in new_sheets)
    return {**model, "sheets": new_sheets, "sheet_count": len(new_sheets), "cell_count": total}


def rename_sheet(model: dict[str, Any], sheet_idx: int, name: str) -> dict[str, Any]:
    """Return a new model with the sheet at sheet_idx renamed (immutable).

    Raises:
        TypeError: If model is not a dict or name is not a str.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    new_sheets = [
        ({**s, "name": name} if i == sheet_idx else s)
        for i, s in enumerate(sheets)
    ]
    return {**model, "sheets": new_sheets}


# ---------------------------------------------------------------------------
# Sprint 4 additions (R136-R137)
# ---------------------------------------------------------------------------

def add_sheet(
    model: dict[str, Any], name: str, insert_at: "int | None" = None
) -> dict[str, Any]:
    """Return a new model with an empty sheet added (immutable).

    Args:
        model: Workbook model dict.
        name: Name for the new sheet. If empty, auto-generates 'Sheet<n>'.
        insert_at: Optional zero-based position to insert the sheet. Appends if None.

    Raises:
        TypeError: If model is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = list(model.get("sheets", []))
    auto_name = name or f"Sheet{len(sheets) + 1}"
    new_sheet: dict[str, Any] = {
        "name": auto_name,
        "cell_count": 0,
        "cell_values": [],
        "cell_grid": {},
    }
    if insert_at is None:
        sheets.append(new_sheet)
    else:
        sheets.insert(insert_at, new_sheet)
    return {**model, "sheets": sheets, "sheet_count": len(sheets)}


def get_sheet_by_name(model: dict[str, Any], name: str) -> "dict[str, Any] | None":
    """Return the first sheet dict with matching name, or None if not found.

    Raises:
        TypeError: If model is not a dict or name is not a str.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    for sheet in model.get("sheets", []):
        if sheet.get("name") == name:
            return sheet
    return None


def copy_sheet(model: dict[str, Any], sheet_idx: int) -> dict[str, Any]:
    """Return a new model with a copy of the sheet at sheet_idx appended (immutable).

    The copy's name is '<original_name> (Copy)'.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    import copy as _copy
    orig = sheets[sheet_idx]
    sheet_copy = _copy.deepcopy(orig)
    sheet_copy["name"] = f"{orig['name']} (Copy)"
    new_sheets = list(sheets) + [sheet_copy]
    total = sum(s["cell_count"] for s in new_sheets)
    return {**model, "sheets": new_sheets, "sheet_count": len(new_sheets), "cell_count": total}


# ---------------------------------------------------------------------------
# Sprint 5 additions (R138)
# ---------------------------------------------------------------------------

def clear_cell(
    model: dict[str, Any], sheet_idx: int, row: int, col: int
) -> dict[str, Any]:
    """Return a new model with the specified cell removed (immutable).

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    new_sheets = []
    for i, sheet in enumerate(sheets):
        if i == sheet_idx:
            new_grid = dict(sheet.get("cell_grid", {}))
            new_grid.pop((row, col), None)
            new_cell_values = [v for v in new_grid.values() if v]
            new_sheets.append({
                **sheet,
                "cell_grid": new_grid,
                "cell_count": len(new_grid),
                "cell_values": new_cell_values,
            })
        else:
            new_sheets.append(sheet)
    total = sum(s["cell_count"] for s in new_sheets)
    return {**model, "sheets": new_sheets, "cell_count": total}


def get_row_count(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of distinct rows with data in the sheet.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return len({r for r, _ in grid})


# ---------------------------------------------------------------------------
# Sprint 6 additions (R140)
# ---------------------------------------------------------------------------

def get_column_count(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of distinct columns with data in the sheet.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return len({c for _, c in grid})


def read_cell(
    model: dict[str, Any], sheet_idx: int, row: int, col: int
) -> "str | None":
    """Return the value at (row, col) or None if cell is empty/missing.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    return sheets[sheet_idx].get("cell_grid", {}).get((row, col))


# ---------------------------------------------------------------------------
# Sprint 7 additions (R142)
# ---------------------------------------------------------------------------

def count_nonempty_cells(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of cells with non-empty values.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    return sum(1 for v in grid.values() if v)


# ---------------------------------------------------------------------------
# Sprint 8 additions (R144)
# ---------------------------------------------------------------------------

def get_sheet_index(model: dict[str, Any], name: str) -> int:
    """Return the zero-based index of the sheet with the given name.

    Raises:
        KeyError: If no sheet with that name exists.
    """
    for i, sheet in enumerate(model.get("sheets", [])):
        if sheet.get("name") == name:
            return i
    raise KeyError(f"Sheet {name!r} not found")


def sum_column(model: dict[str, Any], sheet_idx: int, col_idx: int) -> float:
    """Return the numeric sum of all values in a column (non-numeric values skipped).

    Returns 0.0 if sheet_idx is out of range or column is empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0.0
    grid = sheets[sheet_idx].get("cell_grid", {})
    total = 0.0
    for (r, c), v in grid.items():
        if c == col_idx:
            try:
                total += float(v)
            except (ValueError, TypeError):
                pass
    return total


# ---------------------------------------------------------------------------
# Sprint 9 additions (R146)
# ---------------------------------------------------------------------------

def fill_column(
    model: dict[str, Any], sheet_idx: int, col_idx: int, values: list
) -> dict[str, Any]:
    """Return a new model with values written into a column starting at row 0 (immutable).

    Returns the original model unchanged if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return model
    result = model
    for row_idx, value in enumerate(values):
        result = set_cell_value(result, sheet_idx, row_idx, col_idx, str(value))
    return result


def sum_row(model: dict[str, Any], sheet_idx: int, row_idx: int) -> float:
    """Return the numeric sum of all values in a row (non-numeric values skipped).

    Returns 0.0 if sheet_idx is out of range or row is empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0.0
    grid = sheets[sheet_idx].get("cell_grid", {})
    total = 0.0
    for (r, c), v in grid.items():
        if r == row_idx:
            try:
                total += float(v)
            except (ValueError, TypeError):
                pass
    return total


# ---------------------------------------------------------------------------
# Sprint 10 additions (R148)
# ---------------------------------------------------------------------------

def get_all_values(model: dict[str, Any], sheet_idx: int) -> list[str]:
    """Return a list of all non-empty cell values in the sheet.

    Returns [] if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return []
    grid = sheets[sheet_idx].get("cell_grid", {})
    return [v for v in grid.values() if v]


def clear_sheet(model: dict[str, Any], sheet_idx: int) -> dict[str, Any]:
    """Return a new model with all cells in the sheet cleared (immutable).

    Returns the original model unchanged if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return model
    new_sheets = []
    for i, sheet in enumerate(sheets):
        if i == sheet_idx:
            new_sheets.append({**sheet, "cell_grid": {}, "cell_count": 0, "cell_values": []})
        else:
            new_sheets.append(sheet)
    total = sum(s["cell_count"] for s in new_sheets)
    return {**model, "sheets": new_sheets, "cell_count": total}


# ---------------------------------------------------------------------------
# Sprint 11 additions (R150)
# ---------------------------------------------------------------------------

def get_sheet_as_rows(model: dict[str, Any], sheet_idx: int) -> list[list[str]]:
    """Return sheet data as a list of rows (each row is a list of strings).

    Returns [] if sheet_idx is out of range or the sheet is empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return []
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return []
    max_row = max(r for r, _ in grid)
    max_col = max(c for _, c in grid)
    return [
        [grid.get((r, c), "") for c in range(max_col + 1)]
        for r in range(max_row + 1)
    ]


def fill_row(
    model: dict[str, Any], sheet_idx: int, row_idx: int, values: list
) -> dict[str, Any]:
    """Return a new model with values written into a row starting at col 0 (immutable).

    Returns the original model unchanged if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return model
    result = model
    for col_idx, value in enumerate(values):
        result = set_cell_value(result, sheet_idx, row_idx, col_idx, str(value))
    return result


# ---------------------------------------------------------------------------
# Sprint 12 additions (R152)
# ---------------------------------------------------------------------------

def sheet_names(model: dict[str, Any]) -> list[str]:
    """Return a list of sheet names from a workbook model dict.

    Args:
        model: Workbook model dict (as returned by load() or create_gnumeric()).

    Returns:
        List of sheet names in order.
    """
    return [s.get("name", "") for s in model.get("sheets", [])]


def row_count(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of rows (max_row_index + 1) in the sheet.

    Returns 0 if sheet_idx is out of range or the sheet is empty.
    Does NOT raise on out-of-range sheet_idx (returns 0 instead).
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return max(r for r, _ in grid) + 1


# pfgi-rnext — get_row_values
# FORMAT_FACTORY_EXECUTION: taskcard=PFGI-TC-004; method=MANUAL_GOVERNED_BY_SKILL; skill=add-python-api; idempotency=5af6cdf9727c036f5707097c30b82f6beec55bbeffc0757779d8b6e38027a01c; evidence=.local/evidences/product-first-governed-implementation-rnext/evidence-declaration.yaml
def get_row_values(model: dict[str, Any], sheet_idx: int, row_idx: int) -> list[str]:
    """Return all cell values in a given row as a list of strings.

    Cells not present in the grid are returned as empty strings.
    The list length equals the maximum column index used in that row + 1.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        row_idx: Zero-based row index.

    Returns:
        List of string cell values for the row. Empty list if row has no cells.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise IndexError(f"sheet_idx {sheet_idx} out of range (have {len(sheets)} sheets)")
    grid = sheets[sheet_idx].get("cell_grid", {})
    row_cells = {c: v for (r, c), v in grid.items() if r == row_idx}
    if not row_cells:
        return []
    max_col = max(row_cells.keys())
    return [row_cells.get(c, "") for c in range(max_col + 1)]


# pige-rnext — get_column_values
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-004; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=77ba4df6243dd26d5701d214c8bcf133a53e9ab98a827870976717a0239cbe9f; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def get_column_values(model: dict[str, Any], sheet_idx: int, col_idx: int) -> list[str]:
    """Return all cell values in a given column as a list of strings.

    Cells not present in the grid are returned as empty strings.
    The list length equals the maximum row index used in that column + 1.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        col_idx: Zero-based column index.

    Returns:
        List of string cell values for the column. Empty list if column has no cells.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise IndexError(f"sheet_idx {sheet_idx} out of range (have {len(sheets)} sheets)")
    grid = sheets[sheet_idx].get("cell_grid", {})
    col_cells = {r: v for (r, c), v in grid.items() if c == col_idx}
    if not col_cells:
        return []
    max_row = max(col_cells.keys())
    return [col_cells.get(r, "") for r in range(max_row + 1)]


def min_column_value(model: dict[str, Any], sheet_idx: int, col_idx: int) -> "float | None":
    """Return the minimum numeric value in a column.

    Non-numeric string values are ignored. Returns None if no numeric values.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        col_idx: Zero-based column index.

    Returns:
        Minimum numeric value, or None if no numeric cells found.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    values = get_column_values(model, sheet_idx, col_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return min(nums) if nums else None


def max_column_value(model: dict[str, Any], sheet_idx: int, col_idx: int) -> "float | None":
    """Return the maximum numeric value in a column.

    Non-numeric string values are ignored. Returns None if no numeric values.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        col_idx: Zero-based column index.

    Returns:
        Maximum numeric value, or None if no numeric cells found.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    values = get_column_values(model, sheet_idx, col_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return max(nums) if nums else None


def average_column(model: dict[str, Any], sheet_idx: int, col_idx: int) -> float:
    """Return the average (mean) of numeric values in a column.

    Non-numeric string values are ignored. Returns 0.0 if no numeric values.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        col_idx: Zero-based column index.

    Returns:
        Average of numeric values, or 0.0 if no numeric cells found.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    values = get_column_values(model, sheet_idx, col_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return sum(nums) / len(nums) if nums else 0.0


def average_row(model: dict[str, Any], sheet_idx: int, row_idx: int) -> float:
    """Return the average (mean) of numeric values in a row.

    Non-numeric string values are ignored. Returns 0.0 if no numeric values.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        row_idx: Zero-based row index.

    Returns:
        Average of numeric values in the row, or 0.0 if no numeric cells found.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    values = get_row_values(model, sheet_idx, row_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return sum(nums) / len(nums) if nums else 0.0


def correlation_columns(
    model: dict[str, Any],
    sheet_idx: int,
    col_a: int,
    col_b: int,
) -> float:
    """Compute Pearson correlation coefficient between two columns.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        col_a: Zero-based index of first column.
        col_b: Zero-based index of second column.

    Returns:
        Pearson r in [-1.0, 1.0], or 0.0 if insufficient data.
    """
    vals_a = get_column_values(model, sheet_idx, col_a)
    vals_b = get_column_values(model, sheet_idx, col_b)

    pairs = []
    for va, vb in zip(vals_a, vals_b):
        try:
            pairs.append((float(va), float(vb)))
        except (ValueError, TypeError):
            pass

    n = len(pairs)
    if n < 2:
        return 0.0

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    denom = den_x * den_y
    if denom == 0.0:
        return 0.0
    return num / denom


def gnumeric_sheet_summary(model: "dict[str, Any]", sheet_idx: int) -> "dict[str, Any]":
    """Return a summary dict for a sheet with row_count, col_count, and nonempty_cells."""
    return {
        "row_count": row_count(model, sheet_idx),
        "col_count": get_column_count(model, sheet_idx),
        "nonempty_cells": count_nonempty_cells(model, sheet_idx),
    }


def gnumeric_numeric_cell_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the count of cells whose values are numeric (parseable as float).

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer count of numeric cells. Returns 0 if sheet not found or empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    count = 0
    for val in grid.values():
        if val is not None and val != "":
            try:
                float(str(val))
                count += 1
            except (ValueError, TypeError):
                pass
    return count


def gnumeric_column_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the number of columns (max column index + 1) in a sheet.

    Counts columns by finding the maximum column index among all occupied
    cells in the cell_grid.

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer column count. Returns 0 if sheet not found or empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return max(col for (row, col) in grid.keys()) + 1


def gnumeric_row_count_file(file_path: "str | bytes | Path", sheet_idx: int = 0) -> int:
    """Return the number of distinct row indices with data in the given sheet.

    Args:
        file_path: Path to a .gnumeric file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer row count. Returns 0 for empty sheets.

    Raises:
        GnumericError subclasses on parse failure.
    """
    model = load(file_path)
    return row_count(model, sheet_idx)


def gnumeric_column_count_file(file_path: "str | bytes | Path", sheet_idx: int = 0) -> int:
    """Return the number of distinct column indices with data in the given sheet.

    File-path wrapper around gnumeric_column_count(model, sheet_idx).

    Args:
        file_path: Path to a Gnumeric file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer column count.
    """
    model = load(file_path)
    return gnumeric_column_count(model, sheet_idx)


def gnumeric_cell_count_file(file_path: "str | bytes | Path", sheet_idx: int = 0) -> int:
    """Return the number of non-empty cells in a sheet, taking a file path.

    Convenience wrapper around the model-based ``count_nonempty_cells``.

    Args:
        file_path: Path to a ``.gnumeric`` file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer count of non-empty cells.
    """
    model = load(file_path)
    return count_nonempty_cells(model, sheet_idx)


def gnumeric_string_cell_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the count of cells that contain non-numeric string values.

    A cell is counted as a string cell if its value cannot be converted to float.

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer count of string cells. Returns 0 for empty sheets.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    count = 0
    for v in grid.values():
        try:
            float(v)
        except (ValueError, TypeError):
            count += 1
    return count


def gnumeric_empty_cell_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the count of cells in the grid with empty or None values.

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer count of empty cells. Returns 0 if sheet not found or empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    count = 0
    for v in grid.values():
        if v is None or v == "":
            count += 1
    return count


def gnumeric_nonempty_cell_count_file(
    file_path: "str | bytes | Path", sheet_idx: int = 0
) -> int:
    """Return the count of non-empty cells in a Gnumeric sheet (file-path API).

    Loads the file, parses it, and delegates to count_nonempty_cells.

    Args:
        file_path: Path to a .gnumeric file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer count of non-empty cells. Returns 0 for empty or missing sheets.
    """
    model = load(file_path)
    return count_nonempty_cells(model, sheet_idx)


def gnumeric_total_cell_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of cells across all sheets in a Gnumeric file.

    Sums the cell count from every sheet. Counts cells stored in the
    document (entries in cell_grid), not the theoretical grid size.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Total cell count across all sheets.
    """
    model = load(file_path)
    sheets = model.get("sheets", [])
    total = 0
    for i in range(len(sheets)):
        total += count_nonempty_cells(model, i)
    return total


def gnumeric_sheet_count(file_path: "str | bytes | Path") -> int:
    """Return the number of sheets in a Gnumeric file.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Integer count of sheets.
    """
    model = load(file_path)
    return len(model.get("sheets", []))


def gnumeric_has_multiple_sheets(file_path: "str | bytes | Path") -> bool:
    """Return True if the Gnumeric file contains more than one sheet.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        True if sheet count > 1, False otherwise.
    """
    return gnumeric_sheet_count(file_path) > 1


def gnumeric_average_cells_per_sheet(file_path: "str | bytes | Path") -> float:
    """Return the average number of cells per sheet.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Float average. 0.0 if no sheets.
    """
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    total = sum(len(s.get("cell_values", [])) for s in sheets)
    return total / len(sheets)


def gnumeric_numeric_density(file_path: "str | bytes | Path") -> float:
    """Return the ratio of numeric cells to total cells.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Float between 0.0 and 1.0. 0.0 if no cells.
    """
    model = load(file_path)
    total = 0
    numeric = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            total += 1
            try:
                float(val)
                numeric += 1
            except (ValueError, TypeError):
                pass
    if total == 0:
        return 0.0
    return numeric / total


def gnumeric_string_density(file_path: "str | bytes | Path") -> float:
    """Return the ratio of non-numeric cells to total cells.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Float between 0.0 and 1.0. 0.0 if no cells.
    """
    model = load(file_path)
    total = 0
    string_count = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            total += 1
            try:
                float(val)
            except (ValueError, TypeError):
                string_count += 1
    if total == 0:
        return 0.0
    return string_count / total


def gnumeric_max_cell_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the longest cell value string.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Integer max length. 0 if no cells.
    """
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            max_len = max(max_len, len(str(val)))
    return max_len


def gnumeric_min_cell_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the shortest cell value string.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Integer min length, or 0 if no cells.
    """
    model = load(file_path)
    min_len = None
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            length = len(str(val))
            if min_len is None or length < min_len:
                min_len = length
    return min_len if min_len is not None else 0


def gnumeric_all_sheets_have_data(file_path: "str | bytes | Path") -> bool:
    """Return True if every sheet has at least one non-empty cell value.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        True if all sheets have data; False if any sheet is empty or has no cells.
    """
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return False
    for sheet in sheets:
        vals = [v for v in sheet.get("cell_values", []) if str(v).strip()]
        if not vals:
            return False
    return True


def gnumeric_has_any_string_cell(file_path: "str | bytes | Path") -> bool:
    """Return True if any cell contains a non-empty string value.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        True if at least one cell has a non-empty string value.
    """
    model = load(file_path)
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            if isinstance(val, str) and val.strip():
                return True
    return False


def gnumeric_cell_count_all_sheets(file_path: "str | bytes | Path") -> int:
    """Return total number of cells across all sheets.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Total cell count (sum of cell_values lengths across all sheets).
    """
    model = load(file_path)
    return sum(len(sheet.get("cell_values", [])) for sheet in model.get("sheets", []))


def gnumeric_is_single_sheet(file_path: "str | bytes | Path") -> bool:
    """Return True if the workbook contains exactly one sheet."""
    model = load(file_path)
    return len(model.get("sheets", [])) == 1


def gnumeric_empty_sheet_count(file_path: "str | bytes | Path") -> int:
    """Return the number of sheets that have no non-empty cell values."""
    model = load(file_path)
    count = 0
    for sheet in model.get("sheets", []):
        vals = [v for v in sheet.get("cell_values", []) if str(v).strip()]
        if not vals:
            count += 1
    return count


def gnumeric_data_density(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = gnumeric_total_cell_count(file_path)
    if total == 0:
        return 0.0
    model = load(file_path)
    nonempty = 0
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            if str(v).strip():
                nonempty += 1
    return nonempty / total


def gnumeric_max_row_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum row count across all sheets. 0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    return max(sheet.get("row_count", 0) for sheet in sheets)


def gnumeric_min_row_count(file_path: "str | bytes | Path") -> int:
    """Return the minimum row count across all sheets. 0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    return min(sheet.get("row_count", 0) for sheet in sheets)


def gnumeric_has_empty_sheets(file_path: "str | bytes | Path") -> bool:
    """Return True if any sheet has zero cells."""
    return gnumeric_empty_sheet_count(file_path) > 0


def gnumeric_avg_row_count(file_path: "str | bytes | Path") -> float:
    """Return the average row count across all sheets. 0.0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    return sum(sheet.get("row_count", 0) for sheet in sheets) / len(sheets)


def gnumeric_nonempty_density(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = gnumeric_total_cell_count(file_path)
    if total == 0:
        return 0.0
    model = load(file_path)
    nonempty = 0
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            if str(v).strip():
                nonempty += 1
    return nonempty / total


def gnumeric_is_empty(file_path: "str | bytes | Path") -> bool:
    """Return True if the file has no cells across all sheets."""
    return gnumeric_total_cell_count(file_path) == 0


def gnumeric_max_column_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum number of columns across all sheets. 0 if no cells."""
    model = load(file_path)
    max_col = 0
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        if grid:
            col_max = max(col for (row, col) in grid.keys()) + 1
            if col_max > max_col:
                max_col = col_max
    return max_col


def gnumeric_total_string_length(file_path: "str | bytes | Path") -> int:
    """Return total length of all string cell values across all sheets."""
    model = load(file_path)
    total = 0
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            if isinstance(v, str):
                total += len(v)
    return total


def gnumeric_avg_cell_length(file_path: "str | bytes | Path") -> float:
    """Return average length of non-empty cell values. 0.0 if no cells."""
    model = load(file_path)
    lengths = []
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            s = str(v).strip()
            if s:
                lengths.append(len(s))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def gnumeric_column_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of column counts across sheets. 0.0 if fewer than 2 sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    col_counts = [sheet.get("max_col", 0) + 1 for sheet in sheets]
    mean = sum(col_counts) / len(col_counts)
    return sum((c - mean) ** 2 for c in col_counts) / len(col_counts)


def gnumeric_is_rectangular(file_path: "str | bytes | Path") -> bool:
    """Return True if all sheets have the same column count."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return True
    col_counts = [sheet.get("max_col", 0) for sheet in sheets]
    return len(set(col_counts)) == 1


def gnumeric_min_column_count(file_path: "str | bytes | Path") -> int:
    """Return the minimum number of columns across all sheets. 0 if no cells."""
    model = load(file_path)
    col_counts = []
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        if grid:
            col_counts.append(max(col for (row, col) in grid.keys()) + 1)
        else:
            col_counts.append(0)
    if not col_counts:
        return 0
    return min(col_counts)


def gnumeric_avg_column_count(file_path: "str | bytes | Path") -> float:
    """Return the average number of columns across all sheets. 0.0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    col_counts = []
    for sheet in sheets:
        grid = sheet.get("cell_grid", {})
        if grid:
            col_counts.append(max(col for (row, col) in grid.keys()) + 1)
        else:
            col_counts.append(0)
    return sum(col_counts) / len(col_counts)


def gnumeric_has_empty_cells(file_path: "str | bytes | Path") -> bool:
    """Return True if any sheet has cells with empty or None values."""
    model = load(file_path)
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        for val in grid.values():
            if val is None or (isinstance(val, str) and not val.strip()):
                return True
    return False


def gnumeric_total_row_count(file_path: "str | bytes | Path") -> int:
    """Return total row count across all sheets."""
    model = load(file_path)
    total = 0
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        if grid:
            total += max(row for (row, col) in grid.keys()) + 1
    return total


def gnumeric_is_all_numeric(file_path: "str | bytes | Path") -> bool:
    """Return True if all cells have numeric values. False if no cells."""
    model = load(file_path)
    has_cells = False
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        for val in grid.values():
            has_cells = True
            if val is None:
                return False
            try:
                float(val)
            except (ValueError, TypeError):
                return False
    return has_cells


def gnumeric_nonempty_cell_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    model = load(file_path)
    total = 0
    nonempty = 0
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        total += len(grid)
        for val in grid.values():
            if val is not None and (not isinstance(val, str) or val.strip()):
                nonempty += 1
    if total == 0:
        return 0.0
    return nonempty / total


def gnumeric_row_count_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of row counts across sheets. 0.0 if fewer than 2 sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = [len(s.get("cell_grid", {})) for s in sheets]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def gnumeric_sheet_name_lengths(file_path: "str | bytes | Path") -> list[int]:
    """Return list of character lengths of sheet names."""
    model = load(file_path)
    return [len(s.get("name", "")) for s in model.get("sheets", [])]


def gnumeric_max_cell_value_length(file_path: "str | bytes | Path") -> int:
    """Return the maximum character length of any cell value. 0 if no cells."""
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        for _key, cell in sheet.get("cell_grid", {}).items():
            val = cell.get("value", "")
            if val is not None and len(str(val)) > max_len:
                max_len = len(str(val))
    return max_len


def gnumeric_is_multi_sheet(file_path: "str | bytes | Path") -> bool:
    """Return True if the workbook has more than one sheet."""
    model = load(file_path)
    return len(model.get("sheets", [])) > 1


def gnumeric_avg_numeric_value(file_path: "str | bytes | Path") -> float:
    """Return average of all numeric cell values across all sheets. 0.0 if none."""
    model = load(file_path)
    values = []
    for sheet in model.get("sheets", []):
        for _key, val in sheet.get("cell_grid", {}).items():
            if val is not None:
                try:
                    values.append(float(str(val)))
                except (ValueError, TypeError):
                    pass
    return sum(values) / len(values) if values else 0.0


def gnumeric_nonempty_row_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of rows with at least one non-empty cell to total rows in sheet 0. 0.0 if empty."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return 0.0
    rows_with_data = set()
    all_rows = set()
    for key, val in grid.items():
        row, col = key
        all_rows.add(row)
        if val is not None and str(val).strip():
            rows_with_data.add(row)
    if not all_rows:
        return 0.0
    return len(rows_with_data) / len(all_rows)


def gnumeric_longest_row_index(file_path: "str | bytes | Path") -> int:
    """Return 0-based row index with the most non-empty cells in sheet 0. -1 if empty."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return -1
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return -1
    row_counts: dict = {}
    for key, val in grid.items():
        row, col = key
        if val is not None and str(val).strip():
            row_counts[row] = row_counts.get(row, 0) + 1
    if not row_counts:
        return -1
    return max(row_counts, key=row_counts.get)


def gnumeric_numeric_sum_all(file_path: "str | bytes | Path") -> float:
    """Return sum of all numeric cell values across all sheets."""
    model = load(file_path)
    total = 0.0
    for sheet in model.get("sheets", []):
        for _key, val in sheet.get("cell_grid", {}).items():
            if val is not None:
                try:
                    total += float(str(val))
                except (ValueError, TypeError):
                    pass
    return total


def gnumeric_empty_column_count(file_path: "str | bytes | Path") -> int:
    """Return number of entirely empty columns in sheet 0."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return 0
    all_cols: set = set()
    cols_with_data: set = set()
    for key, val in grid.items():
        row, col = key
        all_cols.add(col)
        if val is not None and str(val).strip():
            cols_with_data.add(col)
    empty_cols = all_cols - cols_with_data
    return len(empty_cols)


def gnumeric_cell_count_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of cell counts across sheets. 0.0 if fewer than 2 sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = [len(s.get("cell_grid", {})) for s in sheets]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def gnumeric_max_row_length(file_path: "str | bytes | Path") -> int:
    """Return maximum number of cells in any single row across all sheets. 0 if no cells."""
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        from collections import Counter as _Counter
        row_counts = _Counter(key[0] for key in sheet.get("cell_grid", {}).keys())
        if row_counts:
            rc = max(row_counts.values())
            if rc > max_len:
                max_len = rc
    return max_len
