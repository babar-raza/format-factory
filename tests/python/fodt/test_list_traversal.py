"""
test_list_traversal.py -- Tests for iterative list traversal (IR-FODT-003).

Verifies that collect_list_items() correctly traverses list structures
without recursion, handles deep nesting (Gate 7 TC-7 requirement), and
maintains document order.

Gate 8 TC-7: PARTIALLY_MITIGATED in prototype (recursive). This module
verifies the product source resolves TC-7 fully.
"""
import xml.etree.ElementTree as ET


from fodt.list_traversal import collect_list_items
from fodt.constants import NS_TEXT


def _build_list_xml(*items, ns=NS_TEXT) -> ET.Element:
    """Build a text:list element with given item texts."""
    list_elem = ET.Element(f"{{{ns}}}list")
    for text in items:
        li = ET.SubElement(list_elem, f"{{{ns}}}list-item")
        p = ET.SubElement(li, f"{{{ns}}}p")
        p.text = text
    return list_elem


def _build_nested_list_xml(ns=NS_TEXT) -> ET.Element:
    """Build a 2-level nested list: [Item1 -> [Nested1.1, Nested1.2], Item2]."""
    list_elem = ET.Element(f"{{{ns}}}list")
    li1 = ET.SubElement(list_elem, f"{{{ns}}}list-item")
    p1 = ET.SubElement(li1, f"{{{ns}}}p")
    p1.text = "Item1"
    nested = ET.SubElement(li1, f"{{{ns}}}list")
    nested_li1 = ET.SubElement(nested, f"{{{ns}}}list-item")
    ET.SubElement(nested_li1, f"{{{ns}}}p").text = "Nested1.1"
    nested_li2 = ET.SubElement(nested, f"{{{ns}}}list-item")
    ET.SubElement(nested_li2, f"{{{ns}}}p").text = "Nested1.2"
    li2 = ET.SubElement(list_elem, f"{{{ns}}}list-item")
    ET.SubElement(li2, f"{{{ns}}}p").text = "Item2"
    return list_elem


def _build_deep_list_xml(depth: int, ns=NS_TEXT) -> ET.Element:
    """Build a singly-nested list of the given depth."""
    root_list = ET.Element(f"{{{ns}}}list")
    current = root_list
    for i in range(depth):
        li = ET.SubElement(current, f"{{{ns}}}list-item")
        ET.SubElement(li, f"{{{ns}}}p").text = f"Level{i + 1}"
        if i < depth - 1:
            current = ET.SubElement(li, f"{{{ns}}}list")
    return root_list


# ---------------------------------------------------------------------------
# Basic collection
# ---------------------------------------------------------------------------

def test_empty_list():
    list_elem = ET.Element(f"{{{NS_TEXT}}}list")
    items = collect_list_items(list_elem)
    assert items == []


def test_single_item():
    list_elem = _build_list_xml("Hello")
    items = collect_list_items(list_elem)
    assert len(items) == 1
    assert items[0]["text"] == "Hello"
    assert items[0]["level"] == 1


def test_multiple_items():
    list_elem = _build_list_xml("Alpha", "Beta", "Gamma")
    items = collect_list_items(list_elem)
    assert len(items) == 3
    assert [i["text"] for i in items] == ["Alpha", "Beta", "Gamma"]


def test_all_items_at_level_1():
    list_elem = _build_list_xml("A", "B", "C")
    items = collect_list_items(list_elem)
    for item in items:
        assert item["level"] == 1


def test_returns_list_of_dicts():
    list_elem = _build_list_xml("X")
    items = collect_list_items(list_elem)
    assert isinstance(items, list)
    assert isinstance(items[0], dict)


# ---------------------------------------------------------------------------
# Nested list traversal
# ---------------------------------------------------------------------------

def test_nested_list_item_count():
    list_elem = _build_nested_list_xml()
    items = collect_list_items(list_elem)
    # Item1 + Nested1.1 + Nested1.2 + Item2 = 4 items
    assert len(items) == 4


def test_nested_list_document_order():
    list_elem = _build_nested_list_xml()
    items = collect_list_items(list_elem)
    texts = [i["text"] for i in items]
    # Document order: Item1, Nested1.1, Nested1.2, Item2
    assert texts[0] == "Item1"
    assert texts[-1] == "Item2"
    # Nested items appear after their parent
    item1_idx = texts.index("Item1")
    nested_idx = texts.index("Nested1.1")
    assert nested_idx > item1_idx


def test_nested_list_levels():
    list_elem = _build_nested_list_xml()
    items = collect_list_items(list_elem)
    levels = {i["text"]: i["level"] for i in items}
    assert levels["Item1"] == 1
    assert levels["Nested1.1"] == 2
    assert levels["Nested1.2"] == 2
    assert levels["Item2"] == 1


# ---------------------------------------------------------------------------
# Deep nesting — no RecursionError (IR-FODT-003, Gate 8 TC-7)
# ---------------------------------------------------------------------------

def test_deep_nesting_50_levels_no_crash():
    """50-level deep nesting must not cause RecursionError (TC-7 requirement)."""
    list_elem = _build_deep_list_xml(50)
    items = collect_list_items(list_elem)
    assert len(items) == 50


def test_deep_nesting_100_levels_no_crash():
    """100-level deep nesting must not cause RecursionError."""
    list_elem = _build_deep_list_xml(100)
    items = collect_list_items(list_elem)
    assert len(items) == 100


def test_deep_nesting_1000_levels_no_crash():
    """1000-level deep nesting must not cause RecursionError."""
    list_elem = _build_deep_list_xml(1000)
    items = collect_list_items(list_elem)
    assert len(items) == 1000


def test_deep_nesting_levels_correct():
    """Items at each depth level have correct level values."""
    list_elem = _build_deep_list_xml(10)
    items = collect_list_items(list_elem)
    for i, item in enumerate(items):
        assert item["level"] == i + 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_item_with_empty_text():
    list_elem = ET.Element(f"{{{NS_TEXT}}}list")
    li = ET.SubElement(list_elem, f"{{{NS_TEXT}}}list-item")
    ET.SubElement(li, f"{{{NS_TEXT}}}p")  # no text
    items = collect_list_items(list_elem)
    assert len(items) == 1
    assert items[0]["text"] == ""


def test_item_with_multiple_paragraphs():
    list_elem = ET.Element(f"{{{NS_TEXT}}}list")
    li = ET.SubElement(list_elem, f"{{{NS_TEXT}}}list-item")
    p1 = ET.SubElement(li, f"{{{NS_TEXT}}}p")
    p1.text = "Part one"
    p2 = ET.SubElement(li, f"{{{NS_TEXT}}}p")
    p2.text = "Part two"
    items = collect_list_items(list_elem)
    assert len(items) == 1
    # Both paragraphs contribute to the item text
    assert "Part one" in items[0]["text"]
    assert "Part two" in items[0]["text"]


def test_list_item_without_paragraph():
    list_elem = ET.Element(f"{{{NS_TEXT}}}list")
    li = ET.SubElement(list_elem, f"{{{NS_TEXT}}}list-item")
    # No text:p child — item should still be returned with empty text
    items = collect_list_items(list_elem)
    assert len(items) == 1
    assert items[0]["text"] == ""
    assert items[0]["level"] == 1
