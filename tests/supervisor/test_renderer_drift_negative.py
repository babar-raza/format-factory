"""Pilots C & D: Negative-control and contract-violation tests — TC-INT-006.

Pilot C: Scaffold is NOT maintained (is_maintained_test returns False on fresh scaffold).
Pilot D: PYTHON_ONLY_BY_DESIGN contract rejects non-Python language requests.
"""
from __future__ import annotations

import pytest

from tools.supervisor.test_drivers import (
    render_probe_test,
    render_getter_test,
    is_maintained_test,
    _validate_language,
    ContractViolationError,
)


def test_fresh_scaffold_is_not_maintained():
    """Pilot C: A freshly rendered probe scaffold must NOT be maintained.

    Confirms FIXTURE_REQUIRED/ORACLE_REQUIRED markers are present and
    is_maintained_test() returns False — a core contract for the scaffold workflow.
    """
    scaffold = render_probe_test(
        "src/python/ndjson/ndjson_codec.py",
        "probe_ndjson",
        "Ndjson",
    )
    assert not is_maintained_test(scaffold), (
        "Fresh scaffold must not pass is_maintained_test() — "
        "it still contains FIXTURE_REQUIRED or ORACLE_REQUIRED markers"
    )


def test_getter_scaffold_is_not_maintained():
    """Pilot C (getter): A freshly rendered getter scaffold is also not maintained."""
    scaffold = render_getter_test(
        "src/python/ndjson/ndjson_codec.py",
        "get_record_count",
        "model: dict",
        "int",
    )
    assert not is_maintained_test(scaffold), (
        "Fresh getter scaffold must not pass is_maintained_test()"
    )


def test_validate_language_python_passes():
    """Pilot D: Python language passes _validate_language without error."""
    _validate_language("python")  # Must not raise


def test_validate_language_csharp_raises_contract_violation():
    """Pilot D: PYTHON_ONLY_BY_DESIGN — csharp language raises ValueError.

    The driver system enforces PYTHON_ONLY_BY_DESIGN. Requesting a .NET
    or other language driver must raise a contract violation.
    """
    with pytest.raises((ValueError, ContractViolationError), match="PYTHON_ONLY_BY_DESIGN"):
        _validate_language("csharp")


def test_validate_language_dotnet_raises():
    """Pilot D: PYTHON_ONLY_BY_DESIGN — dotnet raises as well."""
    with pytest.raises((ValueError, ContractViolationError), match="PYTHON_ONLY_BY_DESIGN"):
        _validate_language("dotnet")
