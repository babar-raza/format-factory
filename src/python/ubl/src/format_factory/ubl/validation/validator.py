"""Structural validation for the stable UBL 2.3 chassis."""

from __future__ import annotations

from format_factory.core import Diagnostic, ResourceLimits, Severity, ValidationReport

from .._generated import ROOT_NAMESPACES, ROOT_NAME_SET
from ..model import UblDocument, XmlNode

_CBC_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
)
_EXT_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
)
_UBL_EXTENSIONS_QNAME = f"{{{_EXT_NAMESPACE}}}UBLExtensions"
_UBL_EXTENSION_QNAME = f"{{{_EXT_NAMESPACE}}}UBLExtension"
_EXTENSION_CONTENT_QNAME = f"{{{_EXT_NAMESPACE}}}ExtensionContent"
_SIGNATURE_LOCAL_NAMES = frozenset({"Signature", "UBLDocumentSignatures"})

_CAC_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
)
_PARTY_QNAME = f"{{{_CAC_NAMESPACE}}}Party"
_POSTAL_ADDRESS_QNAME = f"{{{_CAC_NAMESPACE}}}PostalAddress"
_CONTACT_QNAME = f"{{{_CAC_NAMESPACE}}}Contact"
_PAYMENT_MEANS_QNAME = f"{{{_CAC_NAMESPACE}}}PaymentMeans"
_PAYEE_FINANCIAL_ACCOUNT_QNAME = f"{{{_CAC_NAMESPACE}}}PayeeFinancialAccount"
_CREDIT_NOTE_LINE_QNAME = f"{{{_CAC_NAMESPACE}}}CreditNoteLine"
_RESPONSE_QNAME = f"{{{_CAC_NAMESPACE}}}Response"
_DOCUMENT_REFERENCE_QNAME = f"{{{_CAC_NAMESPACE}}}DocumentReference"
_INVOICE_LINE_QNAME = f"{{{_CAC_NAMESPACE}}}InvoiceLine"
_TAX_SUBTOTAL_QNAME = f"{{{_CAC_NAMESPACE}}}TaxSubtotal"
_TAX_TOTAL_QNAME = f"{{{_CAC_NAMESPACE}}}TaxTotal"
_LEGAL_MONETARY_TOTAL_QNAME = f"{{{_CAC_NAMESPACE}}}LegalMonetaryTotal"
_EXTERNAL_REFERENCE_QNAME = f"{{{_CAC_NAMESPACE}}}ExternalReference"

#: Per the pinned OASIS UBL 2.3 CommonAggregateComponents schema
#: (xsd/common/UBL-CommonAggregateComponents-2.3.xsd, PartyType/AddressType/
#: ContactType/PaymentMeansType/FinancialAccountType complexTypes, read
#: directly from the pinned release ZIP): the minOccurs=0(or 1) maxOccurs=1
#: children of each type that this package currently models as a single
#: typed field (Party.postal_address, Party.contact, PostalAddress.
#: street_name/city_name/postal_zone/country, Contact.name/telephone/
#: electronic_mail, PaymentMeans.payment_means_code/payment_due_date/
#: payee_financial_account, FinancialAccount.id/name/currency_code). This
#: is a deliberately narrow, ongoing slice of "full schema and cardinality
#: validation" -- covering exactly the fields already modeled, not every
#: field of every UBL complexType, which remains a genuinely larger,
#: separate undertaking. PaymentMeans.PaymentID is deliberately excluded:
#: the schema declares it minOccurs=0 maxOccurs=UNBOUNDED (genuinely
#: repeatable), even though this package's own PaymentMeans.payment_id
#: field models only the first occurrence as a singular value -- that
#: model-scoping question is a separate concern from this cardinality
#: check, not silently resolved here.
_PARTY_SINGLE_OCCURRENCE_FIELDS = frozenset({"PostalAddress", "Contact"})
_POSTAL_ADDRESS_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"StreetName", "CityName", "PostalZone", "Country"}
)
_CONTACT_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"Name", "Telephone", "ElectronicMail"}
)
_PAYMENT_MEANS_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"PaymentMeansCode", "PaymentDueDate", "PayeeFinancialAccount"}
)
_FINANCIAL_ACCOUNT_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"ID", "Name", "CurrencyCode"}
)
_CREDIT_NOTE_LINE_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"ID", "CreditedQuantity", "LineExtensionAmount", "Item"}
)
#: ResponseType.Description is deliberately excluded: the schema declares
#: it minOccurs=0 maxOccurs=UNBOUNDED (genuinely repeatable), even though
#: this package's own Response.description field models only the first
#: occurrence as a singular value -- the same class of model-scoping
#: question already documented for PaymentMeans.PaymentID above.
_RESPONSE_SINGLE_OCCURRENCE_FIELDS = frozenset({"ResponseCode"})
_DOCUMENT_REFERENCE_SINGLE_OCCURRENCE_FIELDS = frozenset({"ID", "DocumentTypeCode"})
_INVOICE_LINE_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"ID", "InvoicedQuantity", "LineExtensionAmount", "Item"}
)
#: TaxSubtotal.category_code is projected from the nested cac:TaxCategory's
#: own cbc:ID, not a direct TaxSubtotal child -- TaxCategory itself
#: (maxOccurs=1 in TaxSubtotalType) is the checkable element here.
_TAX_SUBTOTAL_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"TaxableAmount", "TaxAmount", "TaxCategory"}
)
#: TaxTotal.subtotals is deliberately excluded: cac:TaxSubtotal is
#: minOccurs=0 maxOccurs=UNBOUNDED in TaxTotalType, matching the model's
#: own tuple[TaxSubtotal, ...] field -- genuinely repeatable, not a
#: cardinality violation candidate.
_TAX_TOTAL_SINGLE_OCCURRENCE_FIELDS = frozenset({"TaxAmount"})
_LEGAL_MONETARY_TOTAL_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {
        "LineExtensionAmount",
        "PayableAmount",
        "TaxExclusiveAmount",
        "TaxInclusiveAmount",
        "AllowanceTotalAmount",
        "ChargeTotalAmount",
    }
)
#: Description is deliberately excluded: ExternalReferenceType declares it
#: minOccurs=0 maxOccurs=UNBOUNDED (genuinely repeatable), unlike its
#: sibling fields URI/DocumentHash/MimeCode/FileName (all maxOccurs=1).
#: cac:ExternalReference itself is not currently reachable through this
#: package's own typed document-parsing path (it is a child of
#: cac:Attachment, which this package does not model at all) -- this check
#: still applies directly to the raw parsed XML tree, so it is genuine,
#: spec-grounded validation for any document containing the element,
#: independent of whether a typed projector surfaces it today.
_EXTERNAL_REFERENCE_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"URI", "DocumentHash", "MimeCode", "FileName"}
)


def _local(qname: str) -> str:
    return qname.rsplit("}", 1)[-1]


def validate(
    value: UblDocument,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Validate supported root, QName, signature, and basic version invariants.

    This chassis validation is deliberately not an XSD-conformance claim.
    Full schema and cardinality validation remains a mandatory open obligation.
    """

    del limits
    diagnostics: list[Diagnostic] = []
    selected = profile or "UBL-2.3"
    if selected != "UBL-2.3":
        diagnostics.append(
            Diagnostic(
                "ubl.profile.unsupported",
                f"stable profile supports only UBL-2.3, got {selected!r}",
            )
        )
    if value.root_name not in ROOT_NAME_SET:
        diagnostics.append(
            Diagnostic(
                "ubl.root.unsupported",
                f"unsupported UBL document root {value.root_name!r}",
            )
        )
        return ValidationReport(diagnostics)
    expected_namespace = ROOT_NAMESPACES[value.root_name]
    if value.namespace != expected_namespace:
        diagnostics.append(
            Diagnostic(
                "ubl.root.namespace",
                f"{value.root_name} must use namespace {expected_namespace!r}",
            )
        )
    version_values = [
        node.text.strip()
        for node in value.root.children
        if node.qname == f"{{{_CBC_NAMESPACE}}}UBLVersionID"
    ]
    if len(version_values) > 1:
        diagnostics.append(
            Diagnostic(
                "ubl.version.duplicate",
                "document has more than one UBLVersionID",
            )
        )
    for version in version_values:
        if version != "2.3":
            diagnostics.append(
                Diagnostic(
                    "ubl.version.unsupported",
                    f"stable profile requires UBLVersionID 2.3, got {version!r}",
                )
            )
    signature_nodes = [
        node for node in value.root.iter() if _local(node.qname) in _SIGNATURE_LOCAL_NAMES
    ]
    if signature_nodes and not value.signature_preserved:
        diagnostics.append(
            Diagnostic(
                "ubl.signature.invalidated",
                "signed content has been edited or lacks its source digest",
                severity=Severity.WARNING,
            )
        )
    diagnostics.extend(_extension_diagnostics(value))
    diagnostics.extend(_namespace_shadowing_diagnostics(value))
    diagnostics.extend(_cardinality_diagnostics(value))
    return ValidationReport(diagnostics)


def _single_occurrence_violations(
    node: XmlNode, single_occurrence_names: frozenset[str], component_label: str
) -> list[Diagnostic]:
    counts: dict[str, int] = {}
    for child in node.children:
        local = _local(child.qname)
        if local in single_occurrence_names:
            counts[local] = counts.get(local, 0) + 1
    return [
        Diagnostic(
            "ubl.cardinality.exceeded",
            f"{component_label} carries {count} {name!r} elements, but the "
            f"OASIS UBL 2.3 schema declares {name!r} 0..1 (at most one)",
        )
        for name, count in sorted(counts.items())
        if count > 1
    ]


#: qname -> (single-occurrence local names, human-readable component label).
#: Extending this mapping is how this cardinality check grows to cover more
#: already-modeled components over time -- each entry's field set must be
#: read directly from the pinned schema, never guessed.
_CARDINALITY_CHECKED_COMPONENTS: dict[str, tuple[frozenset[str], str]] = {
    _PARTY_QNAME: (_PARTY_SINGLE_OCCURRENCE_FIELDS, "cac:Party"),
    _POSTAL_ADDRESS_QNAME: (_POSTAL_ADDRESS_SINGLE_OCCURRENCE_FIELDS, "cac:PostalAddress"),
    _CONTACT_QNAME: (_CONTACT_SINGLE_OCCURRENCE_FIELDS, "cac:Contact"),
    _PAYMENT_MEANS_QNAME: (_PAYMENT_MEANS_SINGLE_OCCURRENCE_FIELDS, "cac:PaymentMeans"),
    _PAYEE_FINANCIAL_ACCOUNT_QNAME: (
        _FINANCIAL_ACCOUNT_SINGLE_OCCURRENCE_FIELDS,
        "cac:PayeeFinancialAccount",
    ),
    _CREDIT_NOTE_LINE_QNAME: (_CREDIT_NOTE_LINE_SINGLE_OCCURRENCE_FIELDS, "cac:CreditNoteLine"),
    _RESPONSE_QNAME: (_RESPONSE_SINGLE_OCCURRENCE_FIELDS, "cac:Response"),
    _DOCUMENT_REFERENCE_QNAME: (
        _DOCUMENT_REFERENCE_SINGLE_OCCURRENCE_FIELDS,
        "cac:DocumentReference",
    ),
    _INVOICE_LINE_QNAME: (_INVOICE_LINE_SINGLE_OCCURRENCE_FIELDS, "cac:InvoiceLine"),
    _TAX_SUBTOTAL_QNAME: (_TAX_SUBTOTAL_SINGLE_OCCURRENCE_FIELDS, "cac:TaxSubtotal"),
    _TAX_TOTAL_QNAME: (_TAX_TOTAL_SINGLE_OCCURRENCE_FIELDS, "cac:TaxTotal"),
    _LEGAL_MONETARY_TOTAL_QNAME: (
        _LEGAL_MONETARY_TOTAL_SINGLE_OCCURRENCE_FIELDS,
        "cac:LegalMonetaryTotal",
    ),
    _EXTERNAL_REFERENCE_QNAME: (
        _EXTERNAL_REFERENCE_SINGLE_OCCURRENCE_FIELDS,
        "cac:ExternalReference",
    ),
}


def _cardinality_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates:
    "full schema and cardinality validation remains a mandatory open
    obligation." A genuine, spec-grounded, ongoing slice: diagnoses a
    minOccurs=0(or 1) maxOccurs=1 element appearing more than once under
    any of the already-typed aggregate components this package models
    today (see _CARDINALITY_CHECKED_COMPONENTS). Deliberately narrow:
    covers only these already-modeled fields, not every complexType in the
    UBL 2.3 schema, which remains a separate, larger undertaking.
    """
    diagnostics: list[Diagnostic] = []
    for node in value.root.iter():
        checked = _CARDINALITY_CHECKED_COMPONENTS.get(node.qname)
        if checked is not None:
            fields, label = checked
            diagnostics.extend(_single_occurrence_violations(node, fields, label))
    return diagnostics


def _namespace(qname: str) -> str:
    return qname[1:].split("}", 1)[0] if qname.startswith("{") else ""


def _namespace_shadowing_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """SAL-UBL-OBL-0996E6D7B91D544F: model/typed.py's find()/find_all() (the
    navigation primitives used throughout this package) match children by
    local name only, never checking the expanded namespace -- a spoofed
    element sharing a real element's local name but placed in a different,
    untrusted namespace could be returned instead of, or ahead of, the
    genuine one.

    Rewriting find()/find_all() to check an expected namespace per call
    would need auditing and updating roughly 78 call sites across
    typed.py/aggregates.py/charges.py/reference.py/document.py -- a
    cross-cutting change with real blast radius, deliberately out of
    scope here (see this obligation's own missing_behavior text). Instead
    this detects the one structural signature every such spoofing attempt
    must share: two or more same-local-name children, in different
    namespaces, under one parent. No conformant UBL document produces
    this shape -- every field name is namespace-scoped and siblings-unique
    within its own vocabulary (cbc:/cac:/the root's own namespace). This
    makes validate() the safety net: a spoofed sibling fails validation
    before any find()-derived value is trusted downstream, even though
    find() itself remains naively vulnerable if called directly without
    validating first.

    Deliberately does not recurse into ext:ExtensionContent -- that
    subtree is explicitly opaque vendor content this package never reads
    via find()/find_all() by field name, so applying this check inside it
    would be a false-positive risk, not a real protection.
    """
    diagnostics: list[Diagnostic] = []

    def walk(node: XmlNode) -> None:
        by_local_name: dict[str, set[str]] = {}
        for child in node.children:
            by_local_name.setdefault(_local(child.qname), set()).add(
                _namespace(child.qname)
            )
        for local, namespaces in sorted(by_local_name.items()):
            if len(namespaces) > 1:
                diagnostics.append(
                    Diagnostic(
                        "ubl.namespace.shadowed_element",
                        f"element {local!r} appears under {_local(node.qname)!r} "
                        f"in {len(namespaces)} different namespaces "
                        f"{sorted(namespaces)!r} -- this shape never occurs in a "
                        "conformant UBL document and may indicate a spoofed element",
                    )
                )
        for child in node.children:
            if child.qname != _EXTENSION_CONTENT_QNAME:
                walk(child)

    walk(value.root)
    return diagnostics


def _extension_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """ext:UBLExtensions must be the first optional component in sequence
    order; each ext:UBLExtension must contain exactly one ext:ExtensionContent,
    which must itself contain exactly one apex element."""

    diagnostics: list[Diagnostic] = []
    for index, node in enumerate(value.root.children):
        if node.qname != _UBL_EXTENSIONS_QNAME:
            continue
        if index != 0:
            diagnostics.append(
                Diagnostic(
                    "ubl.extensions.position",
                    "ext:UBLExtensions must be the first optional component "
                    "in the document sequence",
                )
            )
        for extension in node.children:
            if extension.qname != _UBL_EXTENSION_QNAME:
                diagnostics.append(
                    Diagnostic(
                        "ubl.extensions.child",
                        "ext:UBLExtensions may only contain ext:UBLExtension "
                        f"children, found {extension.qname!r}",
                    )
                )
                continue
            content_children = [
                child for child in extension.children
                if child.qname == _EXTENSION_CONTENT_QNAME
            ]
            if len(content_children) != 1:
                diagnostics.append(
                    Diagnostic(
                        "ubl.extension.content.cardinality",
                        "ext:UBLExtension must contain exactly one "
                        f"ext:ExtensionContent, found {len(content_children)}",
                    )
                )
                continue
            if len(content_children[0].children) != 1:
                diagnostics.append(
                    Diagnostic(
                        "ubl.extension.content.apex",
                        "ext:ExtensionContent must contain exactly one apex "
                        f"element, found {len(content_children[0].children)}",
                    )
                )
    return diagnostics
