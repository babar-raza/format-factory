"""PgmHeader — production facade for pgm:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.graymap.header import Header as _SpecHeader


class PgmHeader(_SpecHeader):
    """Production facade for pgm:header."""
    spec_qname: ClassVar[str] = "pgm:header"
    spec_fact_ref: ClassVar[str] = "SAL-PGM-00001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pgm:1.0"
