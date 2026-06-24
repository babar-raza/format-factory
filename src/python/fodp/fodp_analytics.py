"""
FODP analytics -- pure functions extracted from fodp_codec.py.
"""
from __future__ import annotations

import re
from typing import Any

from .fodp_codec import load, get_page_count, NS, _parse_xml, _read_source


def fodp_total_text_length(source: "str | bytes | Path") -> int:
    """Return total character count across all slides' text content."""
    doc = load(source)
    total = 0
    for pg in doc.get("pages", []):
        for text in pg.get("text_content", []):
            total += len(text)
    return total


def fodp_slide_count(source: "str | bytes | Path") -> int:
    """Return the number of slides (pages) in a FODP presentation."""
    return get_page_count(source)


def fodp_slide_shape_counts(source: "str | bytes | Path") -> list[int]:
    """Return a list of shape counts, one per slide."""
    model = load(source)
    return [p["shape_count"] for p in model.get("pages", [])]


def fodp_total_shape_count(source: "str | bytes | Path") -> int:
    """Return the total number of shapes across all slides."""
    return sum(fodp_slide_shape_counts(source))


def fodp_notes_text(source: "str | bytes | Path") -> list[str]:
    """Return presentation notes text, one string per slide.

    Extracts text from ``presentation:notes`` elements within each
    ``draw:page``.  Slides without notes produce an empty string.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        List of notes strings in slide order.
    """
    xml_bytes = _read_source(source)
    root = _parse_xml(xml_bytes)
    notes: list[str] = []
    ns_pres = NS["presentation"]
    ns_draw = NS["draw"]
    ns_text = NS["text"]
    for page in root.iter(f"{{{ns_draw}}}page"):
        page_notes_parts: list[str] = []
        for notes_elem in page.findall(f"{{{ns_pres}}}notes"):
            for tp in notes_elem.iter(f"{{{ns_text}}}p"):
                t = "".join(tp.itertext()).strip()
                if t:
                    page_notes_parts.append(t)
        notes.append(" ".join(page_notes_parts))
    return notes


def fodp_has_notes(source: "str | bytes | Path") -> bool:
    """Return True if any slide has non-empty presentation notes."""
    return any(n for n in fodp_notes_text(source))


def fodp_slide_titles(source: "str | bytes | Path") -> "list[str | None]":
    """Return a list of slide titles, one per slide.

    Each entry is the title string extracted from the slide's title frame,
    or None if the slide has no title frame.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        List of title strings (or None) in slide order.
    """
    model = load(source)
    return [p.get("title") for p in model.get("pages", [])]


def fodp_image_count(source: "str | bytes | Path") -> int:
    """Return the total number of embedded images across all slides.

    Counts draw:image elements within the presentation body.
    ODF 1.3 §10.4.3.3 — draw:image is the element for embedded bitmap images.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Total count of draw:image elements.
    """
    xml_bytes = _read_source(source)
    root = _parse_xml(xml_bytes)
    image_tag = f"{{{NS['draw']}}}image"
    return sum(1 for _ in root.iter(image_tag))


def fodp_empty_slide_count(source: "str | bytes | Path") -> int:
    """Return the count of slides with zero shapes."""
    counts = fodp_slide_shape_counts(source)
    return sum(1 for c in counts if c == 0)


def fodp_master_page_count(source: "str | bytes | Path") -> int:
    """Return the number of distinct master pages (slide layouts) used.

    Each slide references a master-page-name via draw:master-page-name.
    This function counts how many unique master page names appear across
    all slides in the presentation.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Count of distinct master page names. Returns 0 if no slides exist.
    """
    model = load(source)
    names = {p.get("master_page", "") for p in model.get("pages", [])}
    names.discard("")
    return len(names)


def fodp_text_per_slide(source: "str | bytes | Path") -> list[str]:
    """Return a list of concatenated text content strings, one per slide.

    Each entry is the full text content of that slide (all text frames
    joined by newlines). Empty slides produce an empty string.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        List of text strings in slide order.
    """
    model = load(source)
    result: list[str] = []
    for page in model.get("pages", []):
        text_content = page.get("text_content", [])
        result.append("\n".join(text_content) if text_content else "")
    return result


def fodp_average_shapes_per_slide(source: "str | bytes | Path") -> float:
    """Return the average number of shapes per slide.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Average shape count. Returns 0.0 for empty presentations.
    """
    model = load(source)
    pages = model.get("pages", [])
    if not pages:
        return 0.0
    total = sum(p.get("shape_count", 0) for p in pages)
    return total / len(pages)


def fodp_max_text_per_slide(source: "str | bytes | Path") -> int:
    """Return the length of the longest slide's text content.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Integer character count of the slide with the most text. 0 if empty.
    """
    texts = fodp_text_per_slide(source)
    if not texts:
        return 0
    return max(len(t) for t in texts)


def fodp_has_images(source: "str | bytes | Path") -> bool:
    """Return True if the presentation contains any images.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        True if image_count > 0.
    """
    return fodp_image_count(source) > 0


def fodp_min_text_per_slide(source: "str | bytes | Path") -> int:
    """Return the length of the shortest slide's text content.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Integer character count of the slide with the least text. 0 if no slides.
    """
    texts = fodp_text_per_slide(source)
    if not texts:
        return 0
    return min(len(t) for t in texts)


def fodp_total_notes_length(source: "str | bytes | Path") -> int:
    """Return the total character length of all slide notes combined.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Integer total character count of notes text.
    """
    notes = fodp_notes_text(source)
    return sum(len(n) for n in notes)


def fodp_slide_text_density(source: "str | bytes | Path") -> float:
    """Return the average text character count per slide. 0.0 if no slides."""
    texts = fodp_text_per_slide(source)
    if not texts:
        return 0.0
    return sum(len(t) for t in texts) / len(texts)


def fodp_nonempty_slide_count(source: "str | bytes | Path") -> int:
    """Return the number of slides that contain at least one text character.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Integer count of slides with non-empty text content.
    """
    texts = fodp_text_per_slide(source)
    return sum(1 for t in texts if t.strip())


def fodp_text_to_slide_ratio(source: "str | bytes | Path") -> float:
    """Return the ratio of total text length to slide count.

    Identical to slide_text_density but named for clarity in analytics.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Float ratio. Returns 0.0 if no slides exist.
    """
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    total = fodp_total_text_length(source)
    return total / count


def fodp_all_slides_have_text(source: "str | bytes | Path") -> bool:
    """Return True if every slide has at least some non-empty text."""
    texts = fodp_text_per_slide(source)
    if not texts:
        return False
    return all(t.strip() for t in texts)


def fodp_max_title_length(source: "str | bytes | Path") -> int:
    """Return the length of the longest slide title. 0 if no slides."""
    doc = load(source)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return max((len(pg.get("title", "")) for pg in pages), default=0)


def fodp_average_text_per_slide(source: "str | bytes | Path") -> float:
    """Return the average character count of text per slide."""
    texts = fodp_text_per_slide(source)
    if not texts:
        return 0.0
    return sum(len(t) for t in texts) / len(texts)


def fodp_shape_to_slide_ratio(source: "str | bytes | Path") -> float:
    """Return the ratio of total shapes to slide count."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    total = fodp_total_shape_count(source)
    return total / count


def fodp_notes_to_slide_ratio(source: "str | bytes | Path") -> float:
    """Return the ratio of total notes text length to slide count."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    total = fodp_total_notes_length(source)
    return total / count


def fodp_image_to_slide_ratio(source: "str | bytes | Path") -> float:
    """Return the ratio of image count to slide count."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    return fodp_image_count(source) / count


def fodp_has_empty_slides(source: "str | bytes | Path") -> bool:
    """Return True if any slide has zero text content."""
    return fodp_empty_slide_count(source) > 0


def fodp_title_coverage(source: "str | bytes | Path") -> float:
    """Return the ratio of slides with non-None titles to total slides."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    titles = fodp_slide_titles(source)
    titled = sum(1 for t in titles if t is not None)
    return titled / count


def fodp_is_single_slide(source: "str | bytes | Path") -> bool:
    """Return True if the presentation has exactly one slide."""
    return fodp_slide_count(source) == 1


def fodp_notes_density(source: "str | bytes | Path") -> float:
    """Return total notes length / slide count. 0.0 if no slides."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    return fodp_total_notes_length(source) / count


def fodp_has_titles(source: "str | bytes | Path") -> bool:
    """Return True if any slide has a non-empty title."""
    titles = fodp_slide_titles(source)
    return any(t is not None and t.strip() for t in titles)


def fodp_min_shapes_per_slide(source: "str | bytes | Path") -> int:
    """Return the minimum shape count across all slides. 0 if no slides."""
    counts = fodp_slide_shape_counts(source)
    if not counts:
        return 0
    return min(counts)


def fodp_has_multi_slide(source: "str | bytes | Path") -> bool:
    """Return True if the presentation has more than one slide."""
    return fodp_slide_count(source) > 1


def fodp_max_shapes_per_slide(source: "str | bytes | Path") -> int:
    """Return the maximum shape count across all slides. 0 if no slides."""
    counts = fodp_slide_shape_counts(source)
    if not counts:
        return 0
    return max(counts)


def fodp_avg_notes_length(source: "str | bytes | Path") -> float:
    """Return the average notes text length per slide. 0.0 if no slides."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    return fodp_total_notes_length(source) / count


def fodp_shape_variance(source: "str | bytes | Path") -> int:
    """Return the difference between max and min shapes per slide. 0 if no slides."""
    counts = fodp_slide_shape_counts(source)
    if not counts:
        return 0
    return max(counts) - min(counts)


def fodp_avg_shapes_per_slide(source: "str | bytes | Path") -> float:
    """Return the average shape count per slide. 0.0 if no slides."""
    count = fodp_slide_count(source)
    if count == 0:
        return 0.0
    return sum(fodp_slide_shape_counts(source)) / count


def fodp_max_text_length(source: "str | bytes | Path") -> int:
    """Return the maximum text length on any single slide. 0 if no slides."""
    doc = load(source)
    slides = doc.get("slides", [])
    if not slides:
        return 0
    return max(len(s.get("text", "")) for s in slides)


def fodp_text_length_variance(source: "str | bytes | Path") -> float:
    """Return variance of text lengths across slides. 0.0 if fewer than 2 slides."""
    doc = load(source)
    slides = doc.get("slides", [])
    if len(slides) < 2:
        return 0.0
    lengths = [len(s.get("text", "")) for s in slides]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def fodp_slide_text_lengths(source: "str | bytes | Path") -> list:
    """Return a list of text lengths, one per slide."""
    doc = load(source)
    return [len(s.get("text", "")) for s in doc.get("slides", [])]


def fodp_avg_title_length(source: "str | bytes | Path") -> float:
    """Return average length of slide titles. 0.0 if no titles."""
    titles = fodp_slide_titles(source)
    named = [t for t in titles if t]
    if not named:
        return 0.0
    return sum(len(t) for t in named) / len(named)


def fodp_is_text_heavy(source: "str | bytes | Path") -> bool:
    """Return True if total text length > 500 chars."""
    return fodp_total_text_length(source) > 500


def fodp_max_notes_length(source: "str | bytes | Path") -> int:
    """Return the length of the longest notes text across slides. 0 if no notes."""
    notes = fodp_notes_text(source)
    if not notes:
        return 0
    return max(len(n) for n in notes)


def fodp_slide_count_is_one(source: "str | bytes | Path") -> bool:
    """Return True if the presentation has exactly one slide."""
    return fodp_slide_count(source) == 1


def fodp_is_shape_heavy(source: "str | bytes | Path") -> bool:
    """Return True if the total shape count exceeds the slide count."""
    sc = fodp_slide_count(source)
    if sc == 0:
        return False
    return fodp_total_shape_count(source) > sc


def fodp_has_zero_shapes(source: "str | bytes | Path") -> bool:
    """Return True if the presentation has no shapes at all."""
    return fodp_total_shape_count(source) == 0


def fodp_min_title_length(source: "str | bytes | Path") -> int:
    """Return length of the shortest slide title. 0 if no titles."""
    titles = fodp_slide_titles(source)
    if not titles:
        return 0
    return min(len(t) for t in titles)


def fodp_image_density(source: "str | bytes | Path") -> float:
    """Return images per slide. 0.0 if no slides."""
    sc = fodp_slide_count(source)
    if sc == 0:
        return 0.0
    return fodp_image_count(source) / sc


def fodp_total_text_chars(source: "str | bytes | Path") -> int:
    """Return total character count of all slide text combined."""
    texts = fodp_text_per_slide(source)
    return sum(len(t) for t in texts)


def fodp_avg_title_words(source: "str | bytes | Path") -> float:
    """Return average word count per slide title. 0.0 if no titles."""
    titles = fodp_slide_titles(source)
    if not titles:
        return 0.0
    total = sum(len(t.split()) for t in titles)
    return total / len(titles)


def fodp_avg_text_length(source: "str | bytes | Path") -> float:
    """Return average total text character count per slide. 0.0 if no slides."""
    doc = load(source)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = sum(
        sum(len(t) for t in pg.get("text_content", []))
        for pg in pages
    )
    return total / len(pages)


def fodp_nonempty_slide_ratio(source: "str | bytes | Path") -> float:
    """Return ratio of slides with non-empty text content to total slides. 0.0 if none."""
    doc = load(source)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    nonempty = sum(
        1 for pg in pages
        if any(t.strip() for t in pg.get("text_content", []))
    )
    return nonempty / len(pages)


def fodp_has_numeric_content(source: "str | bytes | Path") -> bool:
    """Return True if any slide contains text with a digit."""
    import re
    doc = load(source)
    for pg in doc.get("pages", []):
        for text in pg.get("text_content", []):
            if re.search(r"\d", text):
                return True
    return False


def fodp_longest_slide_index(source: "str | bytes | Path") -> int:
    """Return 0-based index of the slide with the most total text characters. -1 if none."""
    doc = load(source)
    pages = doc.get("pages", [])
    if not pages:
        return -1
    totals = [sum(len(t) for t in pg.get("text_content", [])) for pg in pages]
    return max(range(len(totals)), key=lambda i: totals[i])


def fodp_avg_sentence_length(source: "str | bytes | Path") -> float:
    """Return average sentence length in characters across all slides. 0.0 if none."""
    import re
    doc = load(source)
    all_text = " ".join(
        t for pg in doc.get("pages", []) for t in pg.get("text_content", [])
    )
    sentences = [s.strip() for s in re.split(r"[.!?]+", all_text) if s.strip()]
    if not sentences:
        return 0.0
    return sum(len(s) for s in sentences) / len(sentences)


def fodp_slide_text_variance(source: "str | bytes | Path") -> float:
    """Return variance of text lengths per slide. 0.0 if fewer than 2 slides."""
    texts = fodp_text_per_slide(source)
    if len(texts) < 2:
        return 0.0
    lengths = [len(t) for t in texts]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def fodp_total_images(source: "str | bytes | Path") -> int:
    """Return total number of images across all slides."""
    return fodp_image_count(source)


def fodp_shortest_slide_index(source: "str | bytes | Path") -> int:
    """Return the index of the slide with the shortest text. -1 if no slides."""
    texts = fodp_text_per_slide(source)
    if not texts:
        return -1
    min_len = min(len(t) for t in texts)
    for i, t in enumerate(texts):
        if len(t) == min_len:
            return i
    return -1


def fodp_shape_count_variance(source: "str | bytes | Path") -> float:
    """Return variance of shape counts per slide. 0.0 if fewer than 2 slides."""
    counts = fodp_slide_shape_counts(source)
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)
