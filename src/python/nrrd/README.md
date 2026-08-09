# Format Factory — NRRD

Typed, bounded parsing and deterministic writing for NRRD0001 through
NRRD0005 scientific raster data (medical/volumetric imaging arrays), with
attachment-form conversion, encoding/dtype conversion, lazy payload
access, and resource limits enforced by default.

## Installation

```bash
pip install format-factory-nrrd
```

## Common lifecycle

```python
from format_factory.nrrd import dump, load, probe, validate

result = probe("volume.nrrd")
if not result:
    raise ValueError(result.reason)

document = load("volume.nrrd")
report = validate(document)
if report.is_valid:
    dump(document, "volume-copy.nrrd")
```

The production namespace is `format_factory.nrrd`; the collision-prone
alpha namespace `nrrd` is excluded from built distributions. `probe()`
never raises -- it returns a falsy `ProbeResult` for unrecognized input.
`validate()` returns a structured `ValidationReport` rather than raising
on the first problem.

## Attachment-form conversion

```python
from format_factory.nrrd import convert_to_attached, convert_to_detached_list, dump_detached

# Detached (header + separate .raw payload file(s)) -> single attached file
report = convert_to_attached(document, "combined.nrrd")

# Attached -> detached LIST form, one payload file per declared axis slice
report = convert_to_detached_list(document, "volume.nhdr", ["slice-0.raw", "slice-1.raw"])
print(report.bytes_written, report.form)

# Write any document straight to single-file detached form
dump_detached(document, "volume.nhdr", "volume.raw")
```

Composes the existing reader/writer primitives rather than a separate
code path -- the same document round-trips identically regardless of
which attachment form it started or ends in. `dump_detached()` is the
direct write path for the single-file detached case (as opposed to
converting an already-loaded document's own form): the payload
destination must resolve to a path inside the header destination's own
directory, the same confinement `load()` itself enforces when reading a
detached file back.

## Encoding and dtype conversion

```python
from format_factory.nrrd import convert_dtype, convert_encoding, convert_endian, OverflowPolicy, RoundingPolicy

# Re-encode the payload (raw/gzip/bzip2/hex/ascii) -- lossless, no policy needed
gzip_document, encoding_report = convert_encoding(document, "gzip")

# Convert sample values between numeric types -- overflow policy is mandatory;
# a rounding policy is also required whenever the result could be non-integral
# (a float source, or any source under an explicit scale factor)
new_values, dtype_report = convert_dtype(
    values,
    source_type="double",
    target_type="uint8",
    overflow=OverflowPolicy.CLIP,
    rounding=RoundingPolicy.ROUND_HALF_UP,
)

# Byte-swap an already-decoded raw payload's own elements (single-byte
# types are an explicit, documented no-op, not a silently ignored request)
swapped = convert_endian(payload_bytes, type_name="uint16")
```

`convert_encoding()` only changes how the payload is serialized (its
decoded array values are unchanged); `convert_dtype()` changes the
values themselves and requires an explicit `OverflowPolicy` (clip, wrap,
or refuse) since narrowing a numeric type can lose information, plus an
explicit `RoundingPolicy` (truncate or round-half-up) whenever a value
could plausibly be non-integral -- there is no default, since truncation
and round-half-up disagree on exactly 0.5 and this package never
silently picks a business outcome. `convert_endian()` is the third,
independent conversion axis: it swaps a raw payload's own multi-byte
element order without touching dtype or encoding.

## Header-only inspection

```python
from format_factory.nrrd import read_header

header = read_header("large-volume.nrrd")
print(header.header["sizes"], header.header["type"])
print(header.access.mode, header.access.zero_copy)
```

`read_header()` parses only the header and never opens or reads the
payload -- useful for inspecting dimensions, type, and space metadata
across many large files without touching any payload bytes.
`header.access` reports how the payload *would* be read if requested: a
raw, unskipped, single-file payload reports `memory_mapped`/`zero_copy=True`
(eligible for `open_lazy_payload()` below), while a compressed payload
reports `streaming_decode`/`zero_copy=False` (decoded incrementally, never
memory-mapped).

## Lazy payload access

```python
from format_factory.nrrd import open_lazy_payload, PayloadAccessMode

header, payload = open_lazy_payload("large-volume.nrrd")
if header.access.mode is PayloadAccessMode.MEMORY_MAPPED:
    region = payload.region(0, 4096)  # zero-copy memoryview
    region.release()  # release before payload.close()
elif header.access.mode is PayloadAccessMode.STREAMING_DECODE:
    chunk = payload.read_stream(4096)  # sequential decoded bytes
payload.close()
```

`open_lazy_payload()` calls `read_header()` internally and additionally
opens a lazy view of the payload itself (memory-mapped or a streaming
decompressor, per `header.access.mode`). Like `read_header()`, it is a
distinct, explicitly-invoked entry point -- never called implicitly by
`load()`/`loads()`/`validate()`/`dumps()`. `region()` (zero-copy,
`MEMORY_MAPPED` only) and `read_stream()` (sequential, `STREAMING_DECODE`
only) are the two access methods; each raises if called in the other
mode. Any `region()` view must be released before `close()`, the same
borrowed-view discipline used elsewhere in this product line.

Pre-NRRD0004 detached payloads with a bare-relative filename (no leading
`./`) are refused by default -- the spec defines that case as resolved
against the reader's own current working directory, an unconfined base
this reader will not assume silently. `load()`/`loads()`/
`open_lazy_payload()` all accept an explicit `cwd_relative_base=` opt-in
(a caller-supplied directory) to resolve that case instead, with the same
traversal-safety checks (no absolute paths, no escaping the supplied
directory) applied relative to it.

## Space transforms

```python
from format_factory.nrrd import build_space_transform, parse_space_directions, parse_space_origin

directions = parse_space_directions(document.header.get("space directions", ""))
origin = parse_space_origin(document.header.get("space origin", ""))
transform = build_space_transform(directions, origin)
```

Parses NRRD's own `space directions`/`space origin` header fields (the
axis-to-physical-space mapping used by medical imaging tools) into a
typed `SpaceTransform`.

## Measurement frame transforms

```python
from format_factory.nrrd import build_measurement_frame_transform

transform = build_measurement_frame_transform(
    measurement_frame=document.header["measurement frame"],
    space_dimension=3,
)
world_vector = transform.measurement_to_world((1.0, 0.0, 0.0))
```

A NRRD0005+ `measurement frame` is a separate, distinct concept from the
`space directions`/`space origin` transform above: it maps the
*coefficients* of a vector or tensor quantity (for example, a diffusion
gradient direction) into world space, not array-index positions. It is
therefore a pure linear map -- `MeasurementFrameTransform` carries no
origin term at all, unlike `SpaceTransform`. `build_measurement_frame_transform()`
requires exactly `space_dimension` column vectors, each with exactly
`space_dimension` components, and rejects a `"none"` entry (there is no
per-axis concept for this field).

## Typed array view

```python
from format_factory.nrrd import array_view, get_array

view = array_view(document)  # NrrdArrayView -- shape/strides/dtype, zero-copy
print(view.shape, view.strides, view.dtype)

cropped = view.crop((0, 1), (0, 2))    # zero-copy, shares the same backing data
flipped = view.flip(axis=0)            # zero-copy; strides negate, axis metadata updates
permuted = view.permute((1, 0))        # zero-copy axis reorder
materialized = cropped.copy()          # the only operation that copies data
```

`array_view()` returns a lightweight, dependency-free (no numpy) typed
view over a document's decoded elements, distinct from the untyped
`get_array()` nested-list result above. Slicing (`view[...]`),
`.transpose()`/`.permute()`, `.flip()`, and `.crop()` are all zero-copy:
each returns a new `NrrdArrayView` sharing the same immutable backing
data, recomputing only shape/strides/offset and per-axis metadata
(`view.axes` -- kind, label, unit, spacing, axis min/max, center,
thickness, and any per-axis space direction). Per-axis metadata follows
every operation: a flipped axis has its min/max swapped and its space
direction (if any) negated; a "range"-kind axis (for example, a
fixed-width 3-color channel axis) refuses a slice or crop that would
change its own declared size. Only `.copy()` materializes an independent
copy of the data.

## Preservation and array access

```python
from format_factory.nrrd import get_array, get_dimension, preservation_report

array = get_array(document)          # the decoded sample data
dimension = get_dimension(document)  # declared axis count
report = preservation_report(document)
print(report.is_lossless, report.dropped_fields)
```

`preservation_report()` describes whether `document` can be written back
in exact-preservation mode before a caller commits to that choice --
mirroring the LOSSLESS/CANONICAL disclosure pattern used across the
other FF6 formats.

`get_array()`'s decoded array is host-order nested (Python's own outermost
-to-innermost convention), the reverse of NRRD's own fastest-first axis
order. `with_array()` is the explicit write-side counterpart: it accepts a
host-order nested array (for example, a modified `get_array()` result) and
returns a copy of `document` with the payload flattened back to NRRD's own
order, ready to `dump()`:

```python
from format_factory.nrrd import axis_order_report, dump, get_array

array = get_array(document)
edited = document.with_array([[value * 2 for value in row] for row in array])
dump(edited, "scaled.nrrd")

report = axis_order_report(edited.sizes)
print(report.strides, report.nesting_order)
```

`axis_order_report()` returns the same axis-order mapping `get_array()`/
`with_array()` use, callable independently of any array's own values --
useful for a caller who wants to know which NRRD axis a given nesting
depth corresponds to without performing a conversion.

## Recovery mode

```python
from format_factory.nrrd import load

document = load("volume.nrrd", mode="recovery")
if document.recovery_actions:
    for action in document.recovery_actions:
        print(action)
```

`load()`/`loads()` accept a `mode` of `"strict"` (default), `"preservation"`,
or `"recovery"`. `"recovery"` is a tolerant read that recovers where the
format genuinely permits it -- for example, a raw-encoded payload with
extra trailing bytes beyond its declared shape is truncated to the
declared size rather than rejected, since excess trailing bytes can never
be part of any declared element. Every recovery action taken is reported
on the returned document's own `recovery_actions` tuple (empty when
nothing needed recovering), never silently applied. A payload SHORTER
than declared is still rejected in every mode -- there is no safe way to
invent missing bytes -- and every other resource-limit and
structural-validity check still applies unchanged; `"recovery"` only
widens the one specific, spec-safe case above.

## Security and resource limits

```python
from format_factory.nrrd import NRRD_DEFAULT_LIMITS, load

document = load("volume.nrrd", limits=NRRD_DEFAULT_LIMITS.with_overrides(max_input_bytes=10_000_000))
```

Every load enforces `max_input_bytes`, `max_header_bytes`,
`max_decompressed_bytes` (a genuine compression-bomb guard: a
gzip/bzip2 payload whose declared shape implies more bytes than the
ceiling is refused before full inflation), and `max_entries` (declared
axis count) -- all before a document is fully materialized in memory.
`dumps()`/`dump()` enforce `max_output_bytes` at every serialization
exit point. A whole-package static sweep (AST-level) confirms no module
anywhere in this package can reach networking, process-spawning, or
dynamic-import capabilities, and no call site names `eval`/`exec`/
`compile` as a callable.

## Current scope

Complete detached LIST/pattern semantics beyond what `convert_to_detached_list`/
`convert_to_detached_printf`/`dump_multifile`/`dump_multifile_printf`
already cover, block types, mmap-backed streaming beyond
`open_lazy_payload`'s own bounded-region reads, full metadata typing,
and independent Teem/pynrrd interoperability certification remain open.

## License

Apache-2.0. See the repository root `LICENSE` file.
