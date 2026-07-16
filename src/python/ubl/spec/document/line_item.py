"""
UBL structural element: ubl:line-item

Spec ref: OASIS UBL 2.3 Specification
Fact ref: FACT-UBL-002
QName: ubl:line-item
Canonical class: Ubl.LineItem
Facade: UblLineItem
"""
from __future__ import annotations
from typing import Any, ClassVar


class LineItem:
    """Canonical spec-shaped class for ubl:line-item (architecture_only marker).

    Wraps a single InvoiceLine or OrderLine/LineItem dict as produced by
    ubl_codec._parse_invoice / _parse_order.
    """

    spec_qname: ClassVar[str] = "ubl:line-item"
    spec_fact_ref: ClassVar[str] = "FACT-UBL-002"
    namespace_uri: ClassVar[str] = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    local_name: ClassVar[str] = "InvoiceLine"
    facade_names: ClassVar[list] = ["UblLineItem"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def line_id(self) -> str:
        """Return the line item ID (cbc:ID)."""
        return str(self._data.get("id", ""))

    @property
    def quantity(self) -> str:
        """Return the line quantity (cbc:InvoicedQuantity or cbc:Quantity)."""
        return str(self._data.get("quantity", ""))

    @property
    def amount(self) -> str:
        """Return the line extension amount (cbc:LineExtensionAmount), if present."""
        return str(self._data.get("amount", ""))

    @property
    def item_name(self) -> str:
        """Return the item name (cac:Item/cbc:Name)."""
        return str(self._data.get("item_name", ""))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"LineItem(id={self.line_id!r}, item_name={self.item_name!r})"
