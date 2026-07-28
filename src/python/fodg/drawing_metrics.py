"""FODG drawing metrics — derived analytics and comparison functions.

Boolean/comparison/variance analytics for ODF Drawing documents.
These functions derive metrics from already-computed primary counts.

spec_concept: ODF Drawing page/shape/text-item derived metrics
"""
from __future__ import annotations

from pathlib import Path

from .fodg_codec import load
from .drawing_document import (
    fodg_non_text_shape_count,
    fodg_page_count,
    fodg_text_item_count,
    fodg_total_shape_count,
)




def fodg_shapes_exceed_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count exceeds the number of pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    return total_shapes > len(pages)




def fodg_word_count(file_path: "str | bytes | Path") -> int:
    """Return total word count across all text items in the drawing

    Spec: ODF 1.3 office:document root element (SAL-FODG-00030)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    total = 0
    for page in pages:
        for item in page.get("text_items", []):
            total += len(item.split())
    return total




def fodg_shape_text_ratio(file_path: "str | bytes | Path") -> float:
    """Return the ratio of shapes with text to total shapes. 0.0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    if total_shapes == 0:
        return 0.0
    text_count = sum(len(p.get("text_items", [])) for p in pages)
    return min(1.0, text_count / total_shapes)




def fodg_unique_word_count(file_path: "str | bytes | Path") -> int:
    """Return the number of unique words across all text items

    Spec: ODF 1.3 office:document root element (SAL-FODG-00030)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    words = set()
    for page in pages:
        for item in page.get("text_items", []):
            words.update(item.lower().split())
    return len(words)




def fodg_text_and_shape_sum(file_path: "str | bytes | Path") -> int:
    """Return sum of text item count and total shape count

    Spec: ODF 1.3 office:document root element (SAL-FODG-00030)
    """
    return fodg_text_item_count(file_path) + fodg_total_shape_count(file_path)




def fodg_text_items_exceed_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count strictly exceeds page count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)




def fodg_text_item_length_range(file_path: "str | bytes | Path") -> int:
    """Return range (max minus min) of text item lengths. 0 if fewer than 2 items

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    if len(lengths) < 2:
        return 0
    return max(lengths) - min(lengths)




def fodg_text_items_per_shape(file_path: "str | bytes | Path") -> float:
    """Return average text items per shape. 0.0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    if total_shapes == 0:
        return 0.0
    text_items = sum(len(p.get("text_content", [])) for p in pages)
    return text_items / total_shapes




def fodg_shape_count_exceeds_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)




def fodg_has_equal_shapes_and_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)




def fodg_shape_count_equals_page_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals page count

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == fodg_page_count(file_path)




def fodg_non_text_shape_count_exceeds_page_count(file_path: "str | bytes | Path") -> bool:
    """Return True if non-text shape count strictly exceeds page count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_non_text_shape_count(file_path) > fodg_page_count(file_path)




def fodg_text_item_length_sum(file_path: "str | bytes | Path") -> int:
    """Return sum of character lengths of all text_content items across all pages. 0 if none

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    doc = load(file_path)
    return sum(len(t) for p in doc.get("pages", []) for t in p.get("text_content", []))




def fodg_has_more_shapes_than_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)



def fodg_has_exactly_one_text_item(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is exactly one

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) == 1



def fodg_has_no_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if there are no text items in the document

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) == 0



def fodg_has_at_least_two_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is at least two

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) >= 2



def fodg_has_exactly_three_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is exactly three

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == 3



def fodg_has_exactly_two_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is exactly two

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) == 2



def fodg_has_at_least_one_text_item(file_path: "str | bytes | Path") -> bool:
    """Return True if there is at least one text item

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) >= 1



def fodg_has_more_text_than_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count strictly exceeds page count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)



def fodg_has_more_shapes_than_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)



def fodg_has_at_least_two_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if there are at least two text items

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) >= 2



def fodg_has_only_one_shape(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has exactly one shape across all pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == 1



def fodg_has_more_pages_than_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if page count exceeds total shape count

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_page_count(file_path) > fodg_total_shape_count(file_path)



def fodg_has_at_least_three_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has at least three shapes across all pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) >= 3



def fodg_is_single_shape_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has exactly one shape

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == 1



def fodg_page_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals total shape count

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_page_count(file_path) == fodg_total_shape_count(file_path)



def fodg_has_zero_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has no text items

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) == 0



def fodg_text_count_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals shape count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) == fodg_total_shape_count(file_path)



def fodg_text_count_is_positive(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is greater than zero

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) > 0



def fodg_shape_count_is_three(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals 3

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == 3



def fodg_text_count_is_two(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals 2

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) == 2



def fodg_page_count_equals_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals text item count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_page_count(file_path) == fodg_text_item_count(file_path)



def fodg_shape_count_is_one(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals one

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == 1



def fodg_page_count_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals total shape count

    Spec: ODF 1.3 draw:custom-shape child of draw:page (SAL-FODG-00002)
    """
    return fodg_page_count(file_path) == fodg_total_shape_count(file_path)



def fodg_shape_count_equals_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)



def fodg_text_count_not_equal_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is not equal to total shape count

    Spec: ODF 1.3 draw:text-box child of draw:page (SAL-FODG-00002)
    """
    return fodg_text_item_count(file_path) != fodg_total_shape_count(file_path)



def fodg_shape_count_not_equal_text_count(file_path):
    """Return True if total shape count does not equal text item count.

    Spec: ODF 1.3 draw:custom-shape and draw:text-box counts compared (SAL-FODG-00002)
    """
    return fodg_total_shape_count(file_path) != fodg_text_item_count(file_path)



def fodg_is_text_heavy(file_path: "str | Path") -> bool:
    """Return True if text items exceed half of total shapes

    Spec: ODF 1.3 office:document root element (SAL-FODG-00030)
    """
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return False
    return fodg_text_item_count(file_path) > sc / 2

