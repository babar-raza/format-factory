"""IpynbCell — production facade for ipynb:cell."""
from __future__ import annotations
from typing import ClassVar
from ..spec.notebook.cell import Cell as _SpecCell


class IpynbCell(_SpecCell):
    """Production facade for ipynb:cell."""
    spec_qname: ClassVar[str] = "ipynb:cell"
    spec_fact_ref: ClassVar[str] = "FACT-IPYNB-002"
    namespace_uri: ClassVar[str] = "urn:format:ipynb:4.5"
