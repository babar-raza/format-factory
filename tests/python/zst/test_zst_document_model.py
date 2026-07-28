"""Tests for ZstDocument domain model.

Verifies spec_qname class attribute, construction, typed properties,
and from_file factory.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import compress_bytes
from zst.models import ZstDocument


def _make_zst_file(content: bytes = b"hello world test content for zst model") -> str:
    """Create a temp .zst file with compressed content, return path."""
    compressed = compress_bytes(content)
    tmp = tempfile.NamedTemporaryFile(suffix=".zst", delete=False)
    tmp.write(compressed)
    tmp.close()
    return tmp.name


class TestZstDocumentClassAttributes:
    def test_spec_qname_is_class_attribute(self):
        assert ZstDocument.spec_qname == "zst:frame"

    def test_spec_qname_accessible_without_instance(self):
        assert ZstDocument.spec_qname == "zst:frame"

    def test_spec_fact_ref(self):
        assert ZstDocument.spec_fact_ref == "SAL-ZST-00001"

    def test_namespace_uri(self):
        assert ZstDocument.namespace_uri == "urn:ietf:rfc:8878:zstandard"

    def test_local_name(self):
        assert ZstDocument.local_name == "frame"

    def test_facade_names_is_list(self):
        assert isinstance(ZstDocument.facade_names, list)


class TestZstDocumentConstruction:
    def test_construct_from_path_and_data(self):
        doc = ZstDocument("/tmp/test.zst", {"compressed_size": 42, "decompressed_size": 100, "frame_count": 1})
        assert isinstance(doc, ZstDocument)

    def test_compressed_size(self):
        doc = ZstDocument("/tmp/test.zst", {"compressed_size": 42})
        assert doc.compressed_size == 42

    def test_decompressed_size(self):
        doc = ZstDocument("/tmp/test.zst", {"decompressed_size": 100})
        assert doc.decompressed_size == 100

    def test_frame_count(self):
        doc = ZstDocument("/tmp/test.zst", {"frame_count": 3})
        assert doc.frame_count == 3

    def test_empty_data_defaults_to_zero(self):
        doc = ZstDocument("/tmp/test.zst")
        assert doc.compressed_size == 0
        assert doc.decompressed_size == 0
        assert doc.frame_count == 0

    def test_path_property(self):
        doc = ZstDocument("/tmp/test.zst")
        assert doc.path == Path("/tmp/test.zst")


class TestZstDocumentToDict:
    def test_to_dict_returns_dict(self):
        doc = ZstDocument("/tmp/test.zst", {"compressed_size": 42, "frame_count": 1})
        result = doc.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_has_path(self):
        doc = ZstDocument("/tmp/test.zst", {})
        result = doc.to_dict()
        assert "path" in result

    def test_to_dict_has_metrics(self):
        doc = ZstDocument("/tmp/test.zst", {"compressed_size": 42, "frame_count": 1})
        result = doc.to_dict()
        assert result["compressed_size"] == 42
        assert result["frame_count"] == 1


class TestZstDocumentFromFile:
    def test_from_file_returns_instance(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(path)
            assert isinstance(doc, ZstDocument)
        finally:
            os.unlink(path)

    def test_from_file_compressed_size_positive(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(path)
            assert doc.compressed_size > 0
        finally:
            os.unlink(path)

    def test_from_file_decompressed_size_positive(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(path)
            assert doc.decompressed_size > 0
        finally:
            os.unlink(path)

    def test_from_file_frame_count_positive(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(path)
            assert doc.frame_count >= 1
        finally:
            os.unlink(path)

    def test_from_file_path_object(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(Path(path))
            assert doc.compressed_size > 0
        finally:
            os.unlink(path)

    def test_from_file_path_stored(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(path)
            assert doc.path == Path(path)
        finally:
            os.unlink(path)


class TestZstDocumentRepr:
    def test_repr_includes_filename(self):
        path = _make_zst_file()
        try:
            doc = ZstDocument.from_file(path)
            r = repr(doc)
            assert "ZstDocument" in r
            assert "compressed_size" in r
        finally:
            os.unlink(path)
