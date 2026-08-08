"""Structural validation for the stable UBL 2.3 chassis."""

from __future__ import annotations

from format_factory.core import BinarySource, Diagnostic, ResourceLimits, Severity, ValidationReport

from .._generated import ROOT_NAMESPACES, ROOT_NAME_SET
from ..codec import load
from ..errors import UblError
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
_ALLOWANCE_CHARGE_QNAME = f"{{{_CAC_NAMESPACE}}}AllowanceCharge"
_ITEM_QNAME = f"{{{_CAC_NAMESPACE}}}Item"
_PRICE_QNAME = f"{{{_CAC_NAMESPACE}}}Price"

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
#: AllowanceChargeType (read directly from the pinned schema ZIP) declares
#: ChargeIndicator (1) and AllowanceChargeReasonCode/Amount (0..1) as
#: maxOccurs=1, matching this package's own AllowanceCharge.charge_indicator/
#: reason_code/amount fields. AllowanceChargeReason is deliberately
#: excluded: the schema declares it minOccurs=0 maxOccurs=UNBOUNDED
#: (genuinely repeatable), even though this package's own
#: AllowanceCharge.reason field models only the first occurrence as a
#: singular value -- the same model-scoping question already documented
#: for PaymentMeans.PaymentID and Response.Description above. ID,
#: MultiplierFactorNumeric, PrepaidIndicator, SequenceNumeric, BaseAmount,
#: AccountingCostCode, AccountingCost, PerUnitAmount, TaxCategory, TaxTotal,
#: and PaymentMeans (the type's other maxOccurs<=1 or repeatable children)
#: are not modeled by this package's AllowanceCharge class at all -- left
#: unchecked, consistent with covering exactly the fields already modeled.
_ALLOWANCE_CHARGE_SINGLE_OCCURRENCE_FIELDS = frozenset(
    {"ChargeIndicator", "AllowanceChargeReasonCode", "Amount"}
)
#: ItemType (read directly from the pinned schema ZIP) declares Name as
#: maxOccurs=1, matching this package's own Item.name field -- the type's
#: only single-occurrence child this package models at all (identifiers/
#: classification_codes are deliberately excluded: ItemType has no direct
#: cbc:ID or cbc:CommodityClassification child, a genuinely separate,
#: unresolved model-field-mapping question, not a cardinality concern).
_ITEM_SINGLE_OCCURRENCE_FIELDS = frozenset({"Name"})
#: PriceType declares PriceAmount (1, required) and BaseQuantity (0..1) as
#: maxOccurs=1, matching this package's own Price.price_amount/
#: base_quantity fields exactly, in that declared order.
_PRICE_SINGLE_OCCURRENCE_FIELDS = frozenset({"PriceAmount", "BaseQuantity"})


def _local(qname: str) -> str:
    return qname.rsplit("}", 1)[-1]


def validate(
    value: UblDocument | BinarySource,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Validate supported root, QName, signature, and basic version invariants.

    This chassis validation is deliberately not an XSD-conformance claim.
    Full schema and cardinality validation remains a mandatory open obligation.

    `value` may also be a raw source (bytes, path, or stream): it is loaded
    internally, and a load-time failure is reported as a FATAL
    ``ubl.source.unreadable`` Diagnostic instead of propagating as an
    uncaught exception.
    """

    if not isinstance(value, UblDocument):
        try:
            value = load(value, limits=limits)
        except UblError as exc:
            return ValidationReport(
                [Diagnostic("ubl.source.unreadable", str(exc), severity=Severity.FATAL)]
            )

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
    diagnostics.extend(_order_diagnostics(value))
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
    _ALLOWANCE_CHARGE_QNAME: (
        _ALLOWANCE_CHARGE_SINGLE_OCCURRENCE_FIELDS,
        "cac:AllowanceCharge",
    ),
    _ITEM_QNAME: (_ITEM_SINGLE_OCCURRENCE_FIELDS, "cac:Item"),
    _PRICE_QNAME: (_PRICE_SINGLE_OCCURRENCE_FIELDS, "cac:Price"),
}


def _missing_mandatory_field_violations(
    node: XmlNode, mandatory_names: frozenset[str], component_label: str
) -> list[Diagnostic]:
    present = {_local(child.qname) for child in node.children}
    return [
        Diagnostic(
            "ubl.cardinality.missing",
            f"{component_label} is missing {name!r}, which the OASIS UBL 2.3 "
            "schema declares minOccurs=1 (mandatory)",
        )
        for name in sorted(mandatory_names - present)
    ]


#: qname -> (minOccurs=1 local names, human-readable component label).
#: Each entry's own field set must be read directly from the pinned
#: schema, never guessed or assumed symmetric with a sibling type -- a
#: field mandatory on one component can be optional on another that
#: happens to model the same field name. Confirmed directly, not assumed:
#: cac:InvoiceLine's own ID/LineExtensionAmount/Item are all minOccurs="1"
#: in InvoiceLineType, but cac:CreditNoteLine's own otherwise-identically
#: -named LineExtensionAmount and Item are minOccurs="0" in
#: CreditNoteLineType -- only ID is mandatory there. Scoped to fields
#: already covered by _CARDINALITY_CHECKED_COMPONENTS' own field sets for
#: the same component (this check only adds the missing-entirely
#: direction for already-modeled fields, not new fields).
_MANDATORY_FIELD_CHECKED_COMPONENTS: dict[str, tuple[frozenset[str], str]] = {
    _INVOICE_LINE_QNAME: (
        frozenset({"ID", "LineExtensionAmount", "Item"}),
        "cac:InvoiceLine",
    ),
    _CREDIT_NOTE_LINE_QNAME: (frozenset({"ID"}), "cac:CreditNoteLine"),
}


def _cardinality_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates:
    "full schema and cardinality validation remains a mandatory open
    obligation." A genuine, spec-grounded, ongoing slice: diagnoses a
    minOccurs=0(or 1) maxOccurs=1 element appearing more than once under
    any of the already-typed aggregate components this package models
    today (see _CARDINALITY_CHECKED_COMPONENTS), AND -- as of
    FF6-EVENT-000339 -- an already-modeled minOccurs=1 element appearing
    ZERO times under cac:InvoiceLine/cac:CreditNoteLine (see
    _MANDATORY_FIELD_CHECKED_COMPONENTS). Deliberately narrow in both
    directions: covers only these already-modeled fields on these
    already-modeled component types, not every complexType and field in
    the UBL 2.3 schema, which remains a separate, larger undertaking.
    """
    diagnostics: list[Diagnostic] = []
    for node in value.root.iter():
        checked = _CARDINALITY_CHECKED_COMPONENTS.get(node.qname)
        if checked is not None:
            fields, label = checked
            diagnostics.extend(_single_occurrence_violations(node, fields, label))
        mandatory_checked = _MANDATORY_FIELD_CHECKED_COMPONENTS.get(node.qname)
        if mandatory_checked is not None:
            mandatory_fields, mandatory_label = mandatory_checked
            diagnostics.extend(
                _missing_mandatory_field_violations(node, mandatory_fields, mandatory_label)
            )
    return diagnostics


#: Per the pinned OASIS UBL 2.3 CommonAggregateComponents schema, the
#: DECLARED SEQUENCE ORDER of exactly the already-modeled single-occurrence
#: fields from _CARDINALITY_CHECKED_COMPONENTS (a strict subset of each
#: complexType's full xsd:sequence, filtered and order-preserved
#: programmatically from the pinned schema, not transcribed by hand -- a
#: manual transcription of MonetaryTotalType's own order was caught and
#: corrected this way: PayableAmount is declared LAST in the schema, not
#: second, despite appearing second in this package's own frozenset
#: iteration order used for the unrelated cardinality check above).
_ORDER_CHECKED_COMPONENTS: dict[str, tuple[str, ...]] = {
    _PARTY_QNAME: ("PostalAddress", "Contact"),
    _POSTAL_ADDRESS_QNAME: ("StreetName", "CityName", "PostalZone", "Country"),
    _CONTACT_QNAME: ("Name", "Telephone", "ElectronicMail"),
    _PAYMENT_MEANS_QNAME: ("PaymentMeansCode", "PaymentDueDate", "PayeeFinancialAccount"),
    _PAYEE_FINANCIAL_ACCOUNT_QNAME: ("ID", "Name", "CurrencyCode"),
    _CREDIT_NOTE_LINE_QNAME: ("ID", "CreditedQuantity", "LineExtensionAmount", "Item"),
    _RESPONSE_QNAME: ("ResponseCode",),
    _DOCUMENT_REFERENCE_QNAME: ("ID", "DocumentTypeCode"),
    _INVOICE_LINE_QNAME: ("ID", "InvoicedQuantity", "LineExtensionAmount", "Item"),
    _TAX_SUBTOTAL_QNAME: ("TaxableAmount", "TaxAmount", "TaxCategory"),
    _TAX_TOTAL_QNAME: ("TaxAmount",),
    _LEGAL_MONETARY_TOTAL_QNAME: (
        "LineExtensionAmount",
        "TaxExclusiveAmount",
        "TaxInclusiveAmount",
        "AllowanceTotalAmount",
        "ChargeTotalAmount",
        "PayableAmount",
    ),
    _EXTERNAL_REFERENCE_QNAME: ("URI", "DocumentHash", "MimeCode", "FileName"),
    _ALLOWANCE_CHARGE_QNAME: ("ChargeIndicator", "AllowanceChargeReasonCode", "Amount"),
    _ITEM_QNAME: ("Name",),
    _PRICE_QNAME: ("PriceAmount", "BaseQuantity"),
}


def _order_violations(
    node: XmlNode, expected_order: tuple[str, ...], component_label: str
) -> list[Diagnostic]:
    expected_index = {name: index for index, name in enumerate(expected_order)}
    diagnostics: list[Diagnostic] = []
    highest_seen = -1
    highest_seen_name = ""
    for child in node.children:
        name = _local(child.qname)
        index = expected_index.get(name)
        if index is None:
            continue
        if index < highest_seen:
            diagnostics.append(
                Diagnostic(
                    "ubl.order.violation",
                    f"{component_label}: {name!r} appears after {highest_seen_name!r}, "
                    f"but the OASIS UBL 2.3 schema declares {name!r} before "
                    f"{highest_seen_name!r}",
                )
            )
        else:
            highest_seen = index
            highest_seen_name = name
    return diagnostics


def _order_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """SAL-UBL-OBL-3B43504E9C74003C and its cross-capability duplicates:
    "Child elements inside UBL aggregate components must appear in the
    order declared by the schema sequence model for the document to be
    valid." A genuine, spec-grounded slice: diagnoses a present, checked
    child element that appears out of its declared relative order among
    the already-modeled single-occurrence fields this package models today
    (see _ORDER_CHECKED_COMPONENTS -- the exact same already-typed
    components _CARDINALITY_CHECKED_COMPONENTS covers). Deliberately
    narrow, matching the cardinality cluster's own established scope
    discipline: covers only relative order among these already-modeled
    fields, not every child of every UBL complexType, and does not itself
    re-check cardinality (a genuinely duplicated field is handled
    separately by _cardinality_diagnostics; this function simply compares
    each occurrence against the running high-water mark, so a duplicate
    does not spuriously trigger an order violation on its own).
    """
    diagnostics: list[Diagnostic] = []
    for node in value.root.iter():
        expected_order = _ORDER_CHECKED_COMPONENTS.get(node.qname)
        if expected_order is not None:
            label = _CARDINALITY_CHECKED_COMPONENTS[node.qname][1]
            diagnostics.extend(_order_violations(node, expected_order, label))
    return diagnostics


def _reordered_known_children(
    children: tuple[XmlNode, ...], expected_order: tuple[str, ...]
) -> tuple[XmlNode, ...]:
    """Permute only the positions already occupied by a known-order field
    into their schema-declared relative sequence; every other child stays
    exactly where it is. Mirrors `_order_violations`'s own scope exactly:
    the same `expected_order` ground truth, the same "only among these
    already-modeled fields" discipline -- this is that check's writer-side
    counterpart, not a broader reordering of the whole element."""
    expected_index = {name: index for index, name in enumerate(expected_order)}
    known_positions = [
        index for index, child in enumerate(children) if _local(child.qname) in expected_index
    ]
    if len(known_positions) < 2:
        return children
    known_children = [children[index] for index in known_positions]
    sorted_known = sorted(known_children, key=lambda child: expected_index[_local(child.qname)])
    if sorted_known == known_children:
        return children
    reordered = list(children)
    for position, child in zip(known_positions, sorted_known):
        reordered[position] = child
    return tuple(reordered)


def _reorder_node(node: XmlNode) -> XmlNode:
    new_children = tuple(_reorder_node(child) for child in node.children)
    expected_order = _ORDER_CHECKED_COMPONENTS.get(node.qname)
    if expected_order is not None:
        new_children = _reordered_known_children(new_children, expected_order)
    if new_children != node.children:
        return node.with_children(new_children)
    return node


def reorder_for_schema_order(document: UblDocument) -> UblDocument:
    """SAL-UBL-OBL-4BD9BBC9F974C175 (UBL-WRITE-001): "write elements in
    schema-valid order independent of mutation order." Returns `document`
    with every already-modeled, order-checked field (`_ORDER_CHECKED_COMPONENTS`
    -- the same ground truth `_order_diagnostics` validates against) moved
    into its declared relative sequence, wherever in the tree that
    component type appears. A caller who constructs a Party's Contact
    before its PostalAddress, for example, gets schema-valid output
    regardless -- `validate()` never sees the out-of-order state this
    function runs before it. Every other child (any component this
    package does not yet model as order-checked) is left exactly where it
    was; this is a strict subset reorder, not a full schema-sequence
    regeneration, matching the same scope boundary `_order_diagnostics`
    itself declares.
    """
    new_root = _reorder_node(document.root)
    if new_root is document.root:
        return document
    return document.with_root(new_root)


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
