"""
UBL structural element: ubl:invoice

Spec ref: OASIS UBL 2.3 Specification
Fact ref: FACT-UBL-002
QName: ubl:invoice
Canonical class: Ubl.Invoice
Facade: UblInvoice
"""
from __future__ import annotations
from typing import Any, ClassVar


class Invoice:
    """Canonical spec-shaped class for ubl:invoice (architecture_only marker)."""

    spec_qname: ClassVar[str] = "ubl:invoice"
    spec_fact_ref: ClassVar[str] = "FACT-UBL-002"
    namespace_uri: ClassVar[str] = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    local_name: ClassVar[str] = "Invoice"
    facade_names: ClassVar[list] = ["UblInvoice"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def doc_id(self) -> str:
        """Return the invoice document ID (cbc:ID)."""
        return str(self._data.get("id", ""))

    @property
    def issue_date(self) -> str:
        """Return the invoice issue date string (cbc:IssueDate)."""
        return str(self._data.get("issue_date", ""))

    @property
    def currency(self) -> str:
        """Return the document currency code (cbc:DocumentCurrencyCode)."""
        return str(self._data.get("currency", ""))

    @property
    def supplier(self) -> dict[str, Any]:
        """Return the supplier party dict (cac:AccountingSupplierParty)."""
        return dict(self._data.get("supplier", {}))

    @property
    def customer(self) -> dict[str, Any]:
        """Return the customer party dict (cac:AccountingCustomerParty)."""
        return dict(self._data.get("customer", {}))

    @property
    def tax_total(self) -> dict[str, Any]:
        """Return the tax total dict (cac:TaxTotal/TaxSubtotal)."""
        return dict(self._data.get("tax_total", {}))

    @property
    def monetary_total(self) -> dict[str, Any]:
        """Return the legal monetary total dict (cac:LegalMonetaryTotal)."""
        return dict(self._data.get("monetary_total", {}))

    @property
    def lines(self) -> list[dict[str, Any]]:
        """Return the list of invoice line items (cac:InvoiceLine)."""
        return list(self._data.get("lines", []))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Invoice(id={self.doc_id!r})"
