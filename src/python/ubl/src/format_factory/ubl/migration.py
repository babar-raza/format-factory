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
cardinality WIDENING -- never a removal, a reordering, or a tightening.

SAL-UBL-F90975267B9AE315 (the analogous direct structural diff of the
acquired OASIS UBL 2.2 and UBL 2.3 release packages, SRC-UBL-002/SRC-UBL-006):
the same additive/relaxing-only property holds for 81 of the 91 UBL 2.3
root document types between 2.2 and 2.3.

SAL-UBL-1FBA330BB51DAEF5 (the analogous direct structural diff of the
acquired OASIS UBL 2.0 and UBL 2.3 release packages, SRC-UBL-002/SRC-UBL-007):
the same additive/relaxing-only property holds for 31 of the 91 UBL 2.3
root document types between 2.0 and 2.3 -- UBL 2.0 is the oldest OASIS
release and defines maindoc schemas for far fewer root types than the
later versions.

A valid document of one of these covered types is therefore ALREADY
structurally valid content under the 2.3 schema: migration needs no content
rewriting at all, only relabeling ``cbc:UBLVersionID`` to "2.3" -- and even
that relabel only happens after this package's own ``validate()`` confirms
the relabeled result genuinely passes the stable 2.3 profile, per this
obligation's own "never label... without... validation" clause, enforced
here as a hard precondition rather than a disclosed caveat.

``migrate_document()`` deliberately supports ONLY the 2.0-to-2.3, 2.1-to-2.3,
and 2.2-to-2.3 directions, the three pairs this package has an acquired,
diffed authority source for -- covering every UBL version OASIS has ever
released prior to 2.3. The root types with no maindoc schema at all in a
given source version (for example ``ImportCustomsDeclaration``, absent
from all three older packages; ``BusinessCard``, absent from 2.0 and 2.1)
are refused for that source version, not silently attempted -- every root
type that DID exist in both a source version and 2.3 was independently
confirmed additive/relaxing-only for that pair, with zero exceptions
(confirmed directly against the acquired packages by
``tools/generate_migratable_2_0_roots.py``,
``tools/generate_migratable_2_1_roots.py``, and
``tools/generate_migratable_2_2_roots.py``, not assumed).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final

from ._generated.migratable_2_0_roots import MIGRATABLE_2_0_ROOT_NAMES
from ._generated.migratable_2_1_roots import MIGRATABLE_2_1_ROOT_NAMES
from ._generated.migratable_2_2_roots import MIGRATABLE_2_2_ROOT_NAMES
from .errors import UblValidationError
from .model import UblDocument
from .model.document import _UBL_VERSION_QNAME
from .validation.validator import validate

TARGET_VERSION: Final = "2.3"

_MIGRATIONS: Final[dict[str, tuple[frozenset[str], str]]] = {
    "2.0": (MIGRATABLE_2_0_ROOT_NAMES, "SAL-UBL-1FBA330BB51DAEF5"),
    "2.1": (MIGRATABLE_2_1_ROOT_NAMES, "SAL-UBL-7546731B76606EC0"),
    "2.2": (MIGRATABLE_2_2_ROOT_NAMES, "SAL-UBL-F90975267B9AE315"),
}


@dataclass(frozen=True, slots=True)
class MigrationReport:
    """The outcome of one ``migrate_document()`` call -- this obligation's
    own "producing a migration report" clause, not merely a boolean."""

    root_name: str
    source_version: str
    target_version: str
    note: str


def migrate_document(document: UblDocument) -> tuple[UblDocument, MigrationReport]:
    """Migrate ``document`` from its own declared UBL version (2.0, 2.1, or 2.2) to UBL 2.3.

    Returns ``(migrated_document, MigrationReport)`` on success. Raises
    ``UblValidationError`` -- never a silent no-op or a partially-migrated
    result -- when:

    - ``document`` does not declare a supported source ``UBLVersionID``
      ("2.0", "2.1", or "2.2" -- every UBL version OASIS released prior to
      2.3);
    - ``document``'s root type is not one of the root types the matching
      structural-diff SAL fact proves are additive/relaxing-only for its
      declared source version;
    - the relabeled result fails ``validate()`` against the stable 2.3
      profile.

    ``document`` itself is never mutated (``UblDocument`` is frozen); the
    migrated result is always a new object.
    """
    declared = document.declared_version
    if declared is None or declared not in _MIGRATIONS:
        supported = ", ".join(repr(v) for v in _MIGRATIONS)
        raise UblValidationError(
            f"migrate_document only supports UBL {{{supported}}} as a source version; "
            f"document declares {declared!r}"
        )
    root_names, fact_id = _MIGRATIONS[declared]
    if document.root_name not in root_names:
        raise UblValidationError(
            f"{document.root_name!r} has no verified UBL {declared} schema to migrate "
            f"from -- {fact_id} covers only {len(root_names)} of the 91 supported root types"
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
        source_version=declared,
        target_version=TARGET_VERSION,
        note=(
            f"No content changes were required: {fact_id} proves this root "
            f"type's own UBL {declared} schema differs from 2.3 only by optional additions and "
            "cardinality widenings, so a document valid under its declared source version is "
            "already 2.3-valid content. Only cbc:UBLVersionID was relabeled, and only after the "
            "relabeled result was confirmed to pass validate() against the stable 2.3 profile."
        ),
    )


__all__ = ["MigrationReport", "migrate_document"]
