"""NRRD-MULTIFILE-001 -- "Read and write numbered sequences and LIST
payloads only for NRRD0004 and newer; validate min/max/step/subdimension,
filename expansion, file count, and bytes per file before allocation."

MUST (SAL-NRRD-OBL-807586E5B4D0EDB2 / SAL-NRRD-OBL-EBE5230D5204B4AD):
before this slice, the optional <subdim> parameter of the printf detached
form was entirely unhandled -- confirmed by direct probing that a
legitimately spec-conformant 5-token declaration ("data file: <format>
<min> <max> <step> <subdim>") was outright REJECTED as "invalid detached
printf range", since the parser required exactly 4 tokens.

Grounded directly in the pinned NRRD specification text
(.local/format-contracts/acquired/nrrd/src-nrrd-001.bin, Section 3): "A
different datafile dimension (besides D-1) can be communicated with the
optional <subdim> value. This value can be between 1 and D," D being the
document's own declared `dimension:` field.

Deliberately narrow: this slice recognizes and range-validates <subdim>
for the printf form only, before any file is opened. It does not use
<subdim> to alter which files are read or how their bytes are
concatenated (min/max/step alone already determine that, and the total
assembled payload is independently checked against the declared array
shape downstream via expected_binary_size) -- subdim's semantic effect on
per-file sample layout for lazy/partial access remains a separate,
unbuilt concern. The LIST form's own optional <subdim> ("data file: LIST
<subdim>") is also NOT covered here: _parse_header's list-mode handling
discards the original header line entirely in favor of a reconstructed
"LIST\\n<filenames>" value before _safe_detached_payload ever sees it, a
separate, larger parsing change deliberately not attempted in this slice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import NrrdParseError, load


def _header(dimension: int, sizes: str, data_file: str) -> bytes:
    return (
        f"NRRD0004\ntype: uchar\ndimension: {dimension}\nsizes: {sizes}\n"
        f"encoding: raw\ndata file: {data_file}\n\n"
    ).encode()


def test_a_printf_sequence_with_a_valid_subdim_reads_correctly(tmp_path: Path) -> None:
    (tmp_path / "0.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "1.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "valid.nhdr"
    header_path.write_bytes(_header(2, "2 2", "%d.raw 0 1 1 1"))

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]


def test_a_printf_sequence_with_subdim_equal_to_dimension_reads_correctly(
    tmp_path: Path,
) -> None:
    """subdim == D is the "equal-sized slabs" case the spec names
    separately from subdim < D-1 -- still a legal boundary value."""
    (tmp_path / "0.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "1.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "slabs.nhdr"
    header_path.write_bytes(_header(2, "2 2", "%d.raw 0 1 1 2"))

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]


def test_a_subdim_above_dimension_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "0.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "1.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "too_high.nhdr"
    header_path.write_bytes(_header(2, "2 2", "%d.raw 0 1 1 3"))

    with pytest.raises(NrrdParseError, match="subdim must be between 1 and 2"):
        load(header_path)


def test_a_subdim_of_zero_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "0.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "1.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "zero.nhdr"
    header_path.write_bytes(_header(2, "2 2", "%d.raw 0 1 1 0"))

    with pytest.raises(NrrdParseError, match="subdim must be between 1 and 2"):
        load(header_path)


def test_a_non_integer_subdim_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "0.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "1.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "not_int.nhdr"
    header_path.write_bytes(_header(2, "2 2", "%d.raw 0 1 1 x"))

    with pytest.raises(NrrdParseError, match="subdim must be an integer"):
        load(header_path)


def test_a_printf_sequence_with_no_subdim_still_works_unaffected(tmp_path: Path) -> None:
    (tmp_path / "0.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "1.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "no_subdim.nhdr"
    header_path.write_bytes(_header(2, "2 2", "%d.raw 0 1 1"))

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]
