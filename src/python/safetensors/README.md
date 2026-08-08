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

`validate()` returns deterministic rule-specific diagnostic codes such as
`SAFETENSORS_DTYPE`, `SAFETENSORS_TENSOR_SIZE`,
`SAFETENSORS_OFFSET_COVERAGE`, and `SAFETENSORS_RESOURCE_LIMIT`. Resource
diagnostics include the limit name, actual value, and configured maximum.
Tensor rank is bounded by `ResourceLimits.max_nesting_depth`; header, input,
and tensor-count ceilings use their corresponding resource-limit fields.

Closing a mapped document while an exported region is alive raises
`SafeTensorsError` with code `SAFETENSORS_BORROWED_VIEW_ACTIVE`. The document
retains the mapping owner, so callers can release all regions and retry
`close()` without leaking the mapping. Closed documents reject further region
access with `SAFETENSORS_DOCUMENT_CLOSED`.

For callers who want the whole document decoded up front rather than lazily
mapped, `load`/`loads` (read) and `dump`/`dumps` (write) work with a fully
materialized `SafeTensorsDocument`:

```python
from format_factory.safetensors import dump, load

document = load("model.safetensors")
print(list(document.tensors))
print(bytes(document.tensor_bytes("model.weight"))[:16])

dump(document, "copy.safetensors")
```

`loads`/`dumps` are the bytes-in/bytes-out counterparts of `load`/`dump`.
`dump`/`dumps` re-validate the document and re-derive tensor offsets
deterministically (sorted by descending dtype width, then name) rather than
trusting whatever offsets the document happened to carry, so editing
`document.tensors` between load and dump produces a correctly laid-out file
rather than a corrupt one.

The package does not install a top-level `safetensors` module and can be
co-installed with Hugging Face's official implementation.

Sharded model indexes are a separate JSON lifecycle:

```python
from format_factory.safetensors import load_index

index = load_index("model.safetensors.index.json")
shard_path = index.resolve_shard("model.weight", "model-directory")
```

`load_index` rejects duplicate JSON keys and unsafe shard references.
References must be normalized relative POSIX paths. `dump_index` writes
deterministic compact JSON, and `resolve_shard` proves the resolved path stays
under the caller-provided root.

Optional framework adapters remain separately importable:

```python
from format_factory.safetensors.adapters import to_numpy, to_torch

with safe_open("model.safetensors") as mapped:
    borrowed = to_numpy(mapped, "model.weight")  # read-only; mapped must stay open
    independent = to_numpy(mapped, "model.weight", copy=True)  # writable copy
    gpu_tensor = to_torch(
        mapped,
        "model.weight",
        copy=True,
        device="cuda:0",
    )
```

Importing the base package or the adapter modules does not import NumPy or
PyTorch. NumPy's `copy=False` path is a read-only borrowed view. PyTorch is
intentionally copy-only because PyTorch tensors are mutable and cannot safely
alias a read-only bytes object or memory map. Unsupported framework dtypes are
rejected rather than reinterpreted, and device validation/transfer is delegated
to PyTorch.
