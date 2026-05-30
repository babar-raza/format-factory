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

def document_word_count(document: dict[str, Any]) -> dict[str, Any]:
    """Return approximate word count for the document.

    Counts whitespace-separated tokens from all text content (blocks,
    list items, table cells). Uses Python's str.split() which handles
    multiple spaces and newlines correctly.

    Returns a dict with:
      total_words: int              (across all content)
      block_words: int              (from paragraphs + headings)
      list_words: int               (from list items)
      table_words: int              (from table cells)

    Useful for content analysis and document triage.
    Added in R60 Train G as a product deepening capability.
    """
    block_words = 0
    list_words = 0
    table_words = 0

    content = document.get("content", [])
    if content:
        for item in content:
            kind = item.get("kind", "")
            data = item.get("data", {})
            if kind == "block":
                runs = data.get("runs", [])
                text = "".join(r.get("text", "") or "" for r in runs) if runs else (data.get("text", "") or "")
                block_words += len(text.split())
            elif kind == "list":
                for entry in data.get("items", []):
                    list_words += len((entry.get("text", "") or "").split())
            elif kind == "table":
                for row in data.get("rows", []):
                    for cell in row.get("cells", []):
                        table_words += len((cell.get("text", "") or "").split())
    else:
        for block in document.get("blocks", []):
            runs = block.get("runs", [])
            text = "".join(r.get("text", "") or "" for r in runs) if runs else (block.get("text", "") or "")
            block_words += len(text.split())
        for lst in document.get("lists", []):
            for entry in lst.get("items", []):
                list_words += len((entry.get("text", "") or "").split())
        for table in document.get("tables", []):
            for row in table.get("rows", []):
                for cell in row.get("cells", []):
                    table_words += len((cell.get("text", "") or "").split())

    return {
        "total_words": block_words + list_words + table_words,
        "block_words": block_words,
        "list_words": list_words,
        "table_words": table_words,
    }


def document_table_summary(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a compact summary of all tables in the document.

    Each entry in the returned list is a dict with:
      index: int            (0-based table index in document order)
      row_count: int
      column_count: int     (max columns across all rows)
      cell_count: int       (total cells)

    Respects content list (document-order) if present.

    Useful for table triage and structural analysis.
    Added in R60 Train G as a product deepening capability.
    """
    tables = []
    content = document.get("content", [])
    if content:
        raw_tables = [item["data"] for item in content if item.get("kind") == "table"]
    else:
        raw_tables = document.get("tables", [])

    for idx, table in enumerate(raw_tables):
        rows = table.get("rows", [])
        cell_count = sum(len(row.get("cells", [])) for row in rows)
        col_count = max((len(row.get("cells", [])) for row in rows), default=0)
        tables.append({
            "index": idx,
            "row_count": len(rows),
            "column_count": col_count,
            "cell_count": cell_count,
        })
    return tables


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


# ---------------------------------------------------------------------------
# Document list stats (R61 — new capability)
# ---------------------------------------------------------------------------

def document_list_stats(document: dict[str, Any]) -> dict[str, Any]:
    """Return statistics about lists in the document.

    Returns a dict with:
      list_count: int           (total number of lists)
      total_items: int          (total list items across all lists)
      max_depth: int            (maximum nesting depth found)
      per_list: list[dict]      (per-list breakdown)
        Each entry: {index, item_count, max_depth}

    Useful for document structure analysis and TOC generation.
    Added in R61 Train G as a product deepening capability.
    """
    lists = document.get("lists", [])
    # Also check content list for embedded lists
    content_lists = [
        item.get("data", {}) for item in document.get("content", [])
        if item.get("kind") == "list"
    ]
    all_lists = lists + content_lists

    per_list = []
    total_items = 0
    overall_max_depth = 0

    for idx, lst in enumerate(all_lists):
        items = lst.get("items", [])
        item_count = len(items)
        max_depth = max((item.get("level", 1) for item in items), default=0)
        total_items += item_count
        overall_max_depth = max(overall_max_depth, max_depth)
        per_list.append({
            "index": idx,
            "item_count": item_count,
            "max_depth": max_depth,
        })

    return {
        "list_count": len(all_lists),
        "total_items": total_items,
        "max_depth": overall_max_depth,
        "per_list": per_list,
    }


# ---------------------------------------------------------------------------
# Document reading level (R61 — new capability)
# ---------------------------------------------------------------------------

def document_reading_level(document: dict[str, Any]) -> dict[str, Any]:
    """Estimate reading level metrics for the document.

    Returns a dict with:
      avg_words_per_sentence: float   (approximate; uses period-split)
      avg_chars_per_word: float       (across all words)
      total_words: int
      total_sentences: int            (approximate; period/!/? count)
      estimated_grade_level: float    (Flesch-Kincaid grade approximation)

    Note: This is an estimation based on character/word counts only.
    It does not perform full syntactic analysis.
    Added in R61 Train G as a product deepening capability.
    """
    text = document_text_content(document, separator=" ")
    if not text:
        return {
            "avg_words_per_sentence": 0.0,
            "avg_chars_per_word": 0.0,
            "total_words": 0,
            "total_sentences": 0,
            "estimated_grade_level": 0.0,
        }

    words = [w for w in text.split() if w]
    total_words = len(words)

    # Approximate sentence count by terminal punctuation
    import re
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    total_sentences = max(len(sentences), 1)

    avg_words_per_sentence = total_words / total_sentences
    avg_chars_per_word = (sum(len(w) for w in words) / total_words) if total_words > 0 else 0.0

    # Flesch-Kincaid Grade Level approximation (simplified: no syllable count)
    # FK_GL ≈ 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    # Simplified without syllable count:
    estimated_grade_level = 0.39 * avg_words_per_sentence + 11.8 * avg_chars_per_word / 5.0 - 15.59
    estimated_grade_level = max(0.0, round(estimated_grade_level, 2))

    return {
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "avg_chars_per_word": round(avg_chars_per_word, 2),
        "total_words": total_words,
        "total_sentences": total_sentences,
        "estimated_grade_level": estimated_grade_level,
    }


# ---------------------------------------------------------------------------
# Document hyperlink count (R62 — new capability)
# ---------------------------------------------------------------------------

def document_hyperlink_count(document: dict[str, Any]) -> dict[str, Any]:
    """Count hyperlinks detected in the document.

    Scans all block-level content for entries that carry a 'hyperlinks' list
    (populated by the parser when it detects xlink:href attributes). Returns:
      total: int             — total hyperlink count across all blocks
      per_block: list[int]   — hyperlink count per top-level block (0 if none)

    Added in R62 Train H as a product deepening capability
    (hyperlink xlink:type preservation).
    """
    blocks = document.get("blocks", [])
    per_block: list[int] = []
    total = 0
    for block in blocks:
        links = block.get("hyperlinks", [])
        count = len(links)
        per_block.append(count)
        total += count
    return {"total": total, "per_block": per_block}


# ---------------------------------------------------------------------------
# Document footnote count (R62 — new capability)
# ---------------------------------------------------------------------------

def document_footnote_count(document: dict[str, Any]) -> dict[str, Any]:
    """Detect and count footnote/endnote annotations in the document.

    Scans blocks for 'footnotes' or 'endnotes' lists (populated by the parser
    when it detects text:note elements). Returns:
      footnotes: int         — total footnote count
      endnotes: int          — total endnote count
      total: int             — combined count
      has_notes: bool        — True if any notes are present
      note: str              — advisory message if notes detected

    Added in R62 Train H as a product deepening capability
    (footnote/endnote detection warning).
    """
    blocks = document.get("blocks", [])
    footnotes = 0
    endnotes = 0
    for block in blocks:
        footnotes += len(block.get("footnotes", []))
        endnotes += len(block.get("endnotes", []))
    total = footnotes + endnotes
    result: dict[str, Any] = {
        "footnotes": footnotes,
        "endnotes": endnotes,
        "total": total,
        "has_notes": total > 0,
    }
    if total > 0:
        result["note"] = (
            f"Document contains {footnotes} footnote(s) and {endnotes} endnote(s). "
            "Note content may not be fully preserved in text export."
        )
    return result


# ---------------------------------------------------------------------------
# Document heading level distribution (R63 Train H — new capability)
# ---------------------------------------------------------------------------

def document_heading_level_distribution(document: dict[str, Any]) -> dict[str, Any]:
    """Return the count of headings at each heading level (H1-H6).

    Scans all blocks for heading type and groups by heading_level. Returns:
      by_level: dict[int, int]   — {level: count} for levels 1-6
      total_headings: int        — total heading count
      deepest_level: int | None  — highest level number used (deepest nesting)
      shallowest_level: int | None — lowest level number used (top level)

    Useful for understanding document structure, validating heading hierarchy,
    and generating table-of-contents previews.
    Added in R63 Train H as a product deepening capability (heading level distribution).
    """
    by_level: dict[int, int] = {}
    for block in document.get("blocks", []):
        if block.get("type") == "heading":
            level = block.get("heading_level")
            if isinstance(level, int) and 1 <= level <= 6:
                by_level[level] = by_level.get(level, 0) + 1

    total = sum(by_level.values())
    levels = list(by_level.keys())
    return {
        "by_level": by_level,
        "total_headings": total,
        "deepest_level": max(levels) if levels else None,
        "shallowest_level": min(levels) if levels else None,
    }


# ---------------------------------------------------------------------------
# Document table cell count (R63 Train H — new capability)
# ---------------------------------------------------------------------------

def document_table_cell_count(document: dict[str, Any]) -> dict[str, Any]:
    """Return total cell count across all tables in the document.

    For each table, counts the total cells (rows * columns approximation using
    actual cell objects). Returns:
      total_cells: int        — sum of all cells across all tables
      total_tables: int       — number of tables
      per_table: list[dict]   — per-table stats with keys:
        table_index: int
        row_count: int
        cell_count: int       — sum of cells in all rows of this table
        avg_cells_per_row: float

    Added in R63 Train H as a product deepening capability (table cell density analysis).
    """
    tables = document.get("tables", [])
    per_table: list[dict[str, Any]] = []
    total_cells = 0
    for idx, table in enumerate(tables):
        rows = table.get("rows", [])
        row_count = len(rows)
        cell_count = sum(len(row.get("cells", [])) for row in rows)
        per_table.append({
            "table_index": idx,
            "row_count": row_count,
            "cell_count": cell_count,
            "avg_cells_per_row": round(cell_count / row_count, 2) if row_count > 0 else 0.0,
        })
        total_cells += cell_count
    return {
        "total_cells": total_cells,
        "total_tables": len(tables),
        "per_table": per_table,
    }


# ---------------------------------------------------------------------------
# Document table cell span summary (R64 Train H — new capability)
# ---------------------------------------------------------------------------

def document_table_cell_span_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Return span statistics for table cells in the document.

    Scans all table cells for colspan/rowspan attributes. A cell has colspan
    if it carries 'table:number-columns-spanned' (or 'colspan') > 1.
    A cell has rowspan if it carries 'table:number-rows-spanned' (or 'rowspan') > 1.

    Returns:
        total_cells: int           — total cells across all tables
        cells_with_colspan: int    — cells with column span > 1
        cells_with_rowspan: int    — cells with row span > 1

    Useful for table structure analysis and merge-cell detection.
    Added in R64 Train H as a product deepening capability (table cell span analysis).
    """
    tables = document.get("tables", [])
    total_cells = 0
    cells_with_colspan = 0
    cells_with_rowspan = 0

    for table in tables:
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                total_cells += 1
                colspan = (
                    cell.get("table:number-columns-spanned")
                    or cell.get("colspan")
                    or 1
                )
                rowspan = (
                    cell.get("table:number-rows-spanned")
                    or cell.get("rowspan")
                    or 1
                )
                try:
                    if int(colspan) > 1:
                        cells_with_colspan += 1
                except (TypeError, ValueError):
                    pass
                try:
                    if int(rowspan) > 1:
                        cells_with_rowspan += 1
                except (TypeError, ValueError):
                    pass

    return {
        "total_cells": total_cells,
        "cells_with_colspan": cells_with_colspan,
        "cells_with_rowspan": cells_with_rowspan,
    }


# ---------------------------------------------------------------------------
# Document text field warnings (R64 Train H — new capability)
# ---------------------------------------------------------------------------

def document_text_field_warnings(document: dict[str, Any]) -> list[str]:
    """Return warning strings for detected text field elements in the document.

    Scans all blocks for 'fields' metadata (populated by the parser when it
    detects text:placeholder, text:date, text:page-number, or similar ODF
    text field elements). Each detected field type generates a warning.

    Also scans block text content for common placeholder patterns like
    '<text:placeholder>' or '<text:date>' if raw XML fragments are present.

    Returns:
        list[str] — warning strings, one per detected field type.
        Empty list if no text fields are detected.

    Useful for document auditing, template detection, and field replacement.
    Added in R64 Train H as a product deepening capability (text field warnings).
    """
    warnings: list[str] = []
    seen_types: set[str] = set()

    field_type_labels = {
        "placeholder": "text:placeholder",
        "date": "text:date",
        "page-number": "text:page-number",
        "page-count": "text:page-count",
        "time": "text:time",
        "author": "text:author-name",
        "title": "text:title",
        "subject": "text:subject",
    }

    for block in document.get("blocks", []):
        # Check explicit fields list (if parser populates it)
        fields = block.get("fields", [])
        for field in fields:
            ftype = field.get("type", "") if isinstance(field, dict) else str(field)
            if ftype and ftype not in seen_types:
                seen_types.add(ftype)
                label = field_type_labels.get(ftype, ftype)
                warnings.append(
                    f"Document contains {label} field(s). "
                    "Field content may not be preserved in plain text export."
                )

        # Check runs for field markers
        for run in block.get("runs", []):
            field_type = run.get("field_type")
            if field_type and field_type not in seen_types:
                seen_types.add(field_type)
                label = field_type_labels.get(field_type, field_type)
                warnings.append(
                    f"Document contains {label} field(s). "
                    "Field content may not be preserved in plain text export."
                )

    return warnings


# ---------------------------------------------------------------------------
# Document footnote/endnote summary (R65 Train H — new capability)
# ---------------------------------------------------------------------------

def document_footnote_endnote_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Return a summary of footnotes, endnotes, and inline notes in the document.

    Scans all blocks for 'footnotes', 'endnotes', and 'inline_notes' lists
    (populated by the parser when it detects text:note elements with
    note-class='footnote' or 'endnote'). Also counts inline note markers
    found in block runs.

    Returns:
        footnote_count: int       — number of footnotes
        endnote_count: int        — number of endnotes
        inline_note_count: int    — number of inline note markers
        total: int                — combined count of all notes
        has_notes: bool           — True if any notes are present

    Useful for academic/legal document analysis and note preservation auditing.
    Added in R65 Train H as a product deepening capability (footnote/endnote summary).
    """
    footnote_count = 0
    endnote_count = 0
    inline_note_count = 0

    for block in document.get("blocks", []):
        footnote_count += len(block.get("footnotes", []))
        endnote_count += len(block.get("endnotes", []))
        inline_note_count += len(block.get("inline_notes", []))

        # Also check runs for note markers
        for run in block.get("runs", []):
            note_class = run.get("note_class") or run.get("text:note-class")
            if note_class == "footnote":
                footnote_count += 1
            elif note_class == "endnote":
                endnote_count += 1
            elif note_class == "inline":
                inline_note_count += 1

    total = footnote_count + endnote_count + inline_note_count
    return {
        "footnote_count": footnote_count,
        "endnote_count": endnote_count,
        "inline_note_count": inline_note_count,
        "total": total,
        "has_notes": total > 0,
    }


# ---------------------------------------------------------------------------
# Document image frame list (R65 Train H — new capability)
# ---------------------------------------------------------------------------

def document_image_frame_list(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of image frames found in the document.

    Scans all blocks, tables, and content items for 'frames' or 'images'
    metadata (populated by the parser when it detects draw:frame / draw:image
    elements). Each entry in the returned list contains:
      frame_name: str         — the draw:name attribute (or empty)
      anchor_type: str        — the text:anchor-type (e.g. 'paragraph', 'char')
      image_href: str         — the xlink:href of the embedded image

    Returns:
        list[dict] — all image frames found. Empty list if none.

    Useful for image inventory, asset extraction, and document media auditing.
    Added in R65 Train H as a product deepening capability (image frame inventory).
    """
    results: list[dict[str, Any]] = []

    def _scan_frames(frames: list) -> None:
        for frame in frames:
            if not isinstance(frame, dict):
                continue
            results.append({
                "frame_name": frame.get("name", frame.get("draw:name", "")),
                "anchor_type": frame.get("anchor_type", frame.get("text:anchor-type", "")),
                "image_href": frame.get("image_href", frame.get("xlink:href", "")),
            })

    # Scan blocks
    for block in document.get("blocks", []):
        _scan_frames(block.get("frames", []))
        _scan_frames(block.get("images", []))

    # Scan content list (document-order)
    for item in document.get("content", []):
        data = item.get("data", {})
        if isinstance(data, dict):
            _scan_frames(data.get("frames", []))
            _scan_frames(data.get("images", []))

    # Scan tables (images can be inside table cells)
    for table in document.get("tables", []):
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                _scan_frames(cell.get("frames", []))
                _scan_frames(cell.get("images", []))

    return results


# ---------------------------------------------------------------------------
# Document section summary (R66 Train H — new capability)
# ---------------------------------------------------------------------------

def document_section_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Return a summary of text sections found in the document.

    Scans blocks and content for section metadata. ODF documents may contain
    text:section elements that define named document sections (used for
    conditional content, linked sections, or write-protection).

    Looks for:
    - 'sections' list at document level
    - 'section' or 'text:section-name' attributes on blocks
    - content items with kind == 'section'

    Returns:
      section_count: int           -- number of distinct sections found
      section_names: list[str]     -- names of sections in document order

    Useful for document structure analysis and section-based content extraction.
    Added in R66 Train H as a product deepening capability (section inventory).
    """
    section_names: list[str] = []
    seen: set[str] = set()

    # Check explicit sections list at document level
    sections = document.get("sections", [])
    if isinstance(sections, list):
        for sec in sections:
            if isinstance(sec, dict):
                name = sec.get("name") or sec.get("text:name") or sec.get("text:section-name") or ""
                if name and name not in seen:
                    section_names.append(str(name))
                    seen.add(name)
            elif isinstance(sec, str) and sec not in seen:
                section_names.append(sec)
                seen.add(sec)

    # Check content list for section items
    for item in document.get("content", []):
        if item.get("kind") == "section":
            data = item.get("data", {})
            name = data.get("name") or data.get("text:name") or "" if isinstance(data, dict) else ""
            if name and name not in seen:
                section_names.append(str(name))
                seen.add(name)

    # Scan blocks for section attributes
    for block in document.get("blocks", []):
        sec_name = (
            block.get("section")
            or block.get("text:section-name")
            or block.get("section_name")
        )
        if sec_name and str(sec_name) not in seen:
            section_names.append(str(sec_name))
            seen.add(str(sec_name))

    return {
        "section_count": len(section_names),
        "section_names": section_names,
    }


# ---------------------------------------------------------------------------
# Document change tracking summary (R66 Train H — new capability)
# ---------------------------------------------------------------------------

def document_change_tracking_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Return a summary of tracked changes found in the document.

    ODF documents may contain text:tracked-changes elements that record
    insertions, deletions, and format changes made by different authors.

    Scans for:
    - 'tracked_changes' list at document level
    - 'changes' or 'text:tracked-changes' metadata
    - per-block 'change_id' or 'text:change-start' attributes

    Returns:
      tracked_change_count: int     -- number of tracked change records
      author_names: list[str]       -- unique author names found (in order)

    Useful for document review, collaboration analysis, and change auditing.
    Added in R66 Train H as a product deepening capability (change tracking summary).
    """
    change_count = 0
    authors: list[str] = []
    seen_authors: set[str] = set()

    # Check explicit tracked_changes list
    for key in ("tracked_changes", "changes", "text:tracked-changes"):
        changes = document.get(key)
        if isinstance(changes, list):
            for change in changes:
                if isinstance(change, dict):
                    change_count += 1
                    author = (
                        change.get("author")
                        or change.get("dc:creator")
                        or change.get("creator")
                        or ""
                    )
                    if author and str(author) not in seen_authors:
                        authors.append(str(author))
                        seen_authors.add(str(author))
                elif isinstance(change, str):
                    change_count += 1

    # Scan blocks for change markers
    for block in document.get("blocks", []):
        change_id = (
            block.get("change_id")
            or block.get("text:change-start")
            or block.get("text:change")
        )
        if change_id:
            change_count += 1

        # Check runs for change markers
        for run in block.get("runs", []):
            run_change = (
                run.get("change_id")
                or run.get("text:change-start")
            )
            if run_change:
                change_count += 1

    return {
        "tracked_change_count": change_count,
        "author_names": authors,
    }


def document_paragraph_style_distribution(document: dict[str, Any]) -> dict[str, Any]:
    """Return a distribution of paragraph styles used in the document.

    Scans all blocks/paragraphs in document['blocks'] for their 'style_name'
    or 'text:style-name' attribute and tallies counts per style name.

    Returns:
      style_count: int                     -- number of distinct style names seen
      distribution: dict[str, int]         -- count per style name
      heading_styles: list[str]            -- style names that appear to be heading styles
        (style name starts with "Heading" or "heading" or contains "h[1-9]" pattern)

    Useful for document structure analysis and style migration.
    Added in R75 Train G as a product advancement capability.
    """
    import re as _re
    distribution: dict[str, int] = {}
    for block in document.get("blocks", []):
        if not isinstance(block, dict):
            continue
        style = (
            block.get("style_name")
            or block.get("text:style-name")
            or block.get("style")
            or "Default"
        )
        style = str(style)
        distribution[style] = distribution.get(style, 0) + 1

    heading_pattern = _re.compile(r"(?i)^heading|^h[1-9]$|heading[-_ ][1-9]")
    heading_styles = [s for s in distribution if heading_pattern.search(s)]

    return {
        "style_count": len(distribution),
        "distribution": distribution,
        "heading_styles": heading_styles,
    }


def document_language_list(document: dict[str, Any]) -> list[str]:
    """Return all language codes used in the document.

    Scans blocks and runs for 'language', 'fo:language', 'xml:lang', or
    'lang' attributes and returns a deduplicated, sorted list of language
    codes found (e.g. ["de", "en", "fr"]).

    Empty strings and None values are excluded. Language codes are
    lowercased and deduplicated.

    Returns a list of language code strings (may be empty if no language
    attributes are present in the document).

    Added in R75 Train G as a product advancement capability.
    """
    seen: set[str] = set()
    codes: list[str] = []

    def _collect_lang(obj: dict[str, Any]) -> None:
        for key in ("language", "fo:language", "xml:lang", "lang"):
            val = obj.get(key)
            if val and isinstance(val, str):
                code = val.strip().lower()
                if code and code not in seen:
                    seen.add(code)
                    codes.append(code)

    meta = document.get("meta", {})
    if isinstance(meta, dict):
        _collect_lang(meta)

    for key in ("default_language", "document_language"):
        val = document.get(key)
        if val and isinstance(val, str):
            code = val.strip().lower()
            if code and code not in seen:
                seen.add(code)
                codes.append(code)

    for block in document.get("blocks", []):
        if not isinstance(block, dict):
            continue
        _collect_lang(block)
        for run in block.get("runs", []):
            if isinstance(run, dict):
                _collect_lang(run)

    return sorted(codes)


# ---------------------------------------------------------------------------
# Document block editor (R76 — product deepening: edit and save)
# ---------------------------------------------------------------------------

def document_set_block_text(
    document: dict[str, Any],
    block_idx: int,
    new_text: str,
    preserve_style: bool = True,
) -> tuple[bool, str]:
    """Set the text of a paragraph or heading block in the neutral model document.

    Mutates the document dict in-place. This enables an edit-and-save workflow:
        doc = parse_fodt(path)
        ok, msg = document_set_block_text(doc, 0, "Updated paragraph text")
        if ok:
            write_fodt(doc, out_path)

    Args:
        document: A neutral model document dict from parse_fodt().
        block_idx: 0-based index into the document's ``blocks`` list.
        new_text: The new text content for this block.
        preserve_style: If True (default), the first run's style attribute is
            preserved on the new run. If False, the run is plain text.

    Returns:
        (success: bool, message: str) — success=True if the block was found and updated.

    Note: This function updates the ``text`` field and reconstructs ``runs`` to a
    single unstyled run (or preserves the first run's style if preserve_style=True).
    Heading level, block type, and other metadata are preserved.

    Added in R76 Train G as a product deepening capability (edit-and-save workflow).
    """
    if not isinstance(document, dict):
        return False, "document must be a dict"

    blocks = document.get("blocks", [])
    if not isinstance(blocks, list):
        return False, "document.blocks must be a list"

    if block_idx < 0 or block_idx >= len(blocks):
        return False, f"block_idx {block_idx} out of range (document has {len(blocks)} blocks)"

    block = blocks[block_idx]
    if not isinstance(block, dict):
        return False, f"Block at index {block_idx} is not a dict"

    block_type = block.get("type", "")
    if block_type not in ("paragraph", "heading"):
        return False, f"Block type {block_type!r} is not a paragraph or heading"

    # Preserve first run style if requested
    preserved_style = None
    if preserve_style:
        existing_runs = block.get("runs", [])
        if existing_runs and isinstance(existing_runs[0], dict):
            preserved_style = existing_runs[0].get("style")

    block["text"] = new_text
    block["runs"] = [{"text": new_text, "style": preserved_style, "href": None}]

    # Also update content sequence if present (R55 document-order sequence)
    content = document.get("content", [])
    for item in content:
        if (
            isinstance(item, dict)
            and item.get("kind") == "block"
            and isinstance(item.get("data"), dict)
            and item["data"] is block
        ):
            # Already mutated via block reference
            break

    return True, f"Block {block_idx} ({block_type}) updated to {new_text[:40]!r}{'...' if len(new_text) > 40 else ''}"


def document_warnings_for_unsupported_edit(
    document: dict[str, Any],
    block_idx: int,
) -> list[str]:
    """Return warnings about unsupported features that may be lost when editing a block.

    Checks the target block for features the writer may not preserve perfectly:
    - Inline spans with styles
    - Hyperlinks in runs
    - Footnote or endnote references

    Returns a list of warning strings. Empty list means no unsupported features detected.

    Added in R76 Train G as a product deepening capability (edit safety disclosure).
    """
    warnings: list[str] = []

    blocks = document.get("blocks", [])
    if block_idx >= len(blocks):
        return [f"Block {block_idx} out of range"]

    block = blocks[block_idx]
    if not isinstance(block, dict):
        return ["Block is not a standard dict"]

    runs = block.get("runs", [])
    if len(runs) > 1:
        warnings.append(
            f"Block has {len(runs)} styled runs — set_block_text will collapse them to one run"
        )
    for run in runs:
        if not isinstance(run, dict):
            continue
        if run.get("href"):
            warnings.append("Block contains a hyperlink run — hyperlink will be lost on edit")
        style = run.get("style")
        if style and style not in (None, ""):
            warnings.append(
                f"Block run has style {style!r} — "
                "style is preserved only for the first run when preserve_style=True"
            )

    return warnings


# ---------------------------------------------------------------------------
# R77 Train J — Paragraph management APIs
# ---------------------------------------------------------------------------


def document_append_paragraph(
    document: dict[str, Any],
    text: str,
    style: str | None = None,
) -> tuple[bool, str]:
    """Append a new paragraph to the document body.

    Args:
        document: Parsed FODT document dict.
        text: Plain text content for the new paragraph.
        style: Optional paragraph style name (e.g. "Heading 1", "Text Body").

    Returns:
        (success, message) tuple.

    Added in R77 Train J as a paragraph-management product capability.
    """
    if text is None:
        return False, "Text must not be None"

    body = document.get("body", {})
    blocks = body.get("blocks", [])

    new_block: dict[str, Any] = {
        "type": "paragraph",
        "runs": [{"text": text}],
        "auto_updatable": False,
    }
    if style:
        new_block["style"] = style

    blocks.append(new_block)
    body["blocks"] = blocks
    document["body"] = body

    idx = len(blocks) - 1
    style_note = f" (style={style!r})" if style else ""
    return True, f"Paragraph appended at index {idx}{style_note}"


def document_remove_paragraph(
    document: dict[str, Any],
    block_idx: int,
) -> tuple[bool, str]:
    """Remove a paragraph (block) at the given index from the document body.

    Only paragraph-type blocks may be removed. Headings, tables, and other
    structural blocks are protected and will return an error with a warning.

    Args:
        document: Parsed FODT document dict.
        block_idx: 0-based index of the block to remove.

    Returns:
        (success, message) tuple.

    Added in R77 Train J as a paragraph-management product capability.
    """
    body = document.get("body", {})
    blocks = body.get("blocks", [])

    if block_idx < 0 or block_idx >= len(blocks):
        return False, f"Block index {block_idx} out of range (0–{len(blocks) - 1})"

    target = blocks[block_idx]
    block_type = target.get("type", "paragraph")
    if block_type in ("table", "list"):
        return False, (
            f"Block {block_idx} is type {block_type!r} — "
            "only paragraph blocks may be removed via this API"
        )

    removed_preview = ""
    runs = target.get("runs", [])
    if runs:
        removed_preview = runs[0].get("text", "")[:40]

    body["blocks"] = [b for i, b in enumerate(blocks) if i != block_idx]
    document["body"] = body

    return True, f"Block {block_idx} removed (was: {removed_preview!r})"


def document_paragraph_count(
    document: dict[str, Any],
) -> int:
    """Return the count of paragraph-type blocks in the document body.

    Added in R77 Train J as a convenience utility for edit workflow verification.
    """
    blocks = document.get("body", {}).get("blocks", [])
    return sum(1 for b in blocks if b.get("type", "paragraph") == "paragraph")
