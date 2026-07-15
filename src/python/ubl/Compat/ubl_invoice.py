"""UblInvoice — production facade for ubl:invoice."""
from __future__ import annotations
from ..spec.document.invoice import Invoice as _SpecInvoice


class UblInvoice(_SpecInvoice):
    """Production facade for ubl:invoice."""
    spec_qname = "ubl:invoice"
    spec_fact_ref = "FACT-UBL-002"
    namespace_uri = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
