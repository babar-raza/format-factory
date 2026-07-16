"""Write-path completeness tests for the generic top-level ``nodes`` bucket.

Before this fix, ``write_mtlx`` only serialized ``model["materials"]`` and
``model["node_graphs"]`` -- a ``nodedef``, ``typedef``, ``look``,
``propertyset``, or plain top-level node instance would parse correctly on
load but be silently dropped on write. These tests prove a full load ->
write -> reload cycle preserves every element kind, not just materials and
node graphs.

Spec reference: FACT-MTLX-101.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from mtlx.mtlx_codec import load_mtlx, write_mtlx

_MULTI_ELEMENT_DOC = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodedef name="ND_myfractal_float" node="myfractal" type="float">'
    b'<input name="octaves" type="integer" value="3"/>'
    b'<output name="out" type="float"/>'
    b"</nodedef>"
    b'<typedef name="myarray"/>'
    b'<standard_surface name="ss_instance" type="surfaceshader">'
    b'<input name="base_color" type="color3" value="0.8,0.2,0.2"/>'
    b"</standard_surface>"
    b'<look name="look1">'
    b'<materialassign name="ma1" material="mat1" geom="/robot1"/>'
    b"</look>"
    b'<propertyset name="ps1">'
    b'<property name="twosided" value="true"/>'
    b"</propertyset>"
    b"</materialx>"
)


def _reload_via_roundtrip(source: bytes) -> dict:
    model = load_mtlx(source)
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / "roundtrip.mtlx"
        write_mtlx(model, dest)
        return load_mtlx(dest)


class TestLoadCapturesGenericBucket:
    """Confirm load_mtlx's parsing side already buckets every element kind."""

    def test_all_five_elements_land_in_nodes_bucket(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        assert len(model["nodes"]) == 5
        assert model["materials"] == []
        assert model["node_graphs"] == []

    def test_element_types_recorded(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        types = {n["type"] for n in model["nodes"]}
        assert types == {"nodedef", "typedef", "standard_surface", "look", "propertyset"}


class TestWriteRoundtripPreservesGenericBucket:
    """FACT-MTLX-101: the actual data-loss-on-write bug fix."""

    def test_reloaded_document_has_same_node_count(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        assert len(reloaded["nodes"]) == len(model["nodes"]) == 5

    def test_nodedef_survives_with_category_and_type(self):
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        nodedef = next(n for n in reloaded["nodes"] if n["type"] == "nodedef")
        assert nodedef["name"] == "ND_myfractal_float"
        assert nodedef["node_category"] == "myfractal"
        assert nodedef["attributes"]["type"] == "float"

    def test_nodedef_interface_input_and_output_survive(self):
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        nodedef = next(n for n in reloaded["nodes"] if n["type"] == "nodedef")
        assert len(nodedef["inputs"]) == 1
        assert nodedef["inputs"][0]["name"] == "octaves"
        assert nodedef["inputs"][0]["value"] == "3"
        assert len(nodedef["outputs"]) == 1
        assert nodedef["outputs"][0]["name"] == "out"
        assert nodedef["outputs"][0]["type"] == "float"

    def test_typedef_survives(self):
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        typedef = next(n for n in reloaded["nodes"] if n["type"] == "typedef")
        assert typedef["name"] == "myarray"

    def test_plain_top_level_node_instance_survives_with_input(self):
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        instance = next(n for n in reloaded["nodes"] if n["type"] == "standard_surface")
        assert instance["name"] == "ss_instance"
        assert instance["attributes"]["type"] == "surfaceshader"
        assert instance["inputs"][0]["name"] == "base_color"
        assert instance["inputs"][0]["value"] == "0.8,0.2,0.2"

    def test_look_survives_with_nested_materialassign(self):
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        look = next(n for n in reloaded["nodes"] if n["type"] == "look")
        assert look["name"] == "look1"
        assert len(look["children"]) == 1
        assign = look["children"][0]
        assert assign["tag"] == "materialassign"
        assert assign["attributes"]["material"] == "mat1"
        assert assign["attributes"]["geom"] == "/robot1"

    def test_propertyset_survives_with_nested_property(self):
        reloaded = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        propset = next(n for n in reloaded["nodes"] if n["type"] == "propertyset")
        assert propset["name"] == "ps1"
        assert len(propset["children"]) == 1
        prop = propset["children"][0]
        assert prop["tag"] == "property"
        assert prop["attributes"]["name"] == "twosided"
        assert prop["attributes"]["value"] == "true"

    def test_second_roundtrip_is_stable(self):
        """Write -> reload -> write -> reload again yields the same structure
        (proves the fix is a stable fixed point, not a one-shot patch)."""
        once = _reload_via_roundtrip(_MULTI_ELEMENT_DOC)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "second.mtlx"
            write_mtlx(once, dest)
            twice = load_mtlx(dest)
        assert len(twice["nodes"]) == len(once["nodes"]) == 5
        assert {n["type"] for n in twice["nodes"]} == {n["type"] for n in once["nodes"]}

    def test_materials_and_node_graphs_unaffected_when_nodes_bucket_present(self):
        """The fix must not disturb the existing materials/node_graphs write path."""
        doc = (
            b'<?xml version="1.0"?><materialx version="1.39">'
            b'<surfacematerial name="mat1">'
            b'<input name="surfaceshader" type="surfaceshader" nodename="sh1"/>'
            b"</surfacematerial>"
            b'<nodegraph name="ng1"><node name="n1" type="float"/></nodegraph>'
            b'<nodedef name="ND_foo" node="foo" type="float"/>'
            b"</materialx>"
        )
        reloaded = _reload_via_roundtrip(doc)
        assert len(reloaded["materials"]) == 1
        assert reloaded["materials"][0]["name"] == "mat1"
        assert len(reloaded["node_graphs"]) == 1
        assert reloaded["node_graphs"][0]["name"] == "ng1"
        assert len(reloaded["nodes"]) == 1
        assert reloaded["nodes"][0]["type"] == "nodedef"

    def test_empty_nodes_bucket_writes_nothing_extra(self):
        """Regression guard: a document with no generic elements must not
        gain spurious <node> elements after the fix."""
        model = load_mtlx(
            b'<?xml version="1.0"?><materialx version="1.39">'
            b'<surfacematerial name="mat1"/></materialx>'
        )
        assert model["nodes"] == []
        result_xml = write_mtlx(model)
        assert "<node" not in result_xml
        reloaded_model = load_mtlx(result_xml.encode("utf-8"))
        assert reloaded_model["nodes"] == []


class TestNodegraphResidualDataLoss:
    """TC-S6P4-PROD-002 (select-6 Phase 4, closes D2): the write-path fix
    above covers top-level nodedef/typedef/look/propertyset, but an
    independent audit found a second, undisclosed residual gap specifically
    inside <nodegraph>: the graph element's own extra attributes and
    non-input/output children of graph-internal nodes were still silently
    dropped on write. This directly contradicted the coverage report's
    unqualified FACT-MTLX-101 "IMPLEMENTED" claim. Reproduces the exact
    adversarial construction the audit used.
    """

    _ADVERSARIAL_DOC = (
        b'<?xml version="1.0"?><materialx version="1.39">'
        b'<nodegraph name="NG1" nodedef="ND_test" fileprefix="tex/">'
        b'<image name="img1" type="color3">'
        b'<input name="file" type="filename" value="tex.png"/>'
        b"<xpos>1.5</xpos>"
        b"</image>"
        b'<output name="out" type="color3" nodename="img1"/>'
        b"</nodegraph>"
        b"</materialx>"
    )

    def test_load_captures_nodegraph_level_attributes(self):
        model = load_mtlx(self._ADVERSARIAL_DOC)
        ng = model["node_graphs"][0]
        assert ng["attributes"].get("nodedef") == "ND_test"
        assert ng["attributes"].get("fileprefix") == "tex/"

    def test_load_captures_internal_node_generic_children(self):
        model = load_mtlx(self._ADVERSARIAL_DOC)
        node = model["node_graphs"][0]["nodes"][0]
        assert node["name"] == "img1"
        child_tags = [c["tag"] for c in node["children"]]
        assert "xpos" in child_tags

    def test_roundtrip_preserves_nodegraph_attributes_and_generic_children(self):
        """The exact before/after this audit demonstrated: before the fix,
        writing this document dropped `nodedef`/`fileprefix` from
        <nodegraph> and the <xpos> child from the internal <image> node."""
        reloaded = _reload_via_roundtrip(self._ADVERSARIAL_DOC)
        ng = reloaded["node_graphs"][0]
        assert ng["attributes"].get("nodedef") == "ND_test"
        assert ng["attributes"].get("fileprefix") == "tex/"
        node = ng["nodes"][0]
        child_tags = [c["tag"] for c in node["children"]]
        assert "xpos" in child_tags
        xpos = next(c for c in node["children"] if c["tag"] == "xpos")
        assert xpos["text"] == "1.5"

    def test_nodegraph_without_extra_attributes_unaffected(self):
        """Regression guard: a plain <nodegraph name="..."> with no extra
        attributes and only input/output children must not gain spurious
        attributes or children after the fix."""
        doc = (
            b'<?xml version="1.0"?><materialx version="1.39">'
            b'<nodegraph name="ng_plain">'
            b'<constant name="c1" type="float"><input name="value" type="float" value="1.0"/></constant>'
            b'<output name="out" type="float" nodename="c1"/>'
            b"</nodegraph></materialx>"
        )
        reloaded = _reload_via_roundtrip(doc)
        ng = reloaded["node_graphs"][0]
        assert ng["attributes"] == {}
        assert reloaded["node_graphs"][0]["nodes"][0]["children"] == []


class TestNodegraphOutputResidualDataLoss:
    """TC-S6P4-FINAL-001a (select-6 Phase 4, final independent re-audit,
    2026-07-16): an adversarial re-check of TC-S6P4-PROD-002 (D2) found the
    fix was incomplete -- a graph-internal <output> element (the sibling of
    the node branch PROD-002 already fixed) still silently dropped any
    attribute beyond name/type/nodename and any non-structural child.
    Reproduces the exact adversarial construction the re-audit used.
    """

    _ADVERSARIAL_DOC = (
        b'<?xml version="1.0"?><materialx version="1.39">'
        b'<nodegraph name="ng1">'
        b'<constant name="const1" type="color3">'
        b'<input name="value" type="color3" value="1,0,0"/>'
        b"</constant>"
        b'<output name="out1" type="color3" nodename="const1" '
        b'extra_out_attr="should_this_survive" colorspace="srgb_texture">'
        b'<output_child foo="bar"/>'
        b"</output>"
        b"</nodegraph></materialx>"
    )

    def test_load_captures_output_attributes_and_children(self):
        model = load_mtlx(self._ADVERSARIAL_DOC)
        out = model["node_graphs"][0]["outputs"][0]
        assert out["attributes"].get("extra_out_attr") == "should_this_survive"
        assert out["attributes"].get("colorspace") == "srgb_texture"
        assert any(c["tag"] == "output_child" for c in out["children"])

    def test_roundtrip_preserves_output_attributes_and_children(self):
        reloaded = _reload_via_roundtrip(self._ADVERSARIAL_DOC)
        out = reloaded["node_graphs"][0]["outputs"][0]
        assert out["attributes"].get("extra_out_attr") == "should_this_survive"
        assert out["attributes"].get("colorspace") == "srgb_texture"
        child_tags = [c["tag"] for c in out["children"]]
        assert "output_child" in child_tags
        oc = next(c for c in out["children"] if c["tag"] == "output_child")
        assert oc["attributes"].get("foo") == "bar"
        # Core fields (verified in TestNodegraphResidualDataLoss) unaffected.
        assert out["name"] == "out1"
        assert out["type"] == "color3"
        assert out["nodename"] == "const1"

    def test_plain_output_without_extras_unaffected(self):
        """Regression guard: an <output> with only name/type/nodename must
        not gain spurious attributes or children after the fix."""
        doc = (
            b'<?xml version="1.0"?><materialx version="1.39">'
            b'<nodegraph name="ng_plain">'
            b'<constant name="c1" type="float"><input name="value" type="float" value="1.0"/></constant>'
            b'<output name="out" type="float" nodename="c1"/>'
            b"</nodegraph></materialx>"
        )
        reloaded = _reload_via_roundtrip(doc)
        out = reloaded["node_graphs"][0]["outputs"][0]
        assert out["attributes"] == {}
        assert out["children"] == []
