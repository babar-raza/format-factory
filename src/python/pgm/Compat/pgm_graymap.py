"""PgmGraymap — production facade for pgm:graymap."""
from __future__ import annotations
from typing import ClassVar
from ..spec.graymap.graymap import Graymap as _SpecGraymap


class PgmGraymap(_SpecGraymap):
    """Production facade for pgm:graymap."""
    spec_qname: ClassVar[str] = "pgm:graymap"
    spec_fact_ref: ClassVar[str] = "SAL-PGM-00002"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pgm:1.0"
