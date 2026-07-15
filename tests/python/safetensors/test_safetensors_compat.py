"""Tests for the safetensors spec stubs and Compat facade classes.

Covers `safetensors.spec.header.{header,tensor}` (canonical spec-shaped
classes) and `safetensors.Compat.{safetensors_header,safetensors_tensor}`
(production facades that bind spec_qname/spec_fact_ref/namespace_uri).
"""

from __future__ import annotations

import yaml
import pytest
from pathlib import Path

from safetensors.spec.header.header import Header
from safetensors.spec.header.tensor import Tensor
from safetensors.Compat.safetensors_header import SafetensorsHeader
from safetensors.Compat.safetensors_tensor import SafetensorsTensor
import safetensors.Compat as compat_pkg
import safetensors.spec as spec_pkg

REGISTRY_PATH = (
    Path(__file__).resolve().parents[3] / "shared" / "qname-registry" / "safetensors.yaml"
)


def _registry_entries() -> dict[str, dict]:
    entries = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {e["qname"]: e for e in entries}


class TestSpecHeaderStub:
    """L1 unit: Header spec-shaped class wraps a dict correctly."""

    def test_header_stub_spec_qname_matches_registry(self):
        entries = _registry_entries()
        assert Header.spec_qname == "safetensors:header"
        assert entries["safetensors:header"]["spec_fact_ref"] == Header.spec_fact_ref

    def test_header_stub_properties_from_dict(self):
        h = Header({"header_size": 67, "tensors": {"weight": {}}, "metadata": {"a": "b"}})
        assert h.header_size == 67
        assert h.tensor_count == 1
        assert h.metadata == {"a": "b"}

    def test_header_stub_to_dict_roundtrip(self):
        data = {"header_size": 10, "tensors": {}, "metadata": {}}
        h = Header(data)
        assert h.to_dict() == data
        # to_dict returns a copy, not the same object
        assert h.to_dict() is not data

    def test_header_stub_repr(self):
        h = Header({"header_size": 5, "tensors": {"a": {}, "b": {}}})
        assert repr(h) == "Header(header_size=5, tensor_count=2)"


class TestSpecTensorStub:
    """L1 unit: Tensor spec-shaped class wraps a dict correctly."""

    def test_tensor_stub_spec_qname_matches_registry(self):
        entries = _registry_entries()
        assert Tensor.spec_qname == "safetensors:tensor"
        assert entries["safetensors:tensor"]["spec_fact_ref"] == Tensor.spec_fact_ref

    def test_tensor_stub_properties_from_dict(self):
        t = Tensor("weight", {"dtype": "F32", "shape": [2, 2], "data_offsets": [0, 16]})
        assert t.name == "weight"
        assert t.dtype == "F32"
        assert t.shape == [2, 2]
        assert t.data_offsets == [0, 16]

    def test_tensor_stub_byte_length_calc(self):
        t = Tensor("w", {"dtype": "F32", "shape": [4], "data_offsets": [10, 26]})
        assert t.byte_length == 16

    def test_tensor_stub_to_dict_includes_name(self):
        t = Tensor("w", {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]})
        d = t.to_dict()
        assert d["name"] == "w"
        assert d["dtype"] == "F32"

    def test_tensor_stub_repr(self):
        t = Tensor("w", {"dtype": "F32", "shape": [1]})
        assert repr(t) == "Tensor(name='w', dtype=F32, shape=[1])"


class TestSpecStubClassMetadata:
    """L1 unit: spec stub class-level attributes (local_name, facade_names, dtypes)."""

    def test_header_local_name_and_facade_names(self):
        assert Header.local_name == "header"
        assert Header.facade_names == ["SafetensorsHeader"]

    def test_tensor_local_name_and_facade_names(self):
        assert Tensor.local_name == "tensor"
        assert Tensor.facade_names == ["SafetensorsTensor"]

    def test_tensor_valid_dtypes_contains_common_types(self):
        for dtype in ("F32", "F16", "I8", "U8", "BOOL"):
            assert dtype in Tensor.VALID_DTYPES


class TestCompatSafetensorsHeader:
    """L2 behavior: SafetensorsHeader facade binding and inheritance."""

    def test_facade_subclasses_spec_header(self):
        assert issubclass(SafetensorsHeader, Header)

    def test_facade_header_spec_qname_binding(self):
        entries = _registry_entries()
        assert SafetensorsHeader.spec_qname == entries["safetensors:header"]["qname"]

    def test_facade_header_spec_fact_ref_and_namespace_binding(self):
        entries = _registry_entries()
        entry = entries["safetensors:header"]
        assert SafetensorsHeader.spec_fact_ref == entry["spec_fact_ref"]
        assert SafetensorsHeader.namespace_uri == entry["namespace_uri"]

    def test_facade_header_inherits_properties(self):
        h = SafetensorsHeader({"header_size": 99, "tensors": {"x": {}}, "metadata": {}})
        assert h.header_size == 99
        assert h.tensor_count == 1


class TestCompatSafetensorsTensor:
    """L2 behavior: SafetensorsTensor facade binding and inheritance."""

    def test_facade_subclasses_spec_tensor(self):
        assert issubclass(SafetensorsTensor, Tensor)

    def test_facade_tensor_spec_qname_binding(self):
        entries = _registry_entries()
        assert SafetensorsTensor.spec_qname == entries["safetensors:tensor"]["qname"]

    def test_facade_tensor_spec_fact_ref_and_namespace_binding(self):
        entries = _registry_entries()
        entry = entries["safetensors:tensor"]
        assert SafetensorsTensor.spec_fact_ref == entry["spec_fact_ref"]
        assert SafetensorsTensor.namespace_uri == entry["namespace_uri"]

    def test_facade_tensor_inherits_byte_length(self):
        t = SafetensorsTensor("w", {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]})
        assert t.byte_length == 8


class TestCompatModuleSmoke:
    """L0 smoke: package-level exports for spec and Compat."""

    def test_compat_all_exports(self):
        assert set(compat_pkg.__all__) == {"SafetensorsHeader", "SafetensorsTensor"}
        assert compat_pkg.SafetensorsHeader is SafetensorsHeader
        assert compat_pkg.SafetensorsTensor is SafetensorsTensor

    def test_compat_import_from_package_path(self):
        from safetensors.Compat import SafetensorsHeader as H, SafetensorsTensor as T
        assert H is SafetensorsHeader
        assert T is SafetensorsTensor

    def test_spec_package_all_exports(self):
        assert set(spec_pkg.__all__) == {"Header", "Tensor"}
        assert spec_pkg.Header is Header
        assert spec_pkg.Tensor is Tensor


class TestFacadeEdgeCases:
    """L3 edge: spec/Compat classes on missing or malformed dict input."""

    def test_header_stub_missing_keys_defaults(self):
        h = Header({})
        assert h.header_size == 0
        assert h.tensor_count == 0
        assert h.metadata == {}

    def test_tensor_stub_missing_data_offsets_defaults(self):
        t = Tensor("w", {"dtype": "F32", "shape": [1]})
        assert t.data_offsets == [0, 0]
        assert t.byte_length == 0

    def test_tensor_stub_zero_length_data_offsets(self):
        t = Tensor("w", {"dtype": "F32", "shape": [], "data_offsets": []})
        assert t.byte_length == 0

    def test_tensor_stub_corrupted_dtype_value_passthrough(self):
        t = Tensor("w", {"dtype": 12345, "shape": [1], "data_offsets": [0, 1]})
        # dtype is coerced to str rather than raising — malformed but survivable
        assert t.dtype == "12345"
