# format-factory-safetensors

Framework-neutral SafeTensors v0.8.0 parsing, validation, lazy memory mapping,
and deterministic writing under the collision-free namespace
`format_factory.safetensors`.

```python
from format_factory.safetensors import read_header, safe_open

header = read_header("model.safetensors")
print(header.tensor_names)

with safe_open("model.safetensors") as mapped:
    weights = mapped.tensor_region("model.weight", 0, 4096)
    print(mapped.access.mode, mapped.access.full_decode_required)
    weights.release()
```

The reader executes no code and rejects duplicate JSON keys, unsupported
dtypes, malformed shapes, integer-size overflow, sub-byte misalignment,
overlapping offsets, holes, truncation, unindexed trailing bytes, non-string
metadata, and configured resource-limit violations.

`read_header` neither maps nor copies the payload. Path-backed `safe_open`
uses a read-only memory map and returns borrowed regions. Callers must release
borrowed `memoryview` objects before the document context closes. SafeTensors
has no compressed payload encoding, so access reports
`full_decode_required=False`; non-path streams explicitly report that they
were fully buffered.

The package does not install a top-level `safetensors` module and can be
co-installed with Hugging Face's official implementation.
