"""
FODG FOSS gap closure tests.

Closes:
  GAP-FODG-FOSS-FODG_SHAPES_-001  — fodg_shapes_with_text_count
  GAP-FODG-FOSS-FODG_HAS_NO_-001  — fodg_has_no_shapes
  GAP-FODG-FOSS-FODG_FILE_SI-001  — fodg_file_size_bytes
  GAP-FODG-FOSS-FODG_MIN_TEX-001  — fodg_min_text_item_length
  GAP-FODG-FOSS-FODG_UNIQUE_-001  — fodg_unique_text_item_count
  GAP-FODG-FOSS-FODG_TEXT_IT-001  — fodg_text_item_count
  GAP-FODG-FOSS-FODG_WORD_CO-001  — fodg_word_count
  GAP-FODG-FOSS-FODG_TEXT_AN-001  — fodg_text_and_shape_sum
  GAP-FODG-FOSS-FODG_HAS_EQU-001  — fodg_has_equal_shapes_and_text
  GAP-FODG-FOSS-FODG_PAGE_CO-001  — fodg_page_count_plus_shape_count
  GAP-FODG-FOSS-FODG_SHAPE_P-001  — fodg_shape_plus_text_plus_page_count
  GAP-FODG-FOSS-FODG_HAS_MOR-001  — fodg_has_more_shapes_than_text_items
  GAP-FODG-FOSS-FODG_HAS_EXA-001  — fodg_has_exactly_one_text_item
  GAP-FODG-FOSS-FODG_HAS_AT_-001  — fodg_has_at_least_two_shapes
  GAP-FODG-FOSS-FODG_TEXT_CO-001  — fodg_text_count_plus_page_count
  GAP-FODG-FOSS-FODG_HAS_ONL-001  — fodg_has_only_one_shape
  GAP-FODG-FOSS-FODG_PAGE_EQ-001  — fodg_page_equals_shape_count
  GAP-FODG-FOSS-FODG_HAS_ZER-001  — fodg_has_zero_text_items
  GAP-FODG-FOSS-FODG_TEXT_TI-001  — fodg_text_times_shape_plus_page_count
  GAP-FODG-FOSS-FODG_BYTES_P-001  — fodg_bytes_per_shape
  GAP-FODG-FOSS-FODG_PAGE_TI-001  — fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50

Run from repo root:
    python -m pytest tests/python/fodg/test_fodg_gap_closure_foss.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import fodg_page_count
from fodg.fodg_analytics import (
    fodg_shapes_with_text_count,
    fodg_has_no_shapes,
    fodg_file_size_bytes,
    fodg_min_text_item_length,
    fodg_unique_text_item_count,
    fodg_text_item_count,
    fodg_word_count,
    fodg_text_and_shape_sum,
    fodg_has_equal_shapes_and_text,
    fodg_page_count_plus_shape_count,
    fodg_shape_plus_text_plus_page_count,
    fodg_has_more_shapes_than_text_items,
    fodg_has_exactly_one_text_item,
    fodg_has_at_least_two_shapes,
    fodg_text_count_plus_page_count,
    fodg_has_only_one_shape,
    fodg_page_equals_shape_count,
    fodg_has_zero_text_items,
    fodg_text_times_shape_plus_page_count,
    fodg_bytes_per_shape,
    fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"   # 1 page, 1 shape, 1 text item
EMPTY = SAMPLES / "empty-page.fodg"          # 1 page, 0 shapes, 0 text items
SHAPES = SAMPLES / "shapes-basic.fodg"       # 1 page, 3 shapes, 2 text items


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_SHAPES_-001 — fodg_shapes_with_text_count
# ---------------------------------------------------------------------------

class TestFodgShapesWithTextCount:
    def test_empty_returns_zero(self):
        assert fodg_shapes_with_text_count(EMPTY) == 0

    def test_minimal_returns_int(self):
        assert isinstance(fodg_shapes_with_text_count(MINIMAL), int)

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_shapes_with_text_count(p) >= 0


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_NO_-001 — fodg_has_no_shapes
# ---------------------------------------------------------------------------

class TestFodgHasNoShapes:
    def test_empty_has_no_shapes(self):
        assert fodg_has_no_shapes(EMPTY) is True

    def test_minimal_has_shapes(self):
        assert fodg_has_no_shapes(MINIMAL) is False

    def test_shapes_has_shapes(self):
        assert fodg_has_no_shapes(SHAPES) is False

    def test_returns_bool(self):
        assert isinstance(fodg_has_no_shapes(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_FILE_SI-001 — fodg_file_size_bytes
# ---------------------------------------------------------------------------

class TestFodgFileSizeBytes:
    def test_empty_positive(self):
        assert fodg_file_size_bytes(EMPTY) > 0

    def test_minimal_size(self):
        assert fodg_file_size_bytes(MINIMAL) == 1473

    def test_shapes_larger_than_empty(self):
        assert fodg_file_size_bytes(SHAPES) > fodg_file_size_bytes(EMPTY)

    def test_returns_int(self):
        assert isinstance(fodg_file_size_bytes(MINIMAL), int)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_MIN_TEX-001 — fodg_min_text_item_length
# ---------------------------------------------------------------------------

class TestFodgMinTextItemLength:
    def test_empty_returns_zero(self):
        assert fodg_min_text_item_length(EMPTY) == 0

    def test_minimal_positive(self):
        assert fodg_min_text_item_length(MINIMAL) > 0

    def test_shapes_positive(self):
        assert fodg_min_text_item_length(SHAPES) > 0

    def test_returns_int(self):
        assert isinstance(fodg_min_text_item_length(MINIMAL), int)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_UNIQUE_-001 — fodg_unique_text_item_count
# ---------------------------------------------------------------------------

class TestFodgUniqueTextItemCount:
    def test_empty_returns_zero(self):
        assert fodg_unique_text_item_count(EMPTY) == 0

    def test_minimal_returns_one(self):
        assert fodg_unique_text_item_count(MINIMAL) == 1

    def test_shapes_returns_two(self):
        assert fodg_unique_text_item_count(SHAPES) == 2

    def test_returns_int(self):
        assert isinstance(fodg_unique_text_item_count(MINIMAL), int)

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_unique_text_item_count(p) >= 0


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_TEXT_IT-001 — fodg_text_item_count
# ---------------------------------------------------------------------------

class TestFodgTextItemCount:
    def test_empty_returns_zero(self):
        assert fodg_text_item_count(EMPTY) == 0

    def test_minimal_returns_one(self):
        assert fodg_text_item_count(MINIMAL) == 1

    def test_shapes_returns_two(self):
        assert fodg_text_item_count(SHAPES) == 2

    def test_returns_int(self):
        assert isinstance(fodg_text_item_count(MINIMAL), int)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_WORD_CO-001 — fodg_word_count
# ---------------------------------------------------------------------------

class TestFodgWordCount:
    def test_empty_returns_zero(self):
        assert fodg_word_count(EMPTY) == 0

    def test_returns_int(self):
        assert isinstance(fodg_word_count(MINIMAL), int)

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_word_count(p) >= 0


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_TEXT_AN-001 — fodg_text_and_shape_sum
# ---------------------------------------------------------------------------

class TestFodgTextAndShapeSum:
    def test_empty_returns_zero(self):
        assert fodg_text_and_shape_sum(EMPTY) == 0

    def test_minimal_returns_two(self):
        # 1 shape + 1 text item = 2
        assert fodg_text_and_shape_sum(MINIMAL) == 2

    def test_shapes_returns_five(self):
        # 3 shapes + 2 text items = 5
        assert fodg_text_and_shape_sum(SHAPES) == 5

    def test_returns_int(self):
        assert isinstance(fodg_text_and_shape_sum(MINIMAL), int)

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_text_and_shape_sum(p) >= 0


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_EQU-001 — fodg_has_equal_shapes_and_text
# ---------------------------------------------------------------------------

class TestFodgHasEqualShapesAndText:
    def test_empty_is_equal(self):
        # 0 shapes == 0 text items
        assert fodg_has_equal_shapes_and_text(EMPTY) is True

    def test_minimal_is_equal(self):
        # 1 shape == 1 text item
        assert fodg_has_equal_shapes_and_text(MINIMAL) is True

    def test_shapes_not_equal(self):
        # 3 shapes != 2 text items
        assert fodg_has_equal_shapes_and_text(SHAPES) is False

    def test_returns_bool(self):
        assert isinstance(fodg_has_equal_shapes_and_text(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_PAGE_CO-001 — fodg_page_count_plus_shape_count
# ---------------------------------------------------------------------------

class TestFodgPageCountPlusShapeCount:
    def test_empty_returns_one(self):
        # 1 page + 0 shapes = 1
        assert fodg_page_count_plus_shape_count(EMPTY) == 1

    def test_minimal_returns_two(self):
        # 1 page + 1 shape = 2
        assert fodg_page_count_plus_shape_count(MINIMAL) == 2

    def test_shapes_returns_four(self):
        # 1 page + 3 shapes = 4
        assert fodg_page_count_plus_shape_count(SHAPES) == 4

    def test_returns_int(self):
        assert isinstance(fodg_page_count_plus_shape_count(MINIMAL), int)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_SHAPE_P-001 — fodg_shape_plus_text_plus_page_count
# ---------------------------------------------------------------------------

class TestFodgShapePlusTextPlusPageCount:
    def test_empty_returns_one(self):
        # 0 + 0 + 1 = 1
        assert fodg_shape_plus_text_plus_page_count(EMPTY) == 1

    def test_minimal_returns_three(self):
        # 1 + 1 + 1 = 3
        assert fodg_shape_plus_text_plus_page_count(MINIMAL) == 3

    def test_returns_int(self):
        assert isinstance(fodg_shape_plus_text_plus_page_count(MINIMAL), int)

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_shape_plus_text_plus_page_count(p) >= 0


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_MOR-001 — fodg_has_more_shapes_than_text_items
# ---------------------------------------------------------------------------

class TestFodgHasMoreShapesThanTextItems:
    def test_empty_false(self):
        assert fodg_has_more_shapes_than_text_items(EMPTY) is False

    def test_minimal_false(self):
        # 1 shape == 1 text; not strictly more
        assert fodg_has_more_shapes_than_text_items(MINIMAL) is False

    def test_shapes_true(self):
        # 3 shapes > 2 text items
        assert fodg_has_more_shapes_than_text_items(SHAPES) is True

    def test_returns_bool(self):
        assert isinstance(fodg_has_more_shapes_than_text_items(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_EXA-001 — fodg_has_exactly_one_text_item
# ---------------------------------------------------------------------------

class TestFodgHasExactlyOneTextItem:
    def test_empty_false(self):
        assert fodg_has_exactly_one_text_item(EMPTY) is False

    def test_minimal_true(self):
        assert fodg_has_exactly_one_text_item(MINIMAL) is True

    def test_shapes_false(self):
        assert fodg_has_exactly_one_text_item(SHAPES) is False

    def test_returns_bool(self):
        assert isinstance(fodg_has_exactly_one_text_item(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_AT_-001 — fodg_has_at_least_two_shapes
# ---------------------------------------------------------------------------

class TestFodgHasAtLeastTwoShapes:
    def test_empty_false(self):
        assert fodg_has_at_least_two_shapes(EMPTY) is False

    def test_minimal_false(self):
        assert fodg_has_at_least_two_shapes(MINIMAL) is False

    def test_shapes_true(self):
        assert fodg_has_at_least_two_shapes(SHAPES) is True

    def test_returns_bool(self):
        assert isinstance(fodg_has_at_least_two_shapes(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_TEXT_CO-001 — fodg_text_count_plus_page_count
# ---------------------------------------------------------------------------

class TestFodgTextCountPlusPageCount:
    def test_empty_returns_one(self):
        # 0 text + 1 page = 1
        assert fodg_text_count_plus_page_count(EMPTY) == 1

    def test_minimal_returns_two(self):
        # 1 text + 1 page = 2
        assert fodg_text_count_plus_page_count(MINIMAL) == 2

    def test_shapes_returns_three(self):
        # 2 text + 1 page = 3
        assert fodg_text_count_plus_page_count(SHAPES) == 3

    def test_returns_int(self):
        assert isinstance(fodg_text_count_plus_page_count(MINIMAL), int)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_ONL-001 — fodg_has_only_one_shape
# ---------------------------------------------------------------------------

class TestFodgHasOnlyOneShape:
    def test_empty_false(self):
        assert fodg_has_only_one_shape(EMPTY) is False

    def test_minimal_true(self):
        assert fodg_has_only_one_shape(MINIMAL) is True

    def test_shapes_false(self):
        assert fodg_has_only_one_shape(SHAPES) is False

    def test_returns_bool(self):
        assert isinstance(fodg_has_only_one_shape(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_PAGE_EQ-001 — fodg_page_equals_shape_count
# ---------------------------------------------------------------------------

class TestFodgPageEqualsShapeCount:
    def test_empty_false(self):
        # 1 page != 0 shapes
        assert fodg_page_equals_shape_count(EMPTY) is False

    def test_minimal_true(self):
        # 1 page == 1 shape
        assert fodg_page_equals_shape_count(MINIMAL) is True

    def test_shapes_false(self):
        # 1 page != 3 shapes
        assert fodg_page_equals_shape_count(SHAPES) is False

    def test_returns_bool(self):
        assert isinstance(fodg_page_equals_shape_count(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_HAS_ZER-001 — fodg_has_zero_text_items
# ---------------------------------------------------------------------------

class TestFodgHasZeroTextItems:
    def test_empty_true(self):
        assert fodg_has_zero_text_items(EMPTY) is True

    def test_minimal_false(self):
        assert fodg_has_zero_text_items(MINIMAL) is False

    def test_shapes_false(self):
        assert fodg_has_zero_text_items(SHAPES) is False

    def test_returns_bool(self):
        assert isinstance(fodg_has_zero_text_items(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_TEXT_TI-001 — fodg_text_times_shape_plus_page_count
# ---------------------------------------------------------------------------

class TestFodgTextTimesShapePlusPageCount:
    def test_empty_returns_one(self):
        # 0 * 0 + 1 = 1
        assert fodg_text_times_shape_plus_page_count(EMPTY) == 1

    def test_minimal_returns_two(self):
        # 1 * 1 + 1 = 2
        assert fodg_text_times_shape_plus_page_count(MINIMAL) == 2

    def test_returns_int(self):
        assert isinstance(fodg_text_times_shape_plus_page_count(MINIMAL), int)

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_text_times_shape_plus_page_count(p) >= 0


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_BYTES_P-001 — fodg_bytes_per_shape
# ---------------------------------------------------------------------------

class TestFodgBytesPerShape:
    def test_empty_returns_zero(self):
        # 0 shapes -> 0 or file_size (implementation-defined; just non-negative)
        result = fodg_bytes_per_shape(EMPTY)
        assert result >= 0

    def test_minimal_positive(self):
        assert fodg_bytes_per_shape(MINIMAL) > 0

    def test_shapes_positive(self):
        assert fodg_bytes_per_shape(SHAPES) > 0

    def test_returns_numeric(self):
        assert isinstance(fodg_bytes_per_shape(MINIMAL), (int, float))


# ---------------------------------------------------------------------------
# GAP-FODG-FOSS-FODG_PAGE_TI-001 — fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50
# ---------------------------------------------------------------------------

class TestFodgPageTimes600PlusShapeTimes400PlusFileSizeMod29Times50:
    def test_empty_returns_numeric(self):
        result = fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(EMPTY)
        assert isinstance(result, (int, float))

    def test_minimal_formula(self):
        # 1*600 + 1*400 + (1473 mod 29)*50
        expected = 1 * 600 + 1 * 400 + (1473 % 29) * 50
        assert fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(MINIMAL) == expected

    def test_non_negative(self):
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(p) >= 0
