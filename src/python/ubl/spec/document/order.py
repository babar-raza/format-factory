"""
UBL structural element: ubl:order

Spec ref: OASIS UBL 2.3 Specification
Fact ref: FACT-UBL-001
QName: ubl:order
Canonical class: Ubl.Order
Facade: UblOrder
"""
from __future__ import annotations
from typing import Any, ClassVar


class Order:
    """Canonical spec-shaped class for ubl:order (architecture_only marker)."""

    spec_qname: ClassVar[str] = "ubl:order"
    spec_fact_ref: ClassVar[str] = "FACT-UBL-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:specification:ubl:schema:xsd:Order-2"
    local_name: ClassVar[str] = "Order"
    facade_names: ClassVar[list] = ["UblOrder"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def doc_id(self) -> str:
        """Return the order document ID (cbc:ID)."""
        return str(self._data.get("id", ""))

    @property
    def issue_date(self) -> str:
        """Return the order issue date string (cbc:IssueDate)."""
        return str(self._data.get("issue_date", ""))

    @property
    def buyer(self) -> dict[str, Any]:
        """Return the buyer party dict (cac:BuyerCustomerParty)."""
        return dict(self._data.get("buyer", {}))

    @property
    def seller(self) -> dict[str, Any]:
        """Return the seller party dict (cac:SellerSupplierParty)."""
        return dict(self._data.get("seller", {}))

    @property
    def lines(self) -> list[dict[str, Any]]:
        """Return the list of order line items (cac:OrderLine)."""
        return list(self._data.get("lines", []))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Order(id={self.doc_id!r})"
