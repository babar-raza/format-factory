# format-factory-ora

Typed, bounded OpenRaster (`.ora`) layered raster archive support under the
implicit `format_factory` namespace: load, validate, edit, and write
layered raster documents with atomic transactional edits, deterministic
output, and resource limits enforced by default.

OpenRaster is a ZIP archive holding an ordered layer tree (`stack.xml`),
the layer rasters it references, and required thumbnail/merged-image
viewing assets. Archive members and XML are untrusted passive data:
parsing never executes embedded content and never resolves network
resources.

## Installation

```bash
pip install format-factory-ora
```

## Common lifecycle

```python
from format_factory.ora import load, validate, dump

report = validate("painting.ora")
if report.is_valid:
    image = load("painting.ora")
    dump(image, "canonical.ora")
```

`validate()` accepts the same source forms as `load()` (a path, bytes, or a
readable binary stream) and returns a `ValidationReport` of structured
diagnostics rather than raising on the first problem. `load()` returns an
`OraImage`: its typed `document` (canvas dimensions and the layer/group
tree), the raw archive `members`, and both `declared_version` (read
verbatim, never silently rewritten) and `detected_version` (the lowest
spec version whose features the document actually uses) exposed
separately.

## Transactional editing

```python
from format_factory.ora import apply_transaction

def add_layer(image):
    ...  # return a new OraImage with the layer added

result = apply_transaction(image, [add_layer, rename_layer, reorder_layer])
if result.committed:
    dump(result.image, "edited.ora")
else:
    print(f"rolled back after {result.steps_applied} step(s): {result.error}")
```

Each `EditStep` (a plain `Callable[[OraImage], OraImage]`) receives the
image the previous step produced. If any step raises, or returns
something that is not an `OraImage`, the whole sequence rolls back to the
untouched original -- `result.image` is always a fully valid `OraImage`,
never a partially-applied document, whichever way the transaction ends.

## Layer stack model and composite operations

```python
from format_factory.ora import OraStack, OraLayer, OraText, composite_op_info

for child in image.document.root.children:
    if isinstance(child, OraLayer):
        info = composite_op_info(child.composite_op)
        print(child.name, child.composite_op, info.porter_duff_operator if info else "custom")
    elif isinstance(child, OraStack):
        print(child.name, "group, isolation =", child.isolation)
```

The layer tree is `OraStack`/`OraLayer`/`OraText`/`OraNode`-typed,
recursively nesting groups. Every node tracks `explicit_attributes`
(`node.was_explicit("opacity")`) so a caller can distinguish "the archive
wrote this value" from "this is just the dataclass default." `composite_op_info()`
looks up a composite-op value's documented blend function and Porter-Duff
operator, returning `None` for a value outside the spec's current table --
composite-op is a deliberately open, forward-compatible vocabulary, not an
error to reject.

## Raster asset resolution

```python
from format_factory.ora import OraContainer, resolve_asset, resolve_all_assets

container = OraContainer.from_bytes(open("painting.ora", "rb").read())
assets = resolve_all_assets(container, image.document.root)
for asset in assets:
    print(asset.member_name, asset.metadata.width, asset.metadata.height)
```

`resolve_asset`/`resolve_all_assets` locate a layer's own raster member by
exact, case-sensitive name (OpenRaster member names are never
path-normalized or fuzzily matched) and read its PNG metadata without
decoding pixel data. `resolve_all_assets` fails on the first unresolvable
reference rather than returning a partial list.

Both compose `read_png_metadata()`, which works on any PNG bytes directly
-- useful for inspecting a raster's declared size and bit depth (for
example, before deciding whether it is safe to decode) without needing an
OpenRaster archive at all:

```python
from format_factory.ora import read_png_metadata

metadata = read_png_metadata(png_bytes)
print(metadata.width, metadata.height, metadata.bit_depth, metadata.channels)
```

It parses only the 25-byte IHDR chunk and never inflates pixel data, so a
file whose compressed pixel data is corrupt still yields correct metadata
-- the caller decides whether to spend the decode.

## Baseline asset replacement

```python
from format_factory.ora import replace_baseline_asset

replaced = replace_baseline_asset(image, thumbnail=new_thumbnail_png_bytes)
dump(replaced, "updated.ora")
```

A caller who has already produced a new thumbnail and/or merged-image PNG
by some other means (their own renderer, a different tool) can swap it in
via `thumbnail=`/`merged_image=` (bytes, either or both -- at least one is
required). The replacement is validated against the exact same constraints
load-time parsing enforces: the thumbnail must be a non-interlaced PNG with
8 bits per channel and at most 256x256; the merged image must carry 8 or 16
bits per channel. A non-conforming replacement is refused with
`OraValidationError` rather than silently accepted. `image` itself is never
mutated -- `replace_baseline_asset()` returns a new `OraImage`. This
package has no image-generation capability of its own (no
flattening/downscaling renderer exists), so only the *replace* half of
ORA-BASELINEASSET-001 is built; *generate* remains genuinely unbuilt.

## Preservation modes

```python
from format_factory.ora import dumps, PreservationMode, check_preservation

report = check_preservation(image)  # what CANONICAL mode would drop
canonical_bytes = dumps(image, preservation=PreservationMode.CANONICAL)
lossless_bytes = dumps(image)  # LOSSLESS is the default
```

`LOSSLESS` (the default) round-trips every archive member and
XML-unmodeled attribute verbatim. `CANONICAL` regenerates `stack.xml`
from only what this package's typed model understands.
`check_preservation()` reports exactly what would be dropped before a
caller commits to that choice.

## Security and resource limits

```python
from format_factory.core import ResourceLimits
from format_factory.ora import load, dumps

image = load("painting.ora", limits=ResourceLimits(max_input_bytes=1_000_000))
payload = dumps(image, limits=ResourceLimits(max_output_bytes=5_000_000))
```

Every load enforces `max_input_bytes`, `max_entries` (both the ZIP
central-directory member count and a cumulative per-tree attribute-flood
guard), `max_decompressed_bytes` and `max_compression_ratio` (a genuine
zip-bomb detector, checked from the ZIP central directory alone before any
member is decompressed), `max_xml_nodes`, `max_nesting_depth`, and
`max_header_bytes` -- all before a document is fully materialized in
memory. `dumps()`/`dump()` enforce `max_output_bytes` on the final
serialized archive. A whole-package static sweep (AST-level, not just a
runtime test) confirms no module anywhere in this package can reach
networking, process-spawning, or dynamic-import capabilities.

## Public namespace

The full public surface lives under `format_factory.ora` -- lifecycle
(`load`/`loads`/`dump`/`dumps`/`validate`), the typed model
(`OraDocument`, `OraStack`, `OraLayer`, `OraText`, `OraNode`), the raw
container (`OraContainer`), transactional editing (`apply_transaction`,
`EditStep`, `TransactionResult`), asset resolution (`resolve_asset`,
`resolve_all_assets`, `RasterMetadata`, `ResolvedAsset`), composite
operations (`composite_op_info`, `COMPOSITE_OP_REGISTRY`,
`CompositeOpInfo`), and preservation (`PreservationMode`, `LossReport`,
`LossItem`, `check_preservation`).

## Security boundary

OpenRaster archives are parsed as strict, bounded ZIP + XML -- no DTD
processing, no external entity resolution, and no layer `src` reference
is ever resolved as a network URL (it is used only as an exact ZIP
member-name lookup key). See `SECURITY.md` for the full untrusted-input
policy.

## Current scope

The package is still `0.1.0.dev0`. Rendering/compositing pixel data (as
opposed to reading its declared metadata) and streaming decode for very
large canvases are not yet built.

## License

Apache-2.0. See the repository root `LICENSE` file.
