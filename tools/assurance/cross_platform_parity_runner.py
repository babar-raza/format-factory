"""Cross-Platform Behavioral Parity Runner (TC-C2, playful-swimming-stearns).

Loads YAML parity fixtures, evaluates each one using reference Python implementations,
and verifies the result matches the hand-computed expected value.

The reference implementations are canonical — they define ground truth for both
Python and .NET implementations to agree with.
"""
from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Reference analytics implementations
# ---------------------------------------------------------------------------

def _parse_column(csv_text: str, column: str) -> list[str]:
    """Parse a CSV string and return all values for the named column (excluding header)."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return [row[column] for row in reader if row.get(column) is not None]


def _parse_numeric_column(csv_text: str, column: str) -> list[float]:
    """Parse numeric values from a column, skipping non-numeric rows."""
    values = []
    for v in _parse_column(csv_text, column):
        try:
            values.append(float(v))
        except (ValueError, TypeError):
            pass
    return values


def ref_get_column_mean(csv_text: str, column: str) -> float:
    vals = _parse_numeric_column(csv_text, column)
    return sum(vals) / len(vals) if vals else float("nan")


def ref_get_column_min(csv_text: str, column: str) -> float:
    vals = _parse_numeric_column(csv_text, column)
    return min(vals) if vals else float("nan")


def ref_get_column_max(csv_text: str, column: str) -> float:
    vals = _parse_numeric_column(csv_text, column)
    return max(vals) if vals else float("nan")


def ref_get_column_sum(csv_text: str, column: str) -> float:
    vals = _parse_numeric_column(csv_text, column)
    return sum(vals)


def ref_get_column_variance(csv_text: str, column: str) -> float:
    """Population variance."""
    vals = _parse_numeric_column(csv_text, column)
    if not vals:
        return float("nan")
    mean = sum(vals) / len(vals)
    return sum((v - mean) ** 2 for v in vals) / len(vals)


def ref_get_column_std(csv_text: str, column: str) -> float:
    """Population standard deviation."""
    return math.sqrt(ref_get_column_variance(csv_text, column))


def ref_get_column_median(csv_text: str, column: str) -> float:
    vals = sorted(_parse_numeric_column(csv_text, column))
    n = len(vals)
    if not n:
        return float("nan")
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def ref_get_column_entropy(csv_text: str, column: str) -> float:
    """Shannon entropy in bits."""
    raw = _parse_column(csv_text, column)
    if not raw:
        return 0.0
    from collections import Counter
    counts = Counter(raw)
    n = len(raw)
    entropy = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def ref_get_column_information_content(csv_text: str, column: str) -> float:
    """Information content in bits. After GAP-CSV-003 fix: equals entropy."""
    return ref_get_column_entropy(csv_text, column)


# Registry mapping method names to reference functions
_METHOD_REGISTRY: dict[str, Any] = {
    "get_column_mean": ref_get_column_mean,
    "GetColumnMean": ref_get_column_mean,
    "get_column_min": ref_get_column_min,
    "GetColumnMinValue": ref_get_column_min,
    "get_column_max": ref_get_column_max,
    "GetColumnMaxValue": ref_get_column_max,
    "get_column_sum": ref_get_column_sum,
    "GetColumnSum": ref_get_column_sum,
    "get_column_variance": ref_get_column_variance,
    "GetColumnVariance": ref_get_column_variance,
    "get_column_std": ref_get_column_std,
    "GetColumnStandardDeviation": ref_get_column_std,
    "get_column_median": ref_get_column_median,
    "GetColumnMedian": ref_get_column_median,
    "get_column_entropy": ref_get_column_entropy,
    "GetColumnEntropy": ref_get_column_entropy,
    "get_column_information_content": ref_get_column_information_content,
    "GetColumnInformationContent": ref_get_column_information_content,
}


# ---------------------------------------------------------------------------
# Fixture and result types
# ---------------------------------------------------------------------------

@dataclass
class ParityFixture:
    id: str
    method_dotnet: str
    method_python: str
    input: str
    column: str
    expected: float
    tolerance: float = 1.0e-9
    derivation: str = ""
    note: str = ""


@dataclass
class ParityResult:
    fixture_id: str
    method: str
    computed: float
    expected: float
    tolerance: float
    passed: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "fixture_id": self.fixture_id,
            "method": self.method,
            "computed": self.computed,
            "expected": self.expected,
            "tolerance": self.tolerance,
            "passed": self.passed,
            "delta": abs(self.computed - self.expected) if self.passed or self.error is None else None,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

class CrossPlatformParityRunner:
    """Run parity fixture checks and compare against hand-computed expected values."""

    def load_fixtures(self, yaml_path: Path) -> list[ParityFixture]:
        """Load fixtures from a YAML file."""
        try:
            import yaml  # type: ignore[import]
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except ImportError:
            # Fallback: minimal YAML parsing for simple flat lists
            data = self._parse_yaml_fallback(yaml_path)

        fixtures = []
        for f in data.get("fixtures", []):
            fixtures.append(ParityFixture(
                id=f["id"],
                method_dotnet=f.get("method_dotnet", ""),
                method_python=f.get("method_python", ""),
                input=f["input"],
                column=f["column"],
                expected=float(f["expected"]),
                tolerance=float(f.get("tolerance", 1e-9)),
                derivation=f.get("derivation", ""),
                note=f.get("note", ""),
            ))
        return fixtures

    def _parse_yaml_fallback(self, yaml_path: Path) -> dict:
        """Minimal YAML parser fallback (handles only simple fixtures format)."""
        import re
        content = yaml_path.read_text(encoding="utf-8")
        # Use Python's built-in for structured YAML-like data
        # This is a last resort — prefer installing pyyaml
        fixtures = []
        current: dict = {}
        for line in content.splitlines():
            line = line.rstrip()
            m = re.match(r'^  - id:\s+(.+)$', line)
            if m:
                if current:
                    fixtures.append(current)
                current = {"id": m.group(1).strip()}
                continue
            for key in ("method_dotnet", "method_python", "input", "column",
                        "expected", "tolerance", "derivation", "note"):
                m = re.match(rf'^    {key}:\s+(.+)$', line)
                if m:
                    current[key] = m.group(1).strip().strip('"')
                    break
        if current:
            fixtures.append(current)
        return {"fixtures": fixtures}

    def run_fixture(self, fixture: ParityFixture) -> ParityResult:
        """Evaluate a single fixture using the reference implementation."""
        # Look up the Python method name first, then the .NET name
        fn = _METHOD_REGISTRY.get(fixture.method_python) or _METHOD_REGISTRY.get(fixture.method_dotnet)
        if fn is None:
            return ParityResult(
                fixture_id=fixture.id,
                method=fixture.method_python or fixture.method_dotnet,
                computed=float("nan"),
                expected=fixture.expected,
                tolerance=fixture.tolerance,
                passed=False,
                error=f"No reference implementation for method: {fixture.method_python!r} / {fixture.method_dotnet!r}",
            )

        try:
            computed = fn(fixture.input, fixture.column)
            delta = abs(computed - fixture.expected)
            passed = delta <= fixture.tolerance
            return ParityResult(
                fixture_id=fixture.id,
                method=fixture.method_python or fixture.method_dotnet,
                computed=computed,
                expected=fixture.expected,
                tolerance=fixture.tolerance,
                passed=passed,
                error=None if passed else f"delta={delta:.2e} exceeds tolerance={fixture.tolerance:.2e}",
            )
        except Exception as e:
            return ParityResult(
                fixture_id=fixture.id,
                method=fixture.method_python or fixture.method_dotnet,
                computed=float("nan"),
                expected=fixture.expected,
                tolerance=fixture.tolerance,
                passed=False,
                error=str(e),
            )

    def run_all(self, fixtures: list[ParityFixture]) -> list[ParityResult]:
        return [self.run_fixture(f) for f in fixtures]

    def summary(self, results: list[ParityResult]) -> dict:
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        return {
            "total": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "pass": len(failed) == 0,
            "failures": [r.to_dict() for r in failed],
        }
