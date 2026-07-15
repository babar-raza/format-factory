"""mtlx.Compat — production facade layer for MaterialX.

Exports:
    MtlxMaterial  — facade for materialx:material  (FACT-MTLX-003)
    MtlxNodeGraph — facade for materialx:nodegraph (FACT-MTLX-002)
"""
from .mtlx_material import MtlxMaterial
from .mtlx_nodegraph import MtlxNodeGraph

__all__ = ["MtlxMaterial", "MtlxNodeGraph"]
