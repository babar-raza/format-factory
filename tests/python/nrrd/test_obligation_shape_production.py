"""Installed-wheel evidence for NRRD dimensional payload interpretation."""

from __future__ import annotations

from pathlib import Path

from format_factory.nrrd import NrrdDocument, dump, dumps, load, loads


def test_big_endian_axis_zero_fastest_and_detached_payload(tmp_path: Path) -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint16",
            "dimension": "2",
            "sizes": "2 3",
            "endian": "big",
            "encoding": "raw",
        },
        payload=b"",
        array=[1, 2, 3, 4, 5, 6],
    )
    attached = dumps(document)
    decoded = loads(attached)
    assert decoded.array == [1, 2, 3, 4, 5, 6]
    assert decoded.to_array() == [[1, 2], [3, 4], [5, 6]]

    payload = attached.split(b"\n\n", 1)[1]
    (tmp_path / "payload.raw").write_bytes(payload)
    header = (
        b"NRRD0005\n"
        b"type: uint16\n"
        b"dimension: 2\n"
        b"sizes: 2 3\n"
        b"endian: big\n"
        b"encoding: raw\n"
        b"data file: payload.raw\n\n"
    )
    detached = tmp_path / "image.nhdr"
    detached.write_bytes(header)
    assert load(detached).to_array() == [[1, 2], [3, 4], [5, 6]]

    destination = tmp_path / "canonical.nrrd"
    dump(decoded, destination)
    assert load(destination).array == decoded.array
