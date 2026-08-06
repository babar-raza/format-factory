"""ORA-LIFECYCLE-001 and ORA-WRITE-001 — load, validate, and write back.

This is the slice that makes OpenRaster usable rather than merely inspectable.
The requirements, quoted:

  "Provide load from filesystem path, readable stream, and in-memory bytes,
   returning the format's root document/model object."
  "Provide save to filesystem path and writable stream, plus serialization to
   bytes, producing output the library's own loader accepts."
  "Expose the detected format version and any declared version separately;
   never silently rewrite a declared version."
  "Support a strict read mode that rejects malformed input with diagnostics and
   a tolerant read mode that recovers where the format permits, with recovery
   actions reported."
  "Expose validation as a first-class callable operation returning structured
   diagnostics, not only as exceptions raised during parsing."
  "Offer deterministic serialization such that an unchanged loaded document
   serializes to identical bytes across repeated calls in the same mode."
  "Write stable member order, normalized timestamps and metadata, exact
   sentinels, deterministic XML, validated raster assets, and explicit
   lossless-versus-canonical preservation modes."
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib

import pytest

from format_factory.ora import (
    OraArchiveError,
    OraImage,
    OraValidationError,
    PreservationMode,
    ReadMode,
    dump,
    dumps,
    load,
    loads,
    validate,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def png(width: int = 8, height: int = 8, bit_depth: int = 8, colour_type: int = 6,
        interlace: int = 0) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, colour_type, 0, 0, interlace)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(b"\0" * 16))
        + _chunk(b"IEND", b"")
    )


STACK = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<image w="8" h="8" version="0.0.5">'
    b'<stack><layer name="only" src="data/only.png"/></stack>'
    b"</image>"
)


def archive(
    *,
    stack: bytes = STACK,
    members: dict[str, bytes] | None = None,
    thumbnail: bytes | None = None,
    merged: bytes | None = None,
) -> bytes:
    entries: dict[str, bytes] = {"stack.xml": stack}
    entries.update(members if members is not None else {"data/only.png": png()})
    if thumbnail is not None:
        entries["Thumbnails/thumbnail.png"] = thumbnail
    if merged is not None:
        entries["mergedimage.png"] = merged

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        for name, payload in entries.items():
            zf.writestr(name, payload)
    return buffer.getvalue()


def complete_archive() -> bytes:
    return archive(thumbnail=png(64, 64), merged=png(8, 8))


# ── Loading from every declared source ─────────────────────────────────────


def test_load_from_bytes() -> None:
    image = loads(complete_archive())

    assert isinstance(image, OraImage)
    assert image.document.width == 8


def test_load_from_a_readable_stream() -> None:
    image = load(io.BytesIO(complete_archive()))

    assert image.document.root.children[0].name == "only"


def test_load_from_a_filesystem_path(tmp_path) -> None:
    path = tmp_path / "sample.ora"
    path.write_bytes(complete_archive())

    image = load(path)

    assert image.document.height == 8


def test_load_rejects_an_unsupported_source_type() -> None:
    with pytest.raises(TypeError):
        load(12345)  # type: ignore[arg-type]


# ── Declared version is never silently rewritten ───────────────────────────


def test_declared_version_is_preserved_verbatim() -> None:
    """"never silently rewrite a declared version" -- a writer that normalised
    0.0.3 to 0.0.5 would claim conformance the document never asserted."""
    stack = STACK.replace(b'version="0.0.5"', b'version="0.0.3"')
    image = loads(archive(stack=stack, thumbnail=png(16, 16), merged=png()))

    assert image.declared_version == "0.0.3"
    # Read the member rather than scanning raw archive bytes: stack.xml is
    # DEFLATE-compressed, so the string is not present literally in the file.
    with zipfile.ZipFile(io.BytesIO(dumps(image))) as written:
        assert b'version="0.0.3"' in written.read("stack.xml")


def test_detected_version_is_separate_from_the_declared_one() -> None:
    """Detected is inferred from features actually used; declared is what the
    file says. A document may declare 0.0.1 and use 0.0.4 features."""
    stack = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1" xres="300" yres="300">'
        b'<stack><stack name="group" isolation="isolate">'
        b'<layer name="only" src="data/only.png"/>'
        b"</stack></stack></image>"
    )
    image = loads(archive(stack=stack, thumbnail=png(16, 16), merged=png()))

    assert image.declared_version == "0.0.1"
    assert image.detected_version == "0.0.4"
    assert image.declared_version != image.detected_version


def test_detected_version_of_a_plain_document_is_the_baseline() -> None:
    """Control for the test above: detection must not always report 0.0.4, or
    the comparison would be meaningless."""
    image = loads(complete_archive())

    assert image.detected_version == "0.0.2"


# ── Strict and tolerant read modes ─────────────────────────────────────────


def test_strict_mode_rejects_a_document_missing_its_thumbnail() -> None:
    """"Thumbnails/thumbnail.png is required" -- strict mode enforces it."""
    with pytest.raises(OraValidationError) as raised:
        loads(archive(merged=png()), mode=ReadMode.STRICT)

    assert "thumbnail" in str(raised.value).lower()


def test_tolerant_mode_recovers_and_reports_the_recovery() -> None:
    """"a tolerant read mode that recovers where the format permits, with
    recovery actions reported" -- recovery is only useful if it is visible."""
    image = loads(archive(merged=png()), mode=ReadMode.TOLERANT)

    assert image.document.width == 8
    assert any("thumbnail" in action.lower() for action in image.recovery_actions)


def test_tolerant_mode_reports_nothing_when_nothing_needed_recovery() -> None:
    """Control: recovery_actions must not be populated unconditionally."""
    image = loads(complete_archive(), mode=ReadMode.TOLERANT)

    assert image.recovery_actions == ()


def test_tolerant_mode_still_refuses_structurally_broken_input() -> None:
    """Tolerance covers what "the format permits", not a corrupt container. A
    tolerant mode that accepted anything would be a silent-corruption engine."""
    with pytest.raises(OraArchiveError):
        loads(b"not a zip at all", mode=ReadMode.TOLERANT)


def test_strict_is_the_default_mode() -> None:
    with pytest.raises(OraValidationError):
        loads(archive(merged=png()))


# ── Validation as a first-class callable ───────────────────────────────────


def test_validate_returns_structured_diagnostics_rather_than_raising() -> None:
    """"Expose validation as a first-class callable operation returning
    structured diagnostics, not only as exceptions raised during parsing." """
    report = validate(archive(merged=png()))

    assert report.is_valid is False
    codes = {diagnostic.code for diagnostic in report.diagnostics}
    assert any("THUMBNAIL" in code for code in codes)


def test_validate_reports_a_conforming_document_as_valid() -> None:
    report = validate(complete_archive())

    assert report.is_valid is True
    assert report.diagnostics == ()


def test_validate_does_not_raise_on_a_broken_archive() -> None:
    """A validator that raises on the worst input is not a validator -- the
    caller asked for a report, and "this is not a ZIP" is a finding."""
    report = validate(b"definitely not a zip")

    assert report.is_valid is False
    assert len(report.diagnostics) >= 1


def test_validate_reports_a_non_conforming_thumbnail() -> None:
    """"must be a non-interlaced PNG with 8 bits per channel, and must not
    exceed 256 by 256 pixels." """
    report = validate(archive(thumbnail=png(300, 300), merged=png()))

    assert report.is_valid is False
    assert any("THUMBNAIL" in diagnostic.code for diagnostic in report.diagnostics)


def test_validate_reports_a_non_conforming_merged_image() -> None:
    report = validate(archive(thumbnail=png(16, 16), merged=png(bit_depth=4, colour_type=0)))

    assert any("MERGED" in diagnostic.code for diagnostic in report.diagnostics)


def test_validate_reports_a_missing_merged_image() -> None:
    """"mergedimage.png is mandatory since profile 0.0.2" -- absence itself
    is a distinct, named finding (ORA_MERGED_IMAGE_MISSING), not just a
    side effect of the non-conforming-content check above, which requires
    the member to exist at all before it can inspect its bit depth."""
    report = validate(archive(thumbnail=png(16, 16)))

    assert report.is_valid is False
    assert any(
        diagnostic.code == "ORA_MERGED_IMAGE_MISSING" for diagnostic in report.diagnostics
    )


def test_strict_mode_rejects_a_document_missing_its_mergedimage() -> None:
    """Mirrors test_strict_mode_rejects_a_document_missing_its_thumbnail --
    both required assets enforce identically in strict mode."""
    with pytest.raises(OraValidationError) as raised:
        loads(archive(thumbnail=png(16, 16)), mode=ReadMode.STRICT)

    assert "mergedimage" in str(raised.value).lower()


# ── Deterministic serialization ────────────────────────────────────────────


def test_serialization_is_byte_identical_across_repeated_calls() -> None:
    """"an unchanged loaded document serializes to identical bytes across
    repeated calls in the same mode." """
    image = loads(complete_archive())

    assert dumps(image) == dumps(image) == dumps(image)


def test_serialization_is_stable_across_separate_loads() -> None:
    """Stronger: two independent loads of the same input must also agree, or
    the output depends on load-time state rather than on the document."""
    payload = complete_archive()

    assert dumps(loads(payload)) == dumps(loads(payload))


def test_output_does_not_depend_on_input_member_order() -> None:
    """"stable member order" -- two archives with the same content written in
    different orders must serialize identically, or the writer is echoing the
    input's accidents."""
    first = archive(
        members={"data/a.png": png(4, 4), "data/b.png": png(6, 6)},
        stack=STACK.replace(b"data/only.png", b"data/a.png"),
        thumbnail=png(16, 16),
        merged=png(),
    )
    second_entries = {"data/b.png": png(6, 6), "data/a.png": png(4, 4)}
    second = archive(
        members=second_entries,
        stack=STACK.replace(b"data/only.png", b"data/a.png"),
        thumbnail=png(16, 16),
        merged=png(),
    )

    assert dumps(loads(first)) == dumps(loads(second))


def test_the_written_archive_is_accepted_by_our_own_loader() -> None:
    """"producing output the library's own loader accepts" -- the minimum bar
    for a writer, and the one most easily left unproven."""
    original = loads(complete_archive())

    reloaded = loads(dumps(original))

    assert reloaded.document.width == original.document.width
    assert reloaded.declared_version == original.declared_version


def test_a_round_trip_is_a_fixed_point() -> None:
    """Writing an already-written archive must change nothing. If it does, the
    format is not stable under its own writer and repeated saves drift."""
    once = dumps(loads(complete_archive()))
    twice = dumps(loads(once))

    assert once == twice


# ── The written archive obeys the container rules ──────────────────────────


def test_written_mimetype_is_first_and_stored() -> None:
    """The writer must satisfy the same sentinel rule the reader enforces."""
    payload = dumps(loads(complete_archive()))

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        infos = zf.infolist()
        assert infos[0].filename == "mimetype"
        assert infos[0].compress_type == zipfile.ZIP_STORED
        assert zf.read("mimetype") == b"image/openraster"


def test_written_timestamps_are_normalized() -> None:
    """"normalized timestamps" -- the reason two builds agree. A writer using
    the wall clock produces a different archive every second."""
    payload = dumps(loads(complete_archive()))

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        assert {info.date_time for info in zf.infolist()} == {(1980, 1, 1, 0, 0, 0)}


def test_written_members_use_only_permitted_compression() -> None:
    payload = dumps(loads(complete_archive()))

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        methods = {info.compress_type for info in zf.infolist()}
        assert methods <= {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}


# ── Preservation modes ─────────────────────────────────────────────────────


def test_lossless_mode_preserves_unknown_stack_attributes() -> None:
    """"explicit lossless-versus-canonical preservation modes." Lossless keeps
    the original stack.xml, so a vendor extension this library does not model
    survives a round trip instead of being silently dropped."""
    stack = STACK.replace(
        b'src="data/only.png"', b'src="data/only.png" mypaint:locked="true"'
    ).replace(b"<image ", b'<image xmlns:mypaint="http://mypaint.org/ns/openraster" ')
    payload = archive(stack=stack, thumbnail=png(16, 16), merged=png())

    written = dumps(loads(payload), preservation=PreservationMode.LOSSLESS)

    with zipfile.ZipFile(io.BytesIO(written)) as zf:
        assert b"mypaint:locked" in zf.read("stack.xml")


def test_canonical_mode_regenerates_the_stack_and_drops_unmodelled_content() -> None:
    """Canonical is the honest opposite: it emits only what the model holds, so
    what it drops is visible rather than accidental."""
    stack = STACK.replace(
        b'src="data/only.png"', b'src="data/only.png" mypaint:locked="true"'
    ).replace(b"<image ", b'<image xmlns:mypaint="http://mypaint.org/ns/openraster" ')
    payload = archive(stack=stack, thumbnail=png(16, 16), merged=png())

    written = dumps(loads(payload), preservation=PreservationMode.CANONICAL)

    with zipfile.ZipFile(io.BytesIO(written)) as zf:
        emitted = zf.read("stack.xml")
        assert b"mypaint:locked" not in emitted
        assert b'version="0.0.5"' in emitted


def test_canonical_output_is_also_deterministic() -> None:
    image = loads(complete_archive())

    first = dumps(image, preservation=PreservationMode.CANONICAL)
    second = dumps(image, preservation=PreservationMode.CANONICAL)

    assert first == second


def test_canonical_output_still_loads() -> None:
    canonical = dumps(loads(complete_archive()), preservation=PreservationMode.CANONICAL)

    reloaded = loads(canonical)

    assert reloaded.document.root.children[0].src == "data/only.png"


def test_lossless_is_the_default_preservation_mode() -> None:
    """Defaulting to canonical would silently discard extensions on any
    load-then-save, which is the destructive option."""
    stack = STACK.replace(b'src="data/only.png"', b'src="data/only.png" x-vendor="1"')
    payload = archive(stack=stack, thumbnail=png(16, 16), merged=png())

    with zipfile.ZipFile(io.BytesIO(dumps(loads(payload)))) as zf:
        assert b"x-vendor" in zf.read("stack.xml")


# ── Saving ─────────────────────────────────────────────────────────────────


def test_dump_writes_to_a_stream() -> None:
    image = loads(complete_archive())
    sink = io.BytesIO()

    dump(image, sink)

    assert loads(sink.getvalue()).document.width == 8


def test_dump_writes_to_a_path(tmp_path) -> None:
    image = loads(complete_archive())
    destination = tmp_path / "written.ora"

    dump(image, destination)

    assert loads(destination.read_bytes()).document.width == 8


# ── Layer PNG structural validation ──────────────────────────────────────────


def test_strict_mode_rejects_non_png_layer_source() -> None:
    payload = archive(
        members={"data/only.png": b"this is not a PNG at all"},
        thumbnail=png(16, 16),
        merged=png(),
    )
    with pytest.raises(OraValidationError, match="not a valid PNG"):
        loads(payload, mode=ReadMode.STRICT)


def test_strict_mode_rejects_truncated_png_layer_source() -> None:
    payload = archive(
        members={"data/only.png": PNG_SIGNATURE + b"\x00" * 4},
        thumbnail=png(16, 16),
        merged=png(),
    )
    with pytest.raises(OraValidationError, match="not a valid PNG"):
        loads(payload, mode=ReadMode.STRICT)


def test_tolerant_mode_reports_invalid_layer_png() -> None:
    payload = archive(
        members={"data/only.png": b"not png"},
        thumbnail=png(16, 16),
        merged=png(),
    )
    image = loads(payload, mode=ReadMode.TOLERANT)
    assert any("not a valid PNG" in action for action in image.recovery_actions)


def test_validate_reports_invalid_layer_png() -> None:
    payload = archive(
        members={"data/only.png": b"definitely not a png"},
        thumbnail=png(16, 16),
        merged=png(),
    )
    report = validate(payload)
    assert report.is_valid is False
    assert any("LAYER" in d.code for d in report.diagnostics)


def test_valid_layer_png_passes_validation() -> None:
    report = validate(complete_archive())
    assert report.is_valid is True
    layer_diags = [d for d in report.diagnostics if "LAYER" in d.code]
    assert layer_diags == []


def test_multi_layer_validation_checks_all_sources() -> None:
    multi_stack = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack>'
        b'<layer name="good" src="data/good.png"/>'
        b'<layer name="bad" src="data/bad.png"/>'
        b'</stack></image>'
    )
    payload = archive(
        stack=multi_stack,
        members={"data/good.png": png(), "data/bad.png": b"broken"},
        thumbnail=png(16, 16),
        merged=png(),
    )
    report = validate(payload)
    layer_diags = [d for d in report.diagnostics if "LAYER" in d.code]
    assert len(layer_diags) == 1
    assert "bad.png" in layer_diags[0].message
