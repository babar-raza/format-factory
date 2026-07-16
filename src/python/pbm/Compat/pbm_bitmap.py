"""PbmBitmap — production facade for pbm:bitmap."""
from __future__ import annotations
from typing import ClassVar
from ..spec.bitmap.bitmap import Bitmap as _SpecBitmap


class PbmBitmap(_SpecBitmap):
    """Production facade for pbm:bitmap."""
    spec_qname: ClassVar[str] = "pbm:bitmap"
    spec_fact_ref: ClassVar[str] = "SAL-PBM-00002"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pbm:1.0"
