"""Tests for xliff_analytics — translated/untranslated segment counts and
average source length (FACT-XLIFF-002).

L2 (behavior/analytics) classes: TestTranslatedSegmentCount,
TestUntranslatedSegmentCount, TestAverageSourceLength.
L3 (malformed input / exceptions) class: TestAnalyticsMalformedInput.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from xliff.exceptions import XliffParseError
from xliff.xliff_analytics import (
    xliff_average_source_length,
    xliff_translated_segment_count,
    xliff_untranslated_segment_count,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


def _xml_bytes(pairs: list[tuple[str, "str | None"]]) -> bytes:
    """Build a single-file/single-unit XLIFF 2.0 document from (source, target) pairs.

    target=None omits the <target> element entirely (untranslated by absence).
    """
    segs = []
    for source, target in pairs:
        seg = f"<segment><source>{source}</source>"
        if target is not None:
            seg += f"<target>{target}</target>"
        seg += "</segment>"
        segs.append(seg)
    xml = (
        '<?xml version="1.0"?>'
        '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
        f'<file id="f1"><unit id="u1">{"".join(segs)}</unit></file></xliff>'
    )
    return xml.encode("utf-8")


def _zero_unit_xml_bytes() -> bytes:
    return (
        b'<?xml version="1.0"?>'
        b'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
        b'<file id="f1"></file></xliff>'
    )


class TestTranslatedSegmentCount:
    def test_minimal_single_translated(self):
        assert xliff_translated_segment_count(VALID_DIR / "minimal.xliff") == 1

    def test_multi_unit_all_translated(self):
        assert xliff_translated_segment_count(VALID_DIR / "multi-unit.xliff") == 3

    def test_with_inline_codes_translated(self):
        assert xliff_translated_segment_count(VALID_DIR / "with-inline-codes.xliff") == 1

    def test_mixed_translated_and_untranslated(self):
        data = _xml_bytes([("A", "a"), ("B", None), ("C", "c")])
        assert xliff_translated_segment_count(data) == 2

    def test_zero_segments_zero_units(self):
        assert xliff_translated_segment_count(_zero_unit_xml_bytes()) == 0

    def test_whitespace_only_target_not_counted(self):
        data = _xml_bytes([("A", "   ")])
        assert xliff_translated_segment_count(data) == 0

    def test_all_untranslated_returns_zero(self):
        data = _xml_bytes([("A", None), ("B", None)])
        assert xliff_translated_segment_count(data) == 0

    def test_return_type_is_int(self):
        assert isinstance(xliff_translated_segment_count(VALID_DIR / "minimal.xliff"), int)


class TestUntranslatedSegmentCount:
    def test_minimal_zero_untranslated(self):
        assert xliff_untranslated_segment_count(VALID_DIR / "minimal.xliff") == 0

    def test_missing_target_element_counts_untranslated(self):
        data = _xml_bytes([("A", None)])
        assert xliff_untranslated_segment_count(data) == 1

    def test_empty_target_text_counts_untranslated(self):
        data = _xml_bytes([("A", "")])
        assert xliff_untranslated_segment_count(data) == 1

    def test_whitespace_only_target_counts_untranslated(self):
        data = _xml_bytes([("A", "  \t ")])
        assert xliff_untranslated_segment_count(data) == 1

    def test_mixed_counts_correct_untranslated(self):
        data = _xml_bytes([("A", "a"), ("B", None), ("C", ""), ("D", "d")])
        assert xliff_untranslated_segment_count(data) == 2

    def test_zero_segments_zero_units(self):
        assert xliff_untranslated_segment_count(_zero_unit_xml_bytes()) == 0

    def test_all_translated_returns_zero(self):
        data = _xml_bytes([("A", "a"), ("B", "b")])
        assert xliff_untranslated_segment_count(data) == 0

    def test_return_type_is_int(self):
        assert isinstance(xliff_untranslated_segment_count(VALID_DIR / "minimal.xliff"), int)


class TestAverageSourceLength:
    def test_minimal_single_segment(self):
        assert xliff_average_source_length(VALID_DIR / "minimal.xliff") == pytest.approx(5.0)

    def test_multi_unit_average(self):
        # "Hello"(5) + "World"(5) + "Goodbye"(7) -> 17/3
        result = xliff_average_source_length(VALID_DIR / "multi-unit.xliff")
        assert result == pytest.approx(17 / 3)

    def test_with_inline_codes_length_includes_inline_text(self):
        # "Click " + "here" + " to continue" == 22 chars
        result = xliff_average_source_length(VALID_DIR / "with-inline-codes.xliff")
        assert result == pytest.approx(22.0)

    def test_zero_segments_returns_zero(self):
        assert xliff_average_source_length(_zero_unit_xml_bytes()) == 0.0

    def test_empty_source_string_contributes_zero(self):
        data = _xml_bytes([("", "x"), ("AB", "y")])
        assert xliff_average_source_length(data) == pytest.approx(1.0)

    def test_single_char_sources(self):
        data = _xml_bytes([("a", "1"), ("b", "2"), ("c", "3")])
        assert xliff_average_source_length(data) == pytest.approx(1.0)

    def test_return_type_is_float(self):
        assert isinstance(xliff_average_source_length(VALID_DIR / "minimal.xliff"), float)

    def test_average_matches_manual_calc_for_bytes_source(self):
        data = _xml_bytes([("abcd", "w"), ("ab", "x")])  # lengths 4, 2 -> avg 3.0
        assert xliff_average_source_length(data) == pytest.approx(3.0)


class TestAnalyticsMalformedInput:
    def test_translated_count_raises_on_missing_namespace(self):
        with pytest.raises(XliffParseError):
            xliff_translated_segment_count(INVALID_DIR / "missing-namespace.xliff")

    def test_untranslated_count_raises_on_bad_xml(self):
        with pytest.raises(XliffParseError):
            xliff_untranslated_segment_count(b"<not>closed xml")

    def test_average_length_raises_on_missing_namespace(self):
        with pytest.raises(XliffParseError):
            xliff_average_source_length(INVALID_DIR / "missing-namespace.xliff")

    def test_translated_count_raises_on_nonexistent_file(self):
        with pytest.raises(XliffParseError):
            xliff_translated_segment_count("/nonexistent/file.xliff")
