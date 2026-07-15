"""Semantic round-trip test: load -> add a tensor -> save -> reload -> assert present.

Distinct from the Phase 1 identity round-trip test (test_safetensors_codec.py
TestRoundtrip.test_roundtrip_single_tensor), which only proves the existing
tensor set survives an unmodified load/write/load cycle. This module proves a
genuine edit (a newly-added tensor descriptor) is present after reload.

Sprint: TC-PROLIB-SAFETENSORS-001 (put-the-select-6-snappy-dijkstra.md, Phase 2)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from safetensors.models import SafetensorsDocument
from safetensors.safetensors_codec import write_safetensors

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "safetensors"
VALID_DIR = SAMPLES / "valid"

NEW_TENSOR_NAME = "synthetic_added_tensor"
NEW_TENSOR_DTYPE = "F32"
NEW_TENSOR_SHAPE = [2, 2]
NEW_TENSOR_ELEMENT_SIZE = 4  # bytes per F32 element


def _model_with_added_tensor(source: Path) -> dict:
    """Load source, return a model dict with a new synthetic tensor appended.

    The new tensor's data_offsets are computed to start immediately after the
    highest existing data_offsets[1] end value, per FACT-SAFETENSORS-003
    (tensor data is contiguous, no padding between tensors).
    """
    doc = SafetensorsDocument.from_file(str(source))
    model = doc.to_dict()
    model["tensors"] = dict(model["tensors"])  # shallow copy, don't mutate shared refs

    existing_end = max(
        (info["data_offsets"][1] for info in model["tensors"].values()), default=0
    )
    num_elements = NEW_TENSOR_SHAPE[0] * NEW_TENSOR_SHAPE[1]
    data_size = num_elements * NEW_TENSOR_ELEMENT_SIZE

    model["tensors"][NEW_TENSOR_NAME] = {
        "dtype": NEW_TENSOR_DTYPE,
        "shape": NEW_TENSOR_SHAPE,
        "data_offsets": [existing_end, existing_end + data_size],
    }
    return model


class TestMutationRoundtrip:
    """load -> add tensor -> write -> reload -> assert the new tensor is present."""

    def test_add_tensor_roundtrip(self):
        model = _model_with_added_tensor(VALID_DIR / "single-tensor.safetensors")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.safetensors"
            write_safetensors(model, dest)
            reloaded = SafetensorsDocument.from_file(str(dest))
            assert NEW_TENSOR_NAME in reloaded.tensor_names

    def test_add_tensor_preserves_existing_tensors(self):
        original = SafetensorsDocument.from_file(str(VALID_DIR / "multi-tensor.safetensors"))
        original_names = set(original.tensor_names)
        model = _model_with_added_tensor(VALID_DIR / "multi-tensor.safetensors")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.safetensors"
            write_safetensors(model, dest)
            reloaded = SafetensorsDocument.from_file(str(dest))
            assert original_names.issubset(set(reloaded.tensor_names))

    def test_add_tensor_correct_dtype_after_reload(self):
        model = _model_with_added_tensor(VALID_DIR / "single-tensor.safetensors")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.safetensors"
            write_safetensors(model, dest)
            reloaded = SafetensorsDocument.from_file(str(dest))
            assert reloaded.tensors[NEW_TENSOR_NAME]["dtype"] == NEW_TENSOR_DTYPE

    def test_add_tensor_correct_shape_after_reload(self):
        model = _model_with_added_tensor(VALID_DIR / "single-tensor.safetensors")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.safetensors"
            write_safetensors(model, dest)
            reloaded = SafetensorsDocument.from_file(str(dest))
            assert reloaded.tensors[NEW_TENSOR_NAME]["shape"] == NEW_TENSOR_SHAPE

    def test_add_tensor_increases_tensor_count(self):
        original = SafetensorsDocument.from_file(str(VALID_DIR / "with-metadata.safetensors"))
        original_count = original.tensor_count
        model = _model_with_added_tensor(VALID_DIR / "with-metadata.safetensors")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.safetensors"
            write_safetensors(model, dest)
            reloaded = SafetensorsDocument.from_file(str(dest))
            assert reloaded.tensor_count == original_count + 1

    def test_add_tensor_returns_bytes_without_dest(self):
        model = _model_with_added_tensor(VALID_DIR / "single-tensor.safetensors")
        result = write_safetensors(model)
        assert isinstance(result, bytes)
        assert len(result) > 8
