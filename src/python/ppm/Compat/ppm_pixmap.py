"""PpmPixmap — production facade for ppm:pixmap."""
from __future__ import annotations
from typing import ClassVar
from ..spec.pixmap.pixmap import Pixmap as _SpecPixmap


class PpmPixmap(_SpecPixmap):
    """Production facade for ppm:pixmap."""
    spec_qname: ClassVar[str] = "ppm:pixmap"
    spec_fact_ref: ClassVar[str] = "SAL-PPM-00002"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:ppm:1.0"
