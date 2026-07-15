"""UblLineItem — production facade for ubl:line-item."""
from __future__ import annotations
from ..spec.document.line_item import LineItem as _SpecLineItem


class UblLineItem(_SpecLineItem):
    """Production facade for ubl:line-item."""
    spec_qname = "ubl:line-item"
    spec_fact_ref = "FACT-UBL-002"
    namespace_uri = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
