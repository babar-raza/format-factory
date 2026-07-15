"""OASIS UBL (.xml) codec — probe, load, write.

Supports UBL 2.x Invoice and Order documents. Detection uses
namespace URI matching on the root element.

Spec reference: FACT-UBL-001
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Union

from ubl.exceptions import UblParseError, UblWriteError

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB guard

NS_INVOICE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
NS_ORDER = "urn:oasis:names:specification:ubl:schema:xsd:Order-2"
NS_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NS_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

UBL_NAMESPACES = {NS_INVOICE: "Invoice", NS_ORDER: "Order"}

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "invoice",
    "order",
    "line_items",
    "party_info",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "credit_note",
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


def _parse_party(elem: ET.Element | None) -> dict[str, str]:
    """Extract party information."""
    if elem is None:
        return {}
    party = elem.find(f"{{{NS_CAC}}}Party")
    if party is None:
        return {}
    name_elem = party.find(f"{{{NS_CAC}}}PartyName")
    name = ""
    if name_elem is not None:
        name = _text(name_elem.find(f"{{{NS_CBC}}}Name"))
    return {"name": name}


def _parse_invoice(root: ET.Element) -> dict[str, Any]:
    """Parse UBL Invoice."""
    doc_id = _text(root.find(f"{{{NS_CBC}}}ID"))
    issue_date = _text(root.find(f"{{{NS_CBC}}}IssueDate"))
    currency = _text(root.find(f"{{{NS_CBC}}}DocumentCurrencyCode"))

    supplier = _parse_party(root.find(f"{{{NS_CAC}}}AccountingSupplierParty"))
    customer = _parse_party(root.find(f"{{{NS_CAC}}}AccountingCustomerParty"))

    lines: list[dict[str, Any]] = []
    for line_elem in root.findall(f"{{{NS_CAC}}}InvoiceLine"):
        line_id = _text(line_elem.find(f"{{{NS_CBC}}}ID"))
        quantity = _text(line_elem.find(f"{{{NS_CBC}}}InvoicedQuantity"))
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

    return {
        "document_type": "Invoice",
        "id": doc_id,
        "issue_date": issue_date,
        "currency": currency,
        "supplier": supplier,
        "customer": customer,
        "lines": lines,
    }


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
    elif doc_type == "Order":
        return _parse_order(root)
    else:
        raise UblParseError(f"Unsupported UBL document type: {doc_type}")


def write_ubl(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> str:
    """Serialize a UBL model dict to UBL 2.1 Invoice XML string."""
    doc_type = model.get("document_type", "Invoice")

    if doc_type == "Invoice":
        ns = NS_INVOICE
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

    if doc_type == "Invoice":
        if model.get("currency"):
            cbc_curr = ET.SubElement(root, f"{{{NS_CBC}}}DocumentCurrencyCode")
            cbc_curr.text = html.escape(model["currency"])

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
