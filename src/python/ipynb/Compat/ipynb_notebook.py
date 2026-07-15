"""IpynbNotebook — production facade for ipynb:notebook."""
from __future__ import annotations
from ..spec.notebook.notebook import Notebook as _SpecNotebook


class IpynbNotebook(_SpecNotebook):
    """Production facade for ipynb:notebook."""
    spec_qname = "ipynb:notebook"
    spec_fact_ref = "FACT-IPYNB-001"
    namespace_uri = "urn:format:ipynb:4.5"
