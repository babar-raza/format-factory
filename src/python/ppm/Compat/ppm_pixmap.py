"""PpmPixmap — production facade for ppm:pixmap."""
from __future__ import annotations
from ..spec.pixmap.pixmap import Pixmap as _SpecPixmap


class PpmPixmap(_SpecPixmap):
    """Production facade for ppm:pixmap."""
    spec_qname = "ppm:pixmap"
    spec_fact_ref = "FACT-PPM-002"
    namespace_uri = "urn:format:netpbm:ppm:1.0"
