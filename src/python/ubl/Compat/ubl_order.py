"""UblOrder — production facade for ubl:order."""
from __future__ import annotations
from ..spec.document.order import Order as _SpecOrder


class UblOrder(_SpecOrder):
    """Production facade for ubl:order."""
    spec_qname = "ubl:order"
    spec_fact_ref = "FACT-UBL-001"
    namespace_uri = "urn:oasis:names:specification:ubl:schema:xsd:Order-2"
