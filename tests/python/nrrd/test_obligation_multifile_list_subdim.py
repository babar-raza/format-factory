"""NRRD-MULTIFILE-001 -- "Read and write numbered sequences and LIST
payloads only for NRRD0004 and newer; validate min/max/step/subdimension,
filename expansion, file count, and bytes per file before allocation."

MUST (SAL-NRRD-OBL-807586E5B4D0EDB2 / SAL-NRRD-OBL-EBE5230D5204B4AD):
before this slice, the LIST detached form's own optional <subdim> token
("data file: LIST <subdim>") was silently discarded rather than validated
or even preserved: _parse_header's list-mode handling reconstructed the
header's "data file" value as a hardcoded "LIST\\n<filenames>" literal,
regardless of what the original captured line actually said, so a
declaration like "data file: LIST 2" lost its "2" before
_safe_detached_payload ever saw the value.

Grounded directly in the pinned NRRD specification text
(.local/format-contracts/acquired/nrrd/src-nrrd-001.bin, Section 3):
"data file: LIST [<subdim>]" ... "A different datafile dimension (besides
D-1) can be communicated with the optional <subdim> value. This value can
be between 1 and D," D being the document's own declared `dimension:`
field -- the identical <subdim> semantics already implemented for the
printf form's fifth token in test_obligation_multifile_printf_subdim.py.

Deliberately narrow, mirroring the printf form's own precedent exactly:
this slice preserves the LIST form's original header line (so a <subdim>
token survives reconstruction) and range-validates it before any file is
opened. It does not use <subdim> to alter which files are read or how
their bytes are concatenated (the declared array shape is independently
checked against the assembled payload's total byte count downstream) --
subdim's semantic effect on per-file sample layout for lazy/partial
access remains a separate, unbuilt concern, same as for the printf form.
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


def test_a_list_sequence_with_a_valid_subdim_reads_correctly(tmp_path: Path) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "b.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "valid.nhdr"
    header_path.write_bytes(_header(2, "2 2", "LIST 1\na.raw\nb.raw"))

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]


def test_a_list_sequence_with_subdim_equal_to_dimension_reads_correctly(
    tmp_path: Path,
) -> None:
    """subdim == D is the "equal-sized slabs" case the spec names
    separately from subdim < D-1 -- still a legal boundary value."""
    (tmp_path / "a.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "b.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "slabs.nhdr"
    header_path.write_bytes(_header(2, "2 2", "LIST 2\na.raw\nb.raw"))

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]


def test_a_list_subdim_above_dimension_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "b.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "too_high.nhdr"
    header_path.write_bytes(_header(2, "2 2", "LIST 3\na.raw\nb.raw"))

    with pytest.raises(NrrdParseError, match="subdim must be between 1 and 2"):
        load(header_path)


def test_a_list_subdim_of_zero_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "b.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "zero.nhdr"
    header_path.write_bytes(_header(2, "2 2", "LIST 0\na.raw\nb.raw"))

    with pytest.raises(NrrdParseError, match="subdim must be between 1 and 2"):
        load(header_path)


def test_a_non_integer_list_subdim_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "b.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "not_int.nhdr"
    header_path.write_bytes(_header(2, "2 2", "LIST x\na.raw\nb.raw"))

    with pytest.raises(NrrdParseError, match="subdim must be an integer"):
        load(header_path)


def test_a_list_sequence_with_no_subdim_still_works_unaffected(tmp_path: Path) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([1, 2]))
    (tmp_path / "b.raw").write_bytes(bytes([3, 4]))
    header_path = tmp_path / "no_subdim.nhdr"
    header_path.write_bytes(_header(2, "2 2", "LIST\na.raw\nb.raw"))

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]
