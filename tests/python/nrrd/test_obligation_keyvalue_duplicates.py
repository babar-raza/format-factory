"""NRRD-KEYVALUE-001 -- duplicate key/value keys use last-value-wins.

MUST (SAL-NRRD-OBL-48CB227B444651BA / SAL-NRRD-OBL-6533C8FB0044E3A2, Teem NRRD
Format Specification Sections 1.1 and 1.2): "key:=value pairs... last-value-wins
duplicate-key behavior."

Before this slice, a repeated key:=value key raised NrrdParseError instead --
the opposite of the spec-mandated behavior. Confirmed no test anywhere in the
suite relied on the reject-on-duplicate behavior before changing it.
"""

from __future__ import annotations

from format_factory.nrrd import loads


def _source(*key_value_lines: str) -> bytes:
    header = (
        b"NRRD0005\n"
        b"type: uint8\n"
        b"dimension: 1\n"
        b"sizes: 2\n"
        b"encoding: raw\n"
    )
    kv = "".join(f"{line}\n" for line in key_value_lines).encode()
    return header + kv + b"\n\x01\x02"


def test_a_repeated_key_keeps_the_last_declared_value() -> None:
    document = loads(_source("acquisition:=scanner-A", "acquisition:=scanner-B"))

    assert document.key_value_pairs == {"acquisition": "scanner-B"}


def test_three_repeats_of_one_key_keep_only_the_final_value() -> None:
    document = loads(
        _source(
            "acquisition:=scanner-A",
            "acquisition:=scanner-B",
            "acquisition:=scanner-C",
        )
    )

    assert document.key_value_pairs == {"acquisition": "scanner-C"}


def test_duplicate_and_distinct_keys_coexist() -> None:
    document = loads(
        _source(
            "acquisition:=scanner-A",
            "operator:=jdoe",
            "acquisition:=scanner-B",
        )
    )

    assert document.key_value_pairs == {
        "acquisition": "scanner-B",
        "operator": "jdoe",
    }
