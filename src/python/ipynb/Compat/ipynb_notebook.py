"""IpynbNotebook — production facade for ipynb:notebook."""
from __future__ import annotations
from typing import ClassVar
from ..spec.notebook.notebook import Notebook as _SpecNotebook


class IpynbNotebook(_SpecNotebook):
    """Production facade for ipynb:notebook."""
    spec_qname: ClassVar[str] = "ipynb:notebook"
    spec_fact_ref: ClassVar[str] = "FACT-IPYNB-001"
    namespace_uri: ClassVar[str] = "urn:format:ipynb:4.5"
