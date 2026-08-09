"""UBL-UPGRADE-001 -- detect older UBL versions and migrate to the stable
profile.

MUST (SAL-UBL-OBL-7B16479ACBBC8EFC): "Detect older specification versions
where practical; migrate via explicit transforms producing a migration
report; never label a document as the target version without structural
migration and validation."

SAL-UBL-7546731B76606EC0 (a direct structural diff of the acquired OASIS
UBL 2.1 and UBL 2.3 release packages, SRC-UBL-002/SRC-UBL-004): for 65 of
the 91 UBL 2.3 root document types, every root-level schema difference
between 2.1 and 2.3 is either a newly-added OPTIONAL element or a
cardinality WIDENING -- never a removal, a reordering, or a tightening. A
valid UBL 2.1 document of one of these 65 types is therefore ALREADY
structurally valid content under the 2.3 schema: migration for these types
needs no content rewriting at all, only relabeling ``cbc:UBLVersionID`` to
"2.3" -- and even that relabel only happens after this package's own
``validate()`` confirms the relabeled result genuinely passes the stable
2.3 profile, per this obligation's own "never label... without...
validation" clause, enforced here as a hard precondition rather than a
disclosed caveat.

``migrate_document()`` deliberately supports ONLY the 2.1-to-2.3
direction, the one pair this package has an acquired, diffed authority
source for. The other 26 UBL 2.3 root types (for example ``BusinessCard``,
``ImportCustomsDeclaration``) never had a UBL 2.1 schema at all -- every
one of the 65 root types that DID exist in both versions was independently
confirmed additive/relaxing-only, with zero exceptions (confirmed directly
against the acquired package by
``tools/generate_migratable_2_1_roots.py``, not assumed). The 26
schema-absent types are refused, not silently attempted. A document
declaring any OTHER older version (2.0, 2.2) is also refused: this package
has not acquired or diffed those schema packages, and inventing a
migration transform without a verified structural basis is exactly what
this session's own evidence discipline exists to prevent.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ._generated.migratable_2_1_roots import (
    MIGRATABLE_2_1_ROOT_NAMES,
    SOURCE_VERSION,
    TARGET_VERSION,
)
from .errors import UblValidationError
from .model import UblDocument
from .model.document import _UBL_VERSION_QNAME
from .validation.validator import validate


@dataclass(frozen=True, slots=True)
class MigrationReport:
    """The outcome of one ``migrate_document()`` call -- this obligation's
    own "producing a migration report" clause, not merely a boolean."""

    root_name: str
    source_version: str
    target_version: str
    note: str


def migrate_document(document: UblDocument) -> tuple[UblDocument, MigrationReport]:
    """Migrate ``document`` from its own declared UBL 2.1 to UBL 2.3.

    Returns ``(migrated_document, MigrationReport)`` on success. Raises
    ``UblValidationError`` -- never a silent no-op or a partially-migrated
    result -- when:

    - ``document`` does not declare ``UBLVersionID`` "2.1" at all (nothing
      to migrate FROM; migrating from any OTHER older version is not
      attempted, since this package has not acquired or diffed that
      version's own schema package);
    - ``document``'s root type is not one of the 65 root types
      ``SAL-UBL-7546731B76606EC0`` proves are additive/relaxing-only
      between 2.1 and 2.3;
    - the relabeled result fails ``validate()`` against the stable 2.3
      profile.

    ``document`` itself is never mutated (``UblDocument`` is frozen); the
    migrated result is always a new object.
    """
    declared = document.declared_version
    if declared != SOURCE_VERSION:
        raise UblValidationError(
            f"migrate_document only supports UBL {SOURCE_VERSION!r} as a source version; "
            f"document declares {declared!r}"
        )
    if document.root_name not in MIGRATABLE_2_1_ROOT_NAMES:
        raise UblValidationError(
            f"{document.root_name!r} has no verified UBL {SOURCE_VERSION} schema to migrate "
            f"from -- SAL-UBL-7546731B76606EC0 covers only {len(MIGRATABLE_2_1_ROOT_NAMES)} "
            "of the 91 supported root types"
        )

    new_children = tuple(
        replace(child, text=TARGET_VERSION) if child.qname == _UBL_VERSION_QNAME else child
        for child in document.root.children
    )
    relabeled = document.with_root(document.root.with_children(new_children))

    report = validate(relabeled)
    if not report.is_valid:
        raise UblValidationError(
            f"migrated {document.root_name} document failed UBL {TARGET_VERSION} validation, "
            f"refusing to relabel: {[d.message for d in report.errors]}"
        )

    return relabeled, MigrationReport(
        root_name=document.root_name,
        source_version=SOURCE_VERSION,
        target_version=TARGET_VERSION,
        note=(
            "No content changes were required: SAL-UBL-7546731B76606EC0 proves this root "
            "type's own UBL 2.1 schema differs from 2.3 only by optional additions and "
            "cardinality widenings, so a UBL 2.1-valid document is already 2.3-valid content. "
            "Only cbc:UBLVersionID was relabeled, and only after the relabeled result was "
            "confirmed to pass validate() against the stable 2.3 profile."
        ),
    )


__all__ = ["MigrationReport", "migrate_document"]
