# Format Factory — nrrd

Parse, edit, and write NRRD (.nrrd, .nhdr) scientific/medical imaging files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-15T19:25:43+00:00 source=package-metadata -->
```bash
pip install format-factory-nrrd
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from nrrd.nrrd_codec import load_nrrd, write_nrrd, roundtrip, get_array

model = load_nrrd("volume.nrrd")
print(model["header"]["type"], model["array_shape"])
array = get_array(model)  # nested list, reshaped per axis

# write_nrrd(model, dest) re-encodes model["array"] by default (not a zero-fill)
write_nrrd(model, "volume-copy.nrrd")
reloaded = roundtrip("volume.nrrd", "volume-roundtrip.nrrd")
```

## Features

- Payload decode into typed, shaped arrays (raw and gzip encodings)
- Endianness byte-swapping when the declared `endian` differs from host order
- `line skip` / `byte skip` offset handling, including the `-1` "skip to tail" case
- `kinds` (domain vs. range axis semantics)
- `space` / `space directions` / `space origin` physical-coordinate mapping
- Key/value pair parsing (`key:=value`)

**Scope note:** ascii/hex/bzip2/zlib encodings and detached (.nhdr) header data loading remain out of scope for this pass. Stdlib-only decode (`struct`) — no numpy dependency. See `reports/spec-coverage/nrrd-deferred.json`.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-15T19:25:43+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-15T19:25:43+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Nearly Raw Raster Data |
| Track | python |
| Package | format-factory-nrrd |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Teem Project NRRD0005 |
| QName coverage | 2/2 implemented |
| Source files | 13 |
| Test files | 5 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-15T19:25:43+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
