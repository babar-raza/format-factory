"""NrrdData — production facade for nrrd:data."""
from __future__ import annotations
from ..spec.header.data import Data as _SpecData


class NrrdData(_SpecData):
    """Production facade for nrrd:data."""
    spec_qname = "nrrd:data"
    spec_fact_ref = "FACT-NRRD-003"
    namespace_uri = "urn:format:nrrd:5.0"
