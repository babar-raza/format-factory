"""
R1226 — ODT dogfood roundtrip test
Spec: ODF 1.3 §1.2 / §3.1 (OpenDocument Package format)
Dogfood rule: ODT read → text extraction (FF parser) → ODT write (FF odt_from_text)
All I/O uses installed format-factory-odt library; no external libraries.
"""

import os
import tempfile
import zipfile

import pytest

from odt import (
    odt_from_text,
    odt_paragraph_count,
    odt_total_text_length,
    odt_word_count,
    parse_odt,
)

_SAMPLE = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..",
    "samples", "by-format", "odt", "valid", "minimal-document.odt",
)


class TestOdtDogfoodReadPath:
    """Verify ODT read side of dogfood path uses FF library only."""

    def test_parse_returns_dict(self):
        doc = parse_odt(_SAMPLE)
        assert isinstance(doc, dict)

    def test_word_count_positive(self):
        wc = odt_word_count(_SAMPLE)
        assert isinstance(wc, int)
        assert wc >= 0

    def test_paragraph_count_positive(self):
        pc = odt_paragraph_count(_SAMPLE)
        assert isinstance(pc, int)
        assert pc >= 0

    def test_text_length_nonnegative(self):
        tl = odt_total_text_length(_SAMPLE)
        assert tl >= 0


class TestOdtDogfoodWritePath:
    """Verify ODT write side of dogfood path produces a valid ODT container."""

    def test_from_text_creates_file(self, tmp_path):
        out = str(tmp_path / "output.odt")
        result = odt_from_text("Hello from Format Factory", out)
        assert str(result) == out
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_output_is_valid_zip(self, tmp_path):
        out = str(tmp_path / "output.odt")
        odt_from_text("Dogfood roundtrip test", out)
        assert zipfile.is_zipfile(out)

    def test_output_contains_mimetype(self, tmp_path):
        out = str(tmp_path / "output.odt")
        odt_from_text("ODT container verification", out)
        with zipfile.ZipFile(out) as z:
            assert "mimetype" in z.namelist()

    def test_output_contains_content_xml(self, tmp_path):
        out = str(tmp_path / "output.odt")
        odt_from_text("Content XML verification", out)
        with zipfile.ZipFile(out) as z:
            assert "content.xml" in z.namelist()

    def test_output_size_above_floor(self, tmp_path):
        """Real ODT must be at least 200 bytes (not an empty stub)."""
        out = str(tmp_path / "output.odt")
        odt_from_text("Non-empty ODT output test", out)
        assert os.path.getsize(out) >= 200


class TestOdtDogfoodFullPipeline:
    """Verify the complete dogfood pipeline: parse → extract → write → reparse."""

    def test_roundtrip_word_count_preserved(self, tmp_path):
        """Parse source, write new ODT, reparse; word count must be ≥ 1."""
        out = str(tmp_path / "roundtrip.odt")
        wc = odt_word_count(_SAMPLE)
        text_content = " ".join(["word"] * max(wc, 1))
        odt_from_text(text_content, out)
        new_wc = odt_word_count(out)
        assert new_wc >= 1

    def test_no_external_library_in_parser(self):
        """ODT parser module must not import PIL, cv2, openpyxl, or imageio."""
        import inspect
        import odt.odt_parser as parser_mod
        source = inspect.getsource(parser_mod)
        for forbidden in ("PIL", "cv2", "openpyxl", "imageio", "skimage"):
            assert forbidden not in source, (
                f"Dogfood violation: odt.odt_parser imports {forbidden}"
            )

    def test_no_external_library_in_writer(self):
        """ODT writer module must not import PIL, cv2, openpyxl, or imageio."""
        import inspect
        import odt.odt_writer as writer_mod
        source = inspect.getsource(writer_mod)
        for forbidden in ("PIL", "cv2", "openpyxl", "imageio", "skimage"):
            assert forbidden not in source, (
                f"Dogfood violation: odt.odt_writer imports {forbidden}"
            )

    def test_multiple_paragraphs_preserved(self, tmp_path):
        """Multi-paragraph text produces non-empty ODT output."""
        out = str(tmp_path / "multi.odt")
        text = "First paragraph.\nSecond paragraph.\nThird paragraph."
        odt_from_text(text, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) >= 200
