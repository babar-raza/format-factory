"""OASIS UBL (.xml) codec — probe, load, write.

Supports UBL 2.x Invoice, CreditNote, and Order documents. Detection uses
namespace URI matching on the root element.

Invoice and CreditNote documents also carry the legally-mandatory VAT
breakdown (cac:TaxTotal/cac:TaxSubtotal, FACT-UBL-101), the legal monetary
total (cac:LegalMonetaryTotal, FACT-UBL-102), and full party depth
(cac:PostalAddress, cac:PartyTaxScheme, cac:PartyLegalEntity, cac:Contact,
cbc:EndpointID — FACT-UBL-103) required to produce a document that could
pass validation at a real e-invoicing / Peppol portal.

Spec reference: FACT-UBL-001, FACT-UBL-002, FACT-UBL-101..105
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Union

from ubl.exceptions import UblParseError, UblWriteError

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB guard

NS_INVOICE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
NS_CREDIT_NOTE = "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"
NS_ORDER = "urn:oasis:names:specification:ubl:schema:xsd:Order-2"
NS_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NS_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

UBL_NAMESPACES = {
    NS_INVOICE: "Invoice",
    NS_CREDIT_NOTE: "CreditNote",
    NS_ORDER: "Order",
}

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "invoice",
    "credit_note",
    "order",
    "line_items",
    "party_info",
    "postal_address",
    "party_tax_scheme",
    "party_legal_entity",
    "contact",
    "endpoint_id",
    "tax_total",
    "legal_monetary_total",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "debit_note",
    "despatch_advice",
    "receipt_advice",
    "waybill",
    "catalogue",
    "signature",
    "streaming_parse",
]

SourceType = Union[str, Path, bytes]


def _read_source(source: SourceType) -> bytes:
    """Read source into bytes."""
    if isinstance(source, bytes):
        return source
    path = Path(source)
    if not path.exists():
        raise UblParseError(f"File not found: {source}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise UblParseError(f"File exceeds {MAX_FILE_SIZE} byte limit: {size} bytes")
    return path.read_bytes()


def _get_ubl_type(root: ET.Element) -> str | None:
    """Return UBL document type from root element namespace, or None."""
    tag = root.tag
    if tag.startswith("{"):
        ns = tag[1 : tag.index("}")]
        return UBL_NAMESPACES.get(ns)
    return None


def _text(elem: ET.Element | None) -> str:
    """Safely extract text content."""
    if elem is None:
        return ""
    return elem.text or ""


def probe_ubl(source: SourceType) -> bool:
    """Return True if source is a valid UBL document. Never raises."""
    try:
        data = _read_source(source)
        root = ET.fromstring(data)
        return _get_ubl_type(root) is not None
    except Exception:
        return False


def _parse_postal_address(addr_elem: ET.Element | None) -> dict[str, str]:
    """Extract cac:PostalAddress fields (street, city, postal code, country).

    Spec: cac:PostalAddress (FACT-UBL-103)
    """
    if addr_elem is None:
        return {}
    result: dict[str, str] = {}
    street_name = _text(addr_elem.find(f"{{{NS_CBC}}}StreetName"))
    if street_name:
        result["street_name"] = street_name
    city_name = _text(addr_elem.find(f"{{{NS_CBC}}}CityName"))
    if city_name:
        result["city_name"] = city_name
    postal_zone = _text(addr_elem.find(f"{{{NS_CBC}}}PostalZone"))
    if postal_zone:
        result["postal_zone"] = postal_zone
    country_elem = addr_elem.find(f"{{{NS_CAC}}}Country")
    if country_elem is not None:
        country_code = _text(country_elem.find(f"{{{NS_CBC}}}IdentificationCode"))
        if country_code:
            result["country_code"] = country_code
    return result


def _parse_party_tax_scheme(scheme_elem: ET.Element | None) -> dict[str, str]:
    """Extract cac:PartyTaxScheme (VAT ID / company id, tax scheme).

    Spec: cac:PartyTaxScheme (FACT-UBL-103)
    """
    if scheme_elem is None:
        return {}
    result: dict[str, str] = {}
    company_id = _text(scheme_elem.find(f"{{{NS_CBC}}}CompanyID"))
    if company_id:
        result["company_id"] = company_id
    tax_scheme_elem = scheme_elem.find(f"{{{NS_CAC}}}TaxScheme")
    if tax_scheme_elem is not None:
        scheme_id = _text(tax_scheme_elem.find(f"{{{NS_CBC}}}ID"))
        if scheme_id:
            result["tax_scheme_id"] = scheme_id
    return result


def _parse_party_legal_entity(elem: ET.Element | None) -> dict[str, str]:
    """Extract cac:PartyLegalEntity (registration name, company id).

    Spec: cac:PartyLegalEntity (FACT-UBL-103)
    """
    if elem is None:
        return {}
    result: dict[str, str] = {}
    registration_name = _text(elem.find(f"{{{NS_CBC}}}RegistrationName"))
    if registration_name:
        result["registration_name"] = registration_name
    company_id = _text(elem.find(f"{{{NS_CBC}}}CompanyID"))
    if company_id:
        result["company_id"] = company_id
    return result


def _parse_contact(elem: ET.Element | None) -> dict[str, str]:
    """Extract cac:Contact (name, telephone, email).

    Spec: cac:Contact (FACT-UBL-103)
    """
    if elem is None:
        return {}
    result: dict[str, str] = {}
    name = _text(elem.find(f"{{{NS_CBC}}}Name"))
    if name:
        result["name"] = name
    telephone = _text(elem.find(f"{{{NS_CBC}}}Telephone"))
    if telephone:
        result["telephone"] = telephone
    email = _text(elem.find(f"{{{NS_CBC}}}ElectronicMail"))
    if email:
        result["email"] = email
    return result


def _parse_endpoint_id(party_elem: ET.Element) -> dict[str, str]:
    """Extract cbc:EndpointID and its schemeID attribute (routing identifier).

    Spec: cbc:EndpointID (FACT-UBL-103, Peppol routing)
    """
    endpoint_elem = party_elem.find(f"{{{NS_CBC}}}EndpointID")
    if endpoint_elem is None:
        return {}
    result: dict[str, str] = {}
    value = _text(endpoint_elem)
    if value:
        result["endpoint_id"] = value
    scheme_id = endpoint_elem.get("schemeID")
    if scheme_id:
        result["endpoint_scheme_id"] = scheme_id
    return result


def _parse_party(elem: ET.Element | None) -> dict[str, Any]:
    """Extract full party information: name, endpoint id, postal address,
    tax scheme, legal entity, and contact.

    Spec: cac:Party (FACT-UBL-103)
    """
    if elem is None:
        return {}
    party = elem.find(f"{{{NS_CAC}}}Party")
    if party is None:
        return {}

    result: dict[str, Any] = {}

    name_elem = party.find(f"{{{NS_CAC}}}PartyName")
    name = ""
    if name_elem is not None:
        name = _text(name_elem.find(f"{{{NS_CBC}}}Name"))
    result["name"] = name

    result.update(_parse_endpoint_id(party))

    postal_address = _parse_postal_address(party.find(f"{{{NS_CAC}}}PostalAddress"))
    if postal_address:
        result["postal_address"] = postal_address

    party_tax_scheme = _parse_party_tax_scheme(party.find(f"{{{NS_CAC}}}PartyTaxScheme"))
    if party_tax_scheme:
        result["party_tax_scheme"] = party_tax_scheme

    party_legal_entity = _parse_party_legal_entity(party.find(f"{{{NS_CAC}}}PartyLegalEntity"))
    if party_legal_entity:
        result["party_legal_entity"] = party_legal_entity

    contact = _parse_contact(party.find(f"{{{NS_CAC}}}Contact"))
    if contact:
        result["contact"] = contact

    return result


def _parse_tax_subtotal(elem: ET.Element) -> dict[str, str]:
    """Extract one cac:TaxSubtotal (taxable amount, tax amount, category, percent).

    Spec: cac:TaxSubtotal (FACT-UBL-101)
    """
    result: dict[str, str] = {}
    taxable_amount = _text(elem.find(f"{{{NS_CBC}}}TaxableAmount"))
    if taxable_amount:
        result["taxable_amount"] = taxable_amount
    tax_amount = _text(elem.find(f"{{{NS_CBC}}}TaxAmount"))
    if tax_amount:
        result["tax_amount"] = tax_amount
    category_elem = elem.find(f"{{{NS_CAC}}}TaxCategory")
    if category_elem is not None:
        category_id = _text(category_elem.find(f"{{{NS_CBC}}}ID"))
        if category_id:
            result["tax_category_id"] = category_id
        percent = _text(category_elem.find(f"{{{NS_CBC}}}Percent"))
        if percent:
            result["tax_percent"] = percent
        scheme_elem = category_elem.find(f"{{{NS_CAC}}}TaxScheme")
        if scheme_elem is not None:
            scheme_id = _text(scheme_elem.find(f"{{{NS_CBC}}}ID"))
            if scheme_id:
                result["tax_scheme_id"] = scheme_id
    return result


def _parse_tax_total(root: ET.Element) -> dict[str, Any]:
    """Extract cac:TaxTotal / cac:TaxSubtotal — mandatory VAT breakdown.

    Spec: cac:TaxTotal (FACT-UBL-101)
    """
    tax_total_elem = root.find(f"{{{NS_CAC}}}TaxTotal")
    if tax_total_elem is None:
        return {}
    result: dict[str, Any] = {}
    tax_amount = _text(tax_total_elem.find(f"{{{NS_CBC}}}TaxAmount"))
    if tax_amount:
        result["tax_amount"] = tax_amount
    subtotals = [
        _parse_tax_subtotal(sub_elem)
        for sub_elem in tax_total_elem.findall(f"{{{NS_CAC}}}TaxSubtotal")
    ]
    if subtotals:
        result["tax_subtotals"] = subtotals
    return result


def _parse_monetary_total(root: ET.Element) -> dict[str, str]:
    """Extract cac:LegalMonetaryTotal (line/tax-exclusive/tax-inclusive/payable).

    Spec: cac:LegalMonetaryTotal (FACT-UBL-102)
    """
    elem = root.find(f"{{{NS_CAC}}}LegalMonetaryTotal")
    if elem is None:
        return {}
    result: dict[str, str] = {}
    for field, tag in (
        ("line_extension_amount", "LineExtensionAmount"),
        ("tax_exclusive_amount", "TaxExclusiveAmount"),
        ("tax_inclusive_amount", "TaxInclusiveAmount"),
        ("payable_amount", "PayableAmount"),
    ):
        value = _text(elem.find(f"{{{NS_CBC}}}{tag}"))
        if value:
            result[field] = value
    return result


def _parse_invoice_like(
    root: ET.Element,
    document_type: str,
    line_tag: str,
    quantity_tag: str,
) -> dict[str, Any]:
    """Parse an Invoice or CreditNote document.

    Invoice and CreditNote share the same cbc:/cac: component set (only the
    root namespace, line container tag, and quantity element name differ),
    so both document types are parsed through this shared routine.

    Spec: FACT-UBL-002 (Invoice), FACT-UBL-105 (CreditNote)
    """
    doc_id = _text(root.find(f"{{{NS_CBC}}}ID"))
    issue_date = _text(root.find(f"{{{NS_CBC}}}IssueDate"))
    currency = _text(root.find(f"{{{NS_CBC}}}DocumentCurrencyCode"))

    supplier = _parse_party(root.find(f"{{{NS_CAC}}}AccountingSupplierParty"))
    customer = _parse_party(root.find(f"{{{NS_CAC}}}AccountingCustomerParty"))
    tax_total = _parse_tax_total(root)
    monetary_total = _parse_monetary_total(root)

    lines: list[dict[str, Any]] = []
    for line_elem in root.findall(f"{{{NS_CAC}}}{line_tag}"):
        line_id = _text(line_elem.find(f"{{{NS_CBC}}}ID"))
        quantity = _text(line_elem.find(f"{{{NS_CBC}}}{quantity_tag}"))
        amount = _text(line_elem.find(f"{{{NS_CBC}}}LineExtensionAmount"))

        item_elem = line_elem.find(f"{{{NS_CAC}}}Item")
        item_name = ""
        if item_elem is not None:
            item_name = _text(item_elem.find(f"{{{NS_CBC}}}Name"))

        lines.append({
            "id": line_id,
            "quantity": quantity,
            "amount": amount,
            "item_name": item_name,
        })

    result: dict[str, Any] = {
        "document_type": document_type,
        "id": doc_id,
        "issue_date": issue_date,
        "currency": currency,
        "supplier": supplier,
        "customer": customer,
        "lines": lines,
    }
    if tax_total:
        result["tax_total"] = tax_total
    if monetary_total:
        result["monetary_total"] = monetary_total
    return result


def _parse_invoice(root: ET.Element) -> dict[str, Any]:
    """Parse UBL Invoice (cac:InvoiceLine / cbc:InvoicedQuantity)."""
    return _parse_invoice_like(root, "Invoice", "InvoiceLine", "InvoicedQuantity")


def _parse_credit_note(root: ET.Element) -> dict[str, Any]:
    """Parse UBL CreditNote (cac:CreditNoteLine / cbc:CreditedQuantity).

    CreditNote is structurally near-identical to Invoice — same cbc:/cac:
    component set, different root namespace
    (urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2). Mandatory
    Peppol pairing for corrections/refunds. Spec: FACT-UBL-105.
    """
    return _parse_invoice_like(root, "CreditNote", "CreditNoteLine", "CreditedQuantity")


def _parse_order(root: ET.Element) -> dict[str, Any]:
    """Parse UBL Order."""
    doc_id = _text(root.find(f"{{{NS_CBC}}}ID"))
    issue_date = _text(root.find(f"{{{NS_CBC}}}IssueDate"))

    buyer = _parse_party(root.find(f"{{{NS_CAC}}}BuyerCustomerParty"))
    seller = _parse_party(root.find(f"{{{NS_CAC}}}SellerSupplierParty"))

    lines: list[dict[str, Any]] = []
    for line_elem in root.findall(f"{{{NS_CAC}}}OrderLine"):
        line_item = line_elem.find(f"{{{NS_CAC}}}LineItem")
        if line_item is None:
            continue
        line_id = _text(line_item.find(f"{{{NS_CBC}}}ID"))
        quantity = _text(line_item.find(f"{{{NS_CBC}}}Quantity"))

        item_elem = line_item.find(f"{{{NS_CAC}}}Item")
        item_name = ""
        if item_elem is not None:
            item_name = _text(item_elem.find(f"{{{NS_CBC}}}Name"))

        lines.append({"id": line_id, "quantity": quantity, "item_name": item_name})

    return {
        "document_type": "Order",
        "id": doc_id,
        "issue_date": issue_date,
        "buyer": buyer,
        "seller": seller,
        "lines": lines,
    }


def load_ubl(source: SourceType) -> dict[str, Any]:
    """Parse a UBL document and return a canonical model dict."""
    data = _read_source(source)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise UblParseError(f"Invalid XML: {exc}") from exc

    doc_type = _get_ubl_type(root)
    if doc_type is None:
        raise UblParseError("Not a UBL document: root namespace is not UBL 2.x")

    if doc_type == "Invoice":
        return _parse_invoice(root)
    elif doc_type == "CreditNote":
        return _parse_credit_note(root)
    elif doc_type == "Order":
        return _parse_order(root)
    else:
        raise UblParseError(f"Unsupported UBL document type: {doc_type}")


def _write_postal_address(party_elem: ET.Element, postal_address: dict[str, Any]) -> None:
    """Serialize cac:PostalAddress. Spec: FACT-UBL-103."""
    if not postal_address:
        return
    addr_elem = ET.SubElement(party_elem, f"{{{NS_CAC}}}PostalAddress")
    if postal_address.get("street_name"):
        e = ET.SubElement(addr_elem, f"{{{NS_CBC}}}StreetName")
        e.text = html.escape(str(postal_address["street_name"]))
    if postal_address.get("city_name"):
        e = ET.SubElement(addr_elem, f"{{{NS_CBC}}}CityName")
        e.text = html.escape(str(postal_address["city_name"]))
    if postal_address.get("postal_zone"):
        e = ET.SubElement(addr_elem, f"{{{NS_CBC}}}PostalZone")
        e.text = html.escape(str(postal_address["postal_zone"]))
    if postal_address.get("country_code"):
        country_elem = ET.SubElement(addr_elem, f"{{{NS_CAC}}}Country")
        code_elem = ET.SubElement(country_elem, f"{{{NS_CBC}}}IdentificationCode")
        code_elem.text = html.escape(str(postal_address["country_code"]))


def _write_party_tax_scheme(party_elem: ET.Element, party_tax_scheme: dict[str, Any]) -> None:
    """Serialize cac:PartyTaxScheme. Spec: FACT-UBL-103."""
    if not party_tax_scheme:
        return
    scheme_wrapper = ET.SubElement(party_elem, f"{{{NS_CAC}}}PartyTaxScheme")
    if party_tax_scheme.get("company_id"):
        e = ET.SubElement(scheme_wrapper, f"{{{NS_CBC}}}CompanyID")
        e.text = html.escape(str(party_tax_scheme["company_id"]))
    if party_tax_scheme.get("tax_scheme_id"):
        tax_scheme_elem = ET.SubElement(scheme_wrapper, f"{{{NS_CAC}}}TaxScheme")
        e = ET.SubElement(tax_scheme_elem, f"{{{NS_CBC}}}ID")
        e.text = html.escape(str(party_tax_scheme["tax_scheme_id"]))


def _write_party_legal_entity(party_elem: ET.Element, party_legal_entity: dict[str, Any]) -> None:
    """Serialize cac:PartyLegalEntity. Spec: FACT-UBL-103."""
    if not party_legal_entity:
        return
    legal_elem = ET.SubElement(party_elem, f"{{{NS_CAC}}}PartyLegalEntity")
    if party_legal_entity.get("registration_name"):
        e = ET.SubElement(legal_elem, f"{{{NS_CBC}}}RegistrationName")
        e.text = html.escape(str(party_legal_entity["registration_name"]))
    if party_legal_entity.get("company_id"):
        e = ET.SubElement(legal_elem, f"{{{NS_CBC}}}CompanyID")
        e.text = html.escape(str(party_legal_entity["company_id"]))


def _write_contact(party_elem: ET.Element, contact: dict[str, Any]) -> None:
    """Serialize cac:Contact. Spec: FACT-UBL-103."""
    if not contact:
        return
    contact_elem = ET.SubElement(party_elem, f"{{{NS_CAC}}}Contact")
    if contact.get("name"):
        e = ET.SubElement(contact_elem, f"{{{NS_CBC}}}Name")
        e.text = html.escape(str(contact["name"]))
    if contact.get("telephone"):
        e = ET.SubElement(contact_elem, f"{{{NS_CBC}}}Telephone")
        e.text = html.escape(str(contact["telephone"]))
    if contact.get("email"):
        e = ET.SubElement(contact_elem, f"{{{NS_CBC}}}ElectronicMail")
        e.text = html.escape(str(contact["email"]))


def _write_party(parent: ET.Element, tag: str, party: dict[str, Any]) -> None:
    """Serialize a party dict as ``<cac:{tag}><cac:Party>...</cac:Party></cac:{tag}>``.

    Fixes the write-side round-trip bug: previously write_ubl silently
    dropped all party data that load_ubl parsed (AccountingSupplierParty /
    AccountingCustomerParty / BuyerCustomerParty / SellerSupplierParty were
    never re-emitted). Spec: FACT-UBL-104.
    """
    if not party:
        return
    wrapper_elem = ET.SubElement(parent, f"{{{NS_CAC}}}{tag}")
    party_elem = ET.SubElement(wrapper_elem, f"{{{NS_CAC}}}Party")

    if party.get("endpoint_id"):
        endpoint_elem = ET.SubElement(party_elem, f"{{{NS_CBC}}}EndpointID")
        endpoint_elem.text = html.escape(str(party["endpoint_id"]))
        if party.get("endpoint_scheme_id"):
            endpoint_elem.set("schemeID", str(party["endpoint_scheme_id"]))

    if party.get("name"):
        party_name_elem = ET.SubElement(party_elem, f"{{{NS_CAC}}}PartyName")
        name_elem = ET.SubElement(party_name_elem, f"{{{NS_CBC}}}Name")
        name_elem.text = html.escape(str(party["name"]))

    _write_postal_address(party_elem, party.get("postal_address", {}))
    _write_party_tax_scheme(party_elem, party.get("party_tax_scheme", {}))
    _write_party_legal_entity(party_elem, party.get("party_legal_entity", {}))
    _write_contact(party_elem, party.get("contact", {}))


def _write_tax_total(root: ET.Element, tax_total: dict[str, Any]) -> None:
    """Serialize cac:TaxTotal / cac:TaxSubtotal. Spec: FACT-UBL-101."""
    if not tax_total:
        return
    tax_total_elem = ET.SubElement(root, f"{{{NS_CAC}}}TaxTotal")
    if tax_total.get("tax_amount"):
        e = ET.SubElement(tax_total_elem, f"{{{NS_CBC}}}TaxAmount")
        e.text = html.escape(str(tax_total["tax_amount"]))
    for subtotal in tax_total.get("tax_subtotals", []):
        sub_elem = ET.SubElement(tax_total_elem, f"{{{NS_CAC}}}TaxSubtotal")
        if subtotal.get("taxable_amount"):
            e = ET.SubElement(sub_elem, f"{{{NS_CBC}}}TaxableAmount")
            e.text = html.escape(str(subtotal["taxable_amount"]))
        if subtotal.get("tax_amount"):
            e = ET.SubElement(sub_elem, f"{{{NS_CBC}}}TaxAmount")
            e.text = html.escape(str(subtotal["tax_amount"]))
        has_category = (
            subtotal.get("tax_category_id")
            or subtotal.get("tax_percent")
            or subtotal.get("tax_scheme_id")
        )
        if has_category:
            cat_elem = ET.SubElement(sub_elem, f"{{{NS_CAC}}}TaxCategory")
            if subtotal.get("tax_category_id"):
                e = ET.SubElement(cat_elem, f"{{{NS_CBC}}}ID")
                e.text = html.escape(str(subtotal["tax_category_id"]))
            if subtotal.get("tax_percent"):
                e = ET.SubElement(cat_elem, f"{{{NS_CBC}}}Percent")
                e.text = html.escape(str(subtotal["tax_percent"]))
            if subtotal.get("tax_scheme_id"):
                scheme_elem = ET.SubElement(cat_elem, f"{{{NS_CAC}}}TaxScheme")
                e = ET.SubElement(scheme_elem, f"{{{NS_CBC}}}ID")
                e.text = html.escape(str(subtotal["tax_scheme_id"]))


def _write_monetary_total(root: ET.Element, monetary_total: dict[str, Any]) -> None:
    """Serialize cac:LegalMonetaryTotal. Spec: FACT-UBL-102."""
    if not monetary_total:
        return
    elem = ET.SubElement(root, f"{{{NS_CAC}}}LegalMonetaryTotal")
    for field, tag in (
        ("line_extension_amount", "LineExtensionAmount"),
        ("tax_exclusive_amount", "TaxExclusiveAmount"),
        ("tax_inclusive_amount", "TaxInclusiveAmount"),
        ("payable_amount", "PayableAmount"),
    ):
        if monetary_total.get(field):
            e = ET.SubElement(elem, f"{{{NS_CBC}}}{tag}")
            e.text = html.escape(str(monetary_total[field]))


def _write_invoice_like(
    root: ET.Element,
    model: dict[str, Any],
    line_tag: str,
    quantity_tag: str,
) -> None:
    """Serialize the shared Invoice/CreditNote body: currency, parties, tax
    total, legal monetary total, and lines — in UBL schema sequence order.
    """
    if model.get("currency"):
        cbc_curr = ET.SubElement(root, f"{{{NS_CBC}}}DocumentCurrencyCode")
        cbc_curr.text = html.escape(model["currency"])

    _write_party(root, "AccountingSupplierParty", model.get("supplier") or {})
    _write_party(root, "AccountingCustomerParty", model.get("customer") or {})

    _write_tax_total(root, model.get("tax_total") or {})
    _write_monetary_total(root, model.get("monetary_total") or {})

    for line in model.get("lines", []):
        line_elem = ET.SubElement(root, f"{{{NS_CAC}}}{line_tag}")
        line_id = ET.SubElement(line_elem, f"{{{NS_CBC}}}ID")
        line_id.text = html.escape(str(line.get("id", "")))
        if line.get("quantity"):
            qty = ET.SubElement(line_elem, f"{{{NS_CBC}}}{quantity_tag}")
            qty.text = html.escape(str(line["quantity"]))
        if line.get("amount"):
            amt = ET.SubElement(line_elem, f"{{{NS_CBC}}}LineExtensionAmount")
            amt.text = html.escape(str(line["amount"]))
        if line.get("item_name"):
            item_elem = ET.SubElement(line_elem, f"{{{NS_CAC}}}Item")
            item_name_elem = ET.SubElement(item_elem, f"{{{NS_CBC}}}Name")
            item_name_elem.text = html.escape(str(line["item_name"]))


def write_ubl(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> str:
    """Serialize a UBL model dict to UBL 2.x XML string.

    Re-emits every field load_ubl() parses: party data (including postal
    address, VAT/tax scheme, legal entity, contact, and endpoint id), tax
    totals, and the legal monetary total (FACT-UBL-101..104).
    """
    doc_type = model.get("document_type", "Invoice")

    if doc_type == "Invoice":
        ns = NS_INVOICE
    elif doc_type == "CreditNote":
        ns = NS_CREDIT_NOTE
    elif doc_type == "Order":
        ns = NS_ORDER
    else:
        raise UblWriteError(f"Unsupported document type: {doc_type}")

    ET.register_namespace("", ns)
    ET.register_namespace("cbc", NS_CBC)
    ET.register_namespace("cac", NS_CAC)

    root = ET.Element(f"{{{ns}}}{doc_type}")

    cbc_id = ET.SubElement(root, f"{{{NS_CBC}}}ID")
    cbc_id.text = html.escape(model.get("id", ""))

    cbc_date = ET.SubElement(root, f"{{{NS_CBC}}}IssueDate")
    cbc_date.text = html.escape(model.get("issue_date", ""))

    if doc_type in ("Invoice", "CreditNote"):
        line_tag = "InvoiceLine" if doc_type == "Invoice" else "CreditNoteLine"
        quantity_tag = "InvoicedQuantity" if doc_type == "Invoice" else "CreditedQuantity"
        _write_invoice_like(root, model, line_tag, quantity_tag)
    elif doc_type == "Order":
        _write_party(root, "BuyerCustomerParty", model.get("buyer") or {})
        _write_party(root, "SellerSupplierParty", model.get("seller") or {})
        for line in model.get("lines", []):
            order_line = ET.SubElement(root, f"{{{NS_CAC}}}OrderLine")
            line_item = ET.SubElement(order_line, f"{{{NS_CAC}}}LineItem")
            line_id = ET.SubElement(line_item, f"{{{NS_CBC}}}ID")
            line_id.text = html.escape(str(line.get("id", "")))
            if line.get("quantity"):
                qty = ET.SubElement(line_item, f"{{{NS_CBC}}}Quantity")
                qty.text = html.escape(str(line["quantity"]))
            if line.get("item_name"):
                item_elem = ET.SubElement(line_item, f"{{{NS_CAC}}}Item")
                item_name_elem = ET.SubElement(item_elem, f"{{{NS_CBC}}}Name")
                item_name_elem.text = html.escape(str(line["item_name"]))

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    result = ET.tostring(root, encoding="unicode", xml_declaration=True)

    if dest is not None:
        path = Path(dest)
        try:
            path.write_text(result, encoding="utf-8")
        except OSError as exc:
            raise UblWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_line_count(model: dict[str, Any]) -> int:
    """Return number of line items."""
    return len(model.get("lines", []))


def roundtrip(source: SourceType, dest: Union[str, Path]) -> dict[str, Any]:
    """Load a UBL file, write it, and reload."""
    model = load_ubl(source)
    write_ubl(model, dest)
    return load_ubl(dest)


def ubl_installed_workflow(source: SourceType) -> dict[str, Any]:
    """Return format metadata for a UBL source (installed-package proof)."""
    model = load_ubl(source)
    return {
        "format": "ubl",
        "loaded": True,
        "document_type": model.get("document_type", ""),
        "id": model.get("id", ""),
        "line_count": get_line_count(model),
    }
