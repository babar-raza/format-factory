"""Lifecycle reports and explicit notebook version conversion."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from ..errors import IpynbValidationError

if TYPE_CHECKING:
    from .document import IpynbDocument


@dataclass(frozen=True, slots=True)
class NotebookVersion:
    """A declared or structurally detected nbformat version."""

    major: int | None
    minor: int | None

    def __post_init__(self) -> None:
        for name, value in (("major", self.major), ("minor", self.minor)):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                raise ValueError(f"{name} must be a non-negative integer or None")

    def as_tuple(self) -> tuple[int | None, int | None]:
        return self.major, self.minor


@dataclass(frozen=True, slots=True)
class RecoveryAction:
    """One deterministic repair made by ``mode='recovery'``."""

    code: str
    path: tuple[str | int, ...]
    message: str


@dataclass(frozen=True, slots=True)
class ConversionAction:
    """One explicit, auditable notebook conversion operation."""

    code: str
    path: tuple[str | int, ...]
    message: str


@dataclass(frozen=True, slots=True)
class CellIdRewrite:
    """Cell ID rewrite emitted by an explicit upgrade."""

    cell_index: int
    old_id: str | None
    new_id: str


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Converted document and the complete conversion ledger."""

    document: IpynbDocument
    actions: tuple[ConversionAction, ...]
    id_rewrites: tuple[CellIdRewrite, ...]


def _target_version(target: str) -> tuple[int, int]:
    selected = target.removeprefix("nbformat-")
    if selected not in {f"4.{minor}" for minor in range(6)}:
        raise ValueError("target must be one of nbformat 4.0 through 4.5")
    major, minor = selected.split(".", 1)
    return int(major), int(minor)


def upgrade(
    value: IpynbDocument | Mapping[str, Any],
    *,
    target: str = "4.5",
) -> ConversionResult:
    """Explicitly upgrade a notebook and return a conversion ledger.

    This is the only production API that synthesizes cell IDs. Downgrades are
    deliberately refused until their loss-report policy is selected explicitly.
    """

    from ..codec.reader import CELL_ID_PATTERN, ensure_cell_id
    from .document import IpynbDocument

    data = deepcopy(value.raw if isinstance(value, IpynbDocument) else dict(value))
    target_major, target_minor = _target_version(target)
    source_major = data.get("nbformat")
    source_minor = data.get("nbformat_minor")
    if (
        isinstance(source_major, bool)
        or not isinstance(source_major, int)
        or isinstance(source_minor, bool)
        or not isinstance(source_minor, int)
    ):
        raise IpynbValidationError(
            "explicit upgrade requires integer nbformat and nbformat_minor fields",
            code="IPYNB_UPGRADE_VERSION",
            context={"path": ("nbformat",)},
        )
    if source_major != 4 or (source_major, source_minor) > (
        target_major,
        target_minor,
    ):
        raise IpynbValidationError(
            "upgrade target must not be older than the declared notebook version",
            code="IPYNB_UPGRADE_DOWNGRADE_REQUIRES_LOSS_REPORT",
            context={
                "source_version": (source_major, source_minor),
                "target_version": (target_major, target_minor),
            },
        )

    cells = data.get("cells")
    if not isinstance(cells, list) or any(not isinstance(cell, dict) for cell in cells):
        raise IpynbValidationError(
            "explicit upgrade requires a cells array of objects",
            code="IPYNB_UPGRADE_CELLS",
            context={"path": ("cells",)},
        )

    actions: list[ConversionAction] = []
    rewrites: list[CellIdRewrite] = []
    if (source_major, source_minor) != (target_major, target_minor):
        data["nbformat"] = target_major
        data["nbformat_minor"] = target_minor
        actions.append(
            ConversionAction(
                "IPYNB_UPGRADE_VERSION",
                ("nbformat", "nbformat_minor"),
                f"changed declared version from {source_major}.{source_minor} "
                f"to {target_major}.{target_minor}",
            )
        )

    if target_minor >= 5:
        used_ids: set[str] = set()
        for index, cell in enumerate(cells):
            old_value = cell.get("id")
            old_id = old_value if isinstance(old_value, str) else None
            is_valid = (
                old_id is not None
                and CELL_ID_PATTERN.fullmatch(old_id) is not None
                and old_id not in used_ids
            )
            ensure_cell_id(cell, used_ids)
            new_id = str(cell["id"])
            if not is_valid:
                rewrites.append(CellIdRewrite(index, old_id, new_id))
                actions.append(
                    ConversionAction(
                        "IPYNB_UPGRADE_CELL_ID",
                        ("cells", index, "id"),
                        "generated a deterministic valid unique cell ID",
                    )
                )

    version = NotebookVersion(target_major, target_minor)
    return ConversionResult(
        document=IpynbDocument(
            data,
            declared_version=version,
            detected_version=version,
        ),
        actions=tuple(actions),
        id_rewrites=tuple(rewrites),
    )
