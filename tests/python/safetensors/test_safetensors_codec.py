"""Core tests for the safetensors codec — probe, load, write, roundtrip."""

from __future__ import annotations

import json
import struct
import tempfile
from pathlib import Path

import pytest

from safetensors.safetensors_codec import (
    get_tensor_count,
    get_tensor_names,
    load_safetensors,
    probe_safetensors,
    roundtrip,
    safetensors_installed_workflow,
    write_safetensors,
)
from safetensors.exceptions import SafetensorsParseError
from safetensors.models import SafetensorsDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "safetensors"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestProbe:
    def test_probe_valid_single_tensor(self):
        assert probe_safetensors(VALID_DIR / "single-tensor.safetensors") is True

    def test_probe_valid_multi_tensor(self):
        assert probe_safetensors(VALID_DIR / "multi-tensor.safetensors") is True

    def test_probe_valid_with_metadata(self):
        assert probe_safetensors(VALID_DIR / "with-metadata.safetensors") is True

    def test_probe_invalid_bad_header(self):
        assert probe_safetensors(INVALID_DIR / "bad-header-length.safetensors") is False

    def test_probe_nonexistent_file(self):
        assert probe_safetensors("/nonexistent/file.safetensors") is False

    def test_probe_random_bytes(self):
        assert probe_safetensors(b"\x00\x01\x02\x03") is False

    def test_probe_empty_bytes(self):
        assert probe_safetensors(b"") is False

    def test_probe_too_short(self):
        assert probe_safetensors(b"\x00\x00\x00") is False

    def test_probe_valid_json_but_no_tensor_keys(self):
        header = json.dumps({"not_a_tensor": "value"}).encode("utf-8")
        data = struct.pack("<Q", len(header)) + header
        assert probe_safetensors(data) is False


class TestLoad:
    def test_load_single_tensor(self):
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        assert isinstance(model, dict)
        assert "tensors" in model
        assert "header_size" in model
        assert len(model["tensors"]) >= 1

    def test_load_multi_tensor(self):
        model = load_safetensors(VALID_DIR / "multi-tensor.safetensors")
        assert len(model["tensors"]) >= 2

    def test_load_with_metadata(self):
        model = load_safetensors(VALID_DIR / "with-metadata.safetensors")
        assert isinstance(model.get("metadata"), dict)

    def test_load_tensor_has_required_keys(self):
        model = load_safetensors(VALID_DIR / "single-tensor.safetensors")
        for name, info in model["tensors"].items():
            assert "dtype" in info
            assert "shape" in info
            assert "data_offsets" in info

    def test_load_invalid_raises(self):
        with pytest.raises(SafetensorsParseError):
            load_safetensors(INVALID_DIR / "bad-header-length.safetensors")

    def test_load_from_bytes(self):
        header = json.dumps({"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]}}).encode("utf-8")
        data = struct.pack("<Q", len(header)) + header + b"\x00" * 8
        model = load_safetensors(data)
        assert "w" in model["tensors"]
        assert model["tensors"]["w"]["dtype"] == "F32"


class TestWrite:
    def test_write_returns_bytes(self):
        model = {"tensors": {"w": {"dtype": "F32", "shape": [3], "data_offsets": [0, 12]}}, "metadata": {}}
        result = write_safetensors(model)
        assert isinstance(result, bytes)
        assert len(result) > 8

    def test_write_to_file(self):
        model = {"tensors": {"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]}}, "metadata": {}}
        with tempfile.NamedTemporaryFile(suffix=".safetensors", delete=False) as f:
            dest = f.name
        try:
            write_safetensors(model, dest)
            assert Path(dest).exists()
            assert Path(dest).stat().st_size > 8
        finally:
            Path(dest).unlink(missing_ok=True)

    def test_write_valid_header(self):
        model = {"tensors": {"x": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16]}}, "metadata": {}}
        result = write_safetensors(model)
        header_len = struct.unpack("<Q", result[:8])[0]
        header = json.loads(result[8:8 + header_len])
        assert "x" in header
        assert header["x"]["dtype"] == "F32"


class TestRoundtrip:
    def test_roundtrip_single_tensor(self):
        with tempfile.NamedTemporaryFile(suffix=".safetensors", delete=False) as f:
            dest = f.name
        try:
            original = load_safetensors(VALID_DIR / "single-tensor.safetensors")
            reloaded = roundtrip(VALID_DIR / "single-tensor.safetensors", dest)
            assert set(original["tensors"].keys()) == set(reloaded["tensors"].keys())
        finally:
            Path(dest).unlink(missing_ok=True)


class TestHelpers:
    def test_get_tensor_count(self):
        model = {"tensors": {"a": {}, "b": {}, "c": {}}}
        assert get_tensor_count(model) == 3

    def test_get_tensor_names(self):
        model = {"tensors": {"z": {}, "a": {}, "m": {}}}
        assert get_tensor_names(model) == ["a", "m", "z"]


class TestModel:
    def test_safetensors_document(self):
        data = {
            "header_size": 100,
            "tensors": {"weight": {"dtype": "F32", "shape": [3, 4], "data_offsets": [0, 48]}},
            "metadata": {"format": "pt"},
        }
        doc = SafetensorsDocument(data)
        assert doc.tensor_count == 1
        assert doc.tensor_names == ["weight"]
        assert doc.metadata == {"format": "pt"}
        assert not doc.is_empty
        assert repr(doc) == "SafetensorsDocument(tensors=1)"


class TestImport:
    def test_import_probe_load(self):
        from safetensors import probe, load
        assert callable(probe)
        assert callable(load)

    def test_import_write(self):
        from safetensors import write
        assert callable(write)

    def test_installed_workflow(self):
        header = json.dumps({"t": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}}).encode("utf-8")
        data = struct.pack("<Q", len(header)) + header + b"\x00" * 4
        result = safetensors_installed_workflow(data)
        assert result["format"] == "safetensors"
        assert result["loaded"] is True
        assert result["tensor_count"] == 1
