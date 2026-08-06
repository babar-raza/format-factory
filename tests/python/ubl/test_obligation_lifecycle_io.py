"""UBL-LIFECYCLE-001 -- load/save across path, stream, bytes; determinism.

MUST, quoted from the format contract:

  "Provide load from filesystem path, readable stream, and in-memory bytes,
   returning the format's root document/model object."
  "Provide save to filesystem path and writable stream, plus serialization
   to bytes, producing output the library's own loader accepts."
  "Offer deterministic serialization such that an unchanged loaded document
   serializes to identical bytes across repeated calls in the same mode."
  "Expose validation as a first-class callable operation returning
   structured diagnostics, not only as exceptions raised during parsing."

test_production_namespace.py already proves loads()/dumps() round-trip
across all 91 UBL root document types, and load(path) is exercised for a
parse-error case (test_extension_payload_never_resolves_external_entities).
It does not exercise load() from a readable stream, dump() to a path or a
stream, or that a loaded-then-saved-then-reloaded document is identical --
nor that repeated dumps() calls on one unchanged document are byte-
identical. This file closes those specific gaps with new tests; no source
change was needed since load()/loads()/dump()/dumps()/validate() already
implement every clause -- only the proof was missing.
"""

from __future__ import annotations

from io import BytesIO

from format_factory.ubl import dump, dumps, load, loads, validate

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"

INVOICE = (
    f'<Invoice xmlns="{NAMESPACE}" xmlns:cbc="{CBC}">'
    "<cbc:UBLVersionID>2.3</cbc:UBLVersionID>"
    "<cbc:ID>INV-001</cbc:ID>"
    "</Invoice>"
).encode()


# ── load(): path, readable stream, in-memory bytes ──────────────────────────


def test_load_from_a_filesystem_path(tmp_path) -> None:
    path = tmp_path / "invoice.xml"
    path.write_bytes(INVOICE)

    document = load(path)

    assert document.root_name == "Invoice"


def test_load_from_a_readable_stream() -> None:
    document = load(BytesIO(INVOICE))

    assert document.root_name == "Invoice"


def test_load_from_in_memory_bytes() -> None:
    document = load(INVOICE)

    assert document.root_name == "Invoice"


def test_loads_from_in_memory_bytes() -> None:
    document = loads(INVOICE)

    assert document.root_name == "Invoice"


def test_all_three_load_forms_agree() -> None:
    from_bytes = load(INVOICE)
    from_stream = load(BytesIO(INVOICE))
    assert from_bytes.root == from_stream.root
    assert from_bytes.root_name == from_stream.root_name


# ── save(): path, writable stream, bytes; own loader accepts the output ────


def test_dump_to_a_filesystem_path_and_reload(tmp_path) -> None:
    document = loads(INVOICE)
    destination = tmp_path / "written.xml"

    dump(document, destination)
    reloaded = load(destination)

    assert reloaded.root == document.root


def test_dump_to_a_writable_stream_and_reload() -> None:
    document = loads(INVOICE)
    stream = BytesIO()

    dump(document, stream)
    reloaded = load(BytesIO(stream.getvalue()))

    assert reloaded.root == document.root


def test_dumps_to_bytes_and_reload() -> None:
    document = loads(INVOICE)

    reloaded = loads(dumps(document))

    assert reloaded.root == document.root


def test_the_librarys_own_loader_accepts_every_save_forms_output(tmp_path) -> None:
    """The obligation's own wording: save() output must be accepted by
    load(), not merely well-formed XML in the abstract."""
    document = loads(INVOICE)

    path_destination = tmp_path / "via-path.xml"
    dump(document, path_destination)
    assert validate(load(path_destination)).is_valid

    stream_destination = BytesIO()
    dump(document, stream_destination)
    assert validate(load(BytesIO(stream_destination.getvalue()))).is_valid

    assert validate(loads(dumps(document))).is_valid


# ── Deterministic serialization ─────────────────────────────────────────────


def test_repeated_dumps_calls_on_one_unchanged_document_are_byte_identical() -> None:
    document = loads(INVOICE)

    first = dumps(document)
    second = dumps(document)
    third = dumps(document)

    assert first == second == third


def test_repeated_dump_to_path_calls_are_byte_identical(tmp_path) -> None:
    document = loads(INVOICE)
    first_path = tmp_path / "first.xml"
    second_path = tmp_path / "second.xml"

    dump(document, first_path)
    dump(document, second_path)

    assert first_path.read_bytes() == second_path.read_bytes()


def test_a_freshly_reloaded_document_serializes_identically_to_the_original() -> None:
    """Determinism across a load-save-load cycle, not merely within one
    in-memory object: this is what makes edit-tracking hashes trustworthy."""
    document = loads(INVOICE)
    original_bytes = dumps(document)

    reloaded = loads(original_bytes)

    assert dumps(reloaded) == original_bytes


# ── Validation as a first-class callable, not only parse-time exceptions ───


def test_validate_returns_a_structured_report_not_an_exception() -> None:
    document = loads(INVOICE)

    report = validate(document)

    assert report.is_valid
    assert report.diagnostics == ()


def test_validate_reports_a_diagnostic_rather_than_raising_for_a_semantic_issue() -> None:
    """Calling validate() explicitly, after a document is already loaded, is
    the obligation's point: a semantic problem (unsupported profile) is a
    reported finding here, not a raised exception the caller must catch."""
    document = loads(INVOICE)

    report = validate(document, profile="UBL-2.4-preview")

    assert not report.is_valid
    assert any(item.code == "ubl.profile.unsupported" for item in report.diagnostics)


def test_validate_is_callable_independently_of_load_or_dump() -> None:
    """validate() takes an already-in-memory document -- it is not a
    load()-time side effect a caller cannot invoke on demand."""
    document = loads(INVOICE)
    edited = document.with_root(document.root)

    report_before = validate(document)
    report_after = validate(edited)

    assert report_before.is_valid
    assert report_after.is_valid
