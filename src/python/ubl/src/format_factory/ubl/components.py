"""Party-scoped update, honestly narrowing UBL-EDIT-001's own compound gap
further, alongside lines.py's own line-scoped narrowing.

SAL-UBL-OBL-237188D47391391E (UBL-EDIT-001): "CRUD for core business
components with schema-order preservation; edits cannot produce elements
the schema forbids at that position." lines.py's own module docstring
already narrowed this to "lines only," documenting that a general,
arbitrary-position CRUD layer for the schema's other core business
components (parties, payment means, tax totals, allowance charges) remains
a separate, larger undertaking -- it would need position-aware INSERT
support extended to cover document root types, which line operations do
not need (lines are always the trailing repeating group).

This module closes one further, genuinely separable piece: UPDATING an
ALREADY-PRESENT cac:Party inside an existing cac:AccountingSupplierParty
or cac:AccountingCustomerParty wrapper. Unlike inserting a brand-new
component, replacing one that already exists needs no position-aware
insertion logic at all -- the wrapper is already at its own schema-correct
position (a root-level, single-occurrence element, per SAL-UBL-00001/
SAL-UBL-00002's own party-role structure), so the update is exactly the
same `with_children()` immutable-replace primitive `lines.py` already
composes, applied one level deeper (replace the wrapper's own child, then
rebuild the wrapper itself as the root's own child).

Creating a brand-new supplier/customer party wrapper a document did not
already have remains out of scope, for the identical reason lines.py's own
"lines only" narrowing gives: that is the arbitrary-position insertion
problem this obligation's own missing_behavior still correctly calls
unbuilt.

``update_component`` generalizes the same insight to any OTHER repeating
root-level component -- cac:PaymentMeans, cac:TaxTotal,
cac:AllowanceCharge, and so on. These are `maxOccurs="unbounded"` in the
pinned UBL 2.3 schema (confirmed by direct XSD read), unlike Party's own
always-exactly-one wrappers, but the same core fact still holds: an
ALREADY-PRESENT occurrence, however many siblings of the same name it
has, is already at its own schema-correct position, so replacing it needs
no position-aware insertion logic either. Creating an ADDITIONAL
occurrence beyond what a document already has remains out of scope for
the identical reason.
"""

from __future__ import annotations

from format_factory.core import Diagnostic, Severity

from .errors import UblValidationError
from .model import UblDocument, XmlNode
from .model.query import DocumentIndex
from .model.typed import local_name
from .validation.validator import validate

_PARTY_ROLE_WRAPPERS = ("AccountingSupplierParty", "AccountingCustomerParty")


def _diagnostics(document: UblDocument) -> list[Diagnostic]:
    diagnostics = list(validate(document).diagnostics)
    for duplicate in DocumentIndex(document.root).duplicate_line_ids():
        diagnostics.append(
            Diagnostic(
                "ubl.referential.duplicate_line_id",
                f"line identifier {duplicate.identifier!r} is not unique",
                severity=Severity.ERROR,
            )
        )
    return diagnostics


def _refuse_if_worse(before: UblDocument, after: UblDocument) -> None:
    before_codes = {d.code for d in _diagnostics(before)}
    new = [d for d in _diagnostics(after) if d.code not in before_codes]
    if new:
        messages = "; ".join(d.message for d in new)
        raise UblValidationError(
            f"edit would introduce a new validation failure the source document "
            f"did not already have: {messages}"
        )


def replace_party(document: UblDocument, *, role: str, new_party: XmlNode) -> UblDocument:
    """Replace the cac:Party inside an existing `role` wrapper
    (cac:AccountingSupplierParty or cac:AccountingCustomerParty) with
    `new_party`.

    Raises `UblValidationError` if `role` is not one of the two known
    party-role wrappers, if `new_party` is not a cac:Party element, if the
    document has no existing `role` wrapper (creating a new one is the
    still-unbuilt arbitrary-position insertion problem), or if the edit
    would introduce a validation failure the source document did not
    already have.
    """
    if role not in _PARTY_ROLE_WRAPPERS:
        raise UblValidationError(
            f"role must be one of {_PARTY_ROLE_WRAPPERS!r}, got {role!r}"
        )
    if local_name(new_party.qname) != "Party":
        raise UblValidationError(
            f"new_party must be a cac:Party element, got {new_party.qname!r}"
        )

    wrapper_matches = [
        index
        for index, child in enumerate(document.root.children)
        if local_name(child.qname) == role
    ]
    if not wrapper_matches:
        raise UblValidationError(
            f"document has no existing {role} to replace the party of -- "
            "creating a new one is not supported"
        )
    if len(wrapper_matches) > 1:
        raise UblValidationError(
            f"document has {len(wrapper_matches)} {role} elements; "
            "replace_party requires exactly one"
        )
    wrapper_index = wrapper_matches[0]
    wrapper = document.root.children[wrapper_index]

    party_matches = [
        index for index, child in enumerate(wrapper.children) if local_name(child.qname) == "Party"
    ]
    if not party_matches:
        raise UblValidationError(f"{role} has no existing cac:Party child to replace")
    party_index = party_matches[0]
    new_wrapper_children = (
        wrapper.children[:party_index] + (new_party,) + wrapper.children[party_index + 1 :]
    )
    new_wrapper = wrapper.with_children(new_wrapper_children)
    new_root_children = (
        document.root.children[:wrapper_index]
        + (new_wrapper,)
        + document.root.children[wrapper_index + 1 :]
    )
    edited = document.with_root(document.root.with_children(new_root_children))
    _refuse_if_worse(document, edited)
    return edited


def update_component(
    document: UblDocument, *, component_name: str, index: int, new_component: XmlNode
) -> UblDocument:
    """Replace the `index`-th (0-based, counted among the document root's
    own same-local-name children) occurrence of a core business component
    -- cac:PaymentMeans, cac:TaxTotal, cac:AllowanceCharge, or any other
    root-level element named `component_name` -- with `new_component`.

    Generalizes `replace_party`'s own insight to any repeating root-level
    component, not just the two single-occurrence party wrappers
    (cac:PaymentMeans/cac:TaxTotal/cac:AllowanceCharge are all
    `maxOccurs="unbounded"` in the pinned UBL 2.3 schema, unlike Party's
    own always-exactly-one wrappers -- confirmed by direct XSD read before
    writing this, not assumed). An already-present occurrence is already
    at its own schema-correct position regardless of how many siblings of
    the same name exist, so replacing it needs no position-aware
    insertion logic at all -- only the same `with_children()` immutable
    -replace primitive `lines.py` and `replace_party` both already
    compose, indexed among same-name siblings instead of assumed unique.

    Raises `UblValidationError` if `new_component`'s own local name does
    not match `component_name`, if `index` is out of range for the
    document's own existing occurrences (creating an ADDITIONAL
    occurrence -- more of `component_name` than the document already has
    -- is the still-unbuilt arbitrary-position insertion problem), or if
    the edit would introduce a validation failure the source document did
    not already have.
    """
    if local_name(new_component.qname) != component_name:
        raise UblValidationError(
            f"new_component must be a cac:{component_name} element, got "
            f"{new_component.qname!r}"
        )

    matches = [
        position
        for position, child in enumerate(document.root.children)
        if local_name(child.qname) == component_name
    ]
    if not 0 <= index < len(matches):
        raise UblValidationError(
            f"index {index} is out of range for {len(matches)} existing "
            f"{component_name} element(s) in this document -- creating an "
            "additional occurrence is not supported"
        )
    target_index = matches[index]
    new_root_children = (
        document.root.children[:target_index]
        + (new_component,)
        + document.root.children[target_index + 1 :]
    )
    edited = document.with_root(document.root.with_children(new_root_children))
    _refuse_if_worse(document, edited)
    return edited


__all__ = ["replace_party", "update_component"]
