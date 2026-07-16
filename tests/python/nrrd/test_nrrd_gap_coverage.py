"""NRRD gap-ledger coverage — explicit tests for every gap-listed capability.

Targets: probe_nrrd, decode_nrrd_data, get_array, get_dimension, get_encoding,
load_nrrd, nrrd_installed_workflow, reshape_nrrd_array, write_nrrd,
NrrdDocument, NrrdError, NrrdParseError, NrrdWriteError,
nrrd_axis_sizes, nrrd_element_count, nrrd_is_compressed, nrrd_kinds, nrrd_to_array.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from nrrd import (
    NrrdDocument,
    NrrdError,
    NrrdParseError,
    NrrdWriteError,
    decode_nrrd_data,
    get_array,
    get_dimension,
    get_encoding,
    load_nrrd,
    nrrd_installed_workflow,
    probe_nrrd,
    reshape_nrrd_array,
    roundtrip,
    write_nrrd,
    nrrd_axis_sizes,
    nrrd_element_count,
    nrrd_is_compressed,
    nrrd_kinds,
    nrrd_to_array,
)

SAMPLES = _REPO / "samples" / "by-format" / "nrrd" / "valid"
SYNTH_1D = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n\n\x01\x02\x03\x04"


class TestProbeNrrd:
    def test_probe_valid_returns_true(self):
        result = probe_nrrd(SAMPLES / "1d-int8.nrrd")
        assert result is True

    def test_probe_invalid_returns_false(self):
        result = probe_nrrd(b"not an nrrd file")
        assert result is False

    def test_probe_bytes_source(self):
        result = probe_nrrd(SYNTH_1D)
        assert result is True

    def test_probe_all_samples(self):
        for sample in SAMPLES.glob("*.nrrd"):
            assert probe_nrrd(sample) is True, f"probe failed for {sample.name}"


class TestLoadNrrd:
    def test_load_returns_dict(self):
        model = load_nrrd(SAMPLES / "1d-int8.nrrd")
        assert isinstance(model, dict)
        assert "header" in model

    def test_load_bytes(self):
        model = load_nrrd(SYNTH_1D)
        assert model["header"]["type"] == "uint8"

    def test_load_has_version(self):
        model = load_nrrd(SAMPLES / "1d-int8.nrrd")
        assert model.get("version", 0) > 0

    def test_load_2d_float32(self):
        model = load_nrrd(SAMPLES / "2d-float32.nrrd")
        assert "2" in model["header"].get("dimension", "")


class TestWriteNrrd:
    def test_write_returns_bytes(self):
        model = load_nrrd(SYNTH_1D)
        result = write_nrrd(model)
        assert isinstance(result, bytes)
        assert result.startswith(b"NRRD")

    def test_write_to_file(self):
        model = load_nrrd(SYNTH_1D)
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_nrrd(model, tmp)
            assert tmp.exists()
            reloaded = load_nrrd(tmp)
            assert reloaded["header"]["type"] == model["header"]["type"]
        finally:
            tmp.unlink(missing_ok=True)

    def test_roundtrip_preserves_header(self):
        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            tmp = Path(f.name)
        try:
            result = roundtrip(SAMPLES / "1d-int8.nrrd", tmp)
            assert isinstance(result, dict)
            assert "type" in result["header"]
        finally:
            tmp.unlink(missing_ok=True)


class TestDecodeNrrdData:
    def test_decode_uint8(self):
        payload = bytes([10, 20, 30])
        result = decode_nrrd_data("uint8", [3], payload)
        assert result == [10, 20, 30]

    def test_decode_int16(self):
        import struct
        payload = struct.pack("<3h", -1, 0, 1)
        result = decode_nrrd_data("int16", [3], payload, endian="little")
        assert result == [-1, 0, 1]

    def test_decode_empty(self):
        assert decode_nrrd_data("uint8", [0], b"") == []


class TestGetArray:
    def test_get_array_1d(self):
        model = load_nrrd(SAMPLES / "1d-int8.nrrd")
        arr = get_array(model)
        assert isinstance(arr, list)
        assert len(arr) == 4

    def test_get_array_2d_is_nested(self):
        model = load_nrrd(SAMPLES / "2d-float32.nrrd")
        arr = get_array(model)
        assert arr is not None
        assert isinstance(arr, list)
        assert isinstance(arr[0], list)


class TestReshapeNrrdArray:
    def test_reshape_1d(self):
        assert reshape_nrrd_array([1, 2, 3], [3]) == [1, 2, 3]

    def test_reshape_2d(self):
        result = reshape_nrrd_array([1, 2, 3, 4, 5, 6], [2, 3])
        assert len(result) == 3
        assert len(result[0]) == 2

    def test_reshape_3d(self):
        flat = list(range(24))
        result = reshape_nrrd_array(flat, [2, 3, 4])
        assert len(result) == 4
        assert len(result[0]) == 3
        assert len(result[0][0]) == 2


class TestGetDimensionEncoding:
    def test_get_dimension(self):
        model = load_nrrd(SAMPLES / "1d-int8.nrrd")
        assert get_dimension(model) == 1

    def test_get_dimension_2d(self):
        model = load_nrrd(SAMPLES / "2d-float32.nrrd")
        assert get_dimension(model) == 2

    def test_get_encoding_raw(self):
        model = load_nrrd(SAMPLES / "1d-int8.nrrd")
        assert get_encoding(model) == "raw"

    def test_get_encoding_gzip(self):
        model = load_nrrd(SAMPLES / "gzip-encoded.nrrd")
        assert get_encoding(model) == "gzip"


class TestNrrdDocument:
    def test_from_file(self):
        doc = NrrdDocument.from_file(str(SAMPLES / "1d-int8.nrrd"))
        assert doc.version > 0

    def test_header_property(self):
        doc = NrrdDocument(load_nrrd(SYNTH_1D))
        assert doc.header["type"] == "uint8"

    def test_dimension_property(self):
        doc = NrrdDocument(load_nrrd(SYNTH_1D))
        assert doc.dimension == 1

    def test_encoding_property(self):
        doc = NrrdDocument(load_nrrd(SYNTH_1D))
        assert doc.encoding == "raw"

    def test_sizes_property(self):
        doc = NrrdDocument(load_nrrd(SYNTH_1D))
        assert doc.sizes == [4]

    def test_raw_property(self):
        data = load_nrrd(SYNTH_1D)
        doc = NrrdDocument(data)
        assert doc.raw is data

    def test_to_dict(self):
        data = load_nrrd(SYNTH_1D)
        doc = NrrdDocument(data)
        d = doc.to_dict()
        assert isinstance(d, dict)
        assert d is not data

    def test_to_array(self):
        doc = NrrdDocument(load_nrrd(SAMPLES / "1d-int8.nrrd"))
        arr = doc.to_array()
        assert isinstance(arr, list)

    def test_repr(self):
        doc = NrrdDocument(load_nrrd(SYNTH_1D))
        assert "NrrdDocument" in repr(doc)

    def test_nrrd_type(self):
        doc = NrrdDocument(load_nrrd(SYNTH_1D))
        assert doc.nrrd_type == "uint8"


class TestErrorClasses:
    def test_nrrd_error_is_exception(self):
        assert issubclass(NrrdError, Exception)

    def test_parse_error_inherits_nrrd_error(self):
        assert issubclass(NrrdParseError, NrrdError)

    def test_write_error_inherits_nrrd_error(self):
        assert issubclass(NrrdWriteError, NrrdError)

    def test_parse_error_instantiation(self):
        err = NrrdParseError("bad data")
        assert str(err) == "bad data"

    def test_write_error_instantiation(self):
        err = NrrdWriteError("write failed")
        assert str(err) == "write failed"

    def test_parse_error_catchable_as_base(self):
        with pytest.raises(NrrdError):
            raise NrrdParseError("test")

    def test_write_error_catchable_as_base(self):
        with pytest.raises(NrrdError):
            raise NrrdWriteError("test")


class TestAnalytics:
    def test_axis_sizes_1d(self):
        assert nrrd_axis_sizes(SAMPLES / "1d-int8.nrrd") == [4]

    def test_is_compressed_raw(self):
        assert nrrd_is_compressed(SAMPLES / "1d-int8.nrrd") is False

    def test_is_compressed_gzip(self):
        assert nrrd_is_compressed(SAMPLES / "gzip-encoded.nrrd") is True

    def test_element_count(self):
        assert nrrd_element_count(SAMPLES / "1d-int8.nrrd") == 4

    def test_element_count_2d(self):
        assert nrrd_element_count(SAMPLES / "2d-float32.nrrd") == 6

    def test_kinds_empty_when_absent(self):
        assert nrrd_kinds(SYNTH_1D) == []

    def test_kinds_with_header(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 3\nencoding: raw\nkinds: RGB-color\n\n\x00\x01\x02"
        assert nrrd_kinds(data) == ["RGB-color"]

    def test_to_array_1d(self):
        result = nrrd_to_array(SAMPLES / "1d-int8.nrrd")
        assert isinstance(result, list)
        assert len(result) == 4

    def test_to_array_bytes(self):
        result = nrrd_to_array(SYNTH_1D)
        assert result == [1, 2, 3, 4]


class TestInstalledWorkflow:
    def test_installed_workflow_returns_dict(self):
        result = nrrd_installed_workflow(SAMPLES / "1d-int8.nrrd")
        assert isinstance(result, dict)
