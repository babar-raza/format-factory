"""SafeTensors analytics — statistics derived from freshly-loaded tensor headers.

Analytics Layer (Dimension 7, production-library-standard-v2): no I/O beyond
calling load_safetensors() on the given source; no domain-model mutation.
Every function re-parses the source rather than operating on a pre-built
SafetensorsDocument, so results always reflect the file's current on-disk state.
"""

from __future__ import annotations

from safetensors.safetensors_codec import SourceType, load_safetensors


def safetensors_dtype_histogram(source: SourceType) -> dict[str, int]:
    """Return a count of tensors grouped by dtype.

    Spec: header tensor descriptors carry a `dtype` field (FACT-SAFETENSORS-002).
    """
    model = load_safetensors(source)
    histogram: dict[str, int] = {}
    for info in model.get("tensors", {}).values():
        dtype = str(info.get("dtype", "unknown"))
        histogram[dtype] = histogram.get(dtype, 0) + 1
    return histogram


def safetensors_total_tensor_bytes(source: SourceType) -> int:
    """Return the sum of (data_offsets[1] - data_offsets[0]) across all tensors.

    Spec: tensor data occupies byte ranges given by `data_offsets` in the
    data section (FACT-SAFETENSORS-003).
    """
    model = load_safetensors(source)
    total = 0
    for info in model.get("tensors", {}).values():
        offsets = info.get("data_offsets", [0, 0])
        if len(offsets) == 2:
            total += max(0, offsets[1] - offsets[0])
    return total


def safetensors_largest_tensor_name(source: SourceType) -> str | None:
    """Return the name of the tensor with the largest byte span, or None if empty.

    Spec: header tensor descriptors carry `data_offsets` used to determine
    each tensor's byte span (FACT-SAFETENSORS-002).
    """
    model = load_safetensors(source)
    tensors = model.get("tensors", {})
    if not tensors:
        return None
    best_name: str | None = None
    best_size = -1
    for name, info in tensors.items():
        offsets = info.get("data_offsets", [0, 0])
        size = max(0, offsets[1] - offsets[0]) if len(offsets) == 2 else 0
        if size > best_size:
            best_size = size
            best_name = name
    return best_name
