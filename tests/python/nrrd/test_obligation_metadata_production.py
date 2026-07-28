"""Installed-wheel evidence for NRRD metadata fidelity."""

from __future__ import annotations

from format_factory.nrrd import dumps, loads


def test_quoted_explicit_and_unknown_metadata_survive_semantic_roundtrip() -> None:
    source = (
        b"NRRD0005\n"
        b"type: uint8\n"
        b"dimension: 1\n"
        b"sizes: 2\n"
        b"encoding: raw\n"
        b"labels: \"left shoulder\"\n"
        b"units: \"mm\"\n"
        b"content: \"\"\n"
        b"vendor field: value with spaces\n"
        b"acquisition:=scanner-A\n\n\x01\x02"
    )

    document = loads(source, mode="preservation")
    assert document.header["labels"] == '"left shoulder"'
    assert document.header["units"] == '"mm"'
    assert document.header["content"] == '""'
    assert document.header["vendor field"] == "value with spaces"
    assert document.key_value_pairs == {"acquisition": "scanner-A"}
    assert "space origin" not in document.header

    canonical = loads(dumps(document))
    assert canonical.header == document.header
    assert canonical.key_value_pairs == document.key_value_pairs
    assert canonical.comments == document.comments
