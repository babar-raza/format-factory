"""NRRD-ARRAY-001 -- typed N-dimensional array access.

MUST: "Expose typed N-dimensional array access with shape, strides, dtype,
slicing, axis permutation, flip, and crop where orientation and per-axis
metadata follow every operation." (SAL-NRRD-OBL-E4B3D1A206784660,
SAL-NRRD-OBL-FEF73EC95DF631C3, both capability_id NRRD-ARRAY-001.)

Before this module, a loaded document's array existed only as
`NrrdDocument.array` (a flat Python `list`, NRRD's own fastest-first
element order) or `NrrdDocument.to_array()` (a nested Python list, host
axis order). Neither carries shape/strides/dtype as first-class objects,
and neither supports slicing, permutation, flip, or crop as operations --
there was nothing to test, per this obligation's own prior evidence.

`NrrdArrayView` is a lightweight, dependency-free (no numpy) typed view
over a document's decoded elements: `.shape`, `.strides` (element-unit,
matching `model/document.py`'s own fastest-first convention -- `axis 0`'s
stride is always the innermost/fastest at construction, though slicing,
permutation and flip change the ORDER and SIGN of the per-axis strides
this view itself carries, not that convention's own meaning), and
`.dtype`. Slicing (`view[...]`), `.transpose()`/`.permute()`, `.flip()`
and `.crop()` are all zero-copy: each returns a new `NrrdArrayView`
sharing the same immutable backing tuple, recomputing only shape/strides/
offset/per-axis metadata. Only `.copy()` materializes independent data.

Per-axis metadata (kind, label, unit, spacing, axis min/max, center,
thickness, and -- for a NRRD0004+ document -- the per-axis space
direction vector) is carried on `AxisMetadata` and follows every
operation: dropped axes are dropped, permuted axes are reordered, a
flipped axis has its min/max swapped and its space direction (if any)
negated with `space_origin` shifted to compensate, and a cropped axis has
its min/max shifted by the crop offset (only when `spacing` is known --
left `None` rather than silently carrying a stale bound forward when it
is not, since node/cell-centering nuance is not modelled here).

A "range" kind axis (SAL-NRRD-00022: a fixed-width axis representing part
of a single logical sample's own structure, e.g. a 3-color channel axis --
`codec/kinds.py`'s `KIND_REQUIRED_SIZE` maps it to a fixed integer rather
than `None`) refuses a slice/crop that would change its own size: a
"3-color" axis cropped to 2 elements would no longer BE a 3-color sample,
which is not a resampling operation this format defines. Domain axes
(`domain`/`space`/`time`, freely resamplable) and unrecognized axes
(no declared `kinds`, or a kind outside `KIND_REQUIRED_SIZE`) are
unaffected by this guard.

Deliberately NOT attempted here, and not claimed: negative-step slicing
(use `.flip()` to reverse an axis, kept as an explicit, separately-tested
operation rather than folded into slice-step semantics); fancy/boolean
indexing; and any numpy interop -- `adapters/` remains empty; a numpy
adapter, if built, is separate, optional, additive work, not required to
satisfy this obligation's own rule_text (which asks for typed array
access, not specifically NumPy).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from format_factory.core import (
    CheckedArithmeticError,
    ResourceLimits,
    checked_product,
)

from ..codec.kinds import KIND_REQUIRED_SIZE, canonical_kind
from ..codec.payload import checked_element_count, dtype_info, is_block_type, parse_block_size
from ..errors import NrrdArrayError
from ..security import effective_limits
from ..space import parse_space_directions, parse_space_origin
from .document import NrrdDocument, _axis_strides


@dataclass(frozen=True, slots=True)
class NrrdDtype:
    """A NRRD scalar (or opaque block) element type, as a reusable object
    rather than the internal `(struct-format-char, byte-width)` pair
    `codec/payload.py`'s own `dtype_info()` returns.

    `name` is the canonical, lowercased NRRD type name as declared by the
    document's own `type` field (SAL-NRRD-00016) -- not normalized to any
    other type-naming convention (e.g. NumPy dtype strings), since this
    module has no numpy dependency to normalize toward.
    """

    name: str
    struct_code: str | None
    itemsize: int
    is_block: bool = False

    @classmethod
    def from_type_name(cls, type_name: str, *, block_size: int | None = None) -> "NrrdDtype":
        if is_block_type(type_name):
            if block_size is None:
                raise NrrdArrayError("a block-typed document requires a declared block size")
            return cls(name="block", struct_code=None, itemsize=block_size, is_block=True)
        struct_code, itemsize = dtype_info(type_name)
        return cls(name=type_name.strip().lower(), struct_code=struct_code, itemsize=itemsize)


@dataclass(frozen=True, slots=True)
class AxisMetadata:
    """One array axis's own declared semantics, independent of its
    current position in a view's `.shape`/`.strides` (which may differ
    from this axis's ORIGINAL NRRD axis index after a permutation)."""

    size: int
    kind: str | None = None
    label: str | None = None
    unit: str | None = None
    spacing: float | None = None
    axis_min: float | None = None
    axis_max: float | None = None
    center: str | None = None
    thickness: float | None = None
    space_direction: tuple[float, ...] | None = None

    @property
    def is_range_kind(self) -> bool:
        """Whether this axis's own kind is a fixed-width "range" axis
        (part of one logical sample's own structure) rather than a
        freely-resamplable domain/space/time/list/unrecognized axis."""
        if self.kind is None:
            return False
        canonical = canonical_kind(self.kind)
        return canonical is not None and KIND_REQUIRED_SIZE.get(canonical) is not None


def _flip_axis_metadata(meta: AxisMetadata) -> AxisMetadata:
    return replace(
        meta,
        axis_min=meta.axis_max,
        axis_max=meta.axis_min,
        space_direction=(
            tuple(-component for component in meta.space_direction)
            if meta.space_direction is not None
            else None
        ),
    )


def _sliced_axis_metadata(meta: AxisMetadata, *, start: int, length: int) -> AxisMetadata:
    """`meta` narrowed to `length` elements beginning at local index
    `start`. `axis_min`/`axis_max` are recomputed only when `spacing` is
    known -- otherwise cleared (`None`) rather than carried forward stale,
    since they cannot be correctly derived from `start` alone.

    Branches on `center`, confirmed directly against the pinned NRRD
    spec's own worked example (5 samples, axis min 0.0, axis max 1.0:
    node-centered samples land at 0.00/0.25/.../1.00 -- spacing
    (max-min)/(n-1); cell-centered samples land at 0.10/0.30/.../0.90 --
    spacing (max-min)/n, each sample offset half a cell from the grid's
    own edge). For a node-centered axis, `axis_min`/`axis_max` ARE sample
    positions, so narrowing to `[start, start+length)` spans
    `(length-1)*spacing` between the first and last retained sample
    (unchanged from this function's original behavior). For a
    cell-centered axis, `axis_min`/`axis_max` are the grid's own OUTER
    EDGES, half a cell short of the first/last sample position on each
    side, so the retained region's own edges span `length*spacing`, one
    full cell more than the node case -- the same edge-to-edge extent a
    single retained cell must have (never zero-width, since a cell always
    covers real space). Any axis with no declared `center`, or a value
    other than the literal `"cell"` token (including the common `"node"`
    case), keeps the node-equivalent formula -- the same conservative
    default this function has always used.
    """
    if meta.spacing is not None and meta.axis_min is not None:
        new_min = meta.axis_min + start * meta.spacing
        span = length if meta.center == "cell" else max(length - 1, 0)
        new_max = new_min + span * meta.spacing
    else:
        new_min = None
        new_max = None
    return replace(meta, size=length, axis_min=new_min, axis_max=new_max)


@dataclass(frozen=True, slots=True)
class NrrdArrayView:
    """A typed, strided view over a NRRD document's decoded elements.

    `data` is an immutable snapshot shared by every view derived from the
    same origin via slicing/`.transpose()`/`.flip()`/`.crop()` -- all
    zero-copy, `copied` stays `False`. Only `.copy()` materializes an
    independent `data` tuple, setting `copied=True`.

    `strides` are element counts (not bytes), matching
    `model/document.py`'s own `_axis_strides` convention, and may be
    negative after `.flip()`.
    """

    data: tuple[Any, ...] = field(repr=False)
    dtype: NrrdDtype
    shape: tuple[int, ...]
    strides: tuple[int, ...]
    offset: int
    axes: tuple[AxisMetadata, ...]
    space_origin: tuple[float, ...] | None = None
    copied: bool = False

    def __post_init__(self) -> None:
        if len(self.shape) != len(self.strides) or len(self.shape) != len(self.axes):
            raise NrrdArrayError(
                f"shape ({len(self.shape)}), strides ({len(self.strides)}) and axes "
                f"({len(self.axes)}) must all have the same length"
            )

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def size(self) -> int:
        total = 1
        for extent in self.shape:
            total *= extent
        return total

    def __len__(self) -> int:
        if not self.shape:
            raise TypeError("len() of a 0-dimensional array view")
        return self.shape[0]

    def _normalize_axis(self, axis: int) -> int:
        normalized = axis + self.ndim if axis < 0 else axis
        if not 0 <= normalized < self.ndim:
            raise NrrdArrayError(f"axis {axis} is out of range for a {self.ndim}-dimensional view")
        return normalized

    def __getitem__(self, key: Any) -> Any:
        indices = key if isinstance(key, tuple) else (key,)
        if len(indices) > self.ndim:
            raise NrrdArrayError(
                f"too many indices for a {self.ndim}-dimensional view: got {len(indices)}"
            )
        indices = indices + (slice(None),) * (self.ndim - len(indices))

        new_offset = self.offset
        new_shape: list[int] = []
        new_strides: list[int] = []
        new_axes: list[AxisMetadata] = []
        for axis, (index_or_slice, extent, stride, meta) in enumerate(
            zip(indices, self.shape, self.strides, self.axes)
        ):
            if isinstance(index_or_slice, bool) or not isinstance(index_or_slice, (int, slice)):
                raise TypeError(
                    f"unsupported index type for axis {axis}: {type(index_or_slice).__name__}"
                )
            if isinstance(index_or_slice, int):
                position = index_or_slice + extent if index_or_slice < 0 else index_or_slice
                if not 0 <= position < extent:
                    raise NrrdArrayError(
                        f"index {index_or_slice} is out of range for axis {axis} with size {extent}"
                    )
                new_offset += position * stride
                continue  # integer indexing drops the axis
            start, stop, step = index_or_slice.indices(extent)
            if step != 1:
                raise NrrdArrayError(
                    "only step-1 slices are supported; call .flip(axis) to reverse an axis"
                )
            length = max(0, stop - start)
            if meta.is_range_kind and length != extent:
                raise NrrdArrayError(
                    f"axis {axis} has kind {meta.kind!r}, a fixed-width sample structure "
                    f"(requires exactly {extent} elements); slicing it to {length} would "
                    "change what the sample means, not resample it"
                )
            new_offset += start * stride
            new_shape.append(length)
            new_strides.append(stride)
            new_axes.append(_sliced_axis_metadata(meta, start=start, length=length))

        if not new_shape:
            return self.data[new_offset]  # every axis integer-indexed: a scalar, not a 0-d view
        return replace(
            self,
            shape=tuple(new_shape),
            strides=tuple(new_strides),
            offset=new_offset,
            axes=tuple(new_axes),
            copied=False,
        )

    def crop(self, *bounds: tuple[int, int]) -> "NrrdArrayView":
        """Select a sub-region: `bounds[axis] = (start, stop)`, one pair
        per leading axis (trailing axes, if any, are kept whole). Thin,
        explicitly-named sugar over `__getitem__`'s own slice handling --
        the same zero-copy and fixed-width-kind guarantees apply."""
        if len(bounds) > self.ndim:
            raise NrrdArrayError(
                f"too many crop bounds for a {self.ndim}-dimensional view: got {len(bounds)}"
            )
        key = tuple(slice(start, stop) for start, stop in bounds)
        result = self[key]
        if not isinstance(result, NrrdArrayView):
            raise NrrdArrayError("crop must not reduce every axis to a scalar")
        return result

    def transpose(self, *order: int) -> "NrrdArrayView":
        """Reorder axes. With no arguments, reverses axis order (the
        conventional `.T` default). `order` must be a permutation of
        `range(self.ndim)` -- every axis exactly once, no drops, no
        repeats. `space_origin` is unaffected (a single world-space
        point, independent of axis order); each axis's own
        `space_direction` moves with it via `self.axes` reordering."""
        if not order:
            order = tuple(reversed(range(self.ndim)))
        if len(order) != self.ndim or set(order) != set(range(self.ndim)):
            raise NrrdArrayError(
                f"transpose order {order} is not a permutation of axes 0..{self.ndim - 1}"
            )
        return replace(
            self,
            shape=tuple(self.shape[axis] for axis in order),
            strides=tuple(self.strides[axis] for axis in order),
            axes=tuple(self.axes[axis] for axis in order),
            copied=False,
        )

    def permute(self, order: "tuple[int, ...] | list[int]") -> "NrrdArrayView":
        """Alias for `.transpose(*order)` taking the order as one sequence
        argument -- this obligation's own rule_text names "permutation" as
        its own word, distinct from `.transpose()`'s NumPy-style calling
        convention; both spellings are kept rather than picking one."""
        return self.transpose(*order)

    def flip(self, axis: int = 0) -> "NrrdArrayView":
        """Reverse axis `axis` (default 0) without copying: negates that
        axis's own stride and shifts `offset` to compensate. The axis's
        own `axis_min`/`axis_max` swap, and if it carries a
        `space_direction`, that vector is negated and `space_origin` is
        shifted by `(size - 1) * old_direction` so the view's world-space
        placement of its own first element is unchanged."""
        normalized = self._normalize_axis(axis)
        extent = self.shape[normalized]
        old_stride = self.strides[normalized]
        meta = self.axes[normalized]

        new_offset = self.offset + max(extent - 1, 0) * old_stride
        new_strides = list(self.strides)
        new_strides[normalized] = -old_stride
        new_axes = list(self.axes)
        new_axes[normalized] = _flip_axis_metadata(meta)

        new_space_origin = self.space_origin
        if self.space_origin is not None and meta.space_direction is not None:
            new_space_origin = tuple(
                origin + max(extent - 1, 0) * direction
                for origin, direction in zip(self.space_origin, meta.space_direction)
            )

        return replace(
            self,
            strides=tuple(new_strides),
            offset=new_offset,
            axes=tuple(new_axes),
            space_origin=new_space_origin,
            copied=False,
        )

    def copy(self) -> "NrrdArrayView":
        """Materialize this view's own visible elements (respecting its
        current shape/strides/offset, however they were derived) into a
        new, independent, contiguous backing tuple. Every other operation
        on the result is zero-copy again from that new backing."""
        new_strides = tuple(_axis_strides(list(self.shape)))
        flat: list[Any] = [None] * self.size

        def walk(axis: int, old_base: int, new_base: int) -> None:
            if axis < 0:
                flat[new_base] = self.data[old_base]
                return
            for index in range(self.shape[axis]):
                walk(
                    axis - 1,
                    old_base + index * self.strides[axis],
                    new_base + index * new_strides[axis],
                )

        if self.shape:
            walk(self.ndim - 1, self.offset, 0)
        else:
            flat = [self.data[self.offset]]

        return replace(self, data=tuple(flat), offset=0, strides=new_strides, copied=True)

    def to_nested_list(self) -> Any:
        """This view's own elements as a host-order nested Python list
        (innermost nesting = axis 0 of THIS view's current shape, the
        same fastest-first-innermost convention `model/document.py`'s
        `reshape_nrrd_array` uses for an untransposed document) --
        independent of `NrrdDocument.to_array()`, which only ever
        reflects the full, un-viewed document."""

        def build(axis: int, base: int) -> Any:
            if axis < 0:
                return self.data[base]
            return [
                build(axis - 1, base + index * self.strides[axis])
                for index in range(self.shape[axis])
            ]

        if not self.shape:
            return self.data[self.offset]
        return build(self.ndim - 1, self.offset)


def array_view(document: NrrdDocument, *, limits: ResourceLimits | None = None) -> NrrdArrayView:
    """Build the full `NrrdArrayView` over `document`'s own decoded
    elements. Element count is bounded against `limits` (checked
    arithmetic, before the immutable backing tuple is materialized) even
    though `document.array` is already fully decoded by this point --
    this is the same declared-vs-actual check `codec/payload.py`'s own
    decode path applies, kept independent so a caller constructing a
    `NrrdDocument` by hand (not through `load`/`loads`) cannot bypass it.
    """
    effective = effective_limits(limits)
    sizes = document.sizes
    expected = checked_element_count(sizes, effective)
    if len(document.array) != expected:
        raise NrrdArrayError(
            f"document.array has {len(document.array)} elements, expected {expected} "
            f"for sizes {sizes}"
        )
    try:
        checked_product(sizes, ceiling=effective.max_entries**2, label="NRRD array-view axis count")
    except CheckedArithmeticError as exc:
        raise NrrdArrayError(str(exc)) from exc

    block_size = (
        parse_block_size(document.header.get("block size", document.header.get("blocksize")))
        if is_block_type(document.nrrd_type)
        else None
    )
    dtype = NrrdDtype.from_type_name(document.nrrd_type, block_size=block_size)
    strides = tuple(_axis_strides(sizes))

    kinds = document.kinds
    labels = document.labels
    units = document.units
    spacings = document.spacings
    axis_mins = document.axis_mins
    axis_maxs = document.axis_maxs
    centers = document.centers
    thicknesses = document.thicknesses
    direction_vectors = (
        parse_space_directions(document.header["space directions"])
        if "space directions" in document.header
        else ()
    )

    def _at(values: list[Any], index: int) -> Any:
        return values[index] if index < len(values) else None

    axes = tuple(
        AxisMetadata(
            size=sizes[axis],
            kind=_at(kinds, axis),
            label=_at(labels, axis),
            unit=_at(units, axis),
            spacing=_at(spacings, axis),
            axis_min=_at(axis_mins, axis),
            axis_max=_at(axis_maxs, axis),
            center=_at(centers, axis),
            thickness=_at(thicknesses, axis),
            space_direction=(direction_vectors[axis] if axis < len(direction_vectors) else None),
        )
        for axis in range(len(sizes))
    )
    space_origin = (
        parse_space_origin(document.header["space origin"])
        if "space origin" in document.header
        else None
    )

    return NrrdArrayView(
        data=tuple(document.array),
        dtype=dtype,
        shape=tuple(sizes),
        strides=strides,
        offset=0,
        axes=axes,
        space_origin=space_origin,
        copied=False,
    )


__all__ = [
    "AxisMetadata",
    "NrrdArrayError",
    "NrrdArrayView",
    "NrrdDtype",
    "array_view",
]
