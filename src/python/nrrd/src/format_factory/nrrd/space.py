"""NRRD-SPACE-001 -- NRRD0004+ orientation and space metadata.

"Starting with NRRD0004, space, space dimension, space units, space origin,
and per-axis space directions describe array orientation in a surrounding
space; measurement frame is not available until NRRD0005." required_behavior
adds: "never infer axis order from a named space" -- stated twice.

This module takes that literally: space dimension is derived from EXPLICIT
data only -- the "space dimension" field if present, or the length of
whatever "space origin" / spatial "space directions" vectors are actually
present -- never from a lookup keyed by the "space" field's name string
(e.g. "left-posterior-superior"). No SAL fact in this repository enumerates
Teem's named-space strings and their exact implied dimensionality precisely
enough to hard-code such a table safely, and doing so anyway would be
exactly the axis-order-from-name inference the obligation forbids. Deriving
dimension from the vectors that are actually present is both safer and is
literally what the obligation asks for.

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
) -> int:
    """Determine the space dimension from explicit data only.

    Never from the "space" field's name -- see this module's docstring.
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
    return candidates.pop()


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
    axis_count: int,
) -> SpaceTransform:
    """Build a validated SpaceTransform from raw NRRD header field values.

    Both `space_directions` and `space_origin` are required: an index-to-
    world transform without an origin, or without knowing which axes are
    spatial, cannot be built at all -- there is no partial or inferred
    transform this function will construct from less.
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
    dimension = _infer_space_dimension(direction_vectors, origin, declared_dimension)

    return SpaceTransform(
        space_dimension=dimension,
        origin=origin,
        direction_vectors=direction_vectors,
    )


__all__ = [
    "SpaceTransform",
    "build_space_transform",
    "parse_space_directions",
    "parse_space_origin",
]
