from collections import Counter

from ..model import SafeTensorsDocument


def dtype_histogram(document: SafeTensorsDocument) -> dict[str, int]:
    return dict(sorted(Counter(item.dtype.value for item in document.tensors.values()).items()))


def total_tensor_bytes(document: SafeTensorsDocument) -> int:
    return sum(end - start for start, end in (item.data_offsets for item in document.tensors.values()))
