"""
tests/python/zst/test_r280_zst_installed_workflow.py

Sprint: ff-sprint-s280-zst-installed-workflow-20260626
Authority: Zstandard compression format

Tests for zst_installed_workflow() in zst_workflow.py.
"""
from __future__ import annotations

import pytest


def _make_compressed(data: bytes = b"hello world test data") -> bytes:
    from zst.zst_codec import compress_bytes
    return compress_bytes(data)


class TestZstInstalledWorkflowImport:
    """zst_installed_workflow is importable and callable."""

    def test_importable_from_zst_workflow(self):
        from zst.zst_workflow import zst_installed_workflow
        assert callable(zst_installed_workflow)

    def test_importable_from_package(self):
        import zst
        assert hasattr(zst, "zst_installed_workflow")


class TestZstInstalledWorkflowOutput:
    """zst_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert isinstance(result, dict)

    def test_format_field_is_zstd(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert result["format"] == "zstd"

    def test_loaded_field_is_true(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert result["loaded"] is True

    def test_compressed_size_is_integer(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert isinstance(result["compressed_size"], int)

    def test_decompressed_size_is_integer(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert isinstance(result["decompressed_size"], int)

    def test_magic_ok_is_true(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert result["magic_ok"] is True

    def test_has_all_required_keys(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(_make_compressed())
        assert {"format", "loaded", "compressed_size", "decompressed_size", "magic_ok"}.issubset(result.keys())

    def test_decompressed_size_matches_original(self):
        from zst.zst_workflow import zst_installed_workflow
        data = b"test data with known length xxxx"
        result = zst_installed_workflow(_make_compressed(data))
        assert result["decompressed_size"] == len(data)

    def test_invalid_bytes_loaded_false(self):
        from zst.zst_workflow import zst_installed_workflow
        result = zst_installed_workflow(b"not valid zstd data at all!!!")
        assert result["loaded"] is False
        assert result["magic_ok"] is False

    def test_consistent_across_calls(self):
        from zst.zst_workflow import zst_installed_workflow
        compressed = _make_compressed()
        r1 = zst_installed_workflow(compressed)
        r2 = zst_installed_workflow(compressed)
        assert r1["compressed_size"] == r2["compressed_size"]
        assert r1["decompressed_size"] == r2["decompressed_size"]
