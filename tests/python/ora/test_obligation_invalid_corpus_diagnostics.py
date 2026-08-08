"""ORA-BASELINEASSET-001 / ORA-STACK-001 — file-based invalid-corpus diagnostics.

Every diagnostic code this module asserts on is already produced by
``format_factory.ora.lifecycle``'s ``validate``/``load`` (see
``_layer_png_diagnostics`` and ``_baseline_asset_diagnostics``); before this
file, none of ORA_THUMBNAIL_MISSING, ORA_LAYER_SOURCE_MISSING, or
ORA_LAYER_SOURCE_INVALID_PNG were exercised by any test in this suite, and
``samples/by-format/ora/invalid/`` had no fixture files at all (unlike every
other FF6 format's own ``invalid/`` directory). This file closes both gaps
together: real committed corpus fixtures, loaded from disk rather than built
in-memory, with tests that name each diagnostic explicitly.

Building the thumbnail/merged-image fixtures below surfaced a real,
previously-undiscovered bug: ``_baseline_asset_diagnostics``'s two
``except OraError`` clauses did not catch ``OraValidationError`` --
``read_png_metadata`` raises the latter for a structurally-invalid PNG, and
``OraError``/``OraValidationError`` are SIBLINGS (each descends directly
from a different `format_factory.core` base), not a hierarchy. The same gap
existed in `validate()`'s own outer handler, which also missed
``OraLimitError`` -- so a malformed ``stack.xml`` or an oversized/hostile
payload crashed `validate()` entirely instead of returning a report,
breaking its own explicitly documented "never raises" contract. Fixed by
naming all three sibling exception types explicitly at each site.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from format_factory.ora import OraValidationError, ReadMode, load, validate

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ora" / "invalid"


def test_missing_layer_source_is_reported_not_silently_accepted() -> None:
    path = SAMPLES / "missing-layer-source.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_LAYER_SOURCE_MISSING" in codes
    finding = next(d for d in report.diagnostics if d.code == "ORA_LAYER_SOURCE_MISSING")
    assert "data/layer.png" in finding.message


def test_missing_layer_source_strict_mode_raises() -> None:
    path = SAMPLES / "missing-layer-source.ora"
    with pytest.raises(OraValidationError, match="data/layer.png"):
        load(path, mode=ReadMode.STRICT)


def test_missing_layer_source_tolerant_mode_recovers_with_reporting() -> None:
    path = SAMPLES / "missing-layer-source.ora"
    image = load(path, mode=ReadMode.TOLERANT)
    assert any("data/layer.png" in action for action in image.recovery_actions)


def test_missing_thumbnail_is_reported_not_silently_accepted() -> None:
    path = SAMPLES / "missing-thumbnail.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_THUMBNAIL_MISSING" in codes


def test_missing_thumbnail_strict_mode_raises() -> None:
    path = SAMPLES / "missing-thumbnail.ora"
    with pytest.raises(OraValidationError, match="Thumbnails/thumbnail.png"):
        load(path, mode=ReadMode.STRICT)


def test_missing_thumbnail_tolerant_mode_recovers_with_reporting() -> None:
    path = SAMPLES / "missing-thumbnail.ora"
    image = load(path, mode=ReadMode.TOLERANT)
    assert any("thumbnail" in action.lower() for action in image.recovery_actions)


def test_corrupt_layer_source_is_reported_not_silently_accepted() -> None:
    path = SAMPLES / "corrupt-layer-source.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_LAYER_SOURCE_INVALID_PNG" in codes
    finding = next(
        d for d in report.diagnostics if d.code == "ORA_LAYER_SOURCE_INVALID_PNG"
    )
    assert "PNG" in finding.message


def test_corrupt_layer_source_strict_mode_raises() -> None:
    path = SAMPLES / "corrupt-layer-source.ora"
    with pytest.raises(OraValidationError, match="not a valid PNG"):
        load(path, mode=ReadMode.STRICT)


def test_corrupt_layer_source_tolerant_mode_recovers_with_reporting() -> None:
    path = SAMPLES / "corrupt-layer-source.ora"
    image = load(path, mode=ReadMode.TOLERANT)
    assert any("not a valid PNG" in action for action in image.recovery_actions)


def test_thumbnail_unreadable_is_reported_not_a_crash() -> None:
    # Regression guard: before the fix, read_png_metadata's OraValidationError
    # was not caught here at all and this call raised uncaught.
    path = SAMPLES / "thumbnail-unreadable.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_THUMBNAIL_UNREADABLE" in codes


def test_thumbnail_unreadable_strict_mode_raises_the_expected_error_type() -> None:
    path = SAMPLES / "thumbnail-unreadable.ora"
    with pytest.raises(OraValidationError, match="not a readable PNG"):
        load(path, mode=ReadMode.STRICT)


def test_thumbnail_non_conforming_is_reported() -> None:
    path = SAMPLES / "thumbnail-non-conforming.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_THUMBNAIL_NON_CONFORMING" in codes
    finding = next(d for d in report.diagnostics if d.code == "ORA_THUMBNAIL_NON_CONFORMING")
    assert "300x300" in finding.message


def test_mergedimage_unreadable_is_reported_not_a_crash() -> None:
    # Regression guard: same missing-except-type bug as the thumbnail case,
    # in the sibling merged-image branch of the same function.
    path = SAMPLES / "mergedimage-unreadable.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_MERGED_IMAGE_UNREADABLE" in codes


def test_mergedimage_non_conforming_is_reported() -> None:
    path = SAMPLES / "mergedimage-non-conforming.ora"
    report = validate(path)
    codes = [diagnostic.code for diagnostic in report.diagnostics]
    assert "ORA_MERGED_IMAGE_NON_CONFORMING" in codes
    finding = next(
        d for d in report.diagnostics if d.code == "ORA_MERGED_IMAGE_NON_CONFORMING"
    )
    assert "4" in finding.message


def test_malformed_stack_xml_is_reported_not_a_crash() -> None:
    # Regression guard for the broader outer-handler bug: parse_stack raises
    # OraValidationError for malformed XML, which validate()'s own
    # `except OraError` did not catch before the fix -- an extremely common
    # real-world malformed-input shape, not an edge case.
    valid_path = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ora" / "valid" / "minimal.ora"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as out, zipfile.ZipFile(valid_path) as src:
        for info in src.infolist():
            data = b"<not-well-formed-xml" if info.filename == "stack.xml" else src.read(info.filename)
            new_info = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            new_info.compress_type = info.compress_type
            out.writestr(new_info, data)

    report = validate(buffer.getvalue())

    assert report.is_valid is False
    assert report.diagnostics[0].code == "ORA_UNREADABLE"
    assert "not well-formed XML" in report.diagnostics[0].message


def test_all_invalid_fixtures_remain_readable_zip_archives() -> None:
    # A weak negative fixture would be one that fails for the WRONG reason
    # (e.g. a corrupt ZIP central directory) rather than the specific
    # OpenRaster-level defect it names. Confirm each fixture's container-level
    # ZIP structure is intact by successfully reaching the OpenRaster-level
    # diagnostic layer at all, not an earlier ORA_UNREADABLE failure.
    for name in (
        "missing-layer-source.ora",
        "missing-thumbnail.ora",
        "corrupt-layer-source.ora",
        "thumbnail-unreadable.ora",
        "thumbnail-non-conforming.ora",
        "mergedimage-unreadable.ora",
        "mergedimage-non-conforming.ora",
    ):
        report = validate(SAMPLES / name)
        codes = [diagnostic.code for diagnostic in report.diagnostics]
        assert "ORA_UNREADABLE" not in codes, f"{name} failed before reaching OpenRaster-level checks"
