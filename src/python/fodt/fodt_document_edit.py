"""FODT document edit — mutation and derived analytics functions.

Document mutation operations and derived analytics that operate on
the neutral model produced by build_document().
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Document section summary
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
# Document change tracking summary
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


# R77 — Paragraph management APIs
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

    """
    if text is None:
        return False, "Text must not be None"

 # R79 : fix GAP-FODT-STRUCT-001 — use root-level doc["blocks"].
    # Also maintain doc["content"] (authoritative write sequence used by write_fodt).
    blocks = document.get("blocks", [])

    new_block: dict[str, Any] = {
        "type": "paragraph",
        "runs": [{"text": text}],
        "auto_updatable": False,
    }
    if style:
        new_block["style"] = style

    blocks.append(new_block)
    document["blocks"] = blocks

    # Keep content sequence in sync (write_fodt uses content when present)
    content = document.get("content")
    if content is not None:
        content.append({"kind": "block", "data": new_block})

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

    """
 # R79 : fix GAP-FODT-STRUCT-001 — use root-level doc["blocks"].
    # Also maintain doc["content"] (authoritative write sequence used by write_fodt).
    blocks = document.get("blocks", [])

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

    document["blocks"] = [b for i, b in enumerate(blocks) if i != block_idx]

    # Remove from content sequence (by object identity, since parser shares objects)
    content = document.get("content")
    if content is not None:
        document["content"] = [
            item for item in content
            if not (item.get("kind") == "block" and item.get("data") is target)
        ]

    return True, f"Block {block_idx} removed (was: {removed_preview!r})"




def document_to_text(
    document: dict[str, Any],
) -> str:
    """Export document as plain text.

    Returns all paragraph and heading text joined by newlines. Tables are
    rendered as tab-delimited rows. Lists are rendered with a leading dash.
    This is the plain-text complement to document_to_xml() and is useful
    for quick content inspection and export workflows.

    Args:
        document: Parsed FODT document dict.

    Returns:
        Plain text string with one block per line.

    """
    lines = []
    blocks = document.get("blocks", [])
    for block in blocks:
        btype = block.get("type", "paragraph")
        text = block.get("text", "")
        if btype == "heading":
            level = block.get("level", 1)
            prefix = "#" * level + " "
            lines.append(prefix + text)
        elif btype == "table":
            rows = block.get("rows", [])
            for row in rows:
                cells = row.get("cells", [])
                lines.append("\t".join(c.get("text", "") for c in cells))
        elif btype == "list":
            items = block.get("items", [])
            for item in items:
                lines.append("- " + item.get("text", ""))
        else:
            lines.append(text)
    return "\n".join(lines)




def document_get_paragraph_text(
    document: dict[str, Any],
    paragraph_index: int,
) -> str | None:
    """Return the text of a specific paragraph block by index.

    Counts only paragraph-type blocks (not headings, tables, or lists).
    Returns None if the index is out of range.

    This is the read-side complement of document_set_block_text for paragraph
    blocks and is useful for roundtrip verification in installed-package workflows.

    Args:
        document: Parsed FODT document dict.
        paragraph_index: 0-based index among paragraph-type blocks only.

    Returns:
        Paragraph text string, or None if not found.

    """
    blocks = document.get("blocks", [])
    paragraphs = [b for b in blocks if b.get("type", "paragraph") == "paragraph"]
    if paragraph_index < 0 or paragraph_index >= len(paragraphs):
        return None
    return paragraphs[paragraph_index].get("text", "")




def document_search_text(
    document: dict[str, Any],
    query: str,
    case_sensitive: bool = False,
) -> list[dict[str, Any]]:
    """Search for a text query across all blocks in the document.

    Searches paragraph and heading blocks for the query string. Returns a list
    of match dicts, one per block that contains the query.

    Aligned with ODF 1.3 text content model (FACT-FODT-001): text content is
    stored in paragraph (text:p) and heading (text:h) blocks.

    Args:
        document: Parsed FODT document dict.
        query: Text to search for.
        case_sensitive: If True, match is case-sensitive. Default False.

    Returns:
        List of match dicts, each containing:
            block_index (int): 0-based index in the blocks list.
            block_type (str): "paragraph" or "heading".
            text (str): Full text of the matching block.
            match_count (int): Number of times query appears in this block.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-PROGRESS-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
    as FODT product feature advancement (authority: P4, FACT-FODT-001).
    """
    if not query:
        return []

    blocks = document.get("blocks", [])
    compare_query = query if case_sensitive else query.lower()
    matches: list[dict[str, Any]] = []

    for idx, block in enumerate(blocks):
        block_type = block.get("type", "paragraph")
        if block_type not in ("paragraph", "heading"):
            continue
        text = block.get("text", "")
        compare_text = text if case_sensitive else text.lower()
        count = compare_text.count(compare_query)
        if count > 0:
            matches.append({
                "block_index": idx,
                "block_type": block_type,
                "text": text,
                "match_count": count,
            })

    return matches




def document_replace_text(
    document: dict[str, Any],
    search: str,
    replacement: str,
    case_sensitive: bool = False,
) -> dict[str, Any]:
    """Replace all occurrences of search text with replacement in all blocks.

    Modifies paragraph and heading blocks in-place.

    Args:
        document: Parsed FODT document dict.
        search: Text to search for.
        replacement: Text to replace with.
        case_sensitive: If True, match is case-sensitive. Default False.

    Returns:
        Result dict with total_replacements and blocks_modified.
    """
    if not search:
        return {"total_replacements": 0, "blocks_modified": 0}

    blocks = document.get("blocks", [])
    total = 0
    modified = 0

    for block in blocks:
        block_type = block.get("type", "paragraph")
        if block_type not in ("paragraph", "heading"):
            continue
        text = block.get("text", "")
        if case_sensitive:
            count = text.count(search)
            if count > 0:
                block["text"] = text.replace(search, replacement)
                total += count
                modified += 1
        else:
            # Case-insensitive replace
            lower_text = text.lower()
            lower_search = search.lower()
            count = lower_text.count(lower_search)
            if count > 0:
                # Build result preserving case of non-matching parts
                result = []
                i = 0
                while i < len(text):
                    if lower_text[i:i + len(search)] == lower_search:
                        result.append(replacement)
                        i += len(search)
                    else:
                        result.append(text[i])
                        i += 1
                block["text"] = "".join(result)
                total += count
                modified += 1

    return {"total_replacements": total, "blocks_modified": modified}




def document_to_html(document: dict[str, Any]) -> str:
    """Convert a FODT document to a simple HTML string.

    Converts paragraphs to <p> and headings to <h1>-<h6> tags.
    Special characters are HTML-escaped.

    Args:
        document: Parsed FODT document dict.

    Returns:
        HTML string.
    """
    from html import escape
    parts: list[str] = ["<!DOCTYPE html>", "<html>", "<head><meta charset=\"utf-8\"></head>", "<body>"]

    for block in document.get("blocks", []):
        text = escape(block.get("text", ""))
        btype = block.get("type", "paragraph")
        if btype == "heading":
            level = block.get("level", 1)
            level = max(1, min(6, level))
            parts.append(f"<h{level}>{text}</h{level}>")
        elif btype == "paragraph":
            parts.append(f"<p>{text}</p>")

    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)




def document_extract_headings(
    document: dict[str, Any],
    min_level: int = 1,
    max_level: int = 6,
) -> list[dict[str, Any]]:
    """Extract all heading blocks from the document in document order.

    Returns headings filtered by level range. Useful for building a table of
    contents or understanding document structure.

    Aligned with ODF 1.3 text heading model (FACT-FODT-001): headings are
    stored as text:h elements with a text:outline-level attribute.

    Args:
        document: Parsed FODT document dict.
        min_level: Minimum heading level to include (inclusive). Default 1.
        max_level: Maximum heading level to include (inclusive). Default 6.

    Returns:
        List of heading dicts, each containing:
            block_index (int): 0-based index in the blocks list.
            level (int): Heading level (1=H1, 2=H2, etc.).
            text (str): Heading text.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
    (authority: P5, FACT-FODT-001).
    """
    headings: list[dict[str, Any]] = []
    for idx, block in enumerate(document.get("blocks", [])):
        if block.get("type") != "heading":
            continue
        level = block.get("level", 1)
        if min_level <= level <= max_level:
            headings.append({
                "block_index": idx,
                "level": level,
                "text": block.get("text", ""),
            })
    return headings


