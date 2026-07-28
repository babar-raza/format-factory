"""Production namespace, safety, and representation characterization."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from format_factory.core import ResourceLimits
from format_factory.nrrd import (
    NrrdDocument,
    NrrdParseError,
    NrrdWriteError,
    dump,
    dumps,
    load,
    loads,
    preservation_report,
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


def test_recovery_mode_is_explicit_and_reports_no_unsafe_repair() -> None:
    encoded = fixture()
    recovered = loads(encoded, mode="recovery")
    assert recovered.recovery_actions == ()
    with pytest.raises(ValueError, match="recovery"):
        loads(encoded, mode="unsafe")


def test_lossless_mode_replays_unchanged_source_and_reports_mutation() -> None:
    source = (
        b"NRRD0004\r\n"
        b"vendor field: retained\r\n"
        b"type: uint8\r\n"
        b"dimension: 1\r\n"
        b"sizes: 2\r\n"
        b"encoding: raw\r\n"
        b"vendor:=value\r\n\r\n\x01\x02"
    )
    document = loads(source, mode="preservation")
    assert preservation_report(document).is_lossless
    assert dumps(document, mode="lossless") == source

    document.header["vendor field"] = "changed"
    report = preservation_report(document)
    assert [issue.code for issue in report.issues] == [
        "nrrd.lossless.document_modified"
    ]
    with pytest.raises(NrrdWriteError, match="lossless output unavailable"):
        dumps(document, mode="lossless")


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
    assert encoded.startswith(b"NRRD0001\n")
    assert dumps(document, profile="NRRD0005").startswith(b"NRRD0005\n")
    assert encoded[-4:] == b"\x01\x02\xff\xfe"
    assert loads(encoded).array == [258, -2]


def test_block_type_roundtrips_and_rejects_invalid_combinations() -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "block",
            "block size": "2",
            "dimension": "1",
            "sizes": "2",
            "encoding": "raw",
        },
        payload=b"",
        array=[b"\x01\x02", b"\x03\x04"],
    )
    assert loads(dumps(document)).array == [b"\x01\x02", b"\x03\x04"]

    invalid_encoding = NrrdDocument(
        version=5,
        header={**document.header, "encoding": "ascii"},
        payload=b"",
        array=list(document.array),
    )
    with pytest.raises(NrrdWriteError, match="block"):
        dumps(invalid_encoding)

    missing_block_size = b"\n".join(
        [
            b"NRRD0005",
            b"type: block",
            b"dimension: 1",
            b"sizes: 1",
            b"encoding: raw",
            b"",
            b"\x01",
        ]
    )
    with pytest.raises(NrrdParseError, match="block size"):
        loads(missing_block_size)


@pytest.mark.parametrize(
    ("nrrd_type", "value"),
    [
        ("signed char", -7), ("int8", -7), ("int8_t", -7),
        ("uchar", 7), ("unsigned char", 7), ("uint8", 7), ("uint8_t", 7),
        ("short", -7), ("short int", -7), ("signed short", -7),
        ("signed short int", -7), ("int16", -7), ("int16_t", -7),
        ("ushort", 7), ("unsigned short", 7), ("unsigned short int", 7),
        ("uint16", 7), ("uint16_t", 7), ("int", -7), ("signed int", -7),
        ("int32", -7), ("int32_t", -7), ("uint", 7), ("unsigned int", 7),
        ("uint32", 7), ("uint32_t", 7), ("longlong", -7),
        ("long long", -7), ("long long int", -7),
        ("signed long long", -7), ("signed long long int", -7),
        ("int64", -7), ("int64_t", -7), ("ulonglong", 7),
        ("unsigned long long", 7), ("unsigned long long int", 7),
        ("uint64", 7), ("uint64_t", 7), ("float", 1.25), ("double", 1.25),
    ],
)
def test_every_normative_scalar_type_alias_roundtrips(
    nrrd_type: str, value: int | float
) -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": nrrd_type,
            "dimension": "1",
            "sizes": "1",
            "encoding": "raw",
            "endian": "little",
        },
        payload=b"",
        array=[value],
    )
    reloaded = loads(dumps(document))
    assert reloaded.header["type"] == nrrd_type
    assert reloaded.array == [value]


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


def test_validation_reports_declared_payload_byte_mismatch() -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint16",
            "dimension": "1",
            "sizes": "1",
            "endian": "little",
            "encoding": "raw",
        },
        payload=b"\x01",
        array=[1],
    )
    report = validate(document)
    assert not report.is_valid
    assert any(item.code == "nrrd.payload.length" for item in report.diagnostics)


def test_resource_limits_are_caller_configurable() -> None:
    limits = ResourceLimits(max_input_bytes=16)
    with pytest.raises(Exception, match="max_input_bytes"):
        loads(fixture(), limits=limits)


def test_production_package_has_no_parent_namespace_initializer() -> None:
    package = Path(__file__).parents[3] / "src/python/nrrd/src/format_factory"
    assert not (package / "__init__.py").exists()
