from __future__ import annotations

import sys
from importlib import util
from importlib.metadata import distribution, version
from pathlib import Path

import numpy as np

import format_factory.safetensors as factory_safetensors
from format_factory.safetensors import (
    DType,
    SafeTensorsDocument,
    TensorDescriptor,
    dumps,
    loads,
)


def _official_safetensors() -> object:
    """Load the installed official package despite this test directory's name."""

    package_root = Path(distribution("safetensors").locate_file("safetensors"))
    spec = util.spec_from_file_location(
        "_format_factory_bidirectional_official_safetensors",
        package_root / "__init__.py",
        submodule_search_locations=[str(package_root)],
    )
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_official_writer_is_readable_by_factory() -> None:
    official_safetensors = _official_safetensors()
    official_values = {
        "f32": np.asarray([[1.5, -2.25], [3.0, 4.5]], dtype="<f4"),
        "u8": np.asarray([0, 7, 255], dtype="u1"),
    }
    specs = {
        name: official_safetensors.TensorSpec(
            dtype=value.dtype.name,
            shape=value.shape,
            data_ptr=value.ctypes.data,
            data_len=value.nbytes,
        )
        for name, value in official_values.items()
    }
    encoded = bytes(
        official_safetensors.serialize(
            specs,
            metadata={"producer": "official-safetensors-0.8.0"},
        )
    )

    with loads(encoded) as document:
        assert document.metadata == {
            "producer": "official-safetensors-0.8.0"
        }
        assert document.tensors["f32"].dtype is DType.F32
        assert document.tensors["f32"].shape == (2, 2)
        assert bytes(document.tensor_bytes("f32")) == official_values["f32"].tobytes()
        assert document.tensors["u8"].dtype is DType.U8
        assert document.tensors["u8"].shape == (3,)
        assert bytes(document.tensor_bytes("u8")) == official_values["u8"].tobytes()


def test_factory_writer_is_readable_by_official_implementation() -> None:
    official_safetensors = _official_safetensors()
    f32 = np.asarray([1.25, -7.5], dtype="<f4")
    u8 = np.asarray([2, 4, 8], dtype="u1")
    payload = f32.tobytes() + u8.tobytes()
    document = SafeTensorsDocument(
        tensors={
            "f32": TensorDescriptor(
                name="f32",
                dtype=DType.F32,
                shape=(2,),
                data_offsets=(0, len(f32.tobytes())),
            ),
            "u8": TensorDescriptor(
                name="u8",
                dtype=DType.U8,
                shape=(3,),
                data_offsets=(len(f32.tobytes()), len(payload)),
            ),
        },
        metadata={"producer": "format-factory"},
        payload=payload,
    )
    with document:
        encoded = dumps(document)

    official_values = dict(official_safetensors.deserialize(encoded))
    assert official_values["f32"] == {
        "dtype": "F32",
        "shape": [2],
        "data": bytearray(f32.tobytes()),
    }
    assert official_values["u8"] == {
        "dtype": "U8",
        "shape": [3],
        "data": bytearray(u8.tobytes()),
    }


def test_official_and_factory_distributions_coinstall_without_collision() -> None:
    official_safetensors = _official_safetensors()
    assert version("safetensors") == "0.8.0"
    assert version("format-factory-safetensors") == "0.2.0.dev0"

    official_origin = Path(official_safetensors.__file__).resolve()
    factory_origin = Path(factory_safetensors.__file__).resolve()
    assert "site-packages" in official_origin.parts
    assert "site-packages" in factory_origin.parts
    assert official_origin != factory_origin
    assert official_origin.parent.name == "safetensors"
    assert factory_origin.parent.name == "safetensors"
    assert factory_origin.parent.parent.name == "format_factory"

    official_root = Path(distribution("safetensors").locate_file("safetensors")).resolve()
    factory_root = Path(
        distribution("format-factory-safetensors").locate_file(
            "format_factory/safetensors"
        )
    ).resolve()
    assert official_origin.is_relative_to(official_root)
    assert factory_origin.is_relative_to(factory_root)
    assert not official_origin.is_relative_to(factory_root)
    assert not factory_origin.is_relative_to(official_root)
