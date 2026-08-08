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
unbuilt. cac:PaymentMeans, cac:TaxTotal, cac:AllowanceCharge and the
schema's other core business components are not attempted here either --
each would need its own investigation into whether it is single-occurrence
and root-level the way Party's own wrappers are (some, like
AllowanceCharge, can repeat, which changes the problem shape); Party was
chosen because it is one of this obligation's own three cited authority
facts (SAL-UBL-00123) and the simplest case to verify first.
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


__all__ = ["replace_party"]
