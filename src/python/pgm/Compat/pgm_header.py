"""PgmHeader — production facade for pgm:header."""
from __future__ import annotations
from ..spec.graymap.header import Header as _SpecHeader


class PgmHeader(_SpecHeader):
    """Production facade for pgm:header."""
    spec_qname = "pgm:header"
    spec_fact_ref = "FACT-PGM-001"
    namespace_uri = "urn:format:netpbm:pgm:1.0"
