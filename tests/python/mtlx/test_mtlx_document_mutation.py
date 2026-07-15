"""Semantic mutation-roundtrip tests for MaterialX documents.

Distinct from the existing identity roundtrip test in test_mtlx_codec.py
(TestRoundtrip.test_roundtrip_simple_material, which proves an unmodified
document survives load -> write -> load unchanged). This suite proves an
*edit survives* the same cycle: load -> mutate the materials list ->
write -> reload -> assert the mutation is present in the reloaded model.

Sprint: TC-PROLIB-MTLX-001 (Phase 2 professional library build-out).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from mtlx.mtlx_codec import load_mtlx, write_mtlx
from mtlx.exceptions import MtlxParseError

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx"
VALID_DIR = SAMPLES / "valid"


def _new_material(name: str, nodename: str = "") -> dict:
    return {
        "name": name,
        "type": "surfacematerial",
        "inputs": [
            {
                "name": "surfaceshader",
                "type": "surfaceshader",
                "value": "" if not nodename else "",
                "nodename": nodename,
                "output": "",
            }
        ],
    }


class TestMutationRoundtrip:
    def test_add_material_present_after_reload(self):
        """load -> add a new surfacematerial -> save -> reload: new material is present."""
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        model["materials"].append(_new_material("added_glass", nodename="glass_shader"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated.mtlx"
            write_mtlx(model, dest)
            reloaded = load_mtlx(dest)
            names = [m["name"] for m in reloaded["materials"]]
            assert "added_glass" in names

    def test_add_material_increases_count(self):
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        original_count = len(model["materials"])
        model["materials"].append(_new_material("added_metal"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated2.mtlx"
            write_mtlx(model, dest)
            reloaded = load_mtlx(dest)
            assert len(reloaded["materials"]) == original_count + 1

    def test_add_material_preserves_existing_materials(self):
        model = load_mtlx(VALID_DIR / "multi-material.mtlx")
        original_names = {m["name"] for m in model["materials"]}
        model["materials"].append(_new_material("newcomer"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated3.mtlx"
            write_mtlx(model, dest)
            reloaded = load_mtlx(dest)
            reloaded_names = {m["name"] for m in reloaded["materials"]}
            assert original_names.issubset(reloaded_names)
            assert "newcomer" in reloaded_names

    def test_added_material_shader_connection_survives_reload(self):
        """The new material's nodename connection (not just its name) survives."""
        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        model["materials"].append(_new_material("connected_mat", nodename="pbr_shader"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated4.mtlx"
            write_mtlx(model, dest)
            reloaded = load_mtlx(dest)
            added = next(m for m in reloaded["materials"] if m["name"] == "connected_mat")
            surfaceshader_input = next(
                i for i in added["inputs"] if i["name"] == "surfaceshader"
            )
            assert surfaceshader_input["nodename"] == "pbr_shader"

    def test_add_material_to_zero_material_document(self):
        """Starting from a document with zero materials (node-graph.mtlx)."""
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        assert len(model["materials"]) == 0
        model["materials"].append(_new_material("first_material"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated5.mtlx"
            write_mtlx(model, dest)
            reloaded = load_mtlx(dest)
            assert len(reloaded["materials"]) == 1
            assert reloaded["materials"][0]["name"] == "first_material"

    def test_reloaded_document_still_parses_as_valid_mtlx(self):
        from mtlx.mtlx_codec import probe_mtlx

        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        model["materials"].append(_new_material("probe_check_mat"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated6.mtlx"
            write_mtlx(model, dest)
            assert probe_mtlx(dest) is True

    def test_node_graphs_untouched_by_material_mutation(self):
        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        original_graph_count = len(model["node_graphs"])
        model["materials"].append(_new_material("side_material"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated7.mtlx"
            write_mtlx(model, dest)
            reloaded = load_mtlx(dest)
            assert len(reloaded["node_graphs"]) == original_graph_count

    def test_analytics_reflects_added_shader_connection(self):
        """After adding a connected material, mtlx_materials_with_shader_count
        on the *reloaded* file reflects the mutation (analytics + mutation
        integration, not identity-only)."""
        from mtlx.mtlx_analytics import mtlx_materials_with_shader_count

        model = load_mtlx(VALID_DIR / "simple-material.mtlx")
        before = mtlx_materials_with_shader_count(VALID_DIR / "simple-material.mtlx")
        model["materials"].append(_new_material("newly_connected", nodename="new_shader"))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated8.mtlx"
            write_mtlx(model, dest)
            after = mtlx_materials_with_shader_count(dest)
            assert after == before + 1
