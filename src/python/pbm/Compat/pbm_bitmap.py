"""PbmBitmap — production facade for pbm:bitmap."""
from __future__ import annotations
from ..spec.bitmap.bitmap import Bitmap as _SpecBitmap


class PbmBitmap(_SpecBitmap):
    """Production facade for pbm:bitmap."""
    spec_qname = "pbm:bitmap"
    spec_fact_ref = "FACT-PBM-002"
    namespace_uri = "urn:format:netpbm:pbm:1.0"
