"""Tests for mtlx.spec stub classes and mtlx.Compat facade classes.

Verifies: spec_qname/spec_fact_ref/namespace_uri bindings match
shared/qname-registry/mtlx.yaml exactly, facade subclassing, and
read-only property correctness for Material and NodeGraph.
"""

from __future__ import annotations

import pytest


class TestSmokeImports:
    def test_import_spec_package(self):
        from mtlx import spec

        assert hasattr(spec, "Material")
        assert hasattr(spec, "NodeGraph")

    def test_import_compat_package(self):
        from mtlx import Compat

        assert hasattr(Compat, "MtlxMaterial")
        assert hasattr(Compat, "MtlxNodeGraph")

    def test_import_from_package_root(self):
        from mtlx import MtlxMaterial, MtlxNodeGraph

        assert MtlxMaterial is not None
        assert MtlxNodeGraph is not None

    def test_exceptions_hierarchy(self):
        from mtlx.exceptions import MtlxError, MtlxParseError, MtlxWriteError

        assert issubclass(MtlxParseError, MtlxError)
        assert issubclass(MtlxWriteError, MtlxError)

    def test_mtlx_document_from_file_smoke(self):
        from pathlib import Path

        from mtlx.models import MtlxDocument

        samples = (
            Path(__file__).resolve().parents[3]
            / "samples"
            / "by-format"
            / "mtlx"
            / "valid"
            / "simple-material.mtlx"
        )
        doc = MtlxDocument.from_file(str(samples))
        assert doc.material_count == 1


class TestMaterialSpecStub:
    def test_spec_qname_matches_registry(self):
        from mtlx.spec.element.material import Material

        assert Material.spec_qname == "materialx:material"

    def test_spec_fact_ref_matches_registry(self):
        from mtlx.spec.element.material import Material

        assert Material.spec_fact_ref == "FACT-MTLX-003"

    def test_namespace_uri_matches_registry(self):
        from mtlx.spec.element.material import Material

        assert Material.namespace_uri == "urn:format:materialx:1.39"

    def test_local_name(self):
        from mtlx.spec.element.material import Material

        assert Material.local_name == "surfacematerial"

    def test_facade_names(self):
        from mtlx.spec.element.material import Material

        assert Material.facade_names == ["MtlxMaterial"]

    def test_name_property(self):
        from mtlx.spec.element.material import Material

        m = Material({"name": "brushed_metal", "inputs": []})
        assert m.name == "brushed_metal"

    def test_inputs_property(self):
        from mtlx.spec.element.material import Material

        m = Material({"name": "m", "inputs": [{"name": "surfaceshader"}]})
        assert m.input_count == 1

    def test_to_dict_returns_copy(self):
        from mtlx.spec.element.material import Material

        data = {"name": "m", "inputs": []}
        m = Material(data)
        copy = m.to_dict()
        copy["name"] = "mutated"
        assert m.name == "m"

    def test_repr(self):
        from mtlx.spec.element.material import Material

        m = Material({"name": "m", "inputs": []})
        assert "Material(" in repr(m)


class TestNodeGraphSpecStub:
    def test_spec_qname_matches_registry(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        assert NodeGraph.spec_qname == "materialx:nodegraph"

    def test_spec_fact_ref_matches_registry(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        assert NodeGraph.spec_fact_ref == "FACT-MTLX-002"

    def test_namespace_uri_matches_registry(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        assert NodeGraph.namespace_uri == "urn:format:materialx:1.39"

    def test_local_name(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        assert NodeGraph.local_name == "nodegraph"

    def test_facade_names(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        assert NodeGraph.facade_names == ["MtlxNodeGraph"]

    def test_node_count_property(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        ng = NodeGraph({"name": "g", "nodes": [{"name": "n1"}, {"name": "n2"}], "outputs": []})
        assert ng.node_count == 2

    def test_is_empty_true_when_no_nodes(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        ng = NodeGraph({"name": "g", "nodes": [], "outputs": []})
        assert ng.is_empty is True

    def test_is_empty_false_when_nodes_present(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        ng = NodeGraph({"name": "g", "nodes": [{"name": "n1"}], "outputs": []})
        assert ng.is_empty is False

    def test_repr(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        ng = NodeGraph({"name": "g", "nodes": [], "outputs": []})
        assert "NodeGraph(" in repr(ng)

    def test_to_dict_returns_copy(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        data = {"name": "g", "nodes": [{"name": "n1"}], "outputs": []}
        ng = NodeGraph(data)
        copy = ng.to_dict()
        copy["name"] = "mutated"
        assert ng.name == "g"


class TestMtlxMaterialFacade:
    def test_subclasses_spec_stub(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial
        from mtlx.spec.element.material import Material

        assert issubclass(MtlxMaterial, Material)

    def test_spec_qname_binding(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial

        assert MtlxMaterial.spec_qname == "materialx:material"

    def test_spec_fact_ref_binding(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial

        assert MtlxMaterial.spec_fact_ref == "FACT-MTLX-003"

    def test_namespace_uri_binding(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial

        assert MtlxMaterial.namespace_uri == "urn:format:materialx:1.39"

    def test_facade_behaves_like_spec_stub(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial

        m = MtlxMaterial(
            {"name": "connected", "inputs": [{"name": "surfaceshader", "nodename": "sh1"}]}
        )
        assert m.has_surfaceshader_input is True
        assert m.shader_nodename == "sh1"

    def test_facade_from_real_sample_data(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial
        from mtlx.mtlx_codec import load_mtlx

        model = load_mtlx(
            __import__("pathlib").Path(__file__).resolve().parents[3]
            / "samples"
            / "by-format"
            / "mtlx"
            / "valid"
            / "simple-material.mtlx"
        )
        facade = MtlxMaterial(model["materials"][0])
        assert facade.name == "simple_mat"

    def test_facade_to_dict_roundtrips_real_data(self):
        from mtlx.Compat.mtlx_material import MtlxMaterial
        from mtlx.mtlx_codec import load_mtlx

        model = load_mtlx(
            __import__("pathlib").Path(__file__).resolve().parents[3]
            / "samples"
            / "by-format"
            / "mtlx"
            / "valid"
            / "simple-material.mtlx"
        )
        original = model["materials"][0]
        facade = MtlxMaterial(original)
        assert facade.to_dict() == original
        assert facade.to_dict() is not original


class TestMtlxNodeGraphFacade:
    def test_subclasses_spec_stub(self):
        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph
        from mtlx.spec.element.nodegraph import NodeGraph

        assert issubclass(MtlxNodeGraph, NodeGraph)

    def test_spec_qname_binding(self):
        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph

        assert MtlxNodeGraph.spec_qname == "materialx:nodegraph"

    def test_spec_fact_ref_binding(self):
        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph

        assert MtlxNodeGraph.spec_fact_ref == "FACT-MTLX-002"

    def test_namespace_uri_binding(self):
        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph

        assert MtlxNodeGraph.namespace_uri == "urn:format:materialx:1.39"

    def test_facade_behaves_like_spec_stub(self):
        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph

        ng = MtlxNodeGraph({"name": "g", "nodes": [{"name": "n1"}], "outputs": []})
        assert ng.node_count == 1

    def test_facade_from_real_sample_data(self):
        from pathlib import Path

        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph
        from mtlx.mtlx_codec import load_mtlx

        model = load_mtlx(
            Path(__file__).resolve().parents[3]
            / "samples"
            / "by-format"
            / "mtlx"
            / "valid"
            / "node-graph.mtlx"
        )
        facade = MtlxNodeGraph(model["node_graphs"][0])
        assert facade.name == "my_graph"
        assert facade.node_count == 2

    def test_facade_to_dict_roundtrips_real_data(self):
        from pathlib import Path

        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph
        from mtlx.mtlx_codec import load_mtlx

        model = load_mtlx(
            Path(__file__).resolve().parents[3]
            / "samples"
            / "by-format"
            / "mtlx"
            / "valid"
            / "node-graph.mtlx"
        )
        original = model["node_graphs"][0]
        facade = MtlxNodeGraph(original)
        assert facade.to_dict() == original
        assert facade.to_dict() is not original


class TestSpecStubsFromRealSamples:
    """L1 unit: Material/NodeGraph spec stubs built directly from load_mtlx() on real fixture files."""

    def test_material_from_simple_material_sample(self):
        from pathlib import Path

        from mtlx.mtlx_codec import load_mtlx
        from mtlx.spec.element.material import Material

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx" / "valid"
        model = load_mtlx(samples / "simple-material.mtlx")
        m = Material(model["materials"][0])
        assert m.name == "simple_mat"

    def test_material_from_multi_material_sample_count(self):
        from pathlib import Path

        from mtlx.mtlx_codec import load_mtlx
        from mtlx.spec.element.material import Material

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx" / "valid"
        model = load_mtlx(samples / "multi-material.mtlx")
        materials = [Material(entry) for entry in model["materials"]]
        assert len(materials) == 3
        assert all(isinstance(m.name, str) and m.name for m in materials)

    def test_nodegraph_from_node_graph_sample(self):
        from pathlib import Path

        from mtlx.mtlx_codec import load_mtlx
        from mtlx.spec.element.nodegraph import NodeGraph

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx" / "valid"
        model = load_mtlx(samples / "node-graph.mtlx")
        ng = NodeGraph(model["node_graphs"][0])
        assert ng.name == "my_graph"
        assert ng.is_empty is False

    def test_load_mtlx_returns_expected_top_level_keys(self):
        from pathlib import Path

        from mtlx.mtlx_codec import load_mtlx

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx" / "valid"
        model = load_mtlx(samples / "simple-material.mtlx")
        assert set(model.keys()) >= {"version", "materials", "node_graphs", "nodes"}
        assert model["version"] == "1.39"

    def test_load_mtlx_multi_material_has_no_node_graphs(self):
        from pathlib import Path

        from mtlx.mtlx_codec import load_mtlx

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx" / "valid"
        model = load_mtlx(samples / "multi-material.mtlx")
        assert model["node_graphs"] == []

    def test_load_mtlx_node_graph_sample_has_no_materials(self):
        from pathlib import Path

        from mtlx.mtlx_codec import load_mtlx

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx" / "valid"
        model = load_mtlx(samples / "node-graph.mtlx")
        assert model["materials"] == []


class TestFacadeEdgeCases:
    """L3 edge cases: malformed/boundary inputs for spec stubs and facades."""

    def test_material_with_no_inputs_key(self):
        from mtlx.spec.element.material import Material

        m = Material({"name": "bare"})
        assert m.inputs == []
        assert m.has_surfaceshader_input is False
        assert m.shader_nodename == ""

    def test_material_with_missing_name_key(self):
        from mtlx.spec.element.material import Material

        m = Material({})
        assert m.name == ""

    def test_nodegraph_with_no_nodes_key(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        ng = NodeGraph({"name": "empty"})
        assert ng.node_count == 0
        assert ng.is_empty is True

    def test_nodegraph_with_missing_name_key(self):
        from mtlx.spec.element.nodegraph import NodeGraph

        ng = NodeGraph({})
        assert ng.name == ""

    def test_facade_qname_mismatch_would_fail_assertion(self):
        # Guard test: proves the qname check is meaningful, not a tautology.
        from mtlx.Compat.mtlx_material import MtlxMaterial
        from mtlx.Compat.mtlx_nodegraph import MtlxNodeGraph

        assert MtlxMaterial.spec_qname != MtlxNodeGraph.spec_qname
        assert MtlxMaterial.spec_fact_ref != MtlxNodeGraph.spec_fact_ref
