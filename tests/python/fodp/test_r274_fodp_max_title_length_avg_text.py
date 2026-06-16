"""Tests for fodp_max_title_length and fodp_avg_text_length (Sprint 64)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodp.fodp_codec import fodp_max_title_length, fodp_avg_text_length

FODP = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodp"


class TestFodpMaxTitleLength:
    def test_minimal(self):
        assert fodp_max_title_length(FODP / "minimal-presentation.fodp") == 5

    def test_title_only_empty(self):
        assert fodp_max_title_length(FODP / "title-only.fodp") == 0

    def test_two_slides(self):
        assert fodp_max_title_length(FODP / "two-slides-basic.fodp") == 12

    def test_returns_int(self):
        assert isinstance(fodp_max_title_length(FODP / "minimal-presentation.fodp"), int)

    def test_nonnegative(self):
        for f in ["minimal-presentation.fodp", "title-only.fodp", "two-slides-basic.fodp"]:
            assert fodp_max_title_length(FODP / f) >= 0


class TestFodpAvgTextLength:
    def test_minimal(self):
        assert abs(fodp_avg_text_length(FODP / "minimal-presentation.fodp") - 5.0) < 0.01

    def test_title_only_zero(self):
        assert fodp_avg_text_length(FODP / "title-only.fodp") == 0.0

    def test_two_slides(self):
        assert abs(fodp_avg_text_length(FODP / "two-slides-basic.fodp") - 21.0) < 0.01

    def test_returns_float(self):
        assert isinstance(fodp_avg_text_length(FODP / "minimal-presentation.fodp"), float)

    def test_nonnegative(self):
        for f in ["minimal-presentation.fodp", "title-only.fodp", "two-slides-basic.fodp"]:
            assert fodp_avg_text_length(FODP / f) >= 0.0
