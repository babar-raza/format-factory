"""FODT document query — read-only derived analytics on the neutral model.

Pure-query functions that inspect the neutral model produced by build_document().
These functions do not perform I/O or mutation — they return scalar/bool/list
summaries from in-memory document dicts.

spec_concept: ODF 1.3 text document block/table/list derived query
"""
from __future__ import annotations

from typing import Any


def document_total_words(document: dict[str, Any]) -> int:
    """Return the total word count across all text blocks in the document.

    Words are counted by splitting on whitespace in each paragraph and
    heading block's text field. Simpler than document_word_count (which
    returns a breakdown dict), this returns just the integer total.

    Args:
        document: Parsed FODT document dict.

    Returns:
        Total word count. Returns 0 for empty documents.
    """
    count = 0
    for block in document.get("blocks", []):
        text = block.get("text", "")
        if isinstance(text, str):
            count += len(text.split())
    return count




def document_list_item_count(document: dict[str, Any]) -> int:
    """Return the total number of list items across all lists in the document.

    Counts every item in every list (including nested items at any level).

    Args:
        document: Parsed FODT document dict.

    Returns:
        Total list item count. Returns 0 for documents with no lists.
    """
    total = 0
    for lst in document.get("lists", []):
        total += len(lst.get("items", []))
    return total




def document_block_type_count(document: dict[str, Any]) -> dict[str, int]:
    """Return a count of blocks grouped by their type.

    Args:
        document: Parsed FODT document dict.

    Returns:
        Dict mapping block type string (e.g. 'paragraph', 'heading') to count.
        Returns empty dict for documents with no blocks.
    """
    counts: dict[str, int] = {}
    for block in document.get("blocks", []):
        block_type = block.get("type", "unknown")
        counts[block_type] = counts.get(block_type, 0) + 1
    return counts




def document_max_paragraph_length(document: dict[str, Any]) -> int:
    """Return the character length of the longest paragraph block.

    Iterates over all blocks of type 'paragraph' and returns the maximum
    text length. Heading blocks are excluded.

    Args:
        document: Parsed FODT document dict.

    Returns:
        Integer length of the longest paragraph text. Returns 0 if no
        paragraph blocks exist.
    """
    max_len = 0
    for block in document.get("blocks", []):
        if block.get("type") == "paragraph":
            text = block.get("text", "")
            if len(text) > max_len:
                max_len = len(text)
    return max_len




def document_has_tables(document: dict[str, Any]) -> bool:
    """Return True if the document contains at least one table.

    Checks the top-level 'tables' list in the document neutral model.

    Args:
        document: Parsed FODT document dict.

    Returns:
        True if the document has one or more tables, False otherwise.
    """
    return len(document.get("tables", [])) > 0


# Closes gaps: GAP-FODT-FOSS-PARAGRAPH_TE-001, GAP-FODT-FOSS-HEADING_TE-001,
#              GAP-FODT-COMM-TABLE_ROW_CO-001
# ---------------------------------------------------------------------------

def document_paragraph_texts(document: dict[str, Any]) -> list[str]:
    """Return a list of text strings for every paragraph block in the document.

    Only paragraph-type blocks are included (headings are excluded).
    Uses the content list (document order) if present; otherwise falls back
    to the top-level blocks list.

    Args:
        document: Parsed FODT document dict.

    Returns:
        List of paragraph text strings (may be empty strings for blank paragraphs).
    """
    result: list[str] = []
    content = document.get("content", [])
    if content:
        blocks = [item["data"] for item in content if item.get("kind") == "block"]
    else:
        blocks = document.get("blocks", [])
    for block in blocks:
        if block.get("type") == "paragraph":
            runs = block.get("runs", [])
            if runs:
                text = "".join(r.get("text", "") or "" for r in runs)
            else:
                text = block.get("text", "") or ""
            result.append(text)
    return result




def document_heading_texts(document: dict[str, Any]) -> list[str]:
    """Return a list of text strings for every heading block in document order.

    Only heading-type blocks are included (paragraphs are excluded).
    Uses the content list (document order) if present; otherwise falls back
    to the top-level blocks list.

    Args:
        document: Parsed FODT document dict.

    Returns:
        List of heading text strings in document order.
    """
    result: list[str] = []
    content = document.get("content", [])
    if content:
        blocks = [item["data"] for item in content if item.get("kind") == "block"]
    else:
        blocks = document.get("blocks", [])
    for block in blocks:
        if block.get("type") == "heading":
            runs = block.get("runs", [])
            if runs:
                text = "".join(r.get("text", "") or "" for r in runs)
            else:
                text = block.get("text", "") or ""
            result.append(text)
    return result




def document_table_row_count(document: dict[str, Any], table_index: int = 0) -> int:
    """Return the number of rows in the specified table.

    Args:
        document:    Parsed FODT document dict.
        table_index: 0-based index into the document's table list.

    Returns:
        Row count for the table at table_index, or 0 if the index is out of range.
    """
    content = document.get("content", [])
    if content:
        tables = [item["data"] for item in content if item.get("kind") == "table"]
    else:
        tables = document.get("tables", [])
    if table_index < 0 or table_index >= len(tables):
        return 0
    return len(tables[table_index].get("rows", []))


# ---------------------------------------------------------------------------
# Empty paragraph count (product-healing pilot)
# ---------------------------------------------------------------------------

def document_empty_paragraph_count(document: dict[str, Any]) -> int:
    """Return the count of empty paragraph blocks in the document.

    A paragraph is considered empty if it has no runs, or all its runs
    have empty or whitespace-only text.
    """
    count = 0
    for block in document.get("blocks", []):
        if block.get("type", "paragraph") != "paragraph":
            continue
        runs = block.get("runs", [])
        if not runs:
            count += 1
        elif all(not (r.get("text") or "").strip() for r in runs):
            count += 1
    return count




def fodt_total_block_count(document: dict[str, Any]) -> int:
    """Return the total number of top-level blocks in the document.

    Counts all entries in the blocks list (paragraphs, headings)
    plus all entries in the lists and tables lists.
    """
    blocks = len(document.get("blocks", []))
    lists = len(document.get("lists", []))
    tables = len(document.get("tables", []))
    return blocks + lists + tables
