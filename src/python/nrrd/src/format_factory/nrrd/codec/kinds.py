"""NRRD-KINDS-001 -- the per-axis `kinds` field's value/alias table.

MUST (SAL-NRRD-OBL-02AE194021A775AC / SAL-NRRD-OBL-7C0FD86BAE579F5C):
"Model every specified axis kind and its aliases only for NRRD0003 and
newer... classifies each axis using one value per declared dimension."

Every string and required-size pair here is read directly from two
independent pinned authoritative sources, not memory or a paraphrase:

* The prose spec's own "Required axis size" table (src-nrrd-001.bin,
  SRC-NRRD-001, Sections 1.1/6) names the 31 canonical kind strings and
  each one's required per-axis element count (or none, for the
  resample-able domain/list-family kinds).
* The Teem 1.9.0 reference implementation's own enum source
  (src-nrrd-002.bin, SRC-NRRD-002, src/nrrd/enumsNrrd.c) supplies
  `_nrrdKindStr_Eqv`/`_nrrdKindVal_Eqv`: the exact alias strings Teem's
  own reader accepts as synonyms for a canonical kind (e.g. "RGB",
  "RGBcolor", and "RGB-color" are all the same kind).

"???" and "none" are the prose spec's own two spellings for "kind
information for this axis is unknown or not representable" -- a
deliberate, explicit unknown marker, distinct from a genuinely
unrecognized (future or foreign) kind string.
"""

from __future__ import annotations

#: canonical kind -> required per-axis element count, or None if any count
#: is legal (the resample-able domain/list-family kinds carry no size
#: constraint of their own).
KIND_REQUIRED_SIZE: dict[str, int | None] = {
    "domain": None,
    "space": None,
    "time": None,
    "list": None,
    "point": None,
    "vector": None,
    "covariant-vector": None,
    "normal": None,
    "stub": 1,
    "scalar": 1,
    "complex": 2,
    "2-vector": 2,
    "3-color": 3,
    "RGB-color": 3,
    "HSV-color": 3,
    "XYZ-color": 3,
    "4-color": 4,
    "RGBA-color": 4,
    "3-vector": 3,
    "3-gradient": 3,
    "3-normal": 3,
    "4-vector": 4,
    "quaternion": 4,
    "2D-symmetric-matrix": 3,
    "2D-masked-symmetric-matrix": 4,
    "2D-matrix": 4,
    "2D-masked-matrix": 4,
    "3D-symmetric-matrix": 6,
    "3D-masked-symmetric-matrix": 7,
    "3D-matrix": 9,
    "3D-masked-matrix": 10,
}

#: alias -> canonical kind, per Teem's own _nrrdKindStr_Eqv/_nrrdKindVal_Eqv.
KIND_ALIASES: dict[str, str] = {
    "contravariant-vector": "vector",
    "RGBcolor": "RGB-color",
    "RGB": "RGB-color",
    "HSVcolor": "HSV-color",
    "HSV": "HSV-color",
    "RGBAcolor": "RGBA-color",
    "RGBA": "RGBA-color",
    "2D-sym-matrix": "2D-symmetric-matrix",
    "2D-symmetric-tensor": "2D-symmetric-matrix",
    "2D-sym-tensor": "2D-symmetric-matrix",
    "2D-masked-sym-matrix": "2D-masked-symmetric-matrix",
    "2D-masked-symmetric-tensor": "2D-masked-symmetric-matrix",
    "2D-masked-sym-tensor": "2D-masked-symmetric-matrix",
    "2D-tensor": "2D-matrix",
    "2D-masked-tensor": "2D-masked-matrix",
    "3D-sym-matrix": "3D-symmetric-matrix",
    "3D-symmetric-tensor": "3D-symmetric-matrix",
    "3D-sym-tensor": "3D-symmetric-matrix",
    "3D-masked-sym-matrix": "3D-masked-symmetric-matrix",
    "3D-masked-symmetric-tensor": "3D-masked-symmetric-matrix",
    "3D-masked-sym-tensor": "3D-masked-symmetric-matrix",
    "3D-tensor": "3D-matrix",
    "3D-masked-tensor": "3D-masked-matrix",
}

#: The prose spec's own two spellings for "kind information for this axis
#: is unknown or not representable" -- a deliberate marker, not an error.
KIND_UNKNOWN_MARKERS = frozenset({"???", "none"})


def canonical_kind(value: str) -> str | None:
    """The canonical kind name for `value` (itself, or via an alias), or
    None if `value` is not a recognized kind string at all (a genuinely
    unrecognized future or foreign kind -- preserved as opaque text
    elsewhere, never rejected outright, only flagged by strict validation)."""
    if value in KIND_REQUIRED_SIZE:
        return value
    return KIND_ALIASES.get(value)


__all__ = [
    "KIND_ALIASES",
    "KIND_REQUIRED_SIZE",
    "KIND_UNKNOWN_MARKERS",
    "canonical_kind",
]
