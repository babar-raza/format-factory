"""NRRD-CONVERT-001 -- attached/detached form conversion (the "attached/
detached form" quarter of the compound rule_text convert_dtype/
convert_encoding/convert_endian cover the other quarters of).

POL-SCR-CONVERT-01 (SHOULD): "Convert dtype, encoding, attached/detached
form, and endian with explicit overflow/clipping/scaling/rounding policies
and a conversion report."

convert.py's own prior docstring called this "a genuinely separate, larger
piece of work" needing real file-splitting/joining logic. Investigated and
found that logic already existed: dump()/dump_multifile()/
dump_multifile_printf() (codec/writer/writer.py) already perform it, built
for NRRD-MULTIFILE-001 earlier this session. NrrdDocument itself carries no
attached/detached state of its own -- the wire form is determined entirely
by which writer function is called -- so "conversion" needs no document
mutation at all, only composing the right existing writer and returning a
report, matching convert_encoding()'s own lossless-by-construction shape.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import (
    NrrdWriteError,
    convert_to_attached,
    convert_to_detached_list,
    convert_to_detached_printf,
    load,
    loads,
)

_HEADER = b"NRRD0004\ntype: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: raw\n\n"
_PAYLOAD = bytes(range(8))


def _document():
    return loads(_HEADER + _PAYLOAD)


class TestConvertToDetachedList:
    def test_round_trips_through_the_existing_reader(self, tmp_path: Path) -> None:
        document = _document()

        report = convert_to_detached_list(
            document, tmp_path / "volume.nhdr", [tmp_path / "p0.raw", tmp_path / "p1.raw"]
        )
        reloaded = load(tmp_path / "volume.nhdr")

        assert reloaded.array == document.array
        assert report.target_form == "detached_list"
        assert report.file_count == 2
        assert report.is_lossless is True

    def test_works_starting_from_an_already_detached_document(self, tmp_path: Path) -> None:
        """A document originally LOADED from a detached source converts to a
        (different) detached form just as cleanly as one loaded attached --
        confirming no attached/detached state leaks from the source form."""
        document = _document()
        convert_to_detached_list(
            document, tmp_path / "src.nhdr", [tmp_path / "s0.raw", tmp_path / "s1.raw"]
        )
        already_detached = load(tmp_path / "src.nhdr")

        convert_to_detached_list(
            already_detached, tmp_path / "dst.nhdr", [tmp_path / "d0.raw", tmp_path / "d1.raw"]
        )
        reloaded = load(tmp_path / "dst.nhdr")

        assert reloaded.array == document.array


class TestConvertToDetachedPrintf:
    def test_round_trips_through_the_existing_reader(self, tmp_path: Path) -> None:
        document = _document()

        report = convert_to_detached_printf(
            document, tmp_path / "volume.nhdr", "slice%d.raw", file_count=2
        )
        reloaded = load(tmp_path / "volume.nhdr")

        assert reloaded.array == document.array
        assert report.target_form == "detached_printf"
        assert report.file_count == 2

    def test_supports_negative_step_and_subdim(self, tmp_path: Path) -> None:
        document = _document()

        convert_to_detached_printf(
            document, tmp_path / "volume.nhdr", "s%d.raw", start=5, step=-1, file_count=2, subdim=2
        )
        reloaded = load(tmp_path / "volume.nhdr")

        assert reloaded.array == document.array


class TestConvertToAttached:
    def test_round_trips_through_the_existing_reader(self, tmp_path: Path) -> None:
        document = _document()

        report = convert_to_attached(document, tmp_path / "volume.nrrd")
        reloaded = load(tmp_path / "volume.nrrd")

        assert reloaded.array == document.array
        assert report.target_form == "attached"
        assert report.file_count == 1
        assert report.is_lossless is True

    def test_converts_a_detached_document_back_to_a_single_attached_file(
        self, tmp_path: Path
    ) -> None:
        document = _document()
        convert_to_detached_list(
            document, tmp_path / "src.nhdr", [tmp_path / "s0.raw", tmp_path / "s1.raw"]
        )
        detached = load(tmp_path / "src.nhdr")

        convert_to_attached(detached, tmp_path / "single.nrrd")
        reloaded = load(tmp_path / "single.nrrd")

        assert reloaded.array == document.array
        # A single-file attached read never returns a printf/LIST-derived
        # array shape mismatch -- confirms the round trip is exact, not
        # merely non-crashing.
        assert reloaded.dimension == document.dimension


class TestRefusalPathsAreInheritedFromTheComposedWriters:
    """These functions add no new validation of their own -- refusals are
    exactly whatever the composed dump()/dump_multifile()/
    dump_multifile_printf() already enforce, proven once each here as a
    smoke check that composition didn't silently swallow them."""

    def test_detached_list_refuses_an_uneven_split(self, tmp_path: Path) -> None:
        document = _document()
        with pytest.raises(NrrdWriteError, match="does not split evenly"):
            convert_to_detached_list(
                document,
                tmp_path / "volume.nhdr",
                [tmp_path / "p0.raw", tmp_path / "p1.raw", tmp_path / "p2.raw"],
            )

    def test_detached_printf_refuses_a_pattern_with_no_conversion(self, tmp_path: Path) -> None:
        document = _document()
        with pytest.raises(NrrdWriteError, match="must contain exactly one"):
            convert_to_detached_printf(
                document, tmp_path / "volume.nhdr", "noformat.raw", file_count=2
            )
