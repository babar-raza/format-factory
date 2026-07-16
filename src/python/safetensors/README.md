# Format Factory — safetensors

Parse, edit, and write SafeTensors (.safetensors) tensor files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-15T19:25:42+00:00 source=package-metadata -->
```bash
pip install format-factory-safetensors
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from safetensors.safetensors_codec import load_safetensors, write_safetensors, get_tensor_bytes, get_tensor

model = load_safetensors("weights.safetensors")
print(list(model["tensors"].keys()))

# Retrieve real tensor bytes / a decoded array
raw = get_tensor_bytes(model, "layer1.weight")
array, shape = get_tensor(model, "layer1.weight")

write_safetensors(model, "weights-copy.safetensors")
```

## Features

- Real tensor byte retrieval (`get_tensor_bytes`) — not header-metadata-only
- Array decode to numpy, including bf16 upcast and fp8 (F8_E4M3, F8_E5M2) dtypes
- Real tensor data on write — `write_safetensors` preserves actual bytes, not a zero-fill placeholder
- Offset overlap/bounds/coverage validation (`validate_tensor_offsets`)
- Duplicate tensor key rejection
- `__metadata__` string map support

**Scope note:** true lazy/memory-mapped streaming access remains out of scope for this pass. See `reports/spec-coverage/safetensors-deferred.json`.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-15T19:25:42+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-15T19:25:42+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | SafeTensors |
| Track | python |
| Package | format-factory-safetensors |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Hugging Face v0.4 |
| QName coverage | 2/2 implemented |
| Source files | 15 |
| Test files | 6 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-15T19:25:42+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
