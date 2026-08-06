"""XLIFF-LIFECYCLE-001 -- load/save across path, stream, bytes; determinism;
validate as a callable; detected vs. declared version.

MUST, quoted from the format contract:

  "Provide load from filesystem path, readable stream, and in-memory bytes,
   returning the format's root document/model object."
  "Provide save to filesystem path and writable stream, plus serialization
   to bytes, producing output the library's own loader accepts."
  "Offer deterministic serialization such that an unchanged loaded document
   serializes to identical bytes across repeated calls in the same mode."
  "Expose validation as a first-class callable operation returning
   structured diagnostics, not only as exceptions raised during parsing."
  "Expose the detected format version and any declared version separately;
   never silently rewrite a declared version."

test_production_namespace.py's test_stream_and_path_lifecycle already
proves dump()-to-stream, dump()-to-path, and load()-from-path, but not
load() from an actual binary stream OBJECT, not determinism, and not
validate() called independently as a first-class operation. This file
closes those specific gaps. detected_version is new production code (this
slice); the rest needed only new tests.
"""

from __future__ import annotations

from io import BytesIO, StringIO

import pytest

from format_factory.xliff import (
    XliffDocument,
    XliffWriteError,
    dump,
    dumps,
    load,
    loads,
    validate,
)

NAMESPACE = "urn:oasis:names:tc:xliff:document:2.0"


def _xliff(version: str = "2.1") -> bytes:
    return (
        f'<xliff xmlns="{NAMESPACE}" version="{version}" srcLang="en">'
        '<file id="f1"><unit id="u1"><segment id="s1">'
        "<source>Hello</source></segment></unit></file></xliff>"
    ).encode()


# ── load(): path, readable stream, in-memory bytes ──────────────────────────


def test_load_from_a_filesystem_path(tmp_path) -> None:
    path = tmp_path / "doc.xlf"
    path.write_bytes(_xliff())

    document = load(path)

    assert document.version == "2.1"


def test_load_from_a_readable_stream() -> None:
    document = load(BytesIO(_xliff()))

    assert document.version == "2.1"


def test_load_from_in_memory_bytes() -> None:
    document = load(_xliff())

    assert document.version == "2.1"


def test_loads_from_in_memory_bytes() -> None:
    document = loads(_xliff())

    assert document.version == "2.1"


def test_all_three_load_forms_agree() -> None:
    from_bytes = load(_xliff())
    from_stream = load(BytesIO(_xliff()))

    assert from_bytes.unit_count == from_stream.unit_count == 1
    assert from_bytes.version == from_stream.version


# ── save(): path, writable stream, bytes; own loader accepts the output ────


def test_dump_to_a_filesystem_path_and_reload(tmp_path) -> None:
    document = loads(_xliff())
    destination = tmp_path / "written.xlf"

    dump(document, destination)
    reloaded = load(destination)

    assert reloaded.unit_count == document.unit_count


def test_dump_to_a_writable_stream_and_reload() -> None:
    """dump()'s destination is a TEXT stream (TextDestination), unlike
    load()'s BINARY-stream source -- an intentional asymmetry in this
    codec, not a bug this test should paper over."""
    document = loads(_xliff())
    stream = StringIO()

    dump(document, stream)
    reloaded = loads(stream.getvalue())

    assert reloaded.unit_count == document.unit_count


def test_dumps_to_bytes_and_reload() -> None:
    document = loads(_xliff())

    reloaded = loads(dumps(document))

    assert reloaded.unit_count == document.unit_count


def test_the_librarys_own_loader_accepts_every_save_forms_output(tmp_path) -> None:
    document = loads(_xliff())

    path_destination = tmp_path / "via-path.xlf"
    dump(document, path_destination)
    assert validate(load(path_destination)).is_valid

    stream_destination = StringIO()
    dump(document, stream_destination)
    assert validate(loads(stream_destination.getvalue())).is_valid

    assert validate(loads(dumps(document))).is_valid


# ── Deterministic serialization ─────────────────────────────────────────────


def test_repeated_dumps_calls_on_one_unchanged_document_are_byte_identical() -> None:
    document = loads(_xliff())

    first = dumps(document)
    second = dumps(document)
    third = dumps(document)

    assert first == second == third


def test_repeated_dump_to_path_calls_are_byte_identical(tmp_path) -> None:
    document = loads(_xliff())
    first_path = tmp_path / "first.xlf"
    second_path = tmp_path / "second.xlf"

    dump(document, first_path)
    dump(document, second_path)

    assert first_path.read_bytes() == second_path.read_bytes()


def test_a_freshly_reloaded_document_serializes_identically_to_the_original() -> None:
    document = loads(_xliff())
    original_bytes = dumps(document)

    reloaded = loads(original_bytes)

    assert dumps(reloaded) == original_bytes


# ── Validation as a first-class callable, not only parse-time exceptions ───


def test_validate_returns_a_structured_report_not_an_exception() -> None:
    document = loads(_xliff())

    report = validate(document)

    assert report.is_valid


def test_validate_reports_a_diagnostic_rather_than_raising_for_a_semantic_issue() -> None:
    document = loads(_xliff())

    report = validate(document, profile="2.9-preview")

    assert not report.is_valid
    assert any(item.code == "xliff.profile.unsupported" for item in report.diagnostics)


def test_validate_is_callable_independently_of_load_or_dump() -> None:
    document = loads(_xliff())

    report = validate(document)
    report_again = validate(document)

    assert report.is_valid
    assert report_again.is_valid


# ── detected_version vs. declared (mutable) version ─────────────────────────


def test_a_freshly_built_document_has_no_detected_version() -> None:
    document = XliffDocument(
        version="2.1", source_language="en", target_language=None, children=[]
    )

    assert document.detected_version is None


def test_loading_a_file_records_its_actual_declared_version_as_detected() -> None:
    document = loads(_xliff("2.0"))

    assert document.detected_version == "2.0"
    assert document.version == "2.0"


def test_mutating_version_never_touches_detected_version() -> None:
    """The obligation's own distinction, directly: editing the declared
    version (a plain field on this non-frozen model) does not silently
    rewrite what was actually detected on read."""
    document = loads(_xliff("2.0"))

    document.version = "2.1"

    assert document.version == "2.1"
    assert document.detected_version == "2.0"


def test_dumps_refuses_rather_than_silently_rewriting_an_unsupported_version() -> None:
    """dumps() validates before writing and accepts only 2.0/2.1. A document
    (or an explicit profile override) declaring an unsupported version is
    refused outright, not coerced -- proving "never silently rewrite" the
    strong way: no code path exists that could substitute a supported
    version and write anyway."""
    document = loads(_xliff("2.1"))

    with pytest.raises(XliffWriteError, match="1.2"):
        dumps(document, profile="1.2")


def test_repeated_round_trips_never_drift_the_declared_or_detected_version() -> None:
    document = loads(_xliff("2.1"))

    once = loads(dumps(document))
    twice = loads(dumps(once))

    assert once.version == once.detected_version == "2.1"
    assert twice.version == twice.detected_version == "2.1"
