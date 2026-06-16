"""Tests for fodp_min_text_per_slide and fodp_total_notes_length.

Product deepening: FODP analytics — TC-H3-002-FODP / PDC-FODP-MINTEXT-NOTES-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import fodp_min_text_per_slide, fodp_total_notes_length

_FODP_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
{slides}
    </office:presentation>
  </office:body>
</office:document>"""


def _slide_with_text(name, text):
    return f'''      <draw:page draw:name="{name}" draw:master-page-name="Default">
        <draw:frame presentation:class="title">
          <text:p>{text}</text:p>
        </draw:frame>
      </draw:page>'''


def _slide_with_notes(name, text, notes):
    return f'''      <draw:page draw:name="{name}" draw:master-page-name="Default">
        <draw:frame presentation:class="title">
          <text:p>{text}</text:p>
        </draw:frame>
        <presentation:notes>
          <draw:frame>
            <text:p>{notes}</text:p>
          </draw:frame>
        </presentation:notes>
      </draw:page>'''


def _empty_slide(name):
    return f'      <draw:page draw:name="{name}" draw:master-page-name="Default"></draw:page>'


def _make_fodp(tmp_path, name, slides_xml):
    p = tmp_path / f"{name}.fodp"
    p.write_text(_FODP_TEMPLATE.format(slides=slides_xml), encoding="utf-8")
    return str(p)


class TestFodpMinTextPerSlide:
    def test_no_slides(self, tmp_path):
        p = _make_fodp(tmp_path, "empty", "")
        assert fodp_min_text_per_slide(p) == 0

    def test_one_slide_with_text(self, tmp_path):
        slides = _slide_with_text("S1", "Hello World")
        p = _make_fodp(tmp_path, "one", slides)
        result = fodp_min_text_per_slide(p)
        assert isinstance(result, int)

    def test_two_slides_different_text(self, tmp_path):
        slides = "\n".join([
            _slide_with_text("S1", "Short"),
            _slide_with_text("S2", "This is longer text"),
        ])
        p = _make_fodp(tmp_path, "diff", slides)
        result = fodp_min_text_per_slide(p)
        assert result >= 0

    def test_empty_slide_is_zero(self, tmp_path):
        slides = "\n".join([_empty_slide("S1"), _slide_with_text("S2", "text")])
        p = _make_fodp(tmp_path, "with_empty", slides)
        assert fodp_min_text_per_slide(p) == 0

    def test_returns_int(self, tmp_path):
        slides = _slide_with_text("S1", "Test")
        p = _make_fodp(tmp_path, "ret_int", slides)
        assert isinstance(fodp_min_text_per_slide(p), int)


class TestFodpTotalNotesLength:
    def test_no_notes(self, tmp_path):
        slides = _slide_with_text("S1", "Title")
        p = _make_fodp(tmp_path, "no_notes", slides)
        assert fodp_total_notes_length(p) == 0

    def test_one_note(self, tmp_path):
        slides = _slide_with_notes("S1", "Title", "Speaker note here")
        p = _make_fodp(tmp_path, "one_note", slides)
        result = fodp_total_notes_length(p)
        assert result > 0

    def test_returns_int(self, tmp_path):
        slides = _slide_with_text("S1", "Title")
        p = _make_fodp(tmp_path, "ret_int2", slides)
        assert isinstance(fodp_total_notes_length(p), int)

    def test_non_negative(self, tmp_path):
        slides = _empty_slide("S1")
        p = _make_fodp(tmp_path, "nn", slides)
        assert fodp_total_notes_length(p) >= 0

    def test_no_slides_zero(self, tmp_path):
        p = _make_fodp(tmp_path, "no_sl", "")
        assert fodp_total_notes_length(p) == 0
