"""
tests/python/fodg/test_r122_fodg_probe.py

Sprint: FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
TC-FODG-PROBE: probe_fodg()
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import probe_fodg


_VALID_FODG = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    b'  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    b'  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">'
    b'<office:body><office:drawing>'
    b'<draw:page draw:name="page1"><draw:rect svg:x="1cm" svg:y="1cm" svg:width="5cm" svg:height="3cm"/>'
    b'</draw:page></office:drawing></office:body>'
    b'</office:document>'
)

_NOT_FODG = b'<?xml version="1.0"?><root><data>not a drawing file</data></root>'
_RANDOM_BYTES = b'\x00\x01\x02\x03\x04\x05\xff\xfe'
_EMPTY = b''


class TestProbeFodg:
    def test_valid_fodg_returns_true(self):
        assert probe_fodg(_VALID_FODG) is True

    def test_non_fodg_xml_returns_false(self):
        assert probe_fodg(_NOT_FODG) is False

    def test_random_bytes_returns_false(self):
        assert probe_fodg(_RANDOM_BYTES) is False

    def test_empty_bytes_returns_false(self):
        assert probe_fodg(_EMPTY) is False

    def test_does_not_raise(self):
        """probe_fodg must never raise, even on garbage input."""
        probe_fodg(b"garbage!!!")
        probe_fodg("")
        probe_fodg(b"\xff\xfe\xfd")

    def test_returns_bool(self):
        result = probe_fodg(_VALID_FODG)
        assert isinstance(result, bool)

    def test_graphics_mime_required(self):
        """Without the graphics MIME type, must return False."""
        no_mime = (
            b'<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
            b'<office:body/></office:document>'
        )
        assert probe_fodg(no_mime) is False

    def test_import_from_package(self):
        import fodg
        assert hasattr(fodg, "probe_fodg")

    def test_in_all(self):
        import fodg
        assert "probe_fodg" in fodg.__all__
