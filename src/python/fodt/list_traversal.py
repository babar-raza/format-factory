"""
list_traversal.py -- Iterative list item collection for format-factory-fodt.

Implements IR-FODT-003: replace recursive _collect_list_items() from the
Gate 4 prototype with an iterative implementation safe for deeply nested
FODT list structures (Gate 7 fixture c03: deep nesting).

Gate 8 TC-7 identified the recursive prototype as PARTIALLY_MITIGATED.
This module resolves TC-7 for product source.

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .constants import QN_LIST, QN_LIST_ITEM, QN_TEXT_P, QN_TEXT_SPAN

if TYPE_CHECKING:
    pass


def collect_list_items(list_elem: Any) -> "list[dict[str, Any]]":
    """Iteratively collect all list items from a text:list element (DFS).

    Replaces the recursive _collect_list_items() from the Gate 4 prototype.
    Uses an explicit stack to perform depth-first traversal, maintaining
    document order without risk of RecursionError on deeply nested lists.

    Args:
        list_elem: A completed text:list element (from iterparse "end" event).

    Returns:
        List of dicts with keys:
          - "text" (str): concatenated text content of the list item
          - "level" (int): nesting depth, 1-based (1 = top-level item)

    IR-FODT-003, IR-FODT-006. Gate 8 TC-7 resolution.
    Spec citation: ODF 1.3 Part 3, section 5.5 (text:list, text:list-item).
    """
    items: list[dict[str, Any]] = []

    # Stack of (list_item_element, level) for DFS traversal.
    # Seed: all list-items in the root text:list, level=1.
    # Items are pushed in reverse order so the first item in the list
    # is processed first (stack pops from the right).
    stack: list[tuple[Any, int]] = []

    root_children = [li for li in list_elem if li.tag == QN_LIST_ITEM]
    for li in reversed(root_children):
        stack.append((li, 1))

    while stack:
        li_elem, level = stack.pop()

        text_parts: list[str] = []
        nested_lists: list[Any] = []

        for child in li_elem:
            if child.tag == QN_TEXT_P:
                text_parts.append(_collect_text(child))
            elif child.tag == QN_LIST:
                nested_lists.append(child)

        text = " ".join(t for t in text_parts if t).strip()
        items.append({"text": text, "level": level})

        # Push nested list items in reverse order so the first nested item
        # is processed immediately after the current item (DFS document order).
        for nested in reversed(nested_lists):
            nested_children = [li for li in nested if li.tag == QN_LIST_ITEM]
            for li in reversed(nested_children):
                stack.append((li, level + 1))

    return items


def _collect_text(elem: Any) -> str:
    """Collect all text content from an element and its descendants."""
    parts: list[str] = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        if child.tag == QN_TEXT_SPAN:
            parts.append(_collect_text(child))
        elif child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)
