"""
neutral_model.py -- Neutral model builder and validator for format-factory-fodt.

Builds and validates the 7-entity FODT neutral model output:
  Document -> Block (paragraph|heading) | List (-> ListItem) | Table (-> TableRow -> TableCell)
  plus Warning (in warnings list)

Gate 5 neutral model: schemas/neutral-model/fodt/ (7 entities, 26 mappings, 19 rules).
Gate 5 PASSED: Babar Raza, 2026-05-08, run046.
IR-FODT-015: validate against neutral model before returning.

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

from __future__ import annotations

from typing import Any

from .constants import FORMAT_ID, SPEC_VERSION


# ---------------------------------------------------------------------------
# Warning helper
# ---------------------------------------------------------------------------

def make_warning(code: str, message: str, source: str | None = None) -> dict[str, Any]:
    """Build a structured Warning dict matching the neutral model Warning entity."""
    w: dict[str, Any] = {"code": code, "message": message}
    if source is not None:
        w["source"] = source
    return w


# ---------------------------------------------------------------------------
# Document builder
# ---------------------------------------------------------------------------

def build_document(
    odf_version_attr: str,
    mimetype: str | None,
    blocks: list[dict[str, Any]],
    lists: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    unsupported_features: list[str],
    parse_errors: list[dict[str, Any]],
    content: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Assemble the Document-level result dict matching the FODT neutral model.

    Fields conform to the Document entity in schemas/neutral-model/fodt/model.yaml.
    Additional fields (unsupported_features, parse_errors) extend the neutral
    model for product parser transparency.

    R55 TC-0060: ``content`` is a unified document-order sequence of dicts each
    with ``{"kind": "block"|"list"|"table", "data": <item_dict>}``.  The writer
    uses ``content`` when present to emit elements in document order.  The legacy
    ``blocks``/``lists``/``tables`` lists are retained for backward compatibility.
    """
    doc: dict[str, Any] = {
        "format_id": FORMAT_ID,
        "spec_version": SPEC_VERSION,
        "odf_version_attr": odf_version_attr,
        "mimetype": mimetype,
        "blocks": blocks,
        "lists": lists,
        "tables": tables,
        "warnings": warnings,
        "unsupported_features": sorted(unsupported_features),
        "parse_errors": parse_errors,
    }
    if content is not None:
        doc["content"] = content
    return doc


# ---------------------------------------------------------------------------
# Document validator (IR-FODT-015)
# ---------------------------------------------------------------------------

def validate_document(result: dict[str, Any]) -> list[str]:
    """Validate a parse_fodt() result against the 7-entity neutral model.

    Returns a list of violation strings. Empty list means valid.
    Does NOT raise -- callers decide whether to treat violations as fatal.
    """
    violations: list[str] = []

    # Required top-level fields
    for field in ("format_id", "spec_version", "odf_version_attr", "blocks", "lists", "tables", "warnings"):
        if field not in result:
            violations.append(f"Document missing required field: {field!r}")

    if result.get("format_id") != FORMAT_ID:
        violations.append(
            f"Document.format_id must be {FORMAT_ID!r}; got {result.get('format_id')!r}"
        )

    blocks = result.get("blocks")
    if not isinstance(blocks, list):
        violations.append("Document.blocks must be a list")
    else:
        for i, block in enumerate(blocks):
            violations.extend(_validate_block(block, i))

    lists = result.get("lists")
    if not isinstance(lists, list):
        violations.append("Document.lists must be a list")
    else:
        for i, lst in enumerate(lists):
            violations.extend(_validate_list(lst, i))

    tables = result.get("tables")
    if not isinstance(tables, list):
        violations.append("Document.tables must be a list")
    else:
        for i, table in enumerate(tables):
            violations.extend(_validate_table(table, i))

    warnings = result.get("warnings")
    if not isinstance(warnings, list):
        violations.append("Document.warnings must be a list")

    return violations


def _validate_block(block: dict[str, Any], idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Block[{idx}]"

    for field in ("type", "text"):
        if field not in block:
            violations.append(f"{prefix} missing required field: {field!r}")

    btype = block.get("type")
    if btype not in ("paragraph", "heading"):
        violations.append(f"{prefix}.type must be 'paragraph' or 'heading'; got {btype!r}")

    if btype == "heading":
        hl = block.get("heading_level")
        if not isinstance(hl, int) or hl < 1 or hl > 6:
            violations.append(f"{prefix}.heading_level must be int 1-6 for headings; got {hl!r}")

    return violations


def _validate_list(lst: dict[str, Any], idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"List[{idx}]"

    if "items" not in lst:
        violations.append(f"{prefix} missing required field: 'items'")
        return violations

    items = lst["items"]
    if not isinstance(items, list):
        violations.append(f"{prefix}.items must be a list")
        return violations

    for j, item in enumerate(items):
        violations.extend(_validate_list_item(item, idx, j))

    return violations


def _validate_list_item(item: dict[str, Any], list_idx: int, item_idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"List[{list_idx}].Item[{item_idx}]"

    for field in ("text", "level"):
        if field not in item:
            violations.append(f"{prefix} missing required field: {field!r}")

    level = item.get("level")
    if not isinstance(level, int) or level < 1:
        violations.append(f"{prefix}.level must be a positive int; got {level!r}")

    return violations


def _validate_table(table: dict[str, Any], idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Table[{idx}]"

    if "rows" not in table:
        violations.append(f"{prefix} missing required field: 'rows'")
        return violations

    rows = table["rows"]
    if not isinstance(rows, list):
        violations.append(f"{prefix}.rows must be a list")
        return violations

    for j, row in enumerate(rows):
        violations.extend(_validate_table_row(row, idx, j))

    return violations


def _validate_table_row(row: dict[str, Any], table_idx: int, row_idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Table[{table_idx}].Row[{row_idx}]"

    if "cells" not in row:
        violations.append(f"{prefix} missing required field: 'cells'")
        return violations

    cells = row["cells"]
    if not isinstance(cells, list):
        violations.append(f"{prefix}.cells must be a list")
        return violations

    for k, cell in enumerate(cells):
        if "text" not in cell:
            violations.append(f"{prefix}.Cell[{k}] missing required field: 'text'")

    return violations


# ---------------------------------------------------------------------------
# Document statistics (R57 — new capability)
# ---------------------------------------------------------------------------

def document_stats(document: dict[str, Any]) -> dict[str, Any]:
    """Return content statistics for a parsed FODT document.

    Returns a dict with:
      block_count: int          (paragraphs + headings)
      paragraph_count: int
      heading_count: int
      list_count: int           (top-level lists)
      list_item_count: int      (all items including nested)
      table_count: int
      table_cell_count: int
      total_text_length: int    (sum of text chars across all content)
      hyperlink_count: int      (runs with href attribute)

    Added in R57 Train E as a new product capability.
    Useful for document triage and content extraction pipelines.
    """
    stats: dict[str, Any] = {
        "block_count": 0,
        "paragraph_count": 0,
        "heading_count": 0,
        "list_count": 0,
        "list_item_count": 0,
        "table_count": 0,
        "table_cell_count": 0,
        "total_text_length": 0,
        "hyperlink_count": 0,
    }

    # Prefer content list (R55 TC-0060 document-order) if present
    content = document.get("content", [])
    blocks = document.get("blocks", [])
    lists = document.get("lists", [])
    tables = document.get("tables", [])

    # If content list is present, count from it; otherwise use separate lists
    if content:
        seen_blocks: list[dict[str, Any]] = []
        seen_lists: list[dict[str, Any]] = []
        seen_tables: list[dict[str, Any]] = []
        for item in content:
            kind = item.get("kind", "")
            data = item.get("data", {})
            if kind == "block":
                seen_blocks.append(data)
            elif kind == "list":
                seen_lists.append(data)
            elif kind == "table":
                seen_tables.append(data)
        blocks = seen_blocks
        lists = seen_lists
        tables = seen_tables

    # Count blocks
    for block in blocks:
        stats["block_count"] += 1
        btype = block.get("type", "")
        if btype == "paragraph":
            stats["paragraph_count"] += 1
        elif btype == "heading":
            stats["heading_count"] += 1
        # Text length from block runs
        runs = block.get("runs", [])
        for run in runs:
            text = run.get("text", "") or ""
            stats["total_text_length"] += len(text)
            if run.get("href"):
                stats["hyperlink_count"] += 1
        # Fallback: text field
        if not runs:
            stats["total_text_length"] += len(block.get("text", "") or "")

    # Count lists and items
    stats["list_count"] = len(lists)
    for lst in lists:
        items = lst.get("items", [])
        stats["list_item_count"] += len(items)
        for item in items:
            stats["total_text_length"] += len(item.get("text", "") or "")

    # Count tables and cells
    stats["table_count"] = len(tables)
    for table in tables:
        for row in table.get("rows", []):
            cells = row.get("cells", [])
            stats["table_cell_count"] += len(cells)
            for cell in cells:
                stats["total_text_length"] += len(cell.get("text", "") or "")

    return stats


# ---------------------------------------------------------------------------
# Document heading outline (R59 — new capability)
# ---------------------------------------------------------------------------

def document_heading_outline(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Return an ordered list of all headings in the document.

    Each entry is: {"level": int, "text": str, "index": int}
    where index is the position among all headings (0-based).

    Respects content list (document-order) if present, otherwise uses
    the blocks list. Only includes blocks with type == "heading".

    Useful for table-of-contents generation and document navigation.
    Added in R59 Train G as a product deepening capability.
    """
    outline: list[dict[str, Any]] = []
    heading_index = 0

    content = document.get("content", [])
    if content:
        blocks = [item["data"] for item in content if item.get("kind") == "block"]
    else:
        blocks = document.get("blocks", [])

    for block in blocks:
        if block.get("type") == "heading":
            level = block.get("heading_level", 1)
            text = block.get("text", "")
            outline.append({"level": level, "text": text, "index": heading_index})
            heading_index += 1

    return outline


# ---------------------------------------------------------------------------
# Document text content (R59 — new capability)
# ---------------------------------------------------------------------------

def document_text_content(document: dict[str, Any], separator: str = "\n") -> str:
    """Return all text content from the document as a single string.

    Concatenates text from blocks (paragraphs + headings), list items,
    and table cells in document order (uses content list if present).

    Args:
        document: Parsed FODT document dict.
        separator: String inserted between content segments (default: newline).

    Useful for full-text extraction and search indexing pipelines.
    Added in R59 Train G as a product deepening capability.
    """
    parts: list[str] = []

    content = document.get("content", [])
    if content:
        for item in content:
            kind = item.get("kind", "")
            data = item.get("data", {})
            if kind == "block":
                runs = data.get("runs", [])
                if runs:
                    parts.append("".join(r.get("text", "") or "" for r in runs))
                else:
                    text = data.get("text", "") or ""
                    if text:
                        parts.append(text)
            elif kind == "list":
                for item_entry in data.get("items", []):
                    text = item_entry.get("text", "") or ""
                    if text:
                        parts.append(text)
            elif kind == "table":
                for row in data.get("rows", []):
                    for cell in row.get("cells", []):
                        text = cell.get("text", "") or ""
                        if text:
                            parts.append(text)
    else:
        for block in document.get("blocks", []):
            runs = block.get("runs", [])
            if runs:
                parts.append("".join(r.get("text", "") or "" for r in runs))
            else:
                text = block.get("text", "") or ""
                if text:
                    parts.append(text)
        for lst in document.get("lists", []):
            for item_entry in lst.get("items", []):
                text = item_entry.get("text", "") or ""
                if text:
                    parts.append(text)
        for table in document.get("tables", []):
            for row in table.get("rows", []):
                for cell in row.get("cells", []):
                    text = cell.get("text", "") or ""
                    if text:
                        parts.append(text)

    return separator.join(parts)
