"""IpynbCell — production facade for ipynb:cell."""
from __future__ import annotations
from ..spec.notebook.cell import Cell as _SpecCell


class IpynbCell(_SpecCell):
    """Production facade for ipynb:cell."""
    spec_qname = "ipynb:cell"
    spec_fact_ref = "FACT-IPYNB-002"
    namespace_uri = "urn:format:ipynb:4.5"
