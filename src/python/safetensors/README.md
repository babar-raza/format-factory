# format-factory-safetensors

Framework-neutral SafeTensors v0.8.0 parsing, validation, lazy memory mapping,
and deterministic writing under the collision-free namespace
`format_factory.safetensors`.

```python
from format_factory.safetensors import load, safe_open

document = load("model.safetensors")
print(document.tensor_names)

with safe_open("model.safetensors") as mapped:
    weights = mapped.tensor_bytes("model.weight")
```

The reader executes no code and rejects duplicate JSON keys, unsupported
dtypes, malformed shapes, integer-size overflow, sub-byte misalignment,
overlapping offsets, holes, truncation, unindexed trailing bytes, non-string
metadata, and configured resource-limit violations.

The package does not install a top-level `safetensors` module and can be
co-installed with Hugging Face's official implementation.
