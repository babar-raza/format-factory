"""
UBL structural element: ubl:credit-note

Spec ref: OASIS UBL 2.3 Specification
Fact ref: FACT-UBL-105
QName: ubl:credit-note
Canonical class: Ubl.CreditNote
Facade: UblCreditNote
"""
from __future__ import annotations
from typing import Any, ClassVar


class CreditNote:
    """Canonical spec-shaped class for ubl:credit-note (architecture_only marker).

    Structurally near-identical to ubl:invoice (same cbc:/cac: component set);
    mandatory Peppol pairing for corrections/refunds against a prior Invoice.
    """

    spec_qname: ClassVar[str] = "ubl:credit-note"
    spec_fact_ref: ClassVar[str] = "FACT-UBL-105"
    namespace_uri: ClassVar[str] = "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"
    local_name: ClassVar[str] = "CreditNote"
    facade_names: ClassVar[list] = ["UblCreditNote"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def doc_id(self) -> str:
        """Return the credit note document ID (cbc:ID)."""
        return str(self._data.get("id", ""))

    @property
    def issue_date(self) -> str:
        """Return the credit note issue date string (cbc:IssueDate)."""
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
        """Return the list of credit note line items (cac:CreditNoteLine)."""
        return list(self._data.get("lines", []))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"CreditNote(id={self.doc_id!r})"
