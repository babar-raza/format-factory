"""FODT neutral model operations — document query and inspection functions.

Query functions that analyze the neutral model produced by build_document().
These functions do not perform I/O — they operate on in-memory dicts.
"""
from __future__ import annotations

from .neutral_model import build_document

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




def document_paragraph_count(
    document: dict[str, Any],
) -> int:
    """Return the count of paragraph-type blocks in the document body.

    Added in R77 Train J as a convenience utility for edit workflow verification.
    """
    # R79 Train G: fix GAP-FODT-STRUCT-001 — use root-level doc["blocks"]
    blocks = document.get("blocks", [])
    return sum(1 for b in blocks if b.get("type", "paragraph") == "paragraph")




def document_count_tables(document: dict[str, Any]) -> int:
    """Return the number of table blocks in the document.

    Aligned with ODF 1.3 text content model (FACT-FODT-001).

    Args:
        document: Parsed FODT document dict.

    Returns:
        Integer count of table blocks (type == 'table').
    """
    return sum(1 for block in document.get("blocks", []) if block.get("type") == "table")

