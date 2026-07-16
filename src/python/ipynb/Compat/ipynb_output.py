"""IpynbOutput — production facade for ipynb:output."""
from __future__ import annotations
from typing import ClassVar
from ..spec.notebook.output import Output as _SpecOutput


class IpynbOutput(_SpecOutput):
    """Production facade for ipynb:output."""
    spec_qname: ClassVar[str] = "ipynb:output"
    spec_fact_ref: ClassVar[str] = "FACT-IPYNB-003"
    namespace_uri: ClassVar[str] = "urn:format:ipynb:4.5"
