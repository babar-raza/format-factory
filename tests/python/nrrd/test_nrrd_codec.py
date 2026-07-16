"""Core tests for the nrrd codec — probe, load, write, roundtrip."""

from __future__ import annotations

import gzip
import json
import struct
import tempfile
from pathlib import Path

import pytest

from nrrd.nrrd_codec import (
    get_dimension,
    get_encoding,
    load_nrrd,
    nrrd_installed_workflow,
    probe_nrrd,
    roundtrip,
    write_nrrd,
)
from nrrd.exceptions import NrrdParseError
from nrrd.models import NrrdDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "nrrd"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestProbe:
    def test_probe_valid_1d_int8(self):
        assert probe_nrrd(VALID_DIR / "1d-int8.nrrd") is True

    def test_probe_valid_2d_float32(self):
        assert probe_nrrd(VALID_DIR / "2d-float32.nrrd") is True

    def test_probe_valid_gzip_encoded(self):
        assert probe_nrrd(VALID_DIR / "gzip-encoded.nrrd") is True

    def test_probe_invalid_bad_magic(self):
        assert probe_nrrd(INVALID_DIR / "bad-magic.nrrd") is False

    def test_probe_nonexistent_file(self):
        assert probe_nrrd("/nonexistent/file.nrrd") is False

    def test_probe_random_bytes(self):
        assert probe_nrrd(b"\x00\x01\x02\x03") is False

    def test_probe_empty(self):
        assert probe_nrrd(b"") is False

    def test_probe_synthetic_valid(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n\n\x00\x01\x02\x03"
        assert probe_nrrd(data) is True


class TestLoad:
    def test_load_1d_int8(self):
        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        assert isinstance(model, dict)
        assert "version" in model
        assert "header" in model
        assert model["header"].get("type") in ("int8", "signed char")

    def test_load_2d_float32(self):
        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        assert "dimension" in model["header"]

    def test_load_gzip_encoded(self):
        model = load_nrrd(VALID_DIR / "gzip-encoded.nrrd")
        encoding = model["header"].get("encoding", "")
        assert encoding in ("gzip", "gz")
        assert model["data_size"] > 0

    def test_load_invalid_raises(self):
        with pytest.raises(NrrdParseError):
            load_nrrd(INVALID_DIR / "bad-magic.nrrd")

    def test_load_from_bytes(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n\n\x00\x01\x02\x03"
        model = load_nrrd(data)
        assert model["version"] == 4
        assert model["element_count"] == 4


class TestWrite:
    def test_write_returns_bytes(self):
        model = {
            "version": 4,
            "header": {"type": "uint8", "dimension": "1", "sizes": "4", "encoding": "raw"},
        }
        result = write_nrrd(model)
        assert isinstance(result, bytes)
        assert result.startswith(b"NRRD0004")

    def test_write_to_file(self):
        model = {
            "version": 4,
            "header": {"type": "uint8", "dimension": "1", "sizes": "3", "encoding": "raw"},
        }
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            dest = f.name
        try:
            write_nrrd(model, dest)
            assert Path(dest).exists()
            assert Path(dest).stat().st_size > 0
        finally:
            Path(dest).unlink(missing_ok=True)


class TestRoundtrip:
    def test_roundtrip_1d_int8(self):
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            dest = f.name
        try:
            original = load_nrrd(VALID_DIR / "1d-int8.nrrd")
            reloaded = roundtrip(VALID_DIR / "1d-int8.nrrd", dest)
            assert original["header"]["type"] == reloaded["header"]["type"]
            # TC-S6P4-PROD-001 (select-6 Phase 4, closes D1): the whole point
            # of roundtrip() is proving data survives, not just header
            # fields -- a prior bug zero-filled the payload here while this
            # exact assertion was absent, so it shipped undetected.
            assert reloaded["array"] == original["array"] == [1, 2, 3, 4]
        finally:
            Path(dest).unlink(missing_ok=True)

    def test_roundtrip_never_zero_fills_when_array_present(self):
        """D1 regression: write_nrrd(model, dest) -- the exact call roundtrip()
        makes -- must re-encode the model's decoded array, not silently
        zero-fill it. Reproduces the precise before/after from the audit:
        orig['array'] == [1,2,3,4] used to reload as [0,0,0,0]."""
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            dest = f.name
        try:
            model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
            assert model["array"] == [1, 2, 3, 4]
            write_nrrd(model, dest)  # no explicit data= -- this is the bug's exact trigger
            reloaded = load_nrrd(dest)
            assert reloaded["array"] == [1, 2, 3, 4]
            assert reloaded["array"] != [0, 0, 0, 0]
        finally:
            Path(dest).unlink(missing_ok=True)

    def test_roundtrip_2d_float32_preserves_values(self):
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            dest = f.name
        try:
            original = load_nrrd(VALID_DIR / "2d-float32.nrrd")
            reloaded = roundtrip(VALID_DIR / "2d-float32.nrrd", dest)
            assert reloaded["array"] == pytest.approx(original["array"])
            assert any(v != 0 for v in original["array"]), (
                "fixture must contain non-zero values or this test can't "
                "distinguish a real fix from the zero-fill bug")
        finally:
            Path(dest).unlink(missing_ok=True)

    def test_roundtrip_gzip_encoded_preserves_values(self):
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            dest = f.name
        try:
            original = load_nrrd(VALID_DIR / "gzip-encoded.nrrd")
            reloaded = roundtrip(VALID_DIR / "gzip-encoded.nrrd", dest)
            assert reloaded["array"] == original["array"]
            assert any(v != 0 for v in original["array"])
        finally:
            Path(dest).unlink(missing_ok=True)

    def test_write_nrrd_falls_back_to_zero_fill_without_array(self):
        """No decoded array available (hand-built model) -- zero-fill
        fallback is still correct and intentional, not a regression."""
        model = {
            "version": 4,
            "header": {"type": "uint8", "dimension": "1", "sizes": "3", "encoding": "raw"},
        }
        result = write_nrrd(model)
        payload = result.split(b"\n\n", 1)[1]
        assert payload == b"\x00\x00\x00"


class TestHelpers:
    def test_get_dimension(self):
        model = {"header": {"dimension": "3"}}
        assert get_dimension(model) == 3

    def test_get_encoding(self):
        model = {"header": {"encoding": "gzip"}}
        assert get_encoding(model) == "gzip"


class TestModel:
    def test_nrrd_document(self):
        data = {
            "version": 4,
            "header": {"type": "float", "dimension": "2", "sizes": "3 4", "encoding": "raw"},
            "data_size": 48,
            "element_count": 12,
        }
        doc = NrrdDocument(data)
        assert doc.version == 4
        assert doc.dimension == 2
        assert doc.encoding == "raw"
        assert doc.sizes == [3, 4]
        assert not doc.is_empty
        assert repr(doc) == "NrrdDocument(version=4, encoding='raw')"


class TestImport:
    def test_import_probe_load(self):
        from nrrd import probe, load
        assert callable(probe)
        assert callable(load)

    def test_import_write(self):
        from nrrd import write
        assert callable(write)

    def test_installed_workflow(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n\n\x00\x01"
        result = nrrd_installed_workflow(data)
        assert result["format"] == "nrrd"
        assert result["loaded"] is True
