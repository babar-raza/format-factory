"""Format Factory mtlx (MaterialX) FOSS Python codec."""

from __future__ import annotations

from mtlx.mtlx_codec import (
    get_material_count,
    get_node_graph_count,
    load_mtlx,
    mtlx_installed_workflow,
    probe_mtlx,
    roundtrip,
    write_mtlx,
)
from mtlx.exceptions import MtlxError, MtlxParseError, MtlxWriteError
from mtlx.models import MtlxDocument
from mtlx.mtlx_analytics import (
    mtlx_materials_with_shader_count,
    mtlx_node_graph_size,
    mtlx_node_type_histogram,
)
from mtlx.Compat import MtlxMaterial, MtlxNodeGraph

__all__ = [
    "get_material_count",
    "get_node_graph_count",
    "load_mtlx",
    "mtlx_installed_workflow",
    "probe_mtlx",
    "roundtrip",
    "write_mtlx",
    "MtlxDocument",
    "MtlxError",
    "MtlxParseError",
    "MtlxWriteError",
    "mtlx_materials_with_shader_count",
    "mtlx_node_graph_size",
    "mtlx_node_type_histogram",
    "MtlxMaterial",
    "MtlxNodeGraph",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False

probe = probe_mtlx
load = load_mtlx
write = write_mtlx
