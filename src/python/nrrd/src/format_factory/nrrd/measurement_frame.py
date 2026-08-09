"""NRRD-FRAME-001 -- NRRD0005 measurement-frame transforms.

(Teem NRRD Format Specification, Sections 1.1 and 4): "Starting with
NRRD0005, measurement frame supplies exactly space-dimension vectors
that transform measurement coefficients into the surrounding space
basis." Deliberately kept as a SEPARATE model and API from space.py's
own NRRD0004+ index-to-world transform -- SAL-NRRD-OBL-666DA3540EE4E38D's
own explicit instruction ("keep NRRD0005 measurement-frame transforms in
a separate model and API"), and confirmed directly against the pinned
spec text to be the right call on the merits too: a measurement frame
maps COEFFICIENTS of a vector/tensor quantity (e.g. the coefficients of
a diffusion-sensitizing gradient direction), not point POSITIONS -- "the
matrix transforms (a column vector of) coordinates in the measurement
frame to coordinates in world space," with no origin/translation term
at all, unlike `SpaceTransform.index_to_world`'s own array-index-to
-world-position mapping.

`vector[i]` gives column i of the spaceDim-by-spaceDim matrix, in the
identical `(v0,v1,...)` parenthesized syntax `space directions` already
uses -- reused directly via `space.parse_space_directions`, not
duplicated -- but EXACTLY `space_dimension` of them are required
(this obligation's own wording, taken literally), with no "none" entries
permitted: a measurement frame is a basic (per-array) field with no
per-axis concept at all, unlike `space directions`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import NrrdParseError
from .space import parse_space_directions


@dataclass(frozen=True, slots=True)
class MeasurementFrameTransform:
    """A validated NRRD0005 measurement-frame matrix and its
    measurement-to-world transform. Deliberately carries no origin --
    see this module's own docstring for why a measurement frame is a
    pure linear map, not an affine one."""

    space_dimension: int
    columns: tuple[tuple[float, ...], ...]

    def measurement_to_world(self, coordinates: tuple[float, ...]) -> tuple[float, ...]:
        """Map a coordinate vector in the measurement frame to world
        space: `world = matrix @ coordinates`, with no origin term,
        distinct from `SpaceTransform.index_to_world`'s own affine map."""
        if len(coordinates) != self.space_dimension:
            raise NrrdParseError(
                f"coordinates has {len(coordinates)} components but the "
                f"measurement frame is {self.space_dimension}-dimensional"
            )
        world = [0.0] * self.space_dimension
        for column, coefficient in zip(self.columns, coordinates):
            for row in range(self.space_dimension):
                world[row] += coefficient * column[row]
        return tuple(world)


def build_measurement_frame_transform(
    *, measurement_frame: str, space_dimension: int
) -> MeasurementFrameTransform:
    """Build a validated `MeasurementFrameTransform` from the raw
    "measurement frame" header field value.

    Requires EXACTLY `space_dimension` vectors, each with exactly
    `space_dimension` components -- this obligation's own "exactly
    space-dimension vectors" wording, taken literally, is a cardinality
    check this function enforces rather than merely documents. A "none"
    entry (`space.py`'s own per-axis non-spatial marker) is never valid
    here: there is no per-axis concept for a basic, per-array field.
    """
    parsed = parse_space_directions(measurement_frame)
    if any(column is None for column in parsed):
        raise NrrdParseError(
            "'measurement frame' entries must all be vectors; 'none' is "
            "not a valid measurement frame column (there is no per-axis "
            "concept for a basic, per-array field)"
        )
    columns = tuple(column for column in parsed if column is not None)
    if len(columns) != space_dimension:
        raise NrrdParseError(
            f"'measurement frame' declares {len(columns)} vectors but "
            f"space dimension is {space_dimension}"
        )
    if any(len(column) != space_dimension for column in columns):
        raise NrrdParseError(
            f"every 'measurement frame' vector must have {space_dimension} "
            "components, matching the space dimension"
        )
    return MeasurementFrameTransform(space_dimension=space_dimension, columns=columns)


__all__ = ["MeasurementFrameTransform", "build_measurement_frame_transform"]
