from __future__ import annotations

import importlib
import json
import struct
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

import pytest

from format_factory.safetensors import loads
from format_factory.safetensors.adapters import to_numpy, to_torch


def _file(
    *,
    dtype: str = "U8",
    shape: list[int] | None = None,
    payload: bytes = b"\x01\x02",
) -> bytes:
    selected_shape = [2] if shape is None else shape
    header = {
        "value": {
            "dtype": dtype,
            "shape": selected_shape,
            "data_offsets": [0, len(payload)],
        }
    }
    encoded = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return struct.pack("<Q", len(encoded)) + encoded + payload


def test_base_and_adapter_imports_do_not_load_optional_frameworks() -> None:
    script = """
import sys
assert "numpy" not in sys.modules
assert "torch" not in sys.modules
import format_factory.safetensors
from format_factory.safetensors import adapters
assert adapters.to_numpy
assert adapters.to_torch
assert "numpy" not in sys.modules
assert "torch" not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_numpy_adapter_discloses_read_only_zero_copy_and_safe_copy() -> None:
    with loads(_file()) as document:
        borrowed = to_numpy(document, "value", copy=False)
        copied = to_numpy(document, "value", copy=True)

        assert borrowed.tolist() == [1, 2]
        assert not borrowed.flags.writeable
        assert copied.tolist() == [1, 2]
        assert copied.flags.writeable
        copied[0] = 9
        assert bytes(document.tensor_bytes("value")) == b"\x01\x02"


def test_numpy_adapter_rejects_non_native_dtype_without_reinterpretation() -> None:
    with loads(_file(dtype="BF16", shape=[1], payload=b"\0\0")) as document:
        with pytest.raises(TypeError, match="does not natively expose"):
            to_numpy(document, "value")


@dataclass
class _FakeTensor:
    source: object
    dtype: object
    count: int
    shape: tuple[int, ...] | None = None
    device: object = "cpu"

    def reshape(self, shape: tuple[int, ...]) -> _FakeTensor:
        self.shape = shape
        return self

    def to(self, *, device: object) -> _FakeTensor:
        self.device = device
        return self


class _FakeTorch:
    uint8 = object()

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def frombuffer(
        self,
        buffer: object,
        *,
        dtype: object,
        count: int,
    ) -> _FakeTensor:
        self.calls.append(("frombuffer", buffer))
        return _FakeTensor(buffer, dtype, count)

    def from_numpy(self, array: object) -> _FakeTensor:
        self.calls.append(("from_numpy", array))
        return _FakeTensor(array, self.uint8, 2)

    def empty(self, shape: tuple[int, ...], *, dtype: object) -> _FakeTensor:
        self.calls.append(("empty", shape))
        return _FakeTensor(b"", dtype, 0, shape=shape)


def _install_fake_torch(monkeypatch: pytest.MonkeyPatch) -> _FakeTorch:
    fake = _FakeTorch()
    adapter = importlib.import_module("format_factory.safetensors.adapters.torch")
    original_import_module = importlib.import_module
    monkeypatch.setattr(
        adapter.importlib,
        "import_module",
        lambda name: fake if name == "torch" else original_import_module(name),
    )
    return fake


def test_torch_adapter_is_copy_only_for_mutable_tensor_safety(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_torch(monkeypatch)
    with loads(_file()) as document:
        with pytest.raises(ValueError, match="copy=True"):
            to_torch(document, "value", copy=False)


def test_torch_adapter_copies_bytes_and_applies_explicit_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _install_fake_torch(monkeypatch)
    with loads(_file()) as document:
        tensor = to_torch(document, "value", copy=True, device="cuda:1")
        assert tensor.shape == (2,)
        assert tensor.device == "cuda:1"
        assert tensor.count == 2
        assert fake.calls[0][0] == "frombuffer"
        assert isinstance(fake.calls[0][1], bytearray)


def test_torch_adapter_handles_empty_tensors_without_buffer_aliasing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _install_fake_torch(monkeypatch)
    with loads(_file(shape=[0], payload=b"")) as document:
        tensor = to_torch(document, "value")
        assert tensor.shape == (0,)
        assert fake.calls == [("empty", (0,))]


def test_torch_adapter_rejects_unavailable_framework_dtype(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_torch(monkeypatch)
    with loads(_file(dtype="BF16", shape=[1], payload=b"\0\0")) as document:
        with pytest.raises(TypeError, match="does not expose"):
            to_torch(document, "value")
