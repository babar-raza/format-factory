"""UBL-PROFILE-001 -- customization and profile identifiers.

MUST (SAL-UBL-00128, verified, "UBL document metadata - customization and
profile"): "cbc:CustomizationID and cbc:ProfileID identify the
customization profile and business process profile a document instance
follows."

Before this slice, UblDocument exposed no accessor for either identifier
at all -- a caller wanting to know which customization or business-process
profile a document declared had to walk the XML tree by hand. Both
properties are live (like `declared_version`): they read the current tree,
so an edit is reflected immediately, and both are simply absent (None)
rather than defaulted to an invented value when the document does not
declare them, since neither is a MUST-present field in every UBL document
type.
"""

from __future__ import annotations

from format_factory.ubl import ROOT_CLASSES, XmlNode, loads

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
Invoice = ROOT_CLASSES["Invoice"]


def _invoice(*, customization: str | None = None, profile: str | None = None) -> bytes:
    parts = [f'<Invoice xmlns="{NAMESPACE}" xmlns:cbc="{CBC}">']
    if customization is not None:
        parts.append(f"<cbc:CustomizationID>{customization}</cbc:CustomizationID>")
    if profile is not None:
        parts.append(f"<cbc:ProfileID>{profile}</cbc:ProfileID>")
    parts.append("<cbc:ID>INV-001</cbc:ID></Invoice>")
    return "".join(parts).encode()


# ── customization_id ─────────────────────────────────────────────────────


def test_customization_id_is_exposed_when_declared() -> None:
    document = loads(_invoice(customization="urn:cen.eu:en16931:2017"))

    assert document.customization_id == "urn:cen.eu:en16931:2017"


def test_customization_id_is_none_when_absent() -> None:
    document = loads(_invoice())

    assert document.customization_id is None


def test_customization_id_on_a_freshly_built_document_is_none() -> None:
    document = Invoice.build(children=(XmlNode.create(f"{{{CBC}}}ID", text="INV-1"),))

    assert document.customization_id is None


# ── profile_id ────────────────────────────────────────────────────────────


def test_profile_id_is_exposed_when_declared() -> None:
    document = loads(_invoice(profile="urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"))

    assert document.profile_id == "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"


def test_profile_id_is_none_when_absent() -> None:
    document = loads(_invoice())

    assert document.profile_id is None


# ── Both identifiers are independent of each other and of the version ──────


def test_customization_and_profile_and_version_are_read_independently() -> None:
    document = loads(_invoice(customization="cust-1", profile="prof-1"))

    assert document.customization_id == "cust-1"
    assert document.profile_id == "prof-1"
    assert document.declared_version is None  # no cbc:UBLVersionID in this fixture


# ── Live: reflects an edit immediately, like declared_version ──────────────


def test_customization_id_reflects_an_edit_to_the_tree() -> None:
    document = loads(_invoice(customization="cust-1"))
    index = next(
        i
        for i, child in enumerate(document.root.children)
        if child.qname == f"{{{CBC}}}CustomizationID"
    )
    new_children = list(document.root.children)
    new_children[index] = XmlNode.create(f"{{{CBC}}}CustomizationID", text="cust-2")
    edited = document.with_root(document.root.with_children(tuple(new_children)))

    assert edited.customization_id == "cust-2"
