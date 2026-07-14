"""oracle_test_adapter.py — Pytest oracle case adapter (TC-W1B-001).

Provides fixtures and parametrize helpers so pytest tests can consume oracle
package case IDs without duplicating expected values.

Usage in test files:
    from tools.oracle.oracle_test_adapter import load_oracle_cases, pytest_oracle_params

    @pytest.mark.parametrize("case", pytest_oracle_params("csv"))
    def test_csv_oracle_case(case):
        ...
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ORACLE_ROOT = REPO_ROOT / "oracle" / "formats"


def load_oracle_cases(format_id: str, case_type: str = "valid") -> list[dict]:
    """Load oracle cases for a format from its oracle-package.yaml.

    Args:
        format_id: The format identifier (e.g., "csv", "fods")
        case_type: "valid", "invalid", "roundtrip", or "all"

    Returns:
        List of case dicts from the oracle package.
    """
    pkg_path = ORACLE_ROOT / format_id / "oracle-package.yaml"
    if not pkg_path.exists():
        raise FileNotFoundError(f"Oracle package not found: {pkg_path}")

    pkg = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))

    if case_type == "all":
        return (
            pkg.get("valid_cases", [])
            + pkg.get("invalid_cases", [])
            + pkg.get("roundtrip_cases", [])
        )
    elif case_type == "valid":
        return pkg.get("valid_cases", [])
    elif case_type == "invalid":
        return pkg.get("invalid_cases", [])
    elif case_type == "roundtrip":
        return pkg.get("roundtrip_cases", [])
    else:
        raise ValueError(f"Unknown case_type: {case_type!r}. Use 'valid', 'invalid', 'roundtrip', or 'all'.")


def load_oracle_package(format_id: str) -> dict:
    """Load the full oracle package dict for a format."""
    pkg_path = ORACLE_ROOT / format_id / "oracle-package.yaml"
    if not pkg_path.exists():
        raise FileNotFoundError(f"Oracle package not found: {pkg_path}")
    return yaml.safe_load(pkg_path.read_text(encoding="utf-8"))


def pytest_oracle_params(format_id: str, case_type: str = "valid") -> list[Any]:
    """Return pytest parametrize values for oracle cases.

    Each returned item is a dict containing the case fields from the oracle package.
    The test function receives the case dict directly.

    Example:
        @pytest.mark.parametrize("case", pytest_oracle_params("csv"))
        def test_csv_oracle(case):
            case_id = case["case_id"]
            # use case["expected_model_properties"] etc.

    Returns:
        List of case dicts suitable for pytest.mark.parametrize.
    """
    cases = load_oracle_cases(format_id, case_type)
    return cases


def resolve_sample_path(case: dict) -> Path | None:
    """Return the absolute path to a case's sample_ref, or None if absent."""
    sample_ref = case.get("sample_ref")
    if not sample_ref or sample_ref == "null":
        return None
    p = REPO_ROOT / sample_ref
    return p if p.exists() and p.is_file() else None


def get_expected_properties(case: dict) -> dict[str, Any]:
    """Extract expected_model_properties as a flat {property_name: value} dict."""
    props = case.get("expected_model_properties", [])
    return {p["property"]: p["value"] for p in props if "property" in p and "value" in p}


def run_oracle_case(format_id: str, case: dict, executor_module: str, executor_callable: str) -> dict:
    """Execute one oracle case using the specified module and callable.

    Args:
        format_id: e.g. "csv"
        case: oracle case dict from oracle-package.yaml
        executor_module: dotted module path, e.g. "csv_codec"
        executor_callable: function name, e.g. "parse_csv"

    Returns:
        The result dict from the callable (whatever the parser returns).
        If sample_ref is None or file missing, returns {"_skipped": True}.
    """
    sample_path = resolve_sample_path(case)
    if sample_path is None:
        return {"_skipped": True, "reason": "no_sample_file"}

    mod = importlib.import_module(executor_module)
    fn = getattr(mod, executor_callable)
    return fn(str(sample_path))
