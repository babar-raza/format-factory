"""
Tests for FODP additional page/title analytics (2 new FOSS functions).
Closes: GAP-FODP-FOSS-FODP_ALL_PAG-001, GAP-FODP-FOSS-FODP_MAX_TEX-001

Known sample values:
  title-only.fodp:           0 pages → all_pages_have_title=False, max_text_item_count=0
  minimal-presentation.fodp: 1 page, title='Hello'     → all_pages_have_title=True,  max_text_item_count=1
  two-slides-basic.fodp:     2 pages, both have titles → all_pages_have_title=True,  max_text_item_count=2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_all_pages_have_title, fodp_max_text_item_count

_FODP = _REPO / "samples" / "by-format" / "fodp"
_EMPTY = _FODP / "title-only.fodp"
_MINIMAL = _FODP / "minimal-presentation.fodp"
_TWO = _FODP / "two-slides-basic.fodp"


class TestFodpAllPagesHaveTitle:
    def test_returns_bool(self):
        assert isinstance(fodp_all_pages_have_title(_EMPTY), bool)

    def test_no_pages_is_false(self):
        # title-only.fodp has 0 pages
        assert fodp_all_pages_have_title(_EMPTY) is False

    def test_minimal_has_title(self):
        # minimal-presentation has page with title='Hello'
        assert fodp_all_pages_have_title(_MINIMAL) is True

    def test_two_slides_have_titles(self):
        # both slides have non-empty titles
        assert fodp_all_pages_have_title(_TWO) is True

    def test_empty_differs_from_minimal(self):
        assert fodp_all_pages_have_title(_EMPTY) is not fodp_all_pages_have_title(_MINIMAL)

    def test_all_return_bool(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert isinstance(fodp_all_pages_have_title(p), bool)


class TestFodpMaxTextItemCount:
    def test_returns_int(self):
        assert isinstance(fodp_max_text_item_count(_EMPTY), int)

    def test_no_pages_returns_zero(self):
        # title-only.fodp has 0 pages
        assert fodp_max_text_item_count(_EMPTY) == 0

    def test_minimal_has_one_text_item(self):
        # minimal-presentation has ['Hello'] on its single page
        assert fodp_max_text_item_count(_MINIMAL) == 1

    def test_two_slides_max_is_two(self):
        # two-slides-basic slide 1 has ['Introduction', 'First slide content.'] = 2 items
        assert fodp_max_text_item_count(_TWO) == 2

    def test_nonnegative(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert fodp_max_text_item_count(p) >= 0

    def test_two_slides_greater_than_minimal(self):
        assert fodp_max_text_item_count(_TWO) > fodp_max_text_item_count(_MINIMAL)

    def test_all_return_int(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert isinstance(fodp_max_text_item_count(p), int)
