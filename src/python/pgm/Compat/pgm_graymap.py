"""PgmGraymap — production facade for pgm:graymap."""
from __future__ import annotations
from ..spec.graymap.graymap import Graymap as _SpecGraymap


class PgmGraymap(_SpecGraymap):
    """Production facade for pgm:graymap."""
    spec_qname = "pgm:graymap"
    spec_fact_ref = "FACT-PGM-002"
    namespace_uri = "urn:format:netpbm:pgm:1.0"
