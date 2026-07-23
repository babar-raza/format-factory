# Format Factory — NRRD

Typed, bounded parsing and deterministic writing for NRRD0001 through
NRRD0005 scientific raster data.

> This package is under production migration. The package chassis and legacy
> characterization are verified; complete contract and interoperability
> certification remain computed release gates.

```bash
pip install format-factory-nrrd
```

```python
from format_factory.nrrd import dump, load, probe, validate

result = probe("volume.nrrd")
if not result:
    raise ValueError(result.reason)

document = load("volume.nrrd")
if not validate(document):
    raise ValueError("invalid NRRD")
dump(document, "volume-copy.nrrd")
```

The production namespace is `format_factory.nrrd`; the collision-prone alpha
namespace `nrrd` is excluded from built distributions. Readers enforce input,
header, decompression, element-count, and allocation limits. Loading never
renders or executes content.

Current chassis support includes attached raw, ASCII, hex, gzip, and bzip2
payloads and safe single-file detached payloads. Complete detached LIST/pattern
semantics, block types, mmap, streaming, full metadata typing, and independent
Teem/pynrrd certification remain mandatory open obligations.

License: Apache-2.0.
