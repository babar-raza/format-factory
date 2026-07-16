"""UblInvoice — production facade for ubl:invoice."""
from __future__ import annotations
from typing import ClassVar
from ..spec.document.invoice import Invoice as _SpecInvoice


class UblInvoice(_SpecInvoice):
    """Production facade for ubl:invoice."""
    spec_qname: ClassVar[str] = "ubl:invoice"
    spec_fact_ref: ClassVar[str] = "FACT-UBL-002"
    namespace_uri: ClassVar[str] = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
