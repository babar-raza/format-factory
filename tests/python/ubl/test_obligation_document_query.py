"""UBL-QUERY-001 against the shipped namespace.

RF-UBL-00006 (MUST): find components by QName, type, ID, business identifier
(party, item, line, document reference), and typed role with path-aware
results, including read-only indexed views for large documents.
"""

from __future__ import annotations

from format_factory.ubl import DocumentIndex, business_role, loads

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

INVOICE = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:ID>INV-001</cbc:ID>
<cac:OrderReference>
  <cbc:ID>ORD-77</cbc:ID>
</cac:OrderReference>
<cac:BillingReference>
  <cac:InvoiceDocumentReference>
    <cbc:ID>PRIOR-INV-9</cbc:ID>
  </cac:InvoiceDocumentReference>
</cac:BillingReference>
<cac:AccountingSupplierParty>
  <cac:Party>
    <cbc:ID>SUPPLIER-1</cbc:ID>
  </cac:Party>
</cac:AccountingSupplierParty>
<cac:AccountingCustomerParty>
  <cac:Party>
    <cbc:ID>CUSTOMER-1</cbc:ID>
  </cac:Party>
</cac:AccountingCustomerParty>
<cac:InvoiceLine>
  <cbc:ID>1</cbc:ID>
  <cbc:InvoicedQuantity unitCode="KGM">2</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">20.00</cbc:LineExtensionAmount>
  <cac:Item>
    <cbc:Name>Coffee beans</cbc:Name>
    <cac:StandardItemIdentification>
      <cbc:ID>ITEM-COFFEE</cbc:ID>
    </cac:StandardItemIdentification>
  </cac:Item>
</cac:InvoiceLine>
<cac:InvoiceLine>
  <cbc:ID>2</cbc:ID>
  <cbc:InvoicedQuantity unitCode="LTR">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">5.00</cbc:LineExtensionAmount>
  <cac:Item>
    <cbc:Name>Milk</cbc:Name>
    <cac:StandardItemIdentification>
      <cbc:ID>ITEM-MILK</cbc:ID>
    </cac:StandardItemIdentification>
  </cac:Item>
</cac:InvoiceLine>
</Invoice>"""


def _root():
    return loads(INVOICE).root


# ── Find by QName and local name ("type") ───────────────────────────────────


def test_by_qname_finds_every_matching_element_anywhere_in_the_tree() -> None:
    index = DocumentIndex(_root())

    matches = index.by_qname(f"{{{CAC}}}InvoiceLine")

    assert len(matches) == 2
    assert all(match.node.qname == f"{{{CAC}}}InvoiceLine" for match in matches)


def test_by_local_name_matches_regardless_of_namespace() -> None:
    index = DocumentIndex(_root())

    matches = index.by_local_name("InvoiceLine")

    assert len(matches) == 2


def test_by_qname_returns_empty_for_a_component_not_present() -> None:
    index = DocumentIndex(_root())

    assert index.by_qname(f"{{{CAC}}}CreditNoteLine") == ()


# ── Path-aware results ───────────────────────────────────────────────────────


def test_matches_carry_a_path_from_the_root() -> None:
    index = DocumentIndex(_root())

    matches = index.by_local_name("Item")

    assert len(matches) == 2
    for match in matches:
        assert match.path[0] == "Invoice[0]"
        assert match.path[-1] == "Item[0]"
        assert any(segment.startswith("InvoiceLine[") for segment in match.path)


def test_paths_distinguish_two_matches_at_different_positions() -> None:
    index = DocumentIndex(_root())

    coffee_line, milk_line = index.by_local_name("InvoiceLine")

    assert coffee_line.path != milk_line.path


# ── Find by ID ────────────────────────────────────────────────────────────


def test_by_id_finds_a_node_whose_own_id_child_matches() -> None:
    index = DocumentIndex(_root())

    matches = index.by_id("ORD-77")

    assert len(matches) == 1
    assert business_role(matches[0].node) == "document_reference"


def test_by_id_finds_a_line_by_its_own_id() -> None:
    index = DocumentIndex(_root())

    matches = index.by_id("2")

    assert len(matches) == 1
    assert business_role(matches[0].node) == "line"


def test_by_id_returns_empty_for_an_identifier_not_present() -> None:
    index = DocumentIndex(_root())

    assert index.by_id("NO-SUCH-ID") == ()


# ── Business role: party, item, line, document reference ───────────────────


def test_business_role_classifies_party_shaped_components() -> None:
    from format_factory.ubl import find as find_child

    party_node = find_child(_root(), "AccountingSupplierParty")
    assert business_role(party_node) == "party"


def test_business_role_classifies_item() -> None:
    index = DocumentIndex(_root())
    (item_match,) = [m for m in index.by_local_name("Item")][:1]

    assert business_role(item_match.node) == "item"


def test_business_role_classifies_line() -> None:
    index = DocumentIndex(_root())
    line_match = index.by_local_name("InvoiceLine")[0]

    assert business_role(line_match.node) == "line"


def test_business_role_classifies_document_reference() -> None:
    index = DocumentIndex(_root())

    order_ref = index.by_local_name("OrderReference")[0]
    invoice_doc_ref = index.by_local_name("InvoiceDocumentReference")[0]

    assert business_role(order_ref.node) == "document_reference"
    assert business_role(invoice_doc_ref.node) == "document_reference"


def test_business_role_is_none_for_an_unrelated_component() -> None:
    index = DocumentIndex(_root())
    quantity = index.by_local_name("InvoicedQuantity")[0]

    assert business_role(quantity.node) is None


def test_by_business_role_finds_all_parties() -> None:
    index = DocumentIndex(_root())

    parties = index.by_business_role("party")

    names = {match.path[-1] for match in parties}
    # Both the outer AccountingSupplierParty/AccountingCustomerParty wrappers
    # and the inner cac:Party are "*Party"-suffixed, so all four are parties.
    assert "AccountingSupplierParty[0]" in names
    assert "AccountingCustomerParty[0]" in names
    assert len(parties) == 4


def test_by_business_role_finds_all_lines() -> None:
    index = DocumentIndex(_root())

    lines = index.by_business_role("line")

    assert len(lines) == 2


def test_by_business_role_finds_all_document_references() -> None:
    index = DocumentIndex(_root())

    refs = index.by_business_role("document_reference")
    names = {match.path[-1] for match in refs}

    assert names == {"OrderReference[0]", "InvoiceDocumentReference[0]"}


# ── The obligation's own worked example ─────────────────────────────────────


def test_finds_every_line_referencing_an_item_identifier() -> None:
    """"A developer finds every line referencing an item identifier and gets
    paths plus typed nodes back." """
    index = DocumentIndex(_root())

    matches = index.lines_referencing_item_id("ITEM-COFFEE")

    assert len(matches) == 1
    assert business_role(matches[0].node) == "line"
    assert matches[0].path[-1].startswith("InvoiceLine[")


def test_lines_referencing_item_id_returns_empty_for_an_unused_item() -> None:
    index = DocumentIndex(_root())

    assert index.lines_referencing_item_id("ITEM-NOT-ON-ANY-LINE") == ()


# ── Read-only index over a large document ───────────────────────────────────


def test_index_reuse_does_not_require_rewalking_the_tree() -> None:
    """The same index answers multiple distinct queries without being
    rebuilt -- "read-only indexed views for large documents" means build
    once, query many times."""
    index = DocumentIndex(_root())

    assert len(index.by_local_name("InvoiceLine")) == 2
    assert len(index.by_business_role("party")) == 4
    assert index.by_id("ORD-77") != ()
