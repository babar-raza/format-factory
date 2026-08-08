"""Line-scoped CRUD, honestly narrowing UBL-EDIT-001's own compound gap.

SAL-UBL-OBL-237188D47391391E (UBL-EDIT-001): "CRUD for core business
components with schema-order preservation; edits cannot produce elements
the schema forbids at that position."

SAL-UBL-OBL-AF5263F0FC7036B9 (UBL-EDIT-001, sibling): "Line insertion,
removal, movement, and renumbering maintain referential integrity via an
explicit reference-rewrite map."

Before this module, no CRUD API existed beyond the low-level, schema-unaware
``XmlNode.with_children()``/``UblDocument.with_root()`` immutable-replace
primitives -- a caller had to hand-construct a replacement tree with no
help staying schema-order-valid. This module composes those existing
primitives with ``reorder_for_schema_order()`` (FF6-EVENT-000286) and
``validate()`` to give line-role components (the one category the second
obligation names explicitly) real add/remove/move/renumber operations that
refuse to leave the document less valid than they found it.

**Honest scope note, narrowing rather than closing the first obligation:**
"core business components" in the schema is far broader than lines --
parties, payment means, tax totals, and more all qualify. This module
covers lines only, the specific category the compound obligation's own
sibling names. A general schema-order-aware CRUD API for arbitrary
component types remains a separate, larger undertaking (it would need
``_ORDER_CHECKED_COMPONENTS``-style ordering knowledge extended to cover
document root types, which line operations do not need -- UBL Line
elements are always the trailing repeating group in every maindoc type's
own schema sequence, so appending/reordering among lines never disturbs
header-field order).

Renumbering does not attempt to rewrite every possible cross-reference a
caller's own extensions or a customization profile might carry to a line
ID -- UBL's own generic model has no closed set of "fields that reference a
line" to walk (that varies by profile). Instead, ``renumber_lines`` returns
an explicit old-ID-to-new-ID map, the mechanism the obligation's own
wording asks for, so a caller can apply it to whatever else in their own
data references these lines.
"""

from __future__ import annotations

from dataclasses import replace

from format_factory.core import Diagnostic, Severity

from .errors import UblValidationError
from .model import UblDocument, XmlNode
from .model.query import DocumentIndex, _own_identifier, business_role
from .validation.validator import reorder_for_schema_order, validate


def _line_children(root: XmlNode) -> list[tuple[int, XmlNode]]:
    return [
        (index, child)
        for index, child in enumerate(root.children)
        if business_role(child) == "line"
    ]


def _referential_diagnostics(document: UblDocument) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for duplicate in DocumentIndex(document.root).duplicate_line_ids():
        diagnostics.append(
            Diagnostic(
                "ubl.referential.duplicate_line_id",
                f"line identifier {duplicate.identifier!r} is not unique",
                severity=Severity.ERROR,
            )
        )
    return diagnostics


def _diagnostics_including_referential(document: UblDocument) -> list[Diagnostic]:
    return list(validate(document).diagnostics) + _referential_diagnostics(document)


def _refuse_if_worse(before: UblDocument, after: UblDocument) -> None:
    """Refuse an edit that leaves the document with a validation or
    referential-integrity failure it did not already have -- the chassis
    check alone (`validate()`) does not include the duplicate-line-id
    referential check `validate_all()`'s own combined layer added
    (FF6-EVENT-000296), so it is run here directly rather than left as a
    gap this module's own edits could silently reintroduce.
    """

    before_diagnostics = _diagnostics_including_referential(before)
    before_codes = {d.code for d in before_diagnostics}
    after_diagnostics = _diagnostics_including_referential(after)
    new = [d for d in after_diagnostics if d.code not in before_codes]
    if new:
        messages = "; ".join(d.message for d in new)
        raise UblValidationError(
            f"edit would introduce a new validation failure the source document "
            f"did not already have: {messages}"
        )


def add_line(document: UblDocument, line: XmlNode) -> UblDocument:
    """Append `line` (a line-role component) after every existing line.

    UBL Line elements (InvoiceLine, CreditNoteLine, OrderLine, ...) are
    always the trailing repeating group in every maindoc type's own schema
    sequence -- appending after the last existing line (or at the end of
    the root's children when there are none) is schema-position-correct by
    construction, without needing root-level reordering support. The
    inserted line's own internal field order is still run through
    `reorder_for_schema_order()` afterward, so a caller does not have to
    get that right by hand either.
    """

    lines = _line_children(document.root)
    insert_at = (lines[-1][0] + 1) if lines else len(document.root.children)
    new_children = (
        document.root.children[:insert_at]
        + (line,)
        + document.root.children[insert_at:]
    )
    edited = document.with_root(document.root.with_children(new_children))
    edited = reorder_for_schema_order(edited)
    _refuse_if_worse(document, edited)
    return edited


def remove_line(document: UblDocument, line_id: str) -> UblDocument:
    """Remove every line-role component whose own identifier equals `line_id`.

    Raises `UblValidationError` if `line_id` matches no line -- silently
    doing nothing on an unmatched ID would hide a caller's own mistake.
    """

    lines = _line_children(document.root)
    matching = [index for index, node in lines if _own_identifier(node) == line_id]
    if not matching:
        raise UblValidationError(f"no line with id {line_id!r} exists in this document")
    remove_set = set(matching)
    new_children = tuple(
        child for index, child in enumerate(document.root.children) if index not in remove_set
    )
    edited = document.with_root(document.root.with_children(new_children))
    _refuse_if_worse(document, edited)
    return edited


def move_line(document: UblDocument, line_id: str, *, to_index: int) -> UblDocument:
    """Move the line-role component identified by `line_id` to `to_index`
    among its own siblings of the same role (0-based, counted among lines
    only -- not among the root's full child list).

    Reordering among lines never disturbs header-field order (lines are
    always the trailing group), so this needs no root-level reorder
    support beyond removing and reinserting the one node.
    """

    lines = _line_children(document.root)
    matches = [index for index, node in lines if _own_identifier(node) == line_id]
    if not matches:
        raise UblValidationError(f"no line with id {line_id!r} exists in this document")
    if len(matches) > 1:
        raise UblValidationError(
            f"line id {line_id!r} is not unique ({len(matches)} lines share it); "
            "move_line requires an unambiguous target"
        )
    source_index = matches[0]
    node = document.root.children[source_index]
    without = tuple(
        child for index, child in enumerate(document.root.children) if index != source_index
    )
    line_positions = [index for index, child in enumerate(without) if business_role(child) == "line"]
    if not 0 <= to_index <= len(line_positions):
        raise UblValidationError(
            f"to_index {to_index} is out of range for {len(line_positions)} lines"
        )
    insert_at = line_positions[to_index] if to_index < len(line_positions) else len(without)
    new_children = without[:insert_at] + (node,) + without[insert_at:]
    edited = document.with_root(document.root.with_children(new_children))
    _refuse_if_worse(document, edited)
    return edited


def renumber_lines(document: UblDocument, id_map: dict[str, str]) -> tuple[UblDocument, dict[str, str]]:
    """Rewrite line identifiers per `id_map` (old ID -> new ID).

    Returns the edited document and `id_map` unchanged as an explicit
    reference-rewrite map -- the mechanism SAL-UBL-OBL-AF5263F0FC7036B9's
    own wording asks for, so a caller can apply it to whatever else in
    their own data (extensions, a profile's own cross-reference fields)
    points at these lines. This package's own generic model does not
    itself walk arbitrary cross-references, since which fields reference a
    line varies by customization profile -- see this module's own
    docstring.

    Raises `UblValidationError` for an unmapped ID, a target ID that
    collides with an existing (unrenamed) line's own ID, or a target ID
    reused for two different source lines.
    """

    lines = _line_children(document.root)
    current_ids = {_own_identifier(node) for _, node in lines}
    unrenamed = current_ids - set(id_map)
    new_ids = list(id_map.values())
    if len(set(new_ids)) != len(new_ids):
        raise UblValidationError("id_map maps two different lines to the same new id")
    colliding = set(new_ids) & unrenamed
    if colliding:
        raise UblValidationError(
            f"id_map target id(s) {sorted(colliding)!r} collide with an existing, "
            "unrenamed line's own id"
        )
    missing = set(id_map) - current_ids
    if missing:
        raise UblValidationError(f"id_map names id(s) not present in this document: {sorted(missing)!r}")

    def _rewrite(node: XmlNode) -> XmlNode:
        current = _own_identifier(node)
        if current not in id_map:
            return node
        new_value = id_map[current]
        new_children = tuple(
            replace(child, text=new_value)
            if child.qname.rsplit("}", 1)[-1] in {"ID", "LineID", "UUID"} and child.text == current
            else child
            for child in node.children
        )
        return node.with_children(new_children)

    new_root_children = tuple(
        _rewrite(child) if business_role(child) == "line" else child for child in document.root.children
    )
    edited = document.with_root(document.root.with_children(new_root_children))
    _refuse_if_worse(document, edited)
    return edited, dict(id_map)


__all__ = ["add_line", "move_line", "remove_line", "renumber_lines"]
