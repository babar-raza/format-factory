"""Coverage tests for mtlx public-surface functions/classes not already
exercised in depth elsewhere.

The existing suite is thorough for load/write/roundtrip on synthetic
fixtures (test_mtlx_codec.py), the three analytics functions on synthetic
node-graph/material shapes (test_mtlx_analytics.py), connection resolution
(test_mtlx_graph.py), the spec-stub/facade layer (test_mtlx_compat.py,
test_mtlx_compat_generic_facades.py, test_mtlx_material_forms.py), the
generic-bucket write path (test_mtlx_write_completeness.py), mutation
roundtrips (test_mtlx_document_mutation.py), and CSV export
(test_mtlx_to_csv.py).

This module fills the remaining gaps:
  - cli.py's main() entry point (previously had zero test coverage at all)
  - get_material_count / get_node_graph_count against real loaded models
    (existing test_mtlx_codec.py::TestHelpers only uses synthetic dicts)
  - roundtrip() against node-graph.mtlx and multi-material.mtlx (existing
    coverage only exercises simple-material.mtlx)
  - mtlx_installed_workflow against the full sample corpus (existing
    coverage only exercises one synthetic single-material document)
  - write_mtlx's MtlxWriteError raise path on an unwritable destination
    (no existing test drives this branch at all)
  - direct instantiation/catchability/hierarchy of all four exception
    classes (existing coverage only checks the hierarchy, not
    instantiation or message propagation)
  - the full mtlx package __all__ export surface as a single contract test
  - MtlxDocument.raw identity, to_dict copy-isolation, is_empty when a
    node graph (not a material) is present, and from_file against
    multi-material.mtlx / node-graph.mtlx
  - an integration pass that chains probe -> load -> analytics -> graph
    resolution -> facades against the real sample corpus, cross-checking
    independently-computed values against each other
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from mtlx import cli
from mtlx.Compat import MtlxMaterial, MtlxNodeGraph
from mtlx.exceptions import (
    MtlxConnectionError,
    MtlxError,
    MtlxParseError,
    MtlxWriteError,
)
from mtlx.models import MtlxDocument
from mtlx.mtlx_analytics import (
    mtlx_materials_with_shader_count,
    mtlx_node_graph_size,
    mtlx_node_type_histogram,
)
from mtlx.mtlx_codec import (
    get_material_count,
    get_node_graph_count,
    load_mtlx,
    mtlx_installed_workflow,
    probe_mtlx,
    roundtrip,
    write_mtlx,
)
from mtlx.mtlx_graph import get_connected_node, resolve_connections

SAMPLES = _REPO / "samples" / "by-format" / "mtlx"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


# ---------------------------------------------------------------------------
# Package-level __all__ export contract.
# ---------------------------------------------------------------------------
class TestPackageExportSurface:
    def test_all_exports_importable_from_package_root(self):
        import mtlx

        for name in mtlx.__all__:
            assert hasattr(mtlx, name), f"mtlx.__all__ names missing attribute: {name}"

    def test_functions_are_callable(self):
        import mtlx

        for name in (
            "get_material_count",
            "get_node_graph_count",
            "load_mtlx",
            "mtlx_installed_workflow",
            "probe_mtlx",
            "roundtrip",
            "write_mtlx",
            "mtlx_materials_with_shader_count",
            "mtlx_node_graph_size",
            "mtlx_node_type_histogram",
            "get_connected_node",
            "resolve_connections",
        ):
            assert callable(getattr(mtlx, name))

    def test_exception_classes_are_exception_subclasses(self):
        import mtlx

        for name in ("MtlxError", "MtlxParseError", "MtlxWriteError", "MtlxConnectionError"):
            assert issubclass(getattr(mtlx, name), Exception)

    def test_model_classes_are_types(self):
        import mtlx

        for name in ("MtlxDocument", "MtlxMaterial", "MtlxNodeGraph"):
            assert isinstance(getattr(mtlx, name), type)

    def test_aliases_bound_to_underlying_functions(self):
        import mtlx

        assert mtlx.probe is mtlx.probe_mtlx
        assert mtlx.load is mtlx.load_mtlx
        assert mtlx.write is mtlx.write_mtlx

    def test_version_and_track_metadata(self):
        import mtlx

        assert isinstance(mtlx.__version__, str) and mtlx.__version__
        assert mtlx.__track__ == "python-foss"
        assert mtlx.__commercial_ready__ is False


# ---------------------------------------------------------------------------
# get_material_count / get_node_graph_count — real loaded models (existing
# test_mtlx_codec.py::TestHelpers only covers synthetic dicts).
# ---------------------------------------------------------------------------
class TestGetMaterialCountRealModels:
    def test_simple_material_has_one(self):
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        assert get_material_count(model) == 1

    def test_multi_material_has_three(self):
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        assert get_material_count(model) == 3

    def test_node_graph_sample_has_zero_materials(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        assert get_material_count(model) == 0

    def test_missing_key_defaults_to_zero(self):
        assert get_material_count({}) == 0


class TestGetNodeGraphCountRealModels:
    def test_node_graph_sample_has_one(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        assert get_node_graph_count(model) == 1

    def test_simple_material_has_zero_node_graphs(self):
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        assert get_node_graph_count(model) == 0

    def test_multi_material_has_zero_node_graphs(self):
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        assert get_node_graph_count(model) == 0

    def test_missing_key_defaults_to_zero(self):
        assert get_node_graph_count({}) == 0


# ---------------------------------------------------------------------------
# roundtrip — existing test_mtlx_codec.py::TestRoundtrip only exercises
# simple-material.mtlx. Extend to the node-graph and multi-material fixtures.
# ---------------------------------------------------------------------------
class TestRoundtripAdditionalFixtures:
    def test_roundtrip_node_graph_sample(self):
        original = load_mtlx(VALID_DIR / "node-graph.mtlx")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "node-graph-roundtrip.mtlx"
            reloaded = roundtrip(VALID_DIR / "node-graph.mtlx", dest)
        assert reloaded["version"] == original["version"]
        assert len(reloaded["node_graphs"]) == len(original["node_graphs"]) == 1
        assert reloaded["node_graphs"][0]["name"] == original["node_graphs"][0]["name"]
        assert len(reloaded["node_graphs"][0]["nodes"]) == len(
            original["node_graphs"][0]["nodes"]
        )

    def test_roundtrip_multi_material_sample(self):
        original = load_mtlx(VALID_DIR / "multi-material.mtlx")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "multi-material-roundtrip.mtlx"
            reloaded = roundtrip(VALID_DIR / "multi-material.mtlx", dest)
        assert len(reloaded["materials"]) == len(original["materials"]) == 3
        original_names = {m["name"] for m in original["materials"]}
        reloaded_names = {m["name"] for m in reloaded["materials"]}
        assert original_names == reloaded_names

    def test_roundtrip_returns_dict_matching_load_mtlx_shape(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "shape-check.mtlx"
            result = roundtrip(VALID_DIR / "node-graph.mtlx", dest)
        assert set(result.keys()) >= {"version", "materials", "node_graphs", "nodes"}

    def test_roundtrip_writes_actual_file_to_dest(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "written.mtlx"
            roundtrip(VALID_DIR / "simple-material.mtlx", dest)
            assert dest.exists()
            assert "materialx" in dest.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# mtlx_installed_workflow — existing test_mtlx_codec.py::TestImport only
# exercises one synthetic single-material document.
# ---------------------------------------------------------------------------
class TestMtlxInstalledWorkflowRealSamples:
    def test_simple_material_workflow(self):
        result = mtlx_installed_workflow(VALID_DIR / "simple-material.mtlx")
        assert result["format"] == "mtlx"
        assert result["loaded"] is True
        assert result["version"] == "1.39"
        assert result["material_count"] == 1
        assert result["node_graph_count"] == 0

    def test_multi_material_workflow(self):
        result = mtlx_installed_workflow(VALID_DIR / "multi-material.mtlx")
        assert result["material_count"] == 3
        assert result["node_graph_count"] == 0

    def test_node_graph_workflow(self):
        result = mtlx_installed_workflow(VALID_DIR / "node-graph.mtlx")
        assert result["material_count"] == 0
        assert result["node_graph_count"] == 1

    def test_workflow_keys_exact(self):
        result = mtlx_installed_workflow(VALID_DIR / "simple-material.mtlx")
        assert set(result.keys()) == {
            "format",
            "loaded",
            "version",
            "material_count",
            "node_graph_count",
        }

    def test_workflow_accepts_string_path(self):
        result = mtlx_installed_workflow(str(VALID_DIR / "node-graph.mtlx"))
        assert result["node_graph_count"] == 1

    def test_workflow_raises_on_invalid_source(self):
        with pytest.raises(MtlxParseError):
            mtlx_installed_workflow(INVALID_DIR / "wrong-root.mtlx")

    def test_workflow_material_count_matches_get_material_count(self):
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        result = mtlx_installed_workflow(VALID_DIR / "multi-material.mtlx")
        assert result["material_count"] == get_material_count(model)

    def test_workflow_node_graph_count_matches_get_node_graph_count(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        result = mtlx_installed_workflow(VALID_DIR / "node-graph.mtlx")
        assert result["node_graph_count"] == get_node_graph_count(model)


# ---------------------------------------------------------------------------
# write_mtlx — MtlxWriteError raise path. No existing test drives an actual
# OSError out of the write branch.
# ---------------------------------------------------------------------------
class TestWriteMtlxErrorPath:
    _MODEL = {
        "version": "1.39",
        "materials": [{"name": "m", "inputs": []}],
        "node_graphs": [],
        "nodes": [],
    }

    def test_raises_mtlx_write_error_on_missing_parent_directory(self, tmp_path):
        dest = tmp_path / "nonexistent_subdir" / "out.mtlx"
        with pytest.raises(MtlxWriteError):
            write_mtlx(self._MODEL, dest)

    def test_write_error_message_includes_path(self, tmp_path):
        dest = tmp_path / "nonexistent_subdir" / "out.mtlx"
        with pytest.raises(MtlxWriteError) as exc_info:
            write_mtlx(self._MODEL, dest)
        assert str(dest) in str(exc_info.value)

    def test_write_error_is_catchable_as_mtlx_error(self, tmp_path):
        dest = tmp_path / "nonexistent_subdir" / "out.mtlx"
        with pytest.raises(MtlxError):
            write_mtlx(self._MODEL, dest)

    def test_no_error_when_dest_is_none(self):
        # dest=None must not attempt any filesystem write at all.
        result = write_mtlx(self._MODEL, None)
        assert isinstance(result, str)

    def test_no_error_when_parent_directory_exists(self, tmp_path):
        dest = tmp_path / "ok.mtlx"
        result = write_mtlx(self._MODEL, dest)
        assert dest.exists()
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# probe_mtlx additional edge cases.
# ---------------------------------------------------------------------------
class TestProbeMtlxAdditionalEdgeCases:
    def test_probe_directory_path_does_not_raise(self):
        # A directory is not a readable file; probe_mtlx must swallow the
        # resulting OSError/IsADirectoryError and return False rather than
        # propagating.
        assert probe_mtlx(VALID_DIR) is False

    def test_probe_returns_bool_type(self):
        result = probe_mtlx(VALID_DIR / "simple-material.mtlx")
        assert result is True
        assert isinstance(result, bool)

    def test_probe_case_insensitive_root_tag(self):
        assert probe_mtlx(b'<?xml version="1.0"?><MaterialX version="1.39"/>') is True

    def test_probe_namespaced_root_tag(self):
        xml = b'<?xml version="1.0"?><materialx xmlns="urn:example" version="1.39"/>'
        assert probe_mtlx(xml) is True


# ---------------------------------------------------------------------------
# Exception classes — existing coverage checks issubclass() hierarchy only;
# this adds direct instantiation, message propagation, and catchability.
# ---------------------------------------------------------------------------
class TestExceptionClasses:
    def test_mtlx_error_instantiation_with_message(self):
        exc = MtlxError("something went wrong")
        assert str(exc) == "something went wrong"

    def test_mtlx_error_is_raisable_and_catchable(self):
        with pytest.raises(MtlxError):
            raise MtlxError("boom")

    def test_mtlx_parse_error_instantiation(self):
        exc = MtlxParseError("bad xml")
        assert str(exc) == "bad xml"
        assert isinstance(exc, MtlxError)

    def test_mtlx_parse_error_catchable_as_mtlx_error(self):
        with pytest.raises(MtlxError):
            raise MtlxParseError("parse failed")

    def test_mtlx_write_error_instantiation(self):
        exc = MtlxWriteError("cannot write")
        assert str(exc) == "cannot write"
        assert isinstance(exc, MtlxError)

    def test_mtlx_write_error_catchable_as_mtlx_error(self):
        with pytest.raises(MtlxError):
            raise MtlxWriteError("write failed")

    def test_mtlx_connection_error_instantiation(self):
        exc = MtlxConnectionError("dangling reference")
        assert str(exc) == "dangling reference"
        assert isinstance(exc, MtlxError)

    def test_mtlx_connection_error_catchable_as_mtlx_error(self):
        with pytest.raises(MtlxError):
            raise MtlxConnectionError("dangling")

    def test_sibling_exceptions_are_distinct(self):
        assert not issubclass(MtlxParseError, MtlxWriteError)
        assert not issubclass(MtlxWriteError, MtlxParseError)
        assert not issubclass(MtlxConnectionError, MtlxParseError)
        assert not issubclass(MtlxConnectionError, MtlxWriteError)
        assert not issubclass(MtlxParseError, MtlxConnectionError)
        assert not issubclass(MtlxWriteError, MtlxConnectionError)

    def test_all_four_are_mtlx_error_subclasses(self):
        for cls in (MtlxError, MtlxParseError, MtlxWriteError, MtlxConnectionError):
            assert issubclass(cls, MtlxError)

    def test_all_four_are_exceptions(self):
        for cls in (MtlxError, MtlxParseError, MtlxWriteError, MtlxConnectionError):
            assert issubclass(cls, Exception)


# ---------------------------------------------------------------------------
# MtlxDocument — fill gaps beyond what test_mtlx_codec.py::TestModel and
# test_mtlx_compat.py::TestSmokeImports already cover (raw identity,
# to_dict copy-isolation, is_empty with a node graph present, from_file
# against multi-material/node-graph fixtures).
# ---------------------------------------------------------------------------
class TestMtlxDocumentAdditionalCoverage:
    def _sample_data(self) -> dict:
        return {
            "version": "1.39",
            "materials": [{"name": "mat1", "inputs": []}],
            "node_graphs": [{"name": "ng1", "nodes": [{"name": "n1"}], "outputs": []}],
            "nodes": [],
        }

    def test_raw_property_returns_same_object(self):
        data = self._sample_data()
        doc = MtlxDocument(data)
        assert doc.raw is data

    def test_to_dict_returns_shallow_copy_not_same_object(self):
        data = self._sample_data()
        doc = MtlxDocument(data)
        copy = doc.to_dict()
        assert copy == data
        assert copy is not data

    def test_to_dict_mutation_does_not_affect_original(self):
        data = self._sample_data()
        doc = MtlxDocument(data)
        copy = doc.to_dict()
        copy["version"] = "MUTATED"
        assert doc.version == "1.39"

    def test_is_empty_false_when_only_node_graphs_present(self):
        data = {"version": "1.39", "materials": [], "node_graphs": [{"name": "ng"}], "nodes": []}
        doc = MtlxDocument(data)
        assert doc.material_count == 0
        assert doc.node_graph_count == 1
        assert doc.is_empty is False

    def test_is_empty_true_when_both_empty(self):
        doc = MtlxDocument({"version": "1.39", "materials": [], "node_graphs": [], "nodes": []})
        assert doc.is_empty is True

    def test_materials_property_defaults_to_empty_list(self):
        doc = MtlxDocument({})
        assert doc.materials == []

    def test_node_graphs_property_defaults_to_empty_list(self):
        doc = MtlxDocument({})
        assert doc.node_graphs == []

    def test_version_defaults_to_empty_string(self):
        doc = MtlxDocument({})
        assert doc.version == ""

    def test_spec_qname_class_var(self):
        assert MtlxDocument.spec_qname == "materialx:material"

    def test_from_file_multi_material(self):
        doc = MtlxDocument.from_file(str(VALID_DIR / "multi-material.mtlx"))
        assert doc.material_count == 3
        assert doc.node_graph_count == 0
        assert doc.is_empty is False

    def test_from_file_node_graph(self):
        doc = MtlxDocument.from_file(str(VALID_DIR / "node-graph.mtlx"))
        assert doc.material_count == 0
        assert doc.node_graph_count == 1

    def test_repr_reflects_zero_materials(self):
        doc = MtlxDocument.from_file(str(VALID_DIR / "node-graph.mtlx"))
        assert repr(doc) == "MtlxDocument(version='1.39', materials=0)"

    def test_repr_reflects_multi_material_count(self):
        doc = MtlxDocument.from_file(str(VALID_DIR / "multi-material.mtlx"))
        assert repr(doc) == "MtlxDocument(version='1.39', materials=3)"


# ---------------------------------------------------------------------------
# Graph resolution against the real node-graph.mtlx sample — extends
# test_mtlx_graph.py's single get_connected_node real-sample check with
# resolve_connections and cross-checks against mtlx_node_graph_size.
# ---------------------------------------------------------------------------
class TestGraphResolutionRealSample:
    def _real_node_graph(self) -> dict:
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        return model["node_graphs"][0]

    def test_resolve_connections_covers_both_nodes(self):
        ng = self._real_node_graph()
        resolved = resolve_connections(ng)
        assert set(resolved.keys()) == {"noise", "color_mix"}

    def test_noise_node_has_no_connections(self):
        # noise's only input ("amplitude") carries a literal value, not a
        # nodename/interfacename reference.
        ng = self._real_node_graph()
        resolved = resolve_connections(ng)
        assert resolved["noise"]["resolved_inputs"] == []

    def test_color_mix_resolves_to_noise_node_object(self):
        ng = self._real_node_graph()
        resolved = resolve_connections(ng)
        mix_inputs = resolved["color_mix"]["resolved_inputs"]
        assert len(mix_inputs) == 1
        assert mix_inputs[0]["upstream_name"] == "noise"
        assert mix_inputs[0]["upstream_node"]["name"] == "noise"

    def test_get_connected_node_unknown_input_on_real_sample_raises(self):
        ng = self._real_node_graph()
        with pytest.raises(MtlxConnectionError):
            get_connected_node(ng, "noise", "does_not_exist")

    def test_resolve_connections_node_count_matches_analytics_size(self):
        ng = self._real_node_graph()
        resolved = resolve_connections(ng)
        size_map = mtlx_node_graph_size(VALID_DIR / "node-graph.mtlx")
        assert len(resolved) == size_map[ng["name"]]


# ---------------------------------------------------------------------------
# Facade (MtlxMaterial / MtlxNodeGraph) workflow against the full sample
# corpus, combined with analytics functions.
# ---------------------------------------------------------------------------
class TestFacadeWorkflowRealSamples:
    def test_all_multi_material_entries_wrap_as_facades(self):
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        facades = [MtlxMaterial(m) for m in model["materials"]]
        assert {f.name for f in facades} == {"metal", "plastic", "glass"}

    def test_multi_material_facades_declare_but_do_not_connect_shader(self):
        # Sample corpus materials declare a surfaceshader input with an
        # empty value and no nodename -- confirms the "declared but
        # unconnected" facade state against the real fixture.
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        for raw in model["materials"]:
            facade = MtlxMaterial(raw)
            assert facade.has_surfaceshader_input is True
            assert facade.shader_nodename == ""
        assert mtlx_materials_with_shader_count(VALID_DIR / "multi-material.mtlx") == 0

    def test_node_graph_facade_matches_analytics_node_count(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        facade = MtlxNodeGraph(model["node_graphs"][0])
        size_map = mtlx_node_graph_size(VALID_DIR / "node-graph.mtlx")
        assert facade.node_count == size_map[facade.name]

    def test_node_graph_facade_output_count(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        facade = MtlxNodeGraph(model["node_graphs"][0])
        assert facade.output_count == 1
        assert facade.is_empty is False


# ---------------------------------------------------------------------------
# End-to-end integration: probe -> load -> analytics -> graph resolution,
# cross-checking independently-computed values against each other on the
# full real sample corpus.
# ---------------------------------------------------------------------------
class TestFullWorkflowIntegration:
    @pytest.mark.parametrize(
        "filename",
        ["simple-material.mtlx", "multi-material.mtlx", "node-graph.mtlx"],
    )
    def test_probe_then_load_succeeds_for_every_valid_sample(self, filename):
        path = VALID_DIR / filename
        assert probe_mtlx(path) is True
        model = load_mtlx(path)
        assert isinstance(model, dict)

    @pytest.mark.parametrize(
        "filename",
        ["simple-material.mtlx", "multi-material.mtlx", "node-graph.mtlx"],
    )
    def test_installed_workflow_counts_match_direct_helpers(self, filename):
        path = VALID_DIR / filename
        model = load_mtlx(path)
        workflow = mtlx_installed_workflow(path)
        assert workflow["material_count"] == get_material_count(model)
        assert workflow["node_graph_count"] == get_node_graph_count(model)

    def test_histogram_and_graph_size_and_resolution_agree_on_node_graph_sample(self):
        path = VALID_DIR / "node-graph.mtlx"
        histogram = mtlx_node_type_histogram(path)
        size_map = mtlx_node_graph_size(path)
        model = load_mtlx(path)
        resolved = resolve_connections(model["node_graphs"][0])

        assert sum(histogram.values()) == sum(size_map.values()) == len(resolved)

    def test_invalid_sample_fails_probe_and_raises_on_load(self):
        path = INVALID_DIR / "wrong-root.mtlx"
        assert probe_mtlx(path) is False
        with pytest.raises(MtlxParseError):
            load_mtlx(path)

    def test_load_roundtrip_write_reload_preserves_analytics_results(self):
        """load -> write -> reload: analytics computed on the reloaded file
        match analytics computed on the original (proves the write path
        doesn't silently corrupt data the analytics layer depends on)."""
        original_histogram = mtlx_node_type_histogram(VALID_DIR / "node-graph.mtlx")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "reloaded.mtlx"
            roundtrip(VALID_DIR / "node-graph.mtlx", dest)
            reloaded_histogram = mtlx_node_type_histogram(dest)
        assert reloaded_histogram == original_histogram


# ---------------------------------------------------------------------------
# cli.py::main() — previously untested entry point.
# ---------------------------------------------------------------------------
class TestCliProbeCommand:
    def test_probe_valid_file_exits_zero(self, capsys):
        target = VALID_DIR / "simple-material.mtlx"
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(target)])
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["probe"] is True
        assert payload["file"] == str(target)

    def test_probe_nonexistent_file_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(VALID_DIR / "does-not-exist.mtlx")])
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["probe"] is False

    def test_probe_wrong_root_sample_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(INVALID_DIR / "wrong-root.mtlx")])
        assert exc_info.value.code == 1

    def test_probe_node_graph_sample_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(VALID_DIR / "node-graph.mtlx")])
        assert exc_info.value.code == 0


class TestCliLoadCommand:
    def test_load_valid_file_prints_json_model(self, capsys):
        target = VALID_DIR / "simple-material.mtlx"
        cli.main(["load", str(target)])
        out = capsys.readouterr().out
        model = json.loads(out)
        assert model["version"] == "1.39"
        assert len(model["materials"]) == 1

    def test_load_multi_material_prints_all_materials(self, capsys):
        cli.main(["load", str(VALID_DIR / "multi-material.mtlx")])
        out = capsys.readouterr().out
        model = json.loads(out)
        assert len(model["materials"]) == 3

    def test_load_does_not_raise_system_exit(self):
        # The "load" branch has no sys.exit() call -- main() should return
        # normally (None) rather than raising SystemExit.
        result = cli.main(["load", str(VALID_DIR / "node-graph.mtlx")])
        assert result is None

    def test_load_nonexistent_file_raises_parse_error(self):
        with pytest.raises(MtlxParseError):
            cli.main(["load", str(VALID_DIR / "does-not-exist.mtlx")])

    def test_load_malformed_xml_raises_parse_error(self, tmp_path):
        bad_file = tmp_path / "malformed.mtlx"
        bad_file.write_text("<not>closed", encoding="utf-8")
        with pytest.raises(MtlxParseError):
            cli.main(["load", str(bad_file)])

    def test_load_wrong_root_raises_parse_error(self):
        with pytest.raises(MtlxParseError):
            cli.main(["load", str(INVALID_DIR / "wrong-root.mtlx")])


class TestCliNoCommand:
    def test_no_command_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main([])
        assert exc_info.value.code == 1

    def test_no_command_prints_help(self, capsys):
        with pytest.raises(SystemExit):
            cli.main([])
        out = capsys.readouterr().out
        assert "ff-mtlx" in out or "usage" in out.lower()


class TestCliArgumentParsing:
    def test_probe_requires_file_argument(self):
        with pytest.raises(SystemExit):
            cli.main(["probe"])

    def test_load_requires_file_argument(self):
        with pytest.raises(SystemExit):
            cli.main(["load"])

    def test_main_accepts_none_argv(self, monkeypatch, capsys):
        # main(None) falls back to argparse reading sys.argv; simulate an
        # empty invocation via monkeypatched sys.argv.
        monkeypatch.setattr(sys, "argv", ["ff-mtlx"])
        with pytest.raises(SystemExit) as exc_info:
            cli.main(None)
        assert exc_info.value.code == 1

    def test_unknown_command_exits_nonzero(self):
        with pytest.raises(SystemExit):
            cli.main(["not-a-real-command"])
