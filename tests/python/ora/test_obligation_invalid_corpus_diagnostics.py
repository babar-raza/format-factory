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
"""

from __future__ import annotations

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


def test_all_three_invalid_fixtures_remain_readable_zip_archives() -> None:
    # A weak negative fixture would be one that fails for the WRONG reason
    # (e.g. a corrupt ZIP central directory) rather than the specific
    # OpenRaster-level defect it names. Confirm each fixture's container-level
    # ZIP structure is intact by successfully reaching the OpenRaster-level
    # diagnostic layer at all, not an earlier ORA_UNREADABLE failure.
    for name in (
        "missing-layer-source.ora",
        "missing-thumbnail.ora",
        "corrupt-layer-source.ora",
    ):
        report = validate(SAMPLES / name)
        codes = [diagnostic.code for diagnostic in report.diagnostics]
        assert "ORA_UNREADABLE" not in codes, f"{name} failed before reaching OpenRaster-level checks"
