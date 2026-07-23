"""Production namespace, safety, and representation characterization."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from format_factory.core import ResourceLimits
from format_factory.nrrd import (
    NrrdDocument,
    NrrdParseError,
    dump,
    dumps,
    load,
    loads,
    probe,
    validate,
)


def fixture(encoding: str = "raw", *, nrrd_type: str = "uint16") -> bytes:
    endian = "endian: little\n" if nrrd_type != "uint8" else ""
    document = NrrdDocument(
        version=5,
        header={
            "type": nrrd_type,
            "dimension": "2",
            "sizes": "2 2",
            "encoding": encoding,
            **({"endian": "little"} if endian else {}),
            "kinds": "domain domain",
            "vendor field": "retained",
        },
        payload=b"",
        array=[1, 2, 3, 4],
        comments=["characterization"],
        key_value_pairs={"vendor": "value"},
    )
    return dumps(document)


@pytest.mark.parametrize("encoding", ["raw", "gzip", "bzip2", "hex", "ascii"])
def test_all_standard_chassis_encodings_roundtrip(encoding: str) -> None:
    encoded = fixture(encoding)
    document = loads(encoded)
    assert document.array == [1, 2, 3, 4]
    assert document.header["vendor field"] == "retained"
    assert document.comments == ["characterization"]
    assert document.key_value_pairs == {"vendor": "value"}
    assert validate(document).is_valid
    assert dumps(document) == encoded


def test_lifecycle_api_and_stream_destination() -> None:
    encoded = fixture()
    result = probe(encoded)
    assert result.matched and result.profile == "NRRD0005"
    document = loads(encoded, mode="preservation")
    stream = BytesIO()
    dump(document, stream)
    assert loads(stream.getvalue()).array == document.array


def test_big_endian_decode_and_default_profile() -> None:
    document = NrrdDocument(
        version=1,
        header={
            "type": "int16",
            "dimension": "1",
            "sizes": "2",
            "endian": "big",
            "encoding": "raw",
        },
        payload=b"",
        array=[258, -2],
    )
    encoded = dumps(document)
    assert encoded.startswith(b"NRRD0005\n")
    assert encoded[-4:] == b"\x01\x02\xff\xfe"
    assert loads(encoded).array == [258, -2]


def test_detached_single_payload_is_bounded_and_path_safe(tmp_path: Path) -> None:
    (tmp_path / "data.raw").write_bytes(b"\x01\x02\x03\x04")
    header = (
        b"NRRD0005\n"
        b"type: uint8\n"
        b"dimension: 1\n"
        b"sizes: 4\n"
        b"encoding: raw\n"
        b"data file: data.raw\n\n"
    )
    path = tmp_path / "image.nhdr"
    path.write_bytes(header)
    assert load(path).array == [1, 2, 3, 4]

    path.write_bytes(header.replace(b"data.raw", b"../data.raw"))
    with pytest.raises(NrrdParseError, match="unsafe detached"):
        load(path)


def test_duplicate_header_and_truncated_payload_fail_closed() -> None:
    duplicate = fixture().replace(b"type: uint16\n", b"type: uint16\ntype: uint16\n")
    with pytest.raises(NrrdParseError, match="duplicate"):
        loads(duplicate)
    with pytest.raises(NrrdParseError, match="payload length mismatch"):
        loads(fixture()[:-1])


def test_resource_limits_are_caller_configurable() -> None:
    limits = ResourceLimits(max_input_bytes=16)
    with pytest.raises(Exception, match="max_input_bytes"):
        loads(fixture(), limits=limits)


def test_production_package_has_no_parent_namespace_initializer() -> None:
    package = Path(__file__).parents[3] / "src/python/nrrd/src/format_factory"
    assert not (package / "__init__.py").exists()
