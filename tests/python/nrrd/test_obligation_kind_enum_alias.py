"""NRRD-KINDS-001 -- the per-axis `kinds` field's value/alias table and
required-size validation.

MUST (SAL-NRRD-OBL-02AE194021A775AC): "Model every specified axis kind and
its aliases only for NRRD0003 and newer; preserve unknown future kinds
safely while strict validation reports them."

MUST (SAL-NRRD-OBL-7C0FD86BAE579F5C; Teem NRRD Format Specification
Sections 1.1 and 6): "Starting with NRRD0003, the per-axis kinds field
classifies each axis using one value per declared dimension."

Before this slice: `document.kinds` only checked cardinality (one token
per axis); nothing validated a kind string against the spec's own 31-value
table (with required per-axis sizes for size-constrained kinds), and
nothing recognized Teem's own accepted aliases (e.g. "RGB"/"RGBcolor" for
"RGB-color"). codec/kinds.py's table is read directly from two independent
pinned sources: the prose spec's own "Required axis size" table
(src-nrrd-001.bin) and the Teem 1.9.0 reference implementation's own enum
source (src-nrrd-002.bin, src/nrrd/enumsNrrd.c's
_nrrdKindStr_Eqv/_nrrdKindVal_Eqv arrays) -- not memory or a paraphrase.
"""

from __future__ import annotations

from format_factory.nrrd import loads, validate
from format_factory.nrrd.codec.kinds import (
    KIND_ALIASES,
    KIND_REQUIRED_SIZE,
    KIND_UNKNOWN_MARKERS,
    canonical_kind,
)


def _header(kind: str, size: int) -> bytes:
    return (
        f"NRRD0005\ntype: uint8\ndimension: 1\nsizes: {size}\n"
        f"encoding: raw\nkinds: {kind}\n\n"
    ).encode() + b"\x00" * size


# ── canonical_kind() and the tables themselves ──────────────────────────


def test_the_kind_table_has_exactly_31_canonical_entries() -> None:
    """The prose spec's own table names exactly 31 kind strings (domain
    through 3D-masked-matrix)."""
    assert len(KIND_REQUIRED_SIZE) == 31


def test_canonical_kind_recognizes_a_canonical_name() -> None:
    assert canonical_kind("3-color") == "3-color"


def test_canonical_kind_resolves_a_known_alias() -> None:
    assert canonical_kind("RGB") == "RGB-color"
    assert canonical_kind("RGBcolor") == "RGB-color"
    assert canonical_kind("contravariant-vector") == "vector"
    assert canonical_kind("3D-tensor") == "3D-matrix"


def test_canonical_kind_returns_none_for_an_unrecognized_string() -> None:
    assert canonical_kind("bogus-kind") is None


def test_no_size_constraint_kinds_have_a_none_required_size() -> None:
    for name in ("domain", "space", "time", "list", "point", "vector", "normal"):
        assert KIND_REQUIRED_SIZE[name] is None


def test_size_constrained_kinds_have_their_spec_required_size() -> None:
    assert KIND_REQUIRED_SIZE["stub"] == 1
    assert KIND_REQUIRED_SIZE["complex"] == 2
    assert KIND_REQUIRED_SIZE["3D-symmetric-matrix"] == 6
    assert KIND_REQUIRED_SIZE["3D-masked-symmetric-matrix"] == 7
    assert KIND_REQUIRED_SIZE["3D-matrix"] == 9
    assert KIND_REQUIRED_SIZE["3D-masked-matrix"] == 10


def test_every_alias_target_is_itself_a_canonical_kind() -> None:
    for alias, target in KIND_ALIASES.items():
        assert target in KIND_REQUIRED_SIZE, f"{alias!r} -> {target!r} is not canonical"


# ── validate() against a real document ──────────────────────────────────


def test_a_canonical_kind_with_the_correct_size_is_valid() -> None:
    report = validate(loads(_header("3-color", 3)))

    assert report.is_valid


def test_an_alias_with_the_correct_size_is_valid() -> None:
    report = validate(loads(_header("RGB", 3)))

    assert report.is_valid


def test_an_alias_with_the_wrong_size_is_reported() -> None:
    report = validate(loads(_header("RGB", 4)))

    assert not report.is_valid
    assert "nrrd.kinds.size_mismatch" in {item.code for item in report.diagnostics}


def test_an_unrecognized_kind_string_is_reported() -> None:
    report = validate(loads(_header("bogus-kind", 3)))

    assert not report.is_valid
    assert "nrrd.kinds.unrecognized" in {item.code for item in report.diagnostics}


def test_the_explicit_unknown_markers_are_valid_and_not_reported() -> None:
    for marker in KIND_UNKNOWN_MARKERS:
        report = validate(loads(_header(marker, 3)))
        assert report.is_valid, f"marker {marker!r} unexpectedly flagged"


def test_a_no_size_constraint_kind_accepts_any_axis_size() -> None:
    report = validate(loads(_header("domain", 7)))

    assert report.is_valid


def test_a_dash_tensor_alias_with_the_correct_size_is_valid() -> None:
    report = validate(loads(_header("3D-tensor", 9)))

    assert report.is_valid
