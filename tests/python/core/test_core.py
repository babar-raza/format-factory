"""Unit behavior for format-factory-core.

visibility: generated
generated_by: codex
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CORE_SRC = Path(__file__).resolve().parents[3] / "src" / "python" / "core" / "src"
sys.path.insert(0, str(CORE_SRC))

from format_factory.core import (  # noqa: E402
    Diagnostic,
    FormatFactoryError,
    ProbeResult,
    ResourceLimitError,
    ResourceLimits,
    Severity,
    SourceLocation,
    ValidationReport,
)


def test_empty_report_is_valid() -> None:
    assert ValidationReport().is_valid


def test_errors_make_report_invalid() -> None:
    report = ValidationReport(
        [
            Diagnostic("warning", "warning", Severity.WARNING),
            Diagnostic("invalid", "invalid value", Severity.ERROR),
        ]
    )
    assert not report.is_valid
    assert [item.code for item in report.errors] == ["invalid"]


def test_report_is_immutable_and_extensible() -> None:
    base = ValidationReport()
    extended = base.extend([Diagnostic("x", "message")])
    assert len(base.diagnostics) == 0
    assert len(extended.diagnostics) == 1


def test_location_rejects_negative_coordinates() -> None:
    with pytest.raises(ValueError, match="line"):
        SourceLocation(line=-1)


def test_limits_reject_non_positive_values() -> None:
    with pytest.raises(ValueError, match="max_entries"):
        ResourceLimits(max_entries=0)


def test_limits_enforce_named_ceiling() -> None:
    limits = ResourceLimits(max_input_bytes=4)
    with pytest.raises(ResourceLimitError) as captured:
        limits.enforce("max_input_bytes", 5)
    assert captured.value.context["maximum"] == 4


def test_limit_overrides_are_immutable() -> None:
    base = ResourceLimits()
    narrowed = base.with_overrides(max_entries=7)
    assert base.max_entries == 100_000
    assert narrowed.max_entries == 7


def test_common_error_has_stable_code_and_defensive_context() -> None:
    context = {"value": 1}
    error = FormatFactoryError("failed", context=context)
    context["value"] = 2
    assert error.code == "format_factory_error"
    assert error.context == {"value": 1}


def test_probe_result_validates_confidence_and_boolean_value() -> None:
    assert ProbeResult(True, 1.0, "ipynb")
    with pytest.raises(ValueError, match="confidence"):
        ProbeResult(False, 1.1, "ipynb")
