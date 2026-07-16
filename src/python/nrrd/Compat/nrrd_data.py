"""NrrdData — production facade for nrrd:data."""
from __future__ import annotations
from typing import ClassVar
from ..spec.header.data import Data as _SpecData


class NrrdData(_SpecData):
    """Production facade for nrrd:data."""
    spec_qname: ClassVar[str] = "nrrd:data"
    spec_fact_ref: ClassVar[str] = "FACT-NRRD-003"
    namespace_uri: ClassVar[str] = "urn:format:nrrd:5.0"
