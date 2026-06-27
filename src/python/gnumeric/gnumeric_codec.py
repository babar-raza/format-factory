"""
Gnumeric codec — minimal Gnumeric spreadsheet API.

Gnumeric (.gnumeric) — gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Uses gzip + xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
spec_concept: Gnumeric XML cell/sheet workbook
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


# ---------------------------------------------------------------------------
# Domain module re-exports
# ---------------------------------------------------------------------------
try:
    from .gnumeric_analytics import *  # noqa: F401, F403
except ImportError:
    pass
try:
    from .gnumeric_workbook_stats import *  # noqa: F401, F403
except ImportError:
    pass


def probe_gnumeric_codec(source) -> dict:
    """gnumeric: Return format metadata without full parse."""
    try:
        from pathlib import Path as _Path
        return {
            "format": "gnumeric",
            "file_size": _Path(source).stat().st_size,
            "valid": True,
        }
    except Exception as exc:
        return {"format": "gnumeric", "valid": False, "error": str(exc)}


def gnumeric_installed_workflow(source: "str | bytes | Path") -> dict:
    """Gnumeric installed-workflow proof: load source and return format metadata.

    Named variant with explicit gnumeric_ prefix for API naming consistency
    across the Format Factory FOSS track.

    Args:
        source: Gnumeric file path or bytes.

    Returns:
        dict with keys: format, loaded, sheet_count, cell_count.
    """
    model = load(source)
    sheet_count = len(model.get("sheets", []))
    cell_count = sum(
        len(sheet.get("cell_grid", {}))
        for sheet in model.get("sheets", [])
    )
    return {
        "format": "gnumeric",
        "loaded": True,
        "sheet_count": sheet_count,
        "cell_count": cell_count,
    }
