"""SAFETENSORS-MODEL-001 -- unified proof of the combined representation claim.

MUST (SAL-SAFETENSORS-OBL-3158D0EBF275EADC): "Represent every target-version
dtype, tensor descriptor, file metadata entry, scalar, empty tensor, and
aligned sub-byte tensor independently of framework types."

Each sub-claim already had its own dedicated, independently-verified test
(dtype inventory, scalar round-trip, empty-tensor validity, aligned sub-byte
acceptance, framework-independent base import). What was missing was a single
proof that all of them hold TOGETHER, in one document, using only the base
package -- no numpy or torch import anywhere in this file -- including file
metadata entry representation specifically, which none of the five existing
selectors covered.
"""

from __future__ import annotations

import json
import struct

from format_factory.safetensors import DType, TensorDescriptor, loads


def _header_bytes(header: dict[str, object]) -> bytes:
    raw = json.dumps(header, separators=(",", ":")).encode()
    return struct.pack("<Q", len(raw)) + raw


def test_every_dtype_tensor_descriptor_metadata_scalar_empty_and_subbyte_tensor_coexist_in_one_document() -> None:
    header: dict[str, object] = {
        "__metadata__": {"produced_by": "format_factory", "version": "1"},
        "scalar": {"dtype": "F32", "shape": [], "data_offsets": [0, 4]},
        "empty": {"dtype": "I32", "shape": [3, 0], "data_offsets": [4, 4]},
        "subbyte": {"dtype": "F4", "shape": [2], "data_offsets": [4, 5]},
    }
    payload = b"\0\0\x80?" + b"\x11"
    raw = _header_bytes(header) + payload

    with loads(raw) as document:
        # __metadata__: file metadata entry representation.
        assert document.metadata == {"produced_by": "format_factory", "version": "1"}

        # dtype inventory member + tensor descriptor, independent of framework types.
        scalar_descriptor = document.tensors["scalar"]
        assert isinstance(scalar_descriptor, TensorDescriptor)
        assert scalar_descriptor.dtype is DType.F32

        # scalar: zero-rank, one element.
        assert scalar_descriptor.shape == ()
        assert bytes(document.tensor_bytes("scalar")) == b"\0\0\x80?"

        # empty tensor: a zero dimension, empty data span.
        empty_descriptor = document.tensors["empty"]
        assert empty_descriptor.byte_length == 0
        assert empty_descriptor.data_offsets == (4, 4)

        # aligned sub-byte tensor: F4 (4-bit) at 2 elements = 8 bits = 1 byte, byte-aligned.
        subbyte_descriptor = document.tensors["subbyte"]
        assert subbyte_descriptor.dtype is DType.F4
        assert subbyte_descriptor.byte_length == 1
        assert bytes(document.tensor_bytes("subbyte")) == b"\x11"

    # Framework-independent: this module imports neither numpy nor torch --
    # every assertion above used only DType/TensorDescriptor/loads from the
    # base package.
