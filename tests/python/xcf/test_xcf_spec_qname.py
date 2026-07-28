"""V53 spec_qname compliance tests for XCF — TC-QHARD-POST-001.

Verifies XcfImage has spec_qname = "xcf:image" as a class-level attribute.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import XcfImage  # type: ignore


class TestXcfImageSpecQname:
    def test_spec_qname_is_correct(self):
        assert XcfImage.spec_qname == "xcf:image"

    def test_spec_qname_class_level(self):
        assert "spec_qname" in XcfImage.__dict__
        assert XcfImage.__dict__["spec_qname"] == "xcf:image"

    def test_spec_fact_ref_set(self):
        assert XcfImage.spec_fact_ref == "SAL-XCF-00001"

    def test_namespace_uri_set(self):
        assert XcfImage.namespace_uri == "https://www.gimp.org/standards/xcf"

    def test_local_name_is_image(self):
        assert XcfImage.local_name == "image"

    def test_instance_inherits_spec_qname(self):
        img = XcfImage()
        assert img.spec_qname == "xcf:image"
