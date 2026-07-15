"""UblCreditNote — production facade for ubl:credit-note."""
from __future__ import annotations
from ..spec.document.credit_note import CreditNote as _SpecCreditNote


class UblCreditNote(_SpecCreditNote):
    """Production facade for ubl:credit-note."""
    spec_qname = "ubl:credit-note"
    spec_fact_ref = "FACT-UBL-105"
    namespace_uri = "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"
