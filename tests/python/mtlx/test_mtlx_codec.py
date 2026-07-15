"""Core tests for the mtlx codec — probe, load, write, roundtrip."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from mtlx.mtlx_codec import (
    get_material_count,
    get_node_graph_count,
    load_mtlx,
    mtlx_installed_workflow,
    probe_mtlx,
    roundtrip,
    write_mtlx,
)
from mtlx.exceptions import MtlxParseError
from mtlx.models import MtlxDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestProbe:
    def test_probe_valid_simple_material(self):
        assert probe_mtlx(VALID_DIR / "simple-material.mtlx") is True

    def test_probe_valid_node_graph(self):
        assert probe_mtlx(VALID_DIR / "node-graph.mtlx") is True

    def test_probe_valid_multi_material(self):
        assert probe_mtlx(VALID_DIR / "multi-material.mtlx") is True

    def test_probe_invalid_wrong_root(self):
        assert probe_mtlx(INVALID_DIR / "wrong-root.mtlx") is False

    def test_probe_nonexistent_file(self):
        assert probe_mtlx("/nonexistent/file.mtlx") is False

    def test_probe_random_bytes(self):
        assert probe_mtlx(b"not xml") is False

    def test_probe_empty(self):
        assert probe_mtlx(b"") is False

    def test_probe_non_materialx_xml(self):
        assert probe_mtlx(b'<?xml version="1.0"?><root/>') is False


class TestLoad:
    def test_load_simple_material(self):
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        assert isinstance(model, dict)
        assert "version" in model
        assert "materials" in model

    def test_load_node_graph(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        assert len(model.get("node_graphs", [])) >= 1

    def test_load_multi_material(self):
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        assert len(model.get("materials", [])) >= 2

    def test_load_material_has_inputs(self):
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        if model["materials"]:
            mat = model["materials"][0]
            assert "inputs" in mat

    def test_load_invalid_raises(self):
        with pytest.raises(MtlxParseError, match="Not a MaterialX"):
            load_mtlx(INVALID_DIR / "wrong-root.mtlx")

    def test_load_bad_xml_raises(self):
        with pytest.raises(MtlxParseError, match="Invalid XML"):
            load_mtlx(b"<not>closed xml")

    def test_load_from_bytes(self):
        xml = b'<?xml version="1.0"?><materialx version="1.39"><surfacematerial name="test"/></materialx>'
        model = load_mtlx(xml)
        assert model["version"] == "1.39"
        assert len(model["materials"]) == 1


class TestWrite:
    def test_write_returns_xml_string(self):
        model = {
            "version": "1.39",
            "materials": [{"name": "mymat", "inputs": []}],
            "node_graphs": [],
            "nodes": [],
        }
        result = write_mtlx(model)
        assert "materialx" in result
        assert "mymat" in result

    def test_write_to_file(self):
        model = {
            "version": "1.39",
            "materials": [{"name": "test_mat", "inputs": []}],
            "node_graphs": [],
            "nodes": [],
        }
        with tempfile.NamedTemporaryFile(suffix=".mtlx", delete=False) as f:
            dest = f.name
        try:
            write_mtlx(model, dest)
            content = Path(dest).read_text(encoding="utf-8")
            assert "test_mat" in content
        finally:
            Path(dest).unlink(missing_ok=True)


class TestRoundtrip:
    def test_roundtrip_simple_material(self):
        with tempfile.NamedTemporaryFile(suffix=".mtlx", delete=False) as f:
            dest = f.name
        try:
            original = load_mtlx(VALID_DIR / "simple-material.mtlx")
            reloaded = roundtrip(VALID_DIR / "simple-material.mtlx", dest)
            assert original["version"] == reloaded["version"]
            assert len(original["materials"]) == len(reloaded["materials"])
        finally:
            Path(dest).unlink(missing_ok=True)


class TestHelpers:
    def test_get_material_count(self):
        model = {"materials": [{"name": "a"}, {"name": "b"}]}
        assert get_material_count(model) == 2

    def test_get_node_graph_count(self):
        model = {"node_graphs": [{"name": "ng1"}]}
        assert get_node_graph_count(model) == 1


class TestModel:
    def test_mtlx_document(self):
        data = {
            "version": "1.39",
            "materials": [{"name": "mat1", "inputs": []}, {"name": "mat2", "inputs": []}],
            "node_graphs": [{"name": "ng1", "nodes": [], "outputs": []}],
            "nodes": [],
        }
        doc = MtlxDocument(data)
        assert doc.version == "1.39"
        assert doc.material_count == 2
        assert doc.node_graph_count == 1
        assert not doc.is_empty
        assert repr(doc) == "MtlxDocument(version='1.39', materials=2)"


class TestImport:
    def test_import_probe_load(self):
        from mtlx import probe, load
        assert callable(probe)
        assert callable(load)

    def test_import_write(self):
        from mtlx import write
        assert callable(write)

    def test_installed_workflow(self):
        xml = b'<?xml version="1.0"?><materialx version="1.39"><surfacematerial name="m1"/></materialx>'
        result = mtlx_installed_workflow(xml)
        assert result["format"] == "mtlx"
        assert result["loaded"] is True
        assert result["material_count"] == 1
