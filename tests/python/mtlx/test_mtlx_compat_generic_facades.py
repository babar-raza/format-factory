"""Tests for MtlxNodeDef/MtlxTypeDef/MtlxLook/MtlxPropertySet facades
(TC-S6P4-PROD-009, select-6 Phase 4: expand mtlx qname registry to cover
nodedef/typedef/look/propertyset per TC-S6P4-PROD-002's write-path fix)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from mtlx.Compat.mtlx_look import MtlxLook
from mtlx.Compat.mtlx_nodedef import MtlxNodeDef
from mtlx.Compat.mtlx_propertyset import MtlxPropertySet
from mtlx.Compat.mtlx_typedef import MtlxTypeDef
from mtlx.mtlx_codec import load_mtlx

_MULTI_ELEMENT_DOC = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodedef name="ND_myfractal_float" node="myfractal" type="float">'
    b'<input name="octaves" type="integer" value="3"/>'
    b'<output name="out" type="float"/>'
    b"</nodedef>"
    b'<typedef name="myarray"><member name="x" type="float"/></typedef>'
    b'<look name="look1">'
    b'<materialassign name="ma1" material="mat1" geom="/robot1"/>'
    b"</look>"
    b'<propertyset name="ps1">'
    b'<property name="twosided" value="true"/>'
    b"</propertyset>"
    b"</materialx>"
)


class TestMtlxNodeDefFacade:
    def test_wraps_generic_node_dict(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        raw = next(n for n in model["nodes"] if n["type"] == "nodedef")
        facade = MtlxNodeDef(raw)
        assert facade.name == "ND_myfractal_float"
        assert facade.node_category == "myfractal"
        assert facade.declared_type == "float"
        assert len(facade.inputs) == 1
        assert len(facade.outputs) == 1
        assert facade.spec_qname == "materialx:nodedef"

    def test_to_dict_and_repr(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        raw = next(n for n in model["nodes"] if n["type"] == "nodedef")
        facade = MtlxNodeDef(raw)
        assert facade.to_dict() == raw
        assert "ND_myfractal_float" in repr(facade)


class TestMtlxTypeDefFacade:
    def test_wraps_generic_node_dict_with_children(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        raw = next(n for n in model["nodes"] if n["type"] == "typedef")
        facade = MtlxTypeDef(raw)
        assert facade.name == "myarray"
        assert any(c["tag"] == "member" for c in facade.children)
        assert facade.spec_qname == "materialx:typedef"


class TestMtlxLookFacade:
    def test_wraps_generic_node_dict_with_material_assigns(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        raw = next(n for n in model["nodes"] if n["type"] == "look")
        facade = MtlxLook(raw)
        assert facade.name == "look1"
        assert len(facade.material_assigns) == 1
        assert facade.material_assigns[0]["attributes"]["material"] == "mat1"
        assert facade.spec_qname == "materialx:look"


class TestMtlxPropertySetFacade:
    def test_wraps_generic_node_dict_with_properties(self):
        model = load_mtlx(_MULTI_ELEMENT_DOC)
        raw = next(n for n in model["nodes"] if n["type"] == "propertyset")
        facade = MtlxPropertySet(raw)
        assert facade.name == "ps1"
        assert len(facade.properties) == 1
        assert facade.properties[0]["attributes"]["name"] == "twosided"
        assert facade.spec_qname == "materialx:propertyset"
