"""UblOrder — production facade for ubl:order."""
from __future__ import annotations
from typing import ClassVar
from ..spec.document.order import Order as _SpecOrder


class UblOrder(_SpecOrder):
    """Production facade for ubl:order."""
    spec_qname: ClassVar[str] = "ubl:order"
    spec_fact_ref: ClassVar[str] = "FACT-UBL-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:specification:ubl:schema:xsd:Order-2"
