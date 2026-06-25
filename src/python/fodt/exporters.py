"""FODT export targets for format-factory-fodt (HO-RC003-FODT-EXPORT).

Provides Python parity with .NET FodtTxtExporter, FodtMarkdownExporter, FodtHtmlExporter.

Public API:
  fodt_to_txt(path_or_model)      — plain text extraction
  fodt_to_markdown(path_or_model) — Markdown output (headings + paragraphs + lists)
  fodt_to_html(path_or_model)     — HTML output (<h1-6>, <p>, <ul>)

Each function accepts either a file path (str|Path) or the neutral model dict
returned by parse_fodt_strict().

Gap closure: GAP-INV-038 (FODT Python missing export targets)
"""

from __future__ import annotations

import html as _html
from pathlib import Path
from typing import Any


def _load(path_or_model: "str | Path | dict[str, Any]") -> dict[str, Any]:
    """Accept a path or pre-loaded neutral model dict."""
    if isinstance(path_or_model, dict):
        return path_or_model
    from .parser import parse_fodt_strict
    return parse_fodt_strict(path_or_model)


def _iter_blocks(model: dict[str, Any]):
    """Iterate content blocks from the neutral model in document order."""
    for item in model.get("content", []):
        if item.get("kind") == "block":
            yield item["data"]
    # also handle legacy 'blocks' key
    for block in model.get("blocks", []):
        yield block


def fodt_to_txt(path_or_model: "str | Path | dict[str, Any]") -> str:
    """Extract plain text from a FODT document.

    Headings and paragraphs are separated by newlines.
    List items are prefixed with '- '.

    Returns:
        Plain text string.
    """
    model = _load(path_or_model)
    lines: list[str] = []
    for block in _iter_blocks(model):
        btype = block.get("type", "")
        text = block.get("text", "").strip()
        if not text:
            continue
        if btype in ("heading", "paragraph"):
            lines.append(text)
        elif btype == "list_item":
            lines.append(f"- {text}")
    return "\n".join(lines)


def fodt_to_markdown(path_or_model: "str | Path | dict[str, Any]") -> str:
    """Convert a FODT document to Markdown.

    Mapping:
      heading (level N) → '#' * N + ' ' + text
      paragraph         → text
      list_item         → '- ' + text

    Returns:
        Markdown-formatted string.
    """
    model = _load(path_or_model)
    parts: list[str] = []
    for block in _iter_blocks(model):
        btype = block.get("type", "")
        text = block.get("text", "").strip()
        if not text:
            continue
        if btype == "heading":
            level = int(block.get("heading_level") or 1)
            level = max(1, min(6, level))
            parts.append(f"{'#' * level} {text}")
        elif btype == "paragraph":
            parts.append(text)
        elif btype == "list_item":
            parts.append(f"- {text}")
    return "\n\n".join(parts)


def fodt_to_html(path_or_model: "str | Path | dict[str, Any]") -> str:
    """Convert a FODT document to HTML.

    Mapping:
      heading (level N) → <h{N}>text</h{N}>
      paragraph         → <p>text</p>
      list_item         → wrapped in <ul><li>text</li></ul>

    Returns:
        HTML string (no <html>/<body> wrapper — fragment only).
    """
    model = _load(path_or_model)
    parts: list[str] = []
    pending_list_items: list[str] = []

    def flush_list():
        if pending_list_items:
            items = "".join(f"<li>{item}</li>" for item in pending_list_items)
            parts.append(f"<ul>{items}</ul>")
            pending_list_items.clear()

    for block in _iter_blocks(model):
        btype = block.get("type", "")
        text = _html.escape(block.get("text", "").strip())
        if not text:
            continue
        if btype == "heading":
            flush_list()
            level = int(block.get("heading_level") or 1)
            level = max(1, min(6, level))
            parts.append(f"<h{level}>{text}</h{level}>")
        elif btype == "paragraph":
            flush_list()
            parts.append(f"<p>{text}</p>")
        elif btype == "list_item":
            pending_list_items.append(text)

    flush_list()
    return "\n".join(parts)
