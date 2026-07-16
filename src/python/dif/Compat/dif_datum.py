"""DifDatum — production facade for dif:datum."""
from __future__ import annotations
from typing import ClassVar
from ..spec.table.datum import Datum as _SpecDatum


class DifDatum(_SpecDatum):
    """Production facade for dif:datum."""
    spec_qname: ClassVar[str] = "dif:datum"
    spec_fact_ref: ClassVar[str] = "SAL-DIF-00003"
    namespace_uri: ClassVar[str] = "urn:format:dif:1.0"
