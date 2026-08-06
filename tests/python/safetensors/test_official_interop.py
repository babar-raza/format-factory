"""Installed-wheel interoperability proofs against official SafeTensors."""

from __future__ import annotations

import json
import struct
import sys
from importlib import util
from importlib.metadata import distribution
from importlib.metadata import version
from pathlib import Path

import format_factory.safetensors as format_factory_safetensors
from format_factory.safetensors import dump, load, loads


def _official_safetensors() -> object:
    """Load the distribution under an alias immune to this test directory's name."""

    package_root = Path(distribution("safetensors").locate_file("safetensors"))
    spec = util.spec_from_file_location(
        "_format_factory_official_safetensors",
        package_root / "__init__.py",
        submodule_search_locations=[str(package_root)],
    )
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _file_bytes(
    metadata: dict[str, str] | None,
    *,
    include_metadata: bool,
) -> bytes:
    header: dict[str, object] = {
        "x": {
            "dtype": "U8",
            "shape": [3],
            "data_offsets": [0, 3],
            "vendor": {"mode": "safe", "revision": 1},
        }
    }
    if include_metadata:
        header["__metadata__"] = metadata or {}
    encoded = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return struct.pack("<Q", len(encoded)) + encoded + b"\x01\x07\xff"


def _header(data: bytes) -> dict[str, object]:
    header_size = struct.unpack("<Q", data[:8])[0]
    value = json.loads(data[8 : 8 + header_size])
    assert isinstance(value, dict)
    return value


def test_preservation_roundtrip_is_officially_readable(
    tmp_path: Path,
) -> None:
    """Preserve safe unknown fields and metadata semantics through an external parser."""

    assert version("safetensors") == "0.8.0"
    official_safetensors = _official_safetensors()
    package_path = Path(format_factory_safetensors.__file__).resolve()
    assert "site-packages" in package_path.parts

    cases = (
        ("absent", None, False),
        ("empty", {}, True),
        ("string-map", {"framework": "independent-oracle"}, True),
    )
    for case_name, metadata, include_metadata in cases:
        destination = tmp_path / f"{case_name}.safetensors"
        with loads(
            _file_bytes(metadata, include_metadata=include_metadata),
            mode="preservation",
        ) as document:
            dump(document, destination)

        rebuilt = destination.read_bytes()
        rebuilt_header = _header(rebuilt)
        descriptor = rebuilt_header["x"]
        assert isinstance(descriptor, dict)
        assert descriptor["vendor"] == {"mode": "safe", "revision": 1}
        if case_name == "absent":
            # SAFETENSORS-PRESERVE-001: no __metadata__ key is a distinct
            # state from an explicitly empty one, and must round-trip as such.
            assert "__metadata__" not in rebuilt_header
        elif case_name == "empty":
            assert rebuilt_header["__metadata__"] == {}
        else:
            assert rebuilt_header["__metadata__"] == metadata

        official_tensors = dict(official_safetensors.deserialize(rebuilt))
        assert official_tensors["x"] == {
            "dtype": "U8",
            "shape": [3],
            "data": bytearray(b"\x01\x07\xff"),
        }

        with load(destination, mode="preservation") as reloaded:
            assert reloaded.tensors["x"].unknown_fields == {
                "vendor": {"mode": "safe", "revision": 1}
            }
            assert dict(reloaded.metadata) == (metadata or {})
            assert bytes(reloaded.tensor_bytes("x")) == b"\x01\x07\xff"
