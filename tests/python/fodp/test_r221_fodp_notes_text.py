"""Tests for fodp_notes_text and fodp_has_notes — R221 product deepening."""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_notes_text, fodp_has_notes


# --- Minimal FODP XML fixtures ---

_FODP_WITH_NOTES = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1">
        <draw:frame presentation:class="title">
          <draw:text-box><text:p>Title</text:p></draw:text-box>
        </draw:frame>
        <presentation:notes>
          <draw:frame>
            <draw:text-box><text:p>Speaker note one</text:p></draw:text-box>
          </draw:frame>
        </presentation:notes>
      </draw:page>
      <draw:page draw:name="Slide2">
        <draw:frame presentation:class="subtitle">
          <draw:text-box><text:p>Body</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
      <draw:page draw:name="Slide3">
        <presentation:notes>
          <draw:frame>
            <draw:text-box>
              <text:p>Note line A</text:p>
              <text:p>Note line B</text:p>
            </draw:text-box>
          </draw:frame>
        </presentation:notes>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>
"""

_FODP_NO_NOTES = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1">
        <draw:frame presentation:class="title">
          <draw:text-box><text:p>Hello</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>
"""


class TestFodpNotesText:
    def test_returns_list_of_notes(self):
        result = fodp_notes_text(_FODP_WITH_NOTES)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_first_slide_has_note(self):
        result = fodp_notes_text(_FODP_WITH_NOTES)
        assert result[0] == "Speaker note one"

    def test_second_slide_no_notes(self):
        result = fodp_notes_text(_FODP_WITH_NOTES)
        assert result[1] == ""

    def test_third_slide_multi_line_notes(self):
        result = fodp_notes_text(_FODP_WITH_NOTES)
        assert "Note line A" in result[2]
        assert "Note line B" in result[2]

    def test_no_notes_returns_empty_strings(self):
        result = fodp_notes_text(_FODP_NO_NOTES)
        assert len(result) == 1
        assert result[0] == ""

    def test_file_path(self, tmp_path):
        fp = tmp_path / "test.fodp"
        fp.write_text(_FODP_WITH_NOTES, encoding="utf-8")
        result = fodp_notes_text(fp)
        assert len(result) == 3
        assert result[0] == "Speaker note one"

    def test_bytes_input(self):
        result = fodp_notes_text(_FODP_WITH_NOTES.encode("utf-8"))
        assert len(result) == 3


class TestFodpHasNotes:
    def test_has_notes_true(self):
        assert fodp_has_notes(_FODP_WITH_NOTES) is True

    def test_has_notes_false(self):
        assert fodp_has_notes(_FODP_NO_NOTES) is False

    def test_file_path(self, tmp_path):
        fp = tmp_path / "test.fodp"
        fp.write_text(_FODP_WITH_NOTES, encoding="utf-8")
        assert fodp_has_notes(fp) is True

    def test_all_empty_notes(self):
        xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
 office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1">
        <presentation:notes>
          <draw:frame><draw:text-box><text:p></text:p></draw:text-box></draw:frame>
        </presentation:notes>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>
"""
        assert fodp_has_notes(xml) is False
