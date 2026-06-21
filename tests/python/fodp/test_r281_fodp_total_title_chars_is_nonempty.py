"""Tests for fodp_total_title_chars and fodp_is_nonempty (Sprint 71)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodp.fodp_codec import fodp_total_title_chars, fodp_is_nonempty

FODP = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodp"


class TestFodpTotalTitleChars:
    def test_minimal(self):
        assert fodp_total_title_chars(FODP / "minimal-presentation.fodp") == 5

    def test_title_only_empty(self):
        assert fodp_total_title_chars(FODP / "title-only.fodp") == 0

    def test_two_slides(self):
        assert fodp_total_title_chars(FODP / "two-slides-basic.fodp") == 22

    def test_returns_int(self):
        assert isinstance(fodp_total_title_chars(FODP / "minimal-presentation.fodp"), int)

    def test_nonnegative(self):
        for f in ["minimal-presentation.fodp", "title-only.fodp", "two-slides-basic.fodp"]:
            assert fodp_total_title_chars(FODP / f) >= 0


class TestFodpIsNonempty:
    def test_minimal_has_slide(self):
        assert fodp_is_nonempty(FODP / "minimal-presentation.fodp") is True

    def test_title_only_empty(self):
        assert fodp_is_nonempty(FODP / "title-only.fodp") is False

    def test_two_slides_nonempty(self):
        assert fodp_is_nonempty(FODP / "two-slides-basic.fodp") is True

    def test_returns_bool(self):
        assert isinstance(fodp_is_nonempty(FODP / "minimal-presentation.fodp"), bool)

    def test_all_files_return_bool(self):
        for f in ["minimal-presentation.fodp", "title-only.fodp", "two-slides-basic.fodp"]:
            assert isinstance(fodp_is_nonempty(FODP / f), bool)
