"""Pluggable code-list registry and offline validation for cac:Code values.

UBL-CODELIST-001's two loading obligations ask for: "Load official code
lists from their distribution artifacts, cache them immutably, and
validate coded values deterministically offline, with user- or
profile-supplied lists pluggable at runtime" and "Load official code-list
resources, map them to coded properties, validate identifiers/agencies/
versions/values, and support user-supplied lists."

This module builds the full pluggable registry and offline validation
mechanism -- immutable :class:`CodeList` entries, a registry callers
populate at runtime, and :func:`validate_code`, which is deterministic
and makes no network or filesystem access. An official list is
registered through exactly the same :func:`CodeListRegistry.register`
call a user- or profile-supplied list uses -- there is no architectural
difference between "official" and "custom" once the data is in hand.

The official code-list data itself (UN/CEFACT UNCL lists, ISO 4217
currency codes, ISO 3166 country codes, and similar) and the OASIS
genericode XML loader those lists ship in both now exist, in
``.genericode`` -- the pinned raw acquisition cache
(.local/format-contracts/acquired/ubl/src-ubl-002.bin) turned out to be
the actual official UBL 2.3 distribution ZIP, not spec prose, and its
``cl/gc/default/`` directory contains the genuine OASIS-published
genericode files. See :func:`.genericode.official_code_list_registry`
for a ready-populated registry.
"""

from __future__ import annotations

from dataclasses import dataclass

from .values import Code


@dataclass(frozen=True, slots=True)
class CodeList:
    """An immutable set of permitted code values for one list identity.

    ``list_id``/``agency_id``/``version`` mirror ``cac:Code``'s own
    ``list_id``/``list_agency_id``/``list_version_id`` fields -- a code is
    matched against the list sharing all three, so two lists with the same
    ``list_id`` but a different agency or version are never conflated.
    """

    list_id: str
    values: frozenset[str]
    agency_id: str | None = None
    version: str | None = None
    source: str = ""

    def __post_init__(self) -> None:
        if not self.list_id:
            raise ValueError("CodeList requires a non-empty list_id")


@dataclass(frozen=True, slots=True)
class CodeListValidation:
    """The outcome of validating a :class:`~.values.Code` against a registry."""

    list_known: bool
    is_valid: bool | None
    detail: str


class CodeListRegistry:
    """A pluggable, in-memory registry of :class:`CodeList` entries.

    Populated at runtime by the caller -- official lists (once sourced)
    and user-/profile-supplied lists register through the same method, so
    neither is a second-class citizen. Lookup and validation never touch
    the network or filesystem: everything this registry can answer, it
    answers from what has already been registered.
    """

    def __init__(self) -> None:
        self._lists: dict[tuple[str, str | None, str | None], CodeList] = {}

    def register(self, code_list: CodeList) -> None:
        """Add or replace a code list, keyed by (list_id, agency_id, version).

        Immutable once registered: the stored :class:`CodeList` itself is
        frozen, so a caller cannot mutate a registered list's ``values``
        out from under a concurrent validation.
        """

        key = (code_list.list_id, code_list.agency_id, code_list.version)
        self._lists[key] = code_list

    def get(
        self, list_id: str, *, agency_id: str | None = None, version: str | None = None
    ) -> CodeList | None:
        return self._lists.get((list_id, agency_id, version))

    def __len__(self) -> int:
        return len(self._lists)

    def __contains__(self, key: tuple[str, str | None, str | None]) -> bool:
        return key in self._lists


def validate_code(registry: CodeListRegistry, code: Code) -> CodeListValidation:
    """Validate a ``Code`` value against the registry, deterministically offline.

    A ``Code`` with no ``list_id`` cannot be checked against anything --
    reported as unknown, not invalid, since the code itself never claimed
    to belong to a list. A ``Code`` naming a list this registry has no
    entry for is reported the same way: an unregistered list is a gap in
    the registry's population, not evidence the code is wrong.
    """

    if code.list_id is None:
        return CodeListValidation(
            list_known=False,
            is_valid=None,
            detail="code has no list_id; nothing to validate against",
        )
    code_list = registry.get(
        code.list_id, agency_id=code.list_agency_id, version=code.list_version_id
    )
    if code_list is None:
        return CodeListValidation(
            list_known=False,
            is_valid=None,
            detail=(
                f"list {code.list_id!r} "
                f"(agency={code.list_agency_id!r}, version={code.list_version_id!r}) "
                "is not registered; cannot validate offline against an unknown list"
            ),
        )
    if code.value in code_list.values:
        return CodeListValidation(
            list_known=True,
            is_valid=True,
            detail=f"{code.value!r} is a member of list {code.list_id!r}",
        )
    return CodeListValidation(
        list_known=True,
        is_valid=False,
        detail=f"{code.value!r} is not a member of list {code.list_id!r}",
    )


__all__ = [
    "CodeList",
    "CodeListRegistry",
    "CodeListValidation",
    "validate_code",
]
