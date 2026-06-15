"""Tests for fodp_master_page_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_master_page_count, FodpError

# Minimal FODP XML templates
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

def _slide(name, master):
    return f'      <draw:page draw:name="{name}" draw:master-page-name="{master}"></draw:page>'


class TestFodpMasterPageCount:
    def test_single_master(self, tmp_path):
        slides = "\n".join([_slide("Slide1", "Default"), _slide("Slide2", "Default")])
        p = tmp_path / "test.fodp"
        p.write_text(_FODP_TEMPLATE.format(slides=slides), encoding="utf-8")
        assert fodp_master_page_count(str(p)) == 1

    def test_two_masters(self, tmp_path):
        slides = "\n".join([_slide("Slide1", "Default"), _slide("Slide2", "Title")])
        p = tmp_path / "test.fodp"
        p.write_text(_FODP_TEMPLATE.format(slides=slides), encoding="utf-8")
        assert fodp_master_page_count(str(p)) == 2

    def test_three_masters(self, tmp_path):
        slides = "\n".join([
            _slide("S1", "Default"), _slide("S2", "Title"),
            _slide("S3", "Blank"), _slide("S4", "Title"),
        ])
        p = tmp_path / "test.fodp"
        p.write_text(_FODP_TEMPLATE.format(slides=slides), encoding="utf-8")
        assert fodp_master_page_count(str(p)) == 3

    def test_no_slides(self, tmp_path):
        p = tmp_path / "test.fodp"
        p.write_text(_FODP_TEMPLATE.format(slides=""), encoding="utf-8")
        assert fodp_master_page_count(str(p)) == 0

    def test_single_slide_single_master(self, tmp_path):
        slides = _slide("Only", "MyLayout")
        p = tmp_path / "test.fodp"
        p.write_text(_FODP_TEMPLATE.format(slides=slides), encoding="utf-8")
        assert fodp_master_page_count(str(p)) == 1

    def test_five_slides_one_master(self, tmp_path):
        slides = "\n".join([_slide(f"S{i}", "Standard") for i in range(5)])
        p = tmp_path / "test.fodp"
        p.write_text(_FODP_TEMPLATE.format(slides=slides), encoding="utf-8")
        assert fodp_master_page_count(str(p)) == 1

    def test_importable_from_package(self):
        from fodp import fodp_master_page_count as fn
        assert callable(fn)
