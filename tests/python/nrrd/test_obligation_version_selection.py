"""NRRD-VERSION-001 / NRRD-LIFECYCLE-001 -- profile-version feature gates.

MUST (SAL-NRRD-00020, verified, "Teem NRRD Format Specification Section
1.1; Teem formatNRRD.c lines 183-205"): "NRRD profile magics are
cumulative: NRRD0001 is the baseline, NRRD0002 adds key/value pairs,
NRRD0003 adds kinds, NRRD0004 adds thicknesses, sample units,
space/orientation fields and multiple data files, and NRRD0005 adds
measurement frame; writers select the oldest version able to represent the
document."

Backed further by SAL-NRRD-00021 (key/value, NRRD0002+), SAL-NRRD-00022
(kinds, NRRD0003+), SAL-NRRD-00023 (thicknesses, NRRD0004+), SAL-NRRD-00019
(space/orientation fields, NRRD0004+; measurement frame withheld until
NRRD0005), SAL-NRRD-00006 (multi-file data file, NRRD0004+), SAL-NRRD-00024
(measurement frame, NRRD0005+), and SAL-NRRD-00010 (spacings, axis
mins/maxs, centers, labels, units are baseline -- NOT version-gated).

NRRD-LIFECYCLE-001 (POL-SLC-LIFECYCLE-01..06): "Expose the detected format
version and any declared version separately; never silently rewrite a
declared version." NrrdDocument.detected_version (reader-only, set once at
parse time) is now distinct from NrrdDocument.version (the mutable,
currently-declared value the writer will emit); the writer and validator
both refuse -- rather than silently accept or silently upgrade -- a
declared/requested profile too old for the fields actually present.

Prior to this slice, `version` was the only field, conflating "what the
file said" with "what will be written," and dumps()/validate() accepted
any profile string regardless of which fields were actually populated.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdDocument, NrrdWriteError, dumps, loads, validate


def _document(version: int = 1, **header_overrides: str) -> NrrdDocument:
    header = {
        "type": "uint16",
        "dimension": "2",
        "sizes": "2 2",
        "encoding": "raw",
        "endian": "little",
        **header_overrides,
    }
    return NrrdDocument(version=version, header=header, payload=b"", array=[1, 2, 3, 4])


# ── version_requirements() / minimal_version_for(): pure feature scan ──────


def test_baseline_only_fields_require_no_version_beyond_one() -> None:
    document = _document(spacings="1 1", labels='"x" "y"', units='"mm" "mm"')
    assert document.version_requirements() == []
    assert document.minimal_version_for() == 1


def test_key_value_pairs_require_at_least_nrrd0002() -> None:
    document = _document()
    document.key_value_pairs["vendor"] = "value"
    assert (2, "key/value pairs") in document.version_requirements()
    assert document.minimal_version_for() == 2


def test_kinds_require_at_least_nrrd0003() -> None:
    document = _document(kinds="domain domain")
    assert (3, "kinds") in document.version_requirements()
    assert document.minimal_version_for() == 3


def test_thicknesses_require_at_least_nrrd0004() -> None:
    document = _document(thicknesses="1.0 1.0")
    assert (4, "thicknesses") in document.version_requirements()
    assert document.minimal_version_for() == 4


def test_sample_units_require_at_least_nrrd0004() -> None:
    document = _document(**{"sample units": "PPM"})
    assert (4, "sample units") in document.version_requirements()
    assert document.minimal_version_for() == 4


def test_sampleunits_unspaced_alias_also_requires_at_least_nrrd0004() -> None:
    document = _document(sampleunits="PPM")
    assert (4, "sample units") in document.version_requirements()
    assert document.minimal_version_for() == 4


@pytest.mark.parametrize(
    "field_name",
    ["space", "space dimension", "space units", "space origin", "space directions"],
)
def test_space_orientation_fields_require_at_least_nrrd0004(field_name: str) -> None:
    document = _document(**{field_name: "right-anterior-superior"})
    assert (4, field_name) in document.version_requirements()
    assert document.minimal_version_for() == 4


def test_single_detached_data_file_stays_baseline() -> None:
    """A single named detached file is NRRD0001-safe; only multi-file forms
    (printf pattern or LIST) are NRRD0004+ (SAL-NRRD-00006)."""
    document = _document(**{"data file": "payload.raw"})
    assert document.version_requirements() == []
    assert document.minimal_version_for() == 1


def test_printf_pattern_data_file_requires_at_least_nrrd0004() -> None:
    document = _document(**{"data file": "slice.%03d.raw 0 9 1"})
    assert (4, "data file (multi-file)") in document.version_requirements()
    assert document.minimal_version_for() == 4


def test_list_data_file_requires_at_least_nrrd0004() -> None:
    document = _document(**{"data file": "LIST\na.raw\nb.raw"})
    assert (4, "data file (multi-file)") in document.version_requirements()
    assert document.minimal_version_for() == 4


def test_measurement_frame_requires_at_least_nrrd0005() -> None:
    document = _document(**{"measurement frame": "(1,0,0) (0,1,0)"})
    assert (5, "measurement frame") in document.version_requirements()
    assert document.minimal_version_for() == 5


def test_minimal_version_is_the_maximum_of_all_gated_fields_present() -> None:
    document = _document(kinds="domain domain", thicknesses="1.0 1.0")
    document.key_value_pairs["vendor"] = "value"
    assert document.minimal_version_for() == 4


# ── writer: refuse an insufficient profile, never silently rewrite it ──────


def test_dumps_refuses_a_declared_version_too_old_for_kinds() -> None:
    document = _document(version=1, kinds="domain domain")
    with pytest.raises(NrrdWriteError, match="kinds"):
        dumps(document)


def test_dumps_refuses_an_explicit_profile_override_too_old() -> None:
    document = _document(version=5, thicknesses="1.0 1.0")
    with pytest.raises(NrrdWriteError, match="NRRD0004"):
        dumps(document, profile="NRRD0002")


def test_dumps_error_names_every_blocking_field() -> None:
    document = _document(version=1, kinds="domain domain")
    document.key_value_pairs["vendor"] = "value"
    with pytest.raises(NrrdWriteError) as excinfo:
        dumps(document)
    message = str(excinfo.value)
    assert "kinds" in message
    assert "key/value pairs" in message


def test_dumps_succeeds_when_declared_version_is_already_sufficient() -> None:
    document = _document(version=5, kinds="domain domain")
    encoded = dumps(document)
    assert encoded.startswith(b"NRRD0005\n")


def test_dumps_succeeds_when_no_gated_field_is_present_at_any_version() -> None:
    for version in range(1, 6):
        document = _document(version=version)
        assert dumps(document).startswith(f"NRRD000{version}\n".encode("ascii"))


def test_profile_auto_selects_the_oldest_sufficient_profile() -> None:
    document = _document(version=5, kinds="domain domain")
    encoded = dumps(document, profile="auto")
    assert encoded.startswith(b"NRRD0003\n")


def test_profile_auto_on_baseline_only_document_selects_nrrd0001() -> None:
    document = _document(version=5)
    encoded = dumps(document, profile="auto")
    assert encoded.startswith(b"NRRD0001\n")


# ── validator: flag an insufficient version as a diagnostic, not silently ──


def test_validate_flags_a_declared_version_too_old_for_populated_fields() -> None:
    document = _document(version=1, kinds="domain domain")
    report = validate(document)
    assert any(d.code == "nrrd.version.insufficient" for d in report.diagnostics)


def test_validate_flags_an_explicit_profile_argument_too_old() -> None:
    document = _document(version=5, thicknesses="1.0 1.0")
    report = validate(document, profile="NRRD0001")
    assert any(d.code == "nrrd.version.insufficient" for d in report.diagnostics)


def test_validate_reports_no_version_diagnostic_when_sufficient() -> None:
    document = _document(version=3, kinds="domain domain")
    report = validate(document)
    assert not any(d.code == "nrrd.version.insufficient" for d in report.diagnostics)


def test_validate_does_not_double_report_an_already_unsupported_profile() -> None:
    """An out-of-range profile string is `nrrd.profile.unsupported`; it must
    not also spuriously trigger the version-insufficiency diagnostic."""
    document = _document(version=1)
    report = validate(document, profile="NRRD0009")
    codes = [d.code for d in report.diagnostics]
    assert "nrrd.profile.unsupported" in codes
    assert "nrrd.version.insufficient" not in codes


# ── detected vs. declared version are distinct, reader-populated fields ────


def test_freshly_constructed_document_has_no_detected_version() -> None:
    document = _document(version=3)
    assert document.detected_version is None


def test_loading_a_file_records_its_actual_magic_line_version_as_detected() -> None:
    document = _document(version=1)
    encoded = dumps(document)
    reloaded = loads(encoded)
    assert reloaded.detected_version == 1
    assert reloaded.version == 1


def test_mutating_the_declared_version_never_touches_detected_version() -> None:
    """Exactly NRRD-LIFECYCLE-001's rule: the two are exposed separately, and
    changing what will be written does not silently rewrite what was
    detected on read."""
    document = loads(dumps(_document(version=1)))
    assert document.detected_version == 1
    document.version = 3
    document.header["kinds"] = "domain domain"
    assert document.detected_version == 1
    assert document.version == 3
    encoded = dumps(document)
    assert encoded.startswith(b"NRRD0003\n")


def test_to_dict_and_from_mapping_round_trip_detected_version() -> None:
    document = loads(dumps(_document(version=2)))
    assert document.detected_version == 2
    restored = NrrdDocument.from_mapping(document.to_dict())
    assert restored.detected_version == 2
