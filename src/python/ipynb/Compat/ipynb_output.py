"""IpynbOutput — production facade for ipynb:output."""
from __future__ import annotations
from ..spec.notebook.output import Output as _SpecOutput


class IpynbOutput(_SpecOutput):
    """Production facade for ipynb:output."""
    spec_qname = "ipynb:output"
    spec_fact_ref = "FACT-IPYNB-003"
    namespace_uri = "urn:format:ipynb:4.5"
