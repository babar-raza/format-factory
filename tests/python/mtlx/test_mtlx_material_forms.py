"""Tests for volumematerial recognition and legacy shaderref/bindinput support.

Before this fix, only the literal ``surfacematerial`` tag was recognized as
a material -- a ``volumematerial`` fell into the generic ``nodes`` bucket
(miscategorized), and the legacy ``shaderref``/``bindinput`` shader-binding
form (used by pre-1.38 MaterialX documents) was not parsed at all.

Spec reference: FACT-MTLX-104.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from mtlx.mtlx_analytics import mtlx_materials_with_shader_count
from mtlx.mtlx_codec import load_mtlx, write_mtlx

_VOLUME_MATERIAL_DOC = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<volumematerial name="fog_vol">'
    b'<input name="volumeshader" type="volumeshader" nodename="fog_shader"/>'
    b"</volumematerial></materialx>"
)

_LEGACY_SHADERREF_DOC = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<surfacematerial name="legacy_mat">'
    b'<shaderref name="sr1" node="standardsurface">'
    b'<bindinput name="base_color" output="marble_out" nodegraph="NG_marble"/>'
    b'<bindinput name="roughness" value="0.3"/>'
    b"</shaderref>"
    b"</surfacematerial></materialx>"
)

_MIXED_LEGACY_AND_MODERN_DOC = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<surfacematerial name="modern_mat">'
    b'<input name="surfaceshader" type="surfaceshader" nodename="sh1"/>'
    b"</surfacematerial>"
    b'<surfacematerial name="legacy_mat">'
    b'<shaderref name="sr1" node="standardsurface"/>'
    b"</surfacematerial></materialx>"
)


def _reload_via_roundtrip(source: bytes) -> dict:
    model = load_mtlx(source)
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / "roundtrip.mtlx"
        write_mtlx(model, dest)
        return load_mtlx(dest)


class TestVolumeMaterial:
    def test_recognized_as_material_not_generic_node(self):
        model = load_mtlx(_VOLUME_MATERIAL_DOC)
        assert len(model["materials"]) == 1
        assert model["nodes"] == []

    def test_material_type_recorded(self):
        model = load_mtlx(_VOLUME_MATERIAL_DOC)
        assert model["materials"][0]["type"] == "volumematerial"
        assert model["materials"][0]["name"] == "fog_vol"

    def test_counted_in_material_count(self):
        from mtlx.mtlx_codec import get_material_count

        model = load_mtlx(_VOLUME_MATERIAL_DOC)
        assert get_material_count(model) == 1

    def test_shader_connection_counted(self):
        assert mtlx_materials_with_shader_count(_VOLUME_MATERIAL_DOC) == 1

    def test_write_roundtrip_preserves_volumematerial_tag(self):
        """Regression guard: write_mtlx used to hardcode 'surfacematerial',
        which would have silently reclassified a volumematerial on write."""
        result_xml = write_mtlx(load_mtlx(_VOLUME_MATERIAL_DOC))
        assert "<volumematerial" in result_xml
        assert "<surfacematerial" not in result_xml

    def test_full_roundtrip_still_a_volumematerial(self):
        reloaded = _reload_via_roundtrip(_VOLUME_MATERIAL_DOC)
        assert len(reloaded["materials"]) == 1
        assert reloaded["materials"][0]["type"] == "volumematerial"
        assert reloaded["materials"][0]["name"] == "fog_vol"


class TestLegacyShaderrefBindinput:
    def test_shaderref_captured_on_material(self):
        model = load_mtlx(_LEGACY_SHADERREF_DOC)
        material = model["materials"][0]
        assert len(material["shaderrefs"]) == 1
        assert material["shaderrefs"][0]["name"] == "sr1"
        assert material["shaderrefs"][0]["node"] == "standardsurface"

    def test_bindinputs_captured(self):
        model = load_mtlx(_LEGACY_SHADERREF_DOC)
        bindinputs = model["materials"][0]["shaderrefs"][0]["bindinputs"]
        assert len(bindinputs) == 2
        base_color = next(b for b in bindinputs if b["name"] == "base_color")
        assert base_color["output"] == "marble_out"
        assert base_color["nodegraph"] == "NG_marble"
        roughness = next(b for b in bindinputs if b["name"] == "roughness")
        assert roughness["value"] == "0.3"

    def test_shaderref_binding_counted_as_connected(self):
        assert mtlx_materials_with_shader_count(_LEGACY_SHADERREF_DOC) == 1

    def test_material_without_shaderref_has_empty_list(self):
        model = load_mtlx(
            b'<?xml version="1.0"?><materialx version="1.39">'
            b'<surfacematerial name="plain"/></materialx>'
        )
        assert model["materials"][0]["shaderrefs"] == []

    def test_shaderref_and_bindinputs_survive_write_roundtrip(self):
        reloaded = _reload_via_roundtrip(_LEGACY_SHADERREF_DOC)
        material = reloaded["materials"][0]
        assert material["name"] == "legacy_mat"
        assert len(material["shaderrefs"]) == 1
        assert material["shaderrefs"][0]["node"] == "standardsurface"
        bindinputs = material["shaderrefs"][0]["bindinputs"]
        assert len(bindinputs) == 2

    def test_mixed_legacy_and_modern_materials_both_counted(self):
        assert mtlx_materials_with_shader_count(_MIXED_LEGACY_AND_MODERN_DOC) == 2

    def test_mixed_document_material_count(self):
        from mtlx.mtlx_codec import get_material_count

        model = load_mtlx(_MIXED_LEGACY_AND_MODERN_DOC)
        assert get_material_count(model) == 2
