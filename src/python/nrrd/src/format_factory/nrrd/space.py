"""NRRD-SPACE-001 -- NRRD0004+ orientation and space metadata.

"Starting with NRRD0004, space, space dimension, space units, space origin,
and per-axis space directions describe array orientation in a surrounding
space; measurement frame is not available until NRRD0005." required_behavior
adds: "never infer axis order from a named space" -- stated twice. It also
asks for "vector-length validation against space dimension."

This module takes the "never infer" instruction literally: space dimension
is always DERIVED from explicit data only -- the "space dimension" field if
present, or the length of whatever "space origin" / spatial "space
directions" vectors are actually present -- never FROM a lookup keyed by
the "space" field's name string (e.g. "left-posterior-superior"). That
architecture is unchanged.

What has changed: this module now also cross-VALIDATES a named space's own
canonical dimension against the already-derived explicit dimension, when a
"space" field is present. The canonical named-space table (12 standard
space names, their string aliases, and each one's own fixed dimension) is
transcribed directly from the pinned Teem 1.9.0 reference implementation's
own source (.local/format-contracts/acquired/nrrd/src-nrrd-002.bin, a gzip
archive containing the full Teem source tree -- src/nrrd/enumsNrrd.c's
_nrrdSpaceStr/_nrrdSpaceStrEqv tables and src/nrrd/simple.c's own
nrrdSpaceDimension() switch statement), not approximated from memory. This
is a genuinely different operation from axis-order inference: a scalar
dimension CHECK against data already derived from explicit fields, not a
per-axis MEANING inferred from the name and substituted for missing data.
An unrecognized (non-standard, but spec-permitted) space name is silently
not cross-checked, not treated as an error.

Measurement-frame transforms (NRRD0005) are a deliberately separate,
unimplemented capability -- this module only ever builds the index-to-world
transform from space directions/origin, matching "keep NRRD0005
measurement-frame transforms in a separate model and API."
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import NrrdParseError

_VECTOR_PATTERN = re.compile(r"\(([^)]*)\)")

#: The 12 standard NRRD space names and each one's own fixed dimension,
#: transcribed directly from the pinned Teem 1.9.0 reference source
#: (src/nrrd/enumsNrrd.c's _nrrdSpaceStr canonical strings and
#: src/nrrd/simple.c's own nrrdSpaceDimension() switch statement -- the
#: non-Time variants are 3-D, the Time variants are 4-D). Keys are the
#: canonical lowercase hyphenated form; lookup normalizes the header's
#: own "space" value to match. Deliberately excludes the "(unknown_space)"
#: sentinel, which has no dimension to cross-check against.
_TEEM_NAMED_SPACE_DIMENSIONS: dict[str, int] = {
    "right-anterior-superior": 3,
    "left-anterior-superior": 3,
    "left-posterior-superior": 3,
    "right-anterior-superior-time": 4,
    "left-anterior-superior-time": 4,
    "left-posterior-superior-time": 4,
    "scanner-xyz": 3,
    "scanner-xyz-time": 4,
    "3d-right-handed": 3,
    "3d-left-handed": 3,
    "3d-right-handed-time": 4,
    "3d-left-handed-time": 4,
    # Teem's own short acronym aliases for the six RAS/LAS/LPS variants.
    "ras": 3,
    "las": 3,
    "lps": 3,
    "rast": 4,
    "last": 4,
    "lpst": 4,
}


def _normalized_space_name(raw: str) -> str:
    return raw.strip().lower()


def named_space_dimension(space: str) -> int | None:
    """The dimension the pinned Teem reference implementation associates
    with a standard named space (`space` header field value), or `None`
    if `space` is not one of the 12 standard names -- an unrecognized
    (but spec-permitted) custom space name is not an error, just not
    cross-checkable against this table.
    """
    return _TEEM_NAMED_SPACE_DIMENSIONS.get(_normalized_space_name(space))


def parse_space_directions(raw: str) -> tuple[tuple[float, ...] | None, ...]:
    """Parse a "space directions" header value into one entry per axis.

    Each whitespace-separated token is either a parenthesized comma-separated
    vector, or the literal "none" marking a non-spatial axis (e.g. a color
    channel or time axis that does not participate in the spatial transform).
    """
    entries: list[tuple[float, ...] | None] = []
    for token in raw.split():
        if token.lower() == "none":
            entries.append(None)
            continue
        match = _VECTOR_PATTERN.fullmatch(token)
        if not match:
            raise NrrdParseError(f"invalid space directions entry: {token!r}")
        try:
            values = tuple(float(part) for part in match.group(1).split(","))
        except ValueError as exc:
            raise NrrdParseError(f"invalid space directions entry: {token!r}") from exc
        if not values:
            raise NrrdParseError(f"empty space directions vector: {token!r}")
        entries.append(values)
    return tuple(entries)


def parse_space_origin(raw: str) -> tuple[float, ...]:
    """Parse a "space origin" header value: a single parenthesized vector."""
    match = _VECTOR_PATTERN.fullmatch(raw.strip())
    if not match:
        raise NrrdParseError(f"invalid space origin: {raw!r}")
    try:
        values = tuple(float(part) for part in match.group(1).split(","))
    except ValueError as exc:
        raise NrrdParseError(f"invalid space origin: {raw!r}") from exc
    if not values:
        raise NrrdParseError(f"empty space origin vector: {raw!r}")
    return values


def _infer_space_dimension(
    direction_vectors: tuple[tuple[float, ...] | None, ...],
    origin: tuple[float, ...],
    declared: int | None,
    space: str | None = None,
) -> int:
    """Determine the space dimension from explicit data only.

    Never FROM the "space" field's name -- see this module's docstring.
    `space`, when given, is used only to cross-CHECK the result already
    derived from explicit data against Teem's own fixed dimension for
    that standard name; it never supplies or overrides the dimension
    itself.
    """
    candidates = {len(origin)}
    if declared is not None:
        candidates.add(declared)
    for vector in direction_vectors:
        if vector is not None:
            candidates.add(len(vector))
    if len(candidates) > 1:
        raise NrrdParseError(
            "inconsistent space dimension across 'space dimension', "
            f"'space origin' and 'space directions': {sorted(candidates)}"
        )
    dimension = candidates.pop()
    if space is not None:
        expected = named_space_dimension(space)
        if expected is not None and expected != dimension:
            raise NrrdParseError(
                f"space {space!r} implies dimension {expected}, but 'space "
                f"origin'/'space directions'/'space dimension' agree on {dimension}"
            )
    return dimension


@dataclass(frozen=True, slots=True)
class SpaceTransform:
    """Validated NRRD0004+ orientation metadata with an index-to-world
    transform. Never carries a measurement-frame transform (NRRD0005) --
    that stays a separate, unimplemented capability."""

    space_dimension: int
    origin: tuple[float, ...]
    direction_vectors: tuple[tuple[float, ...] | None, ...]

    @property
    def spatial_axes(self) -> tuple[int, ...]:
        """Array-axis indices that are spatial (not marked "none")."""
        return tuple(
            index for index, vector in enumerate(self.direction_vectors) if vector is not None
        )

    def index_to_world(self, index: tuple[int, ...]) -> tuple[float, ...]:
        """Map an array index (one component per array axis) to a world
        coordinate. Non-spatial axes contribute nothing to the result --
        their index value is not a position along any world-space direction.
        """
        if len(index) != len(self.direction_vectors):
            raise NrrdParseError(
                f"index has {len(index)} components but the document "
                f"declares {len(self.direction_vectors)} axes"
            )
        world = list(self.origin)
        for axis_index, vector in zip(index, self.direction_vectors):
            if vector is None:
                continue
            for component in range(self.space_dimension):
                world[component] += axis_index * vector[component]
        return tuple(world)


def build_space_transform(
    *,
    space_directions: str,
    space_origin: str,
    space_dimension: str | None = None,
    space: str | None = None,
    axis_count: int,
) -> SpaceTransform:
    """Build a validated SpaceTransform from raw NRRD header field values.

    Both `space_directions` and `space_origin` are required: an index-to-
    world transform without an origin, or without knowing which axes are
    spatial, cannot be built at all -- there is no partial or inferred
    transform this function will construct from less.

    `space` (the header's own "space" field value, e.g. "left-posterior-
    superior") is entirely optional and used only to cross-CHECK Teem's
    own fixed dimension for that standard name against the dimension
    already derived from `space_dimension`/`space_origin`/
    `space_directions` -- never to supply or override it. See this
    module's own docstring.
    """
    direction_vectors = parse_space_directions(space_directions)
    if len(direction_vectors) != axis_count:
        raise NrrdParseError(
            f"'space directions' declares {len(direction_vectors)} entries "
            f"but the document has {axis_count} axes"
        )
    origin = parse_space_origin(space_origin)
    declared_dimension = int(space_dimension) if space_dimension is not None else None
    # _infer_space_dimension already requires every candidate (origin length,
    # declared dimension, and each spatial vector's length) to agree, so by
    # the time it returns, origin and every vector are guaranteed consistent
    # with the result -- a separate per-field length check here would be
    # dead code that could never fire.
    dimension = _infer_space_dimension(direction_vectors, origin, declared_dimension, space)

    return SpaceTransform(
        space_dimension=dimension,
        origin=origin,
        direction_vectors=direction_vectors,
    )


__all__ = [
    "SpaceTransform",
    "build_space_transform",
    "named_space_dimension",
    "parse_space_directions",
    "parse_space_origin",
]
