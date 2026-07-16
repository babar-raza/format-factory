"""PbmRaster — production facade for pbm:raster."""
from __future__ import annotations
from typing import ClassVar
from ..spec.bitmap.raster import Raster as _SpecRaster


class PbmRaster(_SpecRaster):
    """Production facade for pbm:raster."""
    spec_qname: ClassVar[str] = "pbm:raster"
    spec_fact_ref: ClassVar[str] = "SAL-PBM-00002"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pbm:1.0"
