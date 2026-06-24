"""PbmRaster — production facade for pbm:raster."""
from __future__ import annotations
from ..spec.bitmap.raster import Raster as _SpecRaster


class PbmRaster(_SpecRaster):
    """Production facade for pbm:raster."""
    spec_qname = "pbm:raster"
    spec_fact_ref = "FACT-PBM-002"
    namespace_uri = "urn:format:netpbm:pbm:1.0"
