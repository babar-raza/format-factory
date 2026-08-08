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
from format_factory.nrrd import convert_to_attached, convert_to_detached_list

# Detached (header + separate .raw payload file(s)) -> single attached file
report = convert_to_attached(document, "combined.nrrd")

# Attached -> detached LIST form, one payload file per declared axis slice
report = convert_to_detached_list(document, "volume.nhdr", ["slice-0.raw", "slice-1.raw"])
print(report.bytes_written, report.form)
```

Composes the existing reader/writer primitives rather than a separate
code path -- the same document round-trips identically regardless of
which attachment form it started or ends in.

## Encoding and dtype conversion

```python
from format_factory.nrrd import convert_dtype, convert_encoding, OverflowPolicy

# Re-encode the payload (raw/gzip/bzip2/hex/ascii) -- lossless, no policy needed
gzip_document, encoding_report = convert_encoding(document, "gzip")

# Convert sample values between numeric types -- overflow policy is mandatory
new_values, dtype_report = convert_dtype(
    values, source_type="float64", target_type="uint8", overflow=OverflowPolicy.CLIP
)
```

`convert_encoding()` only changes how the payload is serialized (its
decoded array values are unchanged); `convert_dtype()` changes the
values themselves and requires an explicit `OverflowPolicy` (clip, wrap,
or refuse) since narrowing a numeric type can lose information.

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
region = payload.read_region(offset=1024, length=4096, mode=PayloadAccessMode.STRICT)
```

`open_lazy_payload()` calls `read_header()` internally and additionally
opens a lazy view of the payload itself (memory-mapped or a streaming
decompressor, per `header.access.mode`). Like `read_header()`, it is a
distinct, explicitly-invoked entry point -- never called implicitly by
`load()`/`loads()`/`validate()`/`dumps()`.

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
