"""DifDatum — production facade for dif:datum."""
from __future__ import annotations
from ..spec.table.datum import Datum as _SpecDatum


class DifDatum(_SpecDatum):
    """Production facade for dif:datum."""
    spec_qname = "dif:datum"
    spec_fact_ref = "FACT-DIF-003"
    namespace_uri = "urn:format:dif:1.0"
